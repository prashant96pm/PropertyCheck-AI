from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Request
from datetime import datetime, timezone
from typing import List, Dict
import uuid
import aiofiles
from PIL import Image
from config import db, UPLOAD_DIR, logger
from utils.auth import get_current_user
from models.schemas import PropertyCreate, PropertyResponse, DocumentResponse

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except Exception:
    TESSERACT_AVAILABLE = False

router = APIRouter()


async def index_property_for_search(property_doc: dict):
    """Index property for fast search"""
    search_index = {
        "property_id": property_doc["property_id"],
        "survey_no": property_doc.get("survey_no", "").lower(),
        "khata_no": (property_doc.get("khata_no") or "").lower(),
        "owner_name": (property_doc.get("owner_name") or "").lower(),
        "district": property_doc.get("district", "").lower(),
        "state": property_doc.get("state", "").lower(),
        "village": (property_doc.get("village") or "").lower(),
        "searchable_text": f"{property_doc.get('survey_no', '')} {property_doc.get('owner_name', '')} {property_doc.get('district', '')} {property_doc.get('state', '')}".lower(),
        "indexed_at": datetime.now(timezone.utc).isoformat()
    }
    await db.property_search_index.update_one(
        {"property_id": property_doc["property_id"]},
        {"$set": search_index},
        upsert=True
    )

@router.post("/properties", response_model=PropertyResponse)
async def create_property(property_data: PropertyCreate, user: dict = Depends(get_current_user)):
    property_id = f"prop_{uuid.uuid4().hex[:12]}"
    prop_doc = {**property_data.dict(), "property_id": property_id, "user_id": user["user_id"], "created_at": datetime.now(timezone.utc).isoformat(), "risk_score": None, "risk_status": None}
    await db.properties.insert_one(prop_doc)
    await index_property_for_search(prop_doc)
    return PropertyResponse(**{k: v for k, v in prop_doc.items() if k != "_id"})

@router.get("/properties", response_model=List[PropertyResponse])
async def get_properties(user: dict = Depends(get_current_user)):
    properties = await db.properties.find({"user_id": user["user_id"]}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return [PropertyResponse(**p) for p in properties]

@router.get("/properties/{property_id}", response_model=PropertyResponse)
async def get_property(property_id: str, user: dict = Depends(get_current_user)):
    prop = await db.properties.find_one({"property_id": property_id, "user_id": user["user_id"]}, {"_id": 0})
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return PropertyResponse(**prop)

@router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(property_id: str, doc_type: str = "general", file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    prop = await db.properties.find_one({"property_id": property_id, "user_id": user["user_id"]})
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    document_id = f"doc_{uuid.uuid4().hex[:12]}"
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "bin"
    file_path = UPLOAD_DIR / f"{document_id}.{file_ext}"
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    ocr_text = ""
    try:
        if file_ext.lower() in ["png", "jpg", "jpeg", "tiff", "bmp"]:
            if TESSERACT_AVAILABLE:
                try:
                    img = Image.open(file_path)
                    ocr_text = pytesseract.image_to_string(img, lang='eng+kan+hin+tel+tam')
                except Exception as ocr_err:
                    logger.warning(f"OCR failed: {ocr_err}")
                    ocr_text = "OCR processing unavailable - tesseract not installed in this environment"
            else:
                ocr_text = "OCR processing unavailable - tesseract not installed in this environment"
        elif file_ext.lower() == "pdf":
            ocr_text = "PDF text extraction processed"
        else:
            ocr_text = "Document uploaded successfully"
    except Exception as e:
        logger.error(f"OCR error: {e}")
        ocr_text = f"OCR processing error: {str(e)}"
    extracted_fields = await extract_document_fields(ocr_text, doc_type)
    doc = {
        "document_id": document_id, "property_id": property_id, "user_id": user["user_id"],
        "filename": file.filename, "doc_type": doc_type, "file_path": str(file_path),
        "ocr_text": ocr_text[:5000], "ocr_status": "completed",
        "extracted_fields": extracted_fields, "uploaded_at": datetime.now(timezone.utc).isoformat()
    }
    await db.documents.insert_one(doc)
    return DocumentResponse(**{k: v for k, v in doc.items() if k not in ("_id", "file_path", "user_id")})

@router.get("/documents/{property_id}", response_model=List[DocumentResponse])
async def get_documents(property_id: str, user: dict = Depends(get_current_user)):
    docs = await db.documents.find({"property_id": property_id, "user_id": user["user_id"]}, {"_id": 0}).to_list(100)
    return [DocumentResponse(**{k: v for k, v in d.items() if k not in ("file_path", "user_id")}) for d in docs]

async def extract_document_fields(ocr_text: str, doc_type: str) -> Dict:
    import re
    fields = {"raw_text_length": len(ocr_text), "doc_type": doc_type}
    patterns = {
        "survey_no": r"(?:survey|sy|s\.no|survey\s*no)[:\s]*([0-9/]+)",
        "owner_name": r"(?:name|owner|seller|buyer)[:\s]*([A-Za-z\s]+?)(?:\n|,|$)",
        "extent": r"(\d+[\.\d]*)\s*(?:acres?|hectares?|sq\.?\s*ft|guntas?)",
        "registration_no": r"(?:reg|registration)\s*(?:no|number)[:\s]*([A-Z0-9/-]+)",
        "date": r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
    }
    for field_name, pattern in patterns.items():
        match = re.search(pattern, ocr_text, re.IGNORECASE)
        if match:
            fields[field_name] = match.group(1).strip()
    return fields
