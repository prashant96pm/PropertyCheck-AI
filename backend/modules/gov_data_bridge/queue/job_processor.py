"""Job Processor - Async background processing for gov data fetching"""
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from config import db
from modules.gov_data_bridge.scrapers import get_scraper
from modules.gov_data_bridge.storage.document_storage import DocumentStorage

logger = logging.getLogger("govdatabridge")

CACHE_TTL_HOURS = 24
storage = DocumentStorage()


async def process_gov_job(job_id: str):
    """Process a single government data fetch job with step tracking"""
    job = await db.gov_jobs.find_one({"job_id": job_id}, {"_id": 0})
    if not job:
        logger.error(f"Job {job_id} not found")
        return

    state = job["state"]
    doc_type = job["document_type"]
    inputs = job["inputs"]
    steps = []

    async def update_step(name: str, progress: int):
        steps.append({"name": name, "progress": progress, "at": datetime.now(timezone.utc).isoformat()})
        await db.gov_jobs.update_one(
            {"job_id": job_id},
            {"$set": {"status": "PROCESSING", "progress": progress, "current_step": name, "steps": steps, "attempts": job.get("attempts", 0) + 1, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )

    try:
        # Step 1: Check cache
        await update_step(f"Checking cache for {state} {doc_type}", 10)
        await asyncio.sleep(0.5)

        cached = await db.gov_records.find_one({
            "state": state,
            "document_type": doc_type,
            "inputs": inputs,
            "status": "success",
            "cached_until": {"$gt": datetime.now(timezone.utc).isoformat()},
        }, {"_id": 0})

        if cached:
            await update_step("Cache hit - returning stored data", 100)
            await db.gov_jobs.update_one(
                {"job_id": job_id},
                {"$set": {"status": "COMPLETED", "progress": 100, "result": cached, "current_step": "Completed (cached)", "updated_at": datetime.now(timezone.utc).isoformat()}}
            )
            return

        # Step 2: Initialize scraper
        await update_step(f"Initializing {state.title()} portal scraper", 20)
        await asyncio.sleep(0.5)

        scraper = get_scraper(state)
        if not scraper:
            raise Exception(f"No scraper available for state: {state}")

        # Step 3: Connect to portal
        await update_step(f"Connecting to {scraper.name} portal", 30)
        await asyncio.sleep(0.8)

        # Step 4: Solve CAPTCHA if needed
        if scraper.captcha_type != "none":
            await update_step(f"Solving {scraper.captcha_type} CAPTCHA", 40)
            await asyncio.sleep(1.0)

        # Step 5: Submit form and fetch data
        await update_step(f"Fetching {doc_type} records", 55)
        await asyncio.sleep(1.0)

        result = await scraper.fetch(inputs, doc_type)

        # Step 6: Parse and structure data
        await update_step("Parsing and structuring data", 70)
        await asyncio.sleep(0.5)

        # Step 7: Generate/store PDF
        await update_step("Generating PDF document", 85)
        pdf_bytes = await storage.generate_mock_pdf(state, doc_type, result.get("structured_data", {}))
        upload_result = await storage.upload_pdf(pdf_bytes, state, doc_type, job_id)

        result["pdf_url"] = upload_result.get("pdf_url")
        result["pdf_s3_key"] = upload_result.get("s3_key")

        # Step 8: Store in cache
        await update_step("Caching results", 95)
        cache_until = (datetime.now(timezone.utc) + timedelta(hours=CACHE_TTL_HOURS)).isoformat()

        record_doc = {
            "record_id": f"rec_{job_id}",
            "job_id": job_id,
            "user_id": job["user_id"],
            "property_id": job["property_id"],
            "state": state,
            "document_type": doc_type,
            "inputs": inputs,
            "structured_data": result.get("structured_data"),
            "pdf_s3_key": result.get("pdf_s3_key"),
            "pdf_url": result.get("pdf_url"),
            "source_portal": result.get("portal_name"),
            "portal_fetched_at": result.get("fetched_at"),
            "cached_until": cache_until,
            "status": "success",
            "source": result.get("source", "mock"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.gov_records.update_one(
            {"state": state, "document_type": doc_type, "inputs": inputs},
            {"$set": record_doc},
            upsert=True,
        )

        # Step 9: Complete
        await update_step("Completed", 100)
        await db.gov_jobs.update_one(
            {"job_id": job_id},
            {"$set": {
                "status": "COMPLETED",
                "progress": 100,
                "current_step": "Completed",
                "result": {
                    "record_id": record_doc["record_id"],
                    "structured_data": result.get("structured_data"),
                    "pdf_url": result.get("pdf_url"),
                    "portal_name": result.get("portal_name"),
                    "fetched_at": result.get("fetched_at"),
                    "source": result.get("source"),
                },
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }}
        )
        logger.info(f"Job {job_id} completed successfully")

    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        attempts = job.get("attempts", 0) + 1
        status = "FAILED" if attempts >= job.get("max_attempts", 3) else "PENDING"
        await db.gov_jobs.update_one(
            {"job_id": job_id},
            {"$set": {
                "status": status,
                "error": str(e),
                "attempts": attempts,
                "current_step": f"Failed: {str(e)[:100]}",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }}
        )
