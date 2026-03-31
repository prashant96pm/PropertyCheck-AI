"""GovRecord MongoDB model - extends existing motor async pattern"""
from datetime import datetime, timezone
from typing import Optional
import uuid


def new_gov_record(
    property_id: str,
    user_id: str,
    state: str,
    document_type: str,
    inputs: dict,
) -> dict:
    """Create a new GovRecord document for MongoDB"""
    return {
        "record_id": f"gov_{uuid.uuid4().hex[:12]}",
        "property_id": property_id,
        "user_id": user_id,
        "state": state,
        "document_type": document_type,
        "survey_number": inputs.get("surveyNumber", inputs.get("khasraNumber", inputs.get("plotNumber", inputs.get("gutNumber", "")))),
        "district": inputs.get("district", ""),
        "inputs": inputs,
        "structured_data": None,
        "pdf_s3_key": None,
        "pdf_url": None,
        "source_portal": None,
        "portal_fetched_at": None,
        "cached_until": None,
        "status": "pending",
        "error": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def new_gov_job(
    user_id: str,
    property_id: str,
    state: str,
    document_type: str,
    inputs: dict,
) -> dict:
    """Create a new Gov fetch job document"""
    return {
        "job_id": f"govjob_{uuid.uuid4().hex[:12]}",
        "user_id": user_id,
        "property_id": property_id,
        "state": state,
        "document_type": document_type,
        "inputs": inputs,
        "status": "PENDING",
        "attempts": 0,
        "max_attempts": 3,
        "progress": 0,
        "current_step": "Queued",
        "steps": [],
        "result": None,
        "error": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
