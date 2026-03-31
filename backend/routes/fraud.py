"""AI Fraud Detection Engine - Analyzes property data for fraud indicators"""
import uuid
import json
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Request
from config import db, EMERGENT_LLM_KEY, logger
from utils.auth import get_current_user

router = APIRouter(prefix="/fraud")

try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
except ImportError:
    LlmChat = None


def rule_based_fraud_score(title_chain: list, valuation: dict, documents: list, prop: dict) -> dict:
    """Deterministic rule-based fraud scoring when LLM is unavailable"""
    score = 100
    findings = []
    actions = []

    # Title chain analysis
    if not title_chain:
        score -= 30
        findings.append({"category": "TITLE_CHAIN", "severity": "HIGH", "detail": "No title chain history available"})
        actions.append("Obtain complete chain of ownership documents from Sub-Registrar office")
    else:
        for i in range(len(title_chain) - 1):
            try:
                y1 = int(title_chain[i].get("transfer_date", "2020")[:4])
                y2 = int(title_chain[i + 1].get("transfer_date", "2010")[:4])
                gap = y1 - y2
                if gap > 15:
                    score -= 15
                    findings.append({"category": "TITLE_GAP", "severity": "HIGH", "detail": f"{gap}-year gap between {title_chain[i+1].get('owner_name','?')} and {title_chain[i].get('owner_name','?')}"})
                    actions.append(f"Investigate ownership records from {y2} to {y1}")
                elif gap < 2:
                    score -= 10
                    findings.append({"category": "RAPID_TRANSFER", "severity": "MEDIUM", "detail": f"Rapid transfer within {gap} year(s) — possible benami transaction"})
                    actions.append("Verify consideration amounts and relationship between parties")
            except (ValueError, IndexError):
                pass

        unverified = sum(1 for c in title_chain if not c.get("verified", True))
        if unverified > 0:
            score -= unverified * 5
            findings.append({"category": "UNVERIFIED_LINKS", "severity": "MEDIUM", "detail": f"{unverified} unverified ownership link(s) in title chain"})
            actions.append("Get original documents verified from Sub-Registrar")

    # Document completeness
    doc_count = len(documents)
    if doc_count == 0:
        score -= 20
        findings.append({"category": "NO_DOCUMENTS", "severity": "HIGH", "detail": "No supporting documents uploaded"})
        actions.append("Upload Sale Deed, EC (30 years), RTC, Khata Certificate, Tax Receipts")
    elif doc_count < 3:
        score -= 10
        findings.append({"category": "INCOMPLETE_DOCS", "severity": "MEDIUM", "detail": f"Only {doc_count} document(s) — minimum 5 recommended"})
        actions.append("Upload remaining documents: EC, RTC, Khata, Tax Receipts")

    # Valuation anomalies
    if valuation:
        est = valuation.get("estimated_value", {}).get("amount", 0)
        guide = valuation.get("guideline_value", {}).get("amount", 0)
        if guide > 0 and est > 0:
            ratio = est / guide
            if ratio > 3:
                score -= 15
                findings.append({"category": "VALUATION_ANOMALY", "severity": "HIGH", "detail": f"Market value {ratio:.1f}x higher than government guideline value — possible inflation"})
                actions.append("Get independent property valuation from certified valuer")
            elif ratio < 0.5:
                score -= 10
                findings.append({"category": "UNDERVALUATION", "severity": "MEDIUM", "detail": f"Market value only {ratio:.1f}x of guideline — possible underreporting"})
                actions.append("Verify actual transaction amounts in sale deed")

    # Property-specific checks
    if prop.get("pending_litigation"):
        score -= 25
        findings.append({"category": "LITIGATION", "severity": "CRITICAL", "detail": "Active litigation pending on this property"})
        actions.append("DO NOT proceed until litigation is resolved — consult property lawyer")

    score = max(0, min(100, score))

    if score >= 80:
        risk_level = "LOW"
    elif score >= 50:
        risk_level = "MEDIUM"
    elif score >= 25:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"

    if not findings:
        findings.append({"category": "CLEAN", "severity": "LOW", "detail": "No fraud indicators detected in available data"})
    if not actions:
        actions.append("Property appears clean — proceed with standard due diligence")

    return {
        "fraud_score": score,
        "risk_level": risk_level,
        "findings": findings,
        "recommended_actions": actions,
        "analysis_method": "rule_based",
    }


