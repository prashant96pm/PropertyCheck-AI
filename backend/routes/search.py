"""Universal Search Engine - Smart search, fuzzy matching, sample registry"""
from fastapi import APIRouter, Query, Request
from typing import Optional, List, Dict
from datetime import datetime, timezone
import uuid
import json
import re
from rapidfuzz import fuzz

from config import db, EMERGENT_LLM_KEY, logger
from utils.auth import get_optional_user

try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
except ImportError:
    LlmChat = None

router = APIRouter()


async def get_sample_property_registry(limit: int = 20) -> List[Dict]:
    count = await db.property_registry.count_documents({})
    if count < 5:
        await seed_sample_property_registry()
    return await db.property_registry.find({}, {"_id": 0}).limit(limit).to_list(limit)

async def seed_sample_property_registry():
    sample_properties = [
        {"property_id": f"reg_{uuid.uuid4().hex[:12]}", "survey_no": "123/4", "khata_no": "KH-2024-001", "plot_no": "45", "owner_name": "Ramesh Kumar", "father_name": "Late Suresh Kumar", "state": "Karnataka", "district": "Bengaluru Urban", "taluk": "Anekal", "village": "Sarjapur", "extent": "2 Acres 30 Guntas", "land_type": "Agricultural", "risk_status": "GREEN", "risk_score": 85, "registered_at": datetime.now(timezone.utc).isoformat()},
        {"property_id": f"reg_{uuid.uuid4().hex[:12]}", "survey_no": "456/2", "khata_no": "KH-2024-002", "plot_no": "102", "owner_name": "Priya Sharma", "father_name": "Mohan Sharma", "state": "Karnataka", "district": "Bengaluru Urban", "taluk": "Whitefield", "village": "Varthur", "extent": "1200 Sq Ft", "land_type": "Residential", "risk_status": "YELLOW", "risk_score": 62, "registered_at": datetime.now(timezone.utc).isoformat()},
        {"property_id": f"reg_{uuid.uuid4().hex[:12]}", "survey_no": "789/1", "khata_no": "KH-2024-003", "plot_no": "78", "owner_name": "Venkatesh Reddy", "father_name": "Narasimha Reddy", "state": "Telangana", "district": "Hyderabad", "taluk": "Madhapur", "village": "Gachibowli", "extent": "500 Sq Yards", "land_type": "Commercial", "risk_status": "GREEN", "risk_score": 92, "registered_at": datetime.now(timezone.utc).isoformat()},
        {"property_id": f"reg_{uuid.uuid4().hex[:12]}", "survey_no": "234/5", "khata_no": "KH-2024-004", "plot_no": "23", "owner_name": "Anil Patel", "father_name": "Kantilal Patel", "state": "Gujarat", "district": "Ahmedabad", "taluk": "Gandhinagar", "village": "Sabarmati", "extent": "3 Acres", "land_type": "Agricultural", "risk_status": "RED", "risk_score": 35, "registered_at": datetime.now(timezone.utc).isoformat()},
        {"property_id": f"reg_{uuid.uuid4().hex[:12]}", "survey_no": "567/8", "khata_no": "KH-2024-005", "plot_no": "156", "owner_name": "Lakshmi Narayanan", "father_name": "Krishnamurthy", "state": "Tamil Nadu", "district": "Chennai", "taluk": "Tambaram", "village": "Pallikaranai", "extent": "2400 Sq Ft", "land_type": "Residential", "risk_status": "GREEN", "risk_score": 78, "registered_at": datetime.now(timezone.utc).isoformat()},
    ]
    for prop in sample_properties:
        await db.property_registry.update_one({"survey_no": prop["survey_no"], "state": prop["state"]}, {"$set": prop}, upsert=True)


def fuzzy_match_name(query_name: str, target_name: str, threshold: int = 70):
    if not query_name or not target_name:
        return False, 0
    q, t = query_name.lower().strip(), target_name.lower().strip()
    if q == t:
        return True, 100
    best = max(fuzz.ratio(q, t), fuzz.partial_ratio(q, t), fuzz.token_sort_ratio(q, t))
    return best >= threshold, best


