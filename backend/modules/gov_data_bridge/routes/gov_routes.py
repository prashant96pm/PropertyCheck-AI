"""GovDataBridge REST API Routes"""
import asyncio
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import FileResponse
from datetime import datetime, timezone
from config import db, logger
from utils.auth import get_current_user
from modules.gov_data_bridge.models.gov_record import new_gov_job
from modules.gov_data_bridge.config.portals_config import get_all_states, get_portal, get_supported_documents, PORTALS
from modules.gov_data_bridge.queue.job_processor import process_gov_job

router = APIRouter(prefix="/gov")


@router.get("/states")
async def list_states():
    """List all supported states with document types and portal info"""
    states = get_all_states()
    return {"states": states, "total": len(states)}


@router.get("/portals/status")
async def get_portal_status():
    """Get live status of all government portals"""
    import os
    mock_mode = os.environ.get("GOV_MOCK_MODE", "true").lower() == "true"
    statuses = {}
    for state_key, portal in PORTALS.items():
        statuses[state_key] = {
            "name": portal["name"],
            "url": portal["url"],
            "status": "MOCK" if mock_mode else "UP",
            "documents": portal["documents"],
            "captcha_type": portal.get("captcha_type", "none"),
        }
    return {"portals": statuses, "total": len(statuses), "mock_mode": mock_mode}


@router.post("/fetch")
async def fetch_gov_record(request: Request, user: dict = Depends(get_current_user)):
    """Submit a government record fetch job"""
    body = await request.json()
    state = body.get("state", "").lower().replace(" ", "")
    document_type = body.get("documentType") or body.get("document_type")
    inputs = body.get("inputs", {})
    property_id = body.get("propertyId") or body.get("property_id", "")

    if not state or not document_type:
        raise HTTPException(status_code=400, detail="state and documentType are required")

    portal = get_portal(state)
    if not portal:
        raise HTTPException(status_code=400, detail=f"Unsupported state: {state}. Use /api/gov/states for list.")

    if document_type not in portal["documents"]:
        raise HTTPException(status_code=400, detail=f"Unsupported document type '{document_type}' for {state}. Available: {portal['documents']}")

    # Check cache first
    cached = await db.gov_records.find_one({
        "state": state, "document_type": document_type, "inputs": inputs,
        "status": "success", "cached_until": {"$gt": datetime.now(timezone.utc).isoformat()},
    }, {"_id": 0})

    if cached:
        return {
            "job_id": None,
            "status": "CACHED",
            "result": cached,
            "estimated_wait_time": 0,
            "message": "Record found in cache",
        }

    # Create job
    job = new_gov_job(user["user_id"], property_id, state, document_type, inputs)
    await db.gov_jobs.insert_one(job)

    # Process in background
    asyncio.create_task(process_gov_job(job["job_id"]))

    # Estimate wait: depends on captcha + portal complexity
    wait = 8 if portal.get("captcha_type") != "none" else 5

    return {
        "job_id": job["job_id"],
        "status": "PENDING",
        "estimated_wait_time": wait,
        "queue_position": 1,
        "message": f"Fetching {document_type} from {portal['name']} ({state})",
    }


@router.post("/fetch-bulk")
async def fetch_bulk(request: Request, user: dict = Depends(get_current_user)):
    """Submit bulk fetch jobs (max 10)"""
    body = await request.json()
    requests_list = body if isinstance(body, list) else body.get("requests", [])

    if len(requests_list) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 requests per bulk fetch")

    results = []
    for req in requests_list:
        state = req.get("state", "").lower().replace(" ", "")
        doc_type = req.get("documentType") or req.get("document_type")
        inputs = req.get("inputs", {})
        property_id = req.get("propertyId") or req.get("property_id", "")

        portal = get_portal(state)
        if not portal or doc_type not in portal.get("documents", []):
            results.append({"state": state, "document_type": doc_type, "error": "Invalid state or document type"})
            continue

        job = new_gov_job(user["user_id"], property_id, state, doc_type, inputs)
        await db.gov_jobs.insert_one(job)
        asyncio.create_task(process_gov_job(job["job_id"]))
        results.append({"job_id": job["job_id"], "state": state, "document_type": doc_type, "status": "PENDING"})

    return {"jobs": results, "total": len(results)}


@router.get("/job/{job_id}")
async def get_job_status(job_id: str, user: dict = Depends(get_current_user)):
    """Get job status and progress"""
    job = await db.gov_jobs.find_one({"job_id": job_id, "user_id": user["user_id"]}, {"_id": 0})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/document/{record_id}")
async def get_document(record_id: str):
    """Get a fetched government record by ID"""
    record = await db.gov_records.find_one({"record_id": record_id}, {"_id": 0})
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.get("/records/{property_id}")
async def get_property_records(property_id: str, user: dict = Depends(get_current_user)):
    """Get all government records fetched for a property"""
    records = await db.gov_records.find(
        {"property_id": property_id, "user_id": user["user_id"]}, {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    return {"records": records, "total": len(records)}


@router.get("/jobs/history")
async def get_job_history(user: dict = Depends(get_current_user), limit: int = 20):
    """Get user's gov data job history"""
    jobs = await db.gov_jobs.find(
        {"user_id": user["user_id"]}, {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    return {"jobs": jobs, "total": len(jobs)}


@router.get("/download/{state}/{document_type}/{job_id}")
async def download_pdf(state: str, document_type: str, job_id: str):
    """Download a locally stored PDF"""
    import os
    local_path = os.path.join("uploads", "gov_records", state, document_type, f"{job_id}.pdf")
    if not os.path.exists(local_path):
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(local_path, media_type="application/pdf", filename=f"{state}_{document_type}_{job_id}.pdf")
