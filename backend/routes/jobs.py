"""Background Jobs - Async processing simulation with progress tracking"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
import uuid
import asyncio
from config import db, logger
from utils.auth import get_current_user

router = APIRouter(prefix="/jobs")


@router.post("/submit")
async def submit_job(request_body: dict, user: dict = Depends(get_current_user)):
    """Submit a background job (document OCR, risk analysis, govt data retrieval)"""
    job_type = request_body.get("job_type", "risk_analysis")
    property_id = request_body.get("property_id")
    if not property_id:
        raise HTTPException(status_code=400, detail="property_id required")

    valid_types = ["risk_analysis", "document_ocr", "govt_data_retrieval", "title_verification", "valuation_report"]
    if job_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid job type. Must be one of: {valid_types}")

    job_id = f"job_{uuid.uuid4().hex[:12]}"
    job_doc = {
        "job_id": job_id,
        "job_type": job_type,
        "property_id": property_id,
        "user_id": user["user_id"],
        "status": "queued",
        "progress": 0,
        "steps": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.background_jobs.insert_one(job_doc)

    # Simulate async processing in background
    asyncio.create_task(_process_job(job_id, job_type, property_id))

    return {"job_id": job_id, "status": "queued", "message": f"{job_type} job submitted"}


@router.get("/status/{job_id}")
async def get_job_status(job_id: str, user: dict = Depends(get_current_user)):
    """Poll job status and progress"""
    job = await db.background_jobs.find_one(
        {"job_id": job_id, "user_id": user["user_id"]}, {"_id": 0}
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/list")
async def list_jobs(user: dict = Depends(get_current_user), limit: int = 20):
    """List user's background jobs"""
    jobs = await db.background_jobs.find(
        {"user_id": user["user_id"]}, {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    return {"jobs": jobs, "total": len(jobs)}


async def _process_job(job_id: str, job_type: str, property_id: str):
    """Simulate async processing with steps"""
    steps_map = {
        "risk_analysis": [
            ("Initializing risk engine", 10),
            ("Fetching property records", 25),
            ("Analyzing ownership history", 45),
            ("Checking legal encumbrances", 65),
            ("Computing risk score", 85),
            ("Generating report", 100),
        ],
        "document_ocr": [
            ("Loading document", 15),
            ("Running OCR extraction", 35),
            ("Classifying document type", 55),
            ("Extracting entities", 75),
            ("Validating extracted data", 90),
            ("Processing complete", 100),
        ],
        "govt_data_retrieval": [
            ("Connecting to state portals", 10),
            ("Querying Bhoomi (Karnataka)", 25),
            ("Querying IGRS registration", 40),
            ("Fetching CERSAI records", 55),
            ("Checking eCourts litigation", 70),
            ("Querying municipal records", 85),
            ("Compiling results", 100),
        ],
        "title_verification": [
            ("Loading title documents", 15),
            ("Extracting ownership chain", 35),
            ("Verifying each transfer", 55),
            ("Checking gap analysis", 75),
            ("Generating verification report", 100),
        ],
        "valuation_report": [
            ("Collecting market data", 15),
            ("Analyzing comparable properties", 35),
            ("Computing guideline value", 55),
            ("Estimating market value", 75),
            ("Generating valuation report", 100),
        ],
    }

    steps = steps_map.get(job_type, steps_map["risk_analysis"])

    try:
        await db.background_jobs.update_one(
            {"job_id": job_id},
            {"$set": {"status": "processing", "updated_at": datetime.now(timezone.utc).isoformat()}}
        )

        completed_steps = []
        for step_name, progress in steps:
            await asyncio.sleep(1.5)
            completed_steps.append({
                "name": step_name,
                "progress": progress,
                "completed_at": datetime.now(timezone.utc).isoformat(),
            })
            await db.background_jobs.update_one(
                {"job_id": job_id},
                {"$set": {
                    "progress": progress,
                    "current_step": step_name,
                    "steps": completed_steps,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }}
            )

        await db.background_jobs.update_one(
            {"job_id": job_id},
            {"$set": {
                "status": "completed",
                "progress": 100,
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "result": {"message": f"{job_type} completed successfully", "property_id": property_id},
            }}
        )
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        await db.background_jobs.update_one(
            {"job_id": job_id},
            {"$set": {"status": "failed", "error": str(e), "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