def parse_query_fallback(query: str) -> dict:
    params = {}
    ql = query.lower()
    survey_m = re.search(r'survey\s*(?:no\.?|number)?\s*[:\s]?\s*(\d+[/\-]?\d*)', ql)
    if survey_m: params["survey_no"] = survey_m.group(1)
    plot_m = re.search(r'plot\s*(?:no\.?|number)?\s*[:\s]?\s*(\d+)', ql)
    if plot_m: params["plot_no"] = plot_m.group(1)
    states = ["karnataka", "maharashtra", "telangana", "andhra pradesh", "tamil nadu", "kerala", "gujarat", "rajasthan", "uttar pradesh", "madhya pradesh"]
    for s in states:
        if s in ql: params["state"] = s.title(); break
    cities = {"bengaluru": "Bengaluru Urban", "bangalore": "Bengaluru Urban", "mumbai": "Mumbai", "hyderabad": "Hyderabad", "chennai": "Chennai", "pune": "Pune", "ahmedabad": "Ahmedabad", "delhi": "Delhi"}
    for ck, cv in cities.items():
        if ck in ql: params["district"] = cv; break
    owned_by = re.search(r'(?:owned by|owner|belonging to)\s+([a-zA-Z\s]+?)(?:\s+in|\s+at|$)', ql)
    if owned_by: params["owner_name"] = owned_by.group(1).strip().title()
    return params


@router.get("/property/search")
async def search_properties(
    owner_name: Optional[str] = Query(None), survey_no: Optional[str] = Query(None),
    plot_no: Optional[str] = Query(None), khata_no: Optional[str] = Query(None),
    registration_no: Optional[str] = Query(None), district: Optional[str] = Query(None),
    state: Optional[str] = Query(None), village: Optional[str] = Query(None),
    taluk: Optional[str] = Query(None), land_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), request: Request = None
):
    query = {}
    for key, val in [("survey_no", survey_no), ("plot_no", plot_no), ("khata_no", khata_no), ("district", district), ("state", state), ("village", village), ("taluk", taluk), ("land_type", land_type)]:
        if val: query[key] = {"$regex": val, "$options": "i"}
    if not query and not owner_name:
        results = await get_sample_property_registry(limit)
        return {"results": results, "total": len(results), "page": page, "limit": limit, "search_type": "sample_registry"}
    skip = (page - 1) * limit
    properties = await db.properties.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    registry = await db.property_registry.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    all_results = properties + registry
    if owner_name:
        fuzzy_results = []
        for p in all_results:
            is_match, score = fuzzy_match_name(owner_name, p.get("owner_name", ""))
            if is_match: p["match_confidence"] = score; fuzzy_results.append(p)
        owner_q = {"owner_name": {"$regex": owner_name, "$options": "i"}}
        for p in await db.properties.find(owner_q, {"_id": 0}).limit(limit).to_list(limit) + await db.property_registry.find(owner_q, {"_id": 0}).limit(limit).to_list(limit):
            if p not in fuzzy_results: p["match_confidence"] = 100; fuzzy_results.append(p)
        all_results = sorted(fuzzy_results, key=lambda x: x.get("match_confidence", 0), reverse=True)[:limit]
    total = await db.properties.count_documents(query) + await db.property_registry.count_documents(query)
    return {"results": all_results, "total": total, "page": page, "limit": limit, "search_type": "multi_parameter"}


@router.post("/property/ai-smart-search")
async def ai_smart_search(request: Request):
    body = await request.json()
    query_text = body.get("query", "")
    parsed_params = parse_query_fallback(query_text)
    if EMERGENT_LLM_KEY and LlmChat:
        try:
            chat = LlmChat(api_key=EMERGENT_LLM_KEY, model="gemini-2.0-flash")
            prompt = f"""Parse this property search query and return ONLY JSON:\nQuery: "{query_text}"\nReturn: {{"owner_name": null, "survey_no": null, "district": null, "state": null, "village": null, "taluk": null, "land_type": null}}"""
            response = await chat.send_message(user_message=UserMessage(content=prompt))
            resp_text = response.content if hasattr(response, 'content') else str(response)
            if "```json" in resp_text: resp_text = resp_text.split("```json")[1].split("```")[0]
            elif "```" in resp_text: resp_text = resp_text.split("```")[1].split("```")[0]
            parsed_params = json.loads(resp_text.strip())
        except Exception as e:
            logger.warning(f"LLM parse failed: {e}")
    query = {}
    for key in ["survey_no", "plot_no", "khata_no", "district", "state", "village", "taluk", "land_type"]:
        if parsed_params.get(key): query[key] = {"$regex": str(parsed_params[key]), "$options": "i"}
    all_results = await db.properties.find(query, {"_id": 0}).limit(20).to_list(20) + await db.property_registry.find(query, {"_id": 0}).limit(20).to_list(20)
    if parsed_params.get("owner_name"):
        filtered = []
        for p in all_results:
            is_match, score = fuzzy_match_name(str(parsed_params["owner_name"]), p.get("owner_name", ""))
            if is_match: p["match_confidence"] = score; filtered.append(p)
        all_results = sorted(filtered, key=lambda x: x.get("match_confidence", 0), reverse=True) if filtered else all_results
    if not all_results:
        sample = await get_sample_property_registry(10)
        return {"query_parsed": parsed_params, "results": sample, "total": len(sample), "search_type": "ai_smart_search", "note": "No exact matches found. Showing sample properties for review."}
    return {"query_parsed": parsed_params, "results": all_results[:20], "total": len(all_results), "search_type": "ai_smart_search"}


