"""Enterprise API Layer - API key auth for banks, NBFCs, PropTech"""
from fastapi import APIRouter, HTTPException, Header, Depends
from datetime import datetime, timezone
import uuid
from config import db, logger

router = APIRouter(prefix="/enterprise/v1")


async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    api_client = await db.enterprise_api_keys.find_one({"api_key": x_api_key, "active": True}, {"_id": 0})
    if not api_client:
        raise HTTPException(status_code=401, detail="Invalid or inactive API key")
    await db.enterprise_api_keys.update_one({"api_key": x_api_key}, {"$inc": {"request_count": 1}, "$set": {"last_used": datetime.now(timezone.utc).isoformat()}})
    return api_client


@router.post("/api-keys")
async def create_api_key(org_name: str, contact_email: str):
    """Register for enterprise API access"""
    api_key = f"pck_{uuid.uuid4().hex}"
    await db.enterprise_api_keys.insert_one({
        "api_key": api_key, "org_name": org_name, "contact_email": contact_email,
        "active": True, "created_at": datetime.now(timezone.utc).isoformat(),
        "request_count": 0, "plan": "trial", "rate_limit": 100
    })
    return {"api_key": api_key, "org_name": org_name, "plan": "trial", "rate_limit": "100 requests/day"}


@router.get("/verify/{property_id}")
async def enterprise_verify_property(property_id: str, client: dict = Depends(verify_api_key)):
    """Quick property verification for enterprise clients"""
    prop = await db.properties.find_one({"property_id": property_id}, {"_id": 0})
    if not prop:
        prop = await db.property_registry.find_one({"property_id": property_id}, {"_id": 0})
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    report = await db.risk_reports.find_one({"property_id": property_id}, {"_id": 0}, sort=[("generated_at", -1)])
    return {
        "property_id": property_id,
        "survey_no": prop.get("survey_no"), "district": prop.get("district"), "state": prop.get("state"),
        "owner_name": prop.get("owner_name"),
        "risk_score": report.get("risk_score") if report else None,
        "risk_status": report.get("risk_status") if report else "NOT_ASSESSED",
        "verified_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/title-history/{property_id}")
async def enterprise_title_history(property_id: str, client: dict = Depends(verify_api_key)):
    """Title chain for enterprise clients"""
    from routes.intelligence import get_title_chain
    from fastapi import Request
    # Use mock request
    class MockReq:
        cookies = {}
        headers = {}
    return await get_title_chain(property_id, MockReq())


@router.get("/risk-score/{property_id}")
async def enterprise_risk_score(property_id: str, client: dict = Depends(verify_api_key)):
    """Risk score retrieval for enterprise clients"""
    report = await db.risk_reports.find_one({"property_id": property_id}, {"_id": 0}, sort=[("generated_at", -1)])
    if not report:
        raise HTTPException(status_code=404, detail="No risk assessment available")
    return {"property_id": property_id, "risk_score": report["risk_score"], "risk_status": report["risk_status"], "summary": report.get("summary"), "generated_at": report.get("generated_at")}