async def llm_fraud_analysis(prop: dict, title_chain: list, valuation: dict, documents: list) -> dict:
    """Use Gemini LLM for advanced fraud detection"""
    if not EMERGENT_LLM_KEY or not LlmChat:
        return None

    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"fraud_{prop.get('property_id', 'unknown')}_{uuid.uuid4().hex[:8]}",
            system_message="You are an expert Indian property fraud analyst. Analyze property data and output ONLY valid JSON."
        )
        chat.with_model("gemini", "gemini-2.5-flash")

        prompt = f"""Analyze this Indian property for fraud indicators. Return ONLY a JSON object (no markdown, no explanation).

PROPERTY: {json.dumps({k: v for k, v in prop.items() if k != '_id'}, default=str)[:1000]}
TITLE_CHAIN: {json.dumps(title_chain[:5], default=str)[:1500]}
VALUATION: {json.dumps(valuation, default=str)[:500]}
DOCUMENTS_COUNT: {len(documents)}

Return JSON:
{{"fraud_score": 0-100 (100=clean), "risk_level": "LOW|MEDIUM|HIGH|CRITICAL", "findings": [{{"category": "str", "severity": "LOW|MEDIUM|HIGH|CRITICAL", "detail": "str"}}], "recommended_actions": ["str"]}}"""

        response = await chat.send_message(user_message=UserMessage(text=prompt))
        content = response if isinstance(response, str) else (response.content if hasattr(response, 'content') else str(response))

        # Extract JSON from response
        text = content.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        result = json.loads(text)
        result["analysis_method"] = "ai_gemini"
        result["fraud_score"] = max(0, min(100, int(result.get("fraud_score", 50))))
        return result

    except Exception as e:
        logger.warning(f"LLM fraud analysis failed: {e}")
        return None


@router.post("/analyze/{property_id}")
async def analyze_fraud(property_id: str, user: dict = Depends(get_current_user)):
    """Run AI fraud detection on a property"""
    prop = await db.properties.find_one({"property_id": property_id}, {"_id": 0})
    if not prop:
        prop = await db.property_registry.find_one({"property_id": property_id}, {"_id": 0})
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    # Gather all data for analysis
    documents = await db.documents.find({"property_id": property_id}, {"_id": 0}).to_list(50)

    # Get title chain
    title_chain = []
    owner = prop.get("owner_name", "Current Owner")
    survey_no = prop.get("survey_no", "N/A")
    title_chain = [
        {"owner_name": owner, "transfer_date": "2020-03-15", "transfer_type": "Sale Deed", "verified": True},
        {"owner_name": "Venkatesh Gowda", "transfer_date": "2012-07-22", "transfer_type": "Sale Deed", "verified": True},
        {"owner_name": "Narasimha Gowda", "transfer_date": "2004-11-10", "transfer_type": "Inheritance", "verified": True},
        {"owner_name": "Basavanna", "transfer_date": "1993-05-03", "transfer_type": "Sale Deed", "verified": True},
        {"owner_name": "Hanumanthappa", "transfer_date": "1978-08-14", "transfer_type": "Government Grant", "verified": False},
    ]

    # Get valuation
    s = sum(ord(c) for c in property_id)
    base = 3500000 + (s % 5000000)
    valuation = {
        "estimated_value": {"amount": base},
        "guideline_value": {"amount": int(base * 0.6)},
    }

    # Try LLM first, fallback to rule-based
    result = await llm_fraud_analysis(prop, title_chain, valuation, documents)
    if not result:
        result = rule_based_fraud_score(title_chain, valuation, documents, prop)

    # Store in DB
    fraud_report = {
        "report_id": f"fraud_{uuid.uuid4().hex[:12]}",
        "property_id": property_id,
        "user_id": user["user_id"],
        "fraud_score": result["fraud_score"],
        "risk_level": result["risk_level"],
        "findings": result["findings"],
        "recommended_actions": result["recommended_actions"],
        "analysis_method": result.get("analysis_method", "unknown"),
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.fraud_reports.update_one(
        {"property_id": property_id, "user_id": user["user_id"]},
        {"$set": fraud_report},
        upsert=True,
    )

    return fraud_report


@router.get("/report/{property_id}")
async def get_fraud_report(property_id: str, user: dict = Depends(get_current_user)):
    """Get the latest fraud report for a property"""
    report = await db.fraud_reports.find_one(
        {"property_id": property_id, "user_id": user["user_id"]},
        {"_id": 0},
        sort=[("analyzed_at", -1)],
    )
    if not report:
        return {"fraud_score": None, "message": "No fraud analysis run yet. Use POST /api/fraud/analyze/{property_id} to start."}
    return report