@router.get("/property/full-profile/{property_id}")
async def get_full_property_profile(property_id: str, request: Request):
    prop = await db.properties.find_one({"property_id": property_id}, {"_id": 0})
    if not prop:
        prop = await db.property_registry.find_one({"property_id": property_id}, {"_id": 0})
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    from routes.intelligence import get_ownership_history, get_legal_records
    ownership = get_ownership_history(prop)
    legal = get_legal_records(prop)
    docs = await db.documents.find({"property_id": property_id}, {"_id": 0}).to_list(50)
    risk = await db.risk_reports.find_one({"property_id": property_id}, {"_id": 0}, sort=[("generated_at", -1)])
    return {
        "property_id": property_id,
        "basic_details": {k: v for k, v in prop.items() if k not in ("_id",)},
        "ownership_history": ownership,
        "legal_records": legal,
        "documents": docs,
        "geo_spatial": {"coordinates": prop.get("coordinates"), "boundaries": prop.get("boundaries")},
        "risk_assessment": {k: v for k, v in risk.items() if k != "_id"} if risk else None,
        "government_records": {"source": "State Land Records Portal", "survey_no": prop.get("survey_no"), "state": prop.get("state")}
    }


from fastapi import HTTPException


@router.get("/property/documents/{property_id}")
async def get_property_documents(property_id: str, request: Request):
    """Get all documents for a property including registry documents"""
    from utils.auth import get_current_user
    user = None
    try:
        user = await get_current_user(request)
    except Exception:
        pass

    user_docs = await db.documents.find({"property_id": property_id}, {"_id": 0}).to_list(50)
    registry_docs = [
        {"doc_type": "encumbrance_certificate", "doc_name": "Encumbrance Certificate (EC)", "source": "Sub-Registrar Office", "date_range": "1995-2024", "is_available": True, "status": "Available for download"},
        {"doc_type": "rtc_pahani", "doc_name": "RTC / Pahani", "source": "Bhoomi Portal", "date_range": "Current", "is_available": True, "status": "Available"},
        {"doc_type": "khata_certificate", "doc_name": "Khata Certificate", "source": "BBMP/Municipality", "date_range": "Current", "is_available": True, "status": "Available"},
        {"doc_type": "cadastral_map", "doc_name": "Cadastral Map (Bhu-Naksha)", "source": "Survey Department", "date_range": "Current", "is_available": True, "status": "Available"},
        {"doc_type": "mutation_records", "doc_name": "Mutation Records", "source": "Revenue Department", "date_range": "2000-2024", "is_available": True, "status": "5 records found"},
    ]
    return {"property_id": property_id, "uploaded_documents": user_docs, "registry_documents": registry_docs, "total_documents": len(user_docs) + len(registry_docs)}


@router.get("/property/ownership-history/{property_id}")
async def get_property_ownership_history(property_id: str, request: Request):
    """Get detailed ownership history"""
    prop = await db.properties.find_one({"property_id": property_id}, {"_id": 0})
    if not prop:
        prop = await db.property_registry.find_one({"property_id": property_id}, {"_id": 0})
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    from routes.intelligence import get_ownership_history
    history = get_ownership_history(prop)
    return {"property_id": property_id, "ownership_chain": history, "total_transfers": len(history), "first_recorded": history[-1].get("transfer_date") if history else None, "current_owner": history[0].get("owner_name") if history else None}


@router.get("/property/legal-records/{property_id}")
async def get_property_legal_records(property_id: str, request: Request):
    """Get legal records for a property"""
    prop = await db.properties.find_one({"property_id": property_id}, {"_id": 0})
    if not prop:
        prop = await db.property_registry.find_one({"property_id": property_id}, {"_id": 0})
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    from routes.intelligence import get_legal_records
    legal = get_legal_records(prop)
    return {"property_id": property_id, **legal}
