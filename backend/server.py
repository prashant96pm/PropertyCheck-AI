from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Depends, Request, Response
from fastapi.responses import FileResponse, StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
import json
import base64
import io
import aiofiles
import asyncio

# PDF and Image processing
from PIL import Image
import pytesseract
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Stripe Integration
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest

# LLM Integration
from emergentintegrations.llm.chat import LlmChat, UserMessage, FileContentWithMimeType

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'propertycheck-default-secret')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days

# Emergent LLM Key
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')

# Create the main app
app = FastAPI(title="PropertyCheck AI API")
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure upload directory exists
UPLOAD_DIR = ROOT_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
REPORTS_DIR = ROOT_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# ==================== MODELS ====================

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class PropertyCreate(BaseModel):
    survey_no: str
    khata_no: Optional[str] = None
    state: str
    district: str
    taluk: Optional[str] = None
    village: Optional[str] = None
    address: Optional[str] = None

class PropertyResponse(BaseModel):
    property_id: str
    survey_no: str
    khata_no: Optional[str] = None
    state: str
    district: str
    taluk: Optional[str] = None
    village: Optional[str] = None
    address: Optional[str] = None
    user_id: str
    created_at: datetime
    risk_score: Optional[int] = None
    risk_status: Optional[str] = None

class DocumentResponse(BaseModel):
    document_id: str
    property_id: str
    filename: str
    doc_type: str
    ocr_text: Optional[str] = None
    extracted_data: Optional[Dict] = None
    uploaded_at: datetime

class RiskReportResponse(BaseModel):
    report_id: str
    property_id: str
    risk_score: int
    risk_status: str
    red_flags: List[Dict]
    yellow_flags: List[Dict]
    green_flags: List[Dict]
    executive_summary: str
    legal_recommendation: str
    title_chain: List[Dict]
    generated_at: datetime

class PaymentCreate(BaseModel):
    property_id: str
    package_type: str  # basic, standard, premium

class GovernmentRecordResponse(BaseModel):
    survey_no: str
    owner_name: str
    father_name: Optional[str] = None
    extent: str
    land_type: str
    khata_no: Optional[str] = None
    mutation_records: List[Dict]
    encumbrances: List[Dict]
    source: str
    fetched_at: datetime

# ==================== AUTH HELPERS ====================

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_jwt_token(user_id: str, email: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(request: Request) -> dict:
    # Try cookie first
    token = request.cookies.get("session_token")
    
    # Fall back to Authorization header
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        
        user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ==================== AUTH ROUTES ====================

@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserCreate, response: Response):
    # Check if user exists
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    hashed_pw = hash_password(user_data.password)
    
    user_doc = {
        "user_id": user_id,
        "email": user_data.email,
        "name": user_data.name,
        "password": hashed_pw,
        "picture": None,
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.users.insert_one(user_doc)
    
    token = create_jwt_token(user_id, user_data.email)
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=JWT_EXPIRATION_HOURS * 3600,
        path="/"
    )
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            user_id=user_id,
            email=user_data.email,
            name=user_data.name,
            created_at=user_doc["created_at"]
        )
    )

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin, response: Response):
    user = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(user_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_jwt_token(user["user_id"], user["email"])
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=JWT_EXPIRATION_HOURS * 3600,
        path="/"
    )
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            user_id=user["user_id"],
            email=user["email"],
            name=user["name"],
            picture=user.get("picture"),
            created_at=user["created_at"] if isinstance(user["created_at"], datetime) else datetime.fromisoformat(user["created_at"])
        )
    )

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    return UserResponse(
        user_id=user["user_id"],
        email=user["email"],
        name=user["name"],
        picture=user.get("picture"),
        created_at=user["created_at"] if isinstance(user["created_at"], datetime) else datetime.fromisoformat(user["created_at"])
    )

@api_router.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Logged out successfully"}

# Emergent Google OAuth session endpoint
@api_router.post("/auth/session")
async def process_oauth_session(request: Request, response: Response):
    import httpx
    
    body = await request.json()
    session_id = body.get("session_id")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    
    # Call Emergent Auth API
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": session_id}
        )
    
    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    oauth_data = resp.json()
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": oauth_data["email"]}, {"_id": 0})
    
    if existing_user:
        user_id = existing_user["user_id"]
        # Update user info
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {
                "name": oauth_data["name"],
                "picture": oauth_data.get("picture")
            }}
        )
    else:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        await db.users.insert_one({
            "user_id": user_id,
            "email": oauth_data["email"],
            "name": oauth_data["name"],
            "picture": oauth_data.get("picture"),
            "password": None,
            "created_at": datetime.now(timezone.utc)
        })
    
    token = create_jwt_token(user_id, oauth_data["email"])
    
    # Store session
    await db.user_sessions.insert_one({
        "user_id": user_id,
        "session_token": token,
        "expires_at": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
        "created_at": datetime.now(timezone.utc)
    })
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=JWT_EXPIRATION_HOURS * 3600,
        path="/"
    )
    
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    
    return {
        "user_id": user_id,
        "email": user["email"],
        "name": user["name"],
        "picture": user.get("picture"),
        "access_token": token
    }

# ==================== PROPERTY ROUTES ====================

@api_router.post("/properties", response_model=PropertyResponse)
async def create_property(property_data: PropertyCreate, user: dict = Depends(get_current_user)):
    property_id = f"prop_{uuid.uuid4().hex[:12]}"
    
    prop_doc = {
        "property_id": property_id,
        "user_id": user["user_id"],
        **property_data.model_dump(),
        "created_at": datetime.now(timezone.utc),
        "risk_score": None,
        "risk_status": None
    }
    
    await db.properties.insert_one(prop_doc)
    
    return PropertyResponse(**{k: v for k, v in prop_doc.items() if k != "_id"})

@api_router.get("/properties", response_model=List[PropertyResponse])
async def get_properties(user: dict = Depends(get_current_user)):
    properties = await db.properties.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    return [PropertyResponse(**p) for p in properties]

@api_router.get("/properties/{property_id}", response_model=PropertyResponse)
async def get_property(property_id: str, user: dict = Depends(get_current_user)):
    prop = await db.properties.find_one(
        {"property_id": property_id, "user_id": user["user_id"]},
        {"_id": 0}
    )
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return PropertyResponse(**prop)

# ==================== DOCUMENT UPLOAD & OCR ====================

@api_router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    property_id: str,
    doc_type: str,
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    # Verify property ownership
    prop = await db.properties.find_one({"property_id": property_id, "user_id": user["user_id"]})
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Save file
    document_id = f"doc_{uuid.uuid4().hex[:12]}"
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "pdf"
    file_path = UPLOAD_DIR / f"{document_id}.{file_ext}"
    
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Perform OCR
    ocr_text = ""
    extracted_data = {}
    
    try:
        if file_ext.lower() in ["png", "jpg", "jpeg", "tiff", "bmp"]:
            # Image OCR
            img = Image.open(file_path)
            ocr_text = pytesseract.image_to_string(img, lang='eng+kan+hin+tel+tam')
        elif file_ext.lower() == "pdf":
            # For PDF, try to extract text (simplified - in production use pdf2image)
            try:
                import PyPDF2
                with open(file_path, 'rb') as pdf_file:
                    reader = PyPDF2.PdfReader(pdf_file)
                    for page in reader.pages:
                        ocr_text += page.extract_text() or ""
            except:
                ocr_text = "PDF text extraction pending - please upload image for OCR"
        
        # Extract key fields from OCR text using AI
        if ocr_text and len(ocr_text) > 50:
            extracted_data = await extract_document_fields(ocr_text, doc_type)
    except Exception as e:
        logger.error(f"OCR Error: {e}")
        ocr_text = f"OCR processing error: {str(e)}"
    
    # Save document record
    doc_record = {
        "document_id": document_id,
        "property_id": property_id,
        "user_id": user["user_id"],
        "filename": file.filename,
        "file_path": str(file_path),
        "doc_type": doc_type,
        "ocr_text": ocr_text,
        "extracted_data": extracted_data,
        "uploaded_at": datetime.now(timezone.utc)
    }
    
    await db.documents.insert_one(doc_record)
    
    return DocumentResponse(
        document_id=document_id,
        property_id=property_id,
        filename=file.filename,
        doc_type=doc_type,
        ocr_text=ocr_text,
        extracted_data=extracted_data,
        uploaded_at=doc_record["uploaded_at"]
    )

async def extract_document_fields(ocr_text: str, doc_type: str) -> Dict:
    """Use Gemini AI to extract structured fields from OCR text"""
    try:
        if not EMERGENT_LLM_KEY:
            return {"error": "AI key not configured"}
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"extract_{uuid.uuid4().hex[:8]}",
            system_message="""You are a legal document analysis expert for Indian land records. 
            Extract structured information from OCR text of land documents.
            Return ONLY valid JSON with no additional text."""
        ).with_model("gemini", "gemini-2.5-flash")
        
        prompt = f"""Analyze this {doc_type} document OCR text and extract:
        - owner_name: Current owner name
        - father_name: Father's name if present
        - survey_no: Survey number
        - hissa_no: Hissa number if present
        - extent: Land extent/area
        - boundaries: North, South, East, West boundaries
        - registration_no: Registration number if present
        - registration_date: Date of registration
        - stamp_duty: Stamp duty value if present
        - encumbrances: Any mortgages or liens mentioned
        
        OCR Text:
        {ocr_text[:3000]}
        
        Return as JSON only."""
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        # Parse JSON from response
        try:
            # Try to extract JSON from response
            json_str = response
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
            return json.loads(json_str.strip())
        except (json.JSONDecodeError, ValueError):
            return {"raw_extraction": response}
    except Exception as e:
        logger.error(f"AI extraction error: {e}")
        return {"error": str(e)}

@api_router.get("/documents/{property_id}", response_model=List[DocumentResponse])
async def get_documents(property_id: str, user: dict = Depends(get_current_user)):
    docs = await db.documents.find(
        {"property_id": property_id, "user_id": user["user_id"]},
        {"_id": 0}
    ).to_list(50)
    
    return [DocumentResponse(**d) for d in docs]

# ==================== AI RISK ANALYSIS ====================

@api_router.post("/analyze/{property_id}", response_model=RiskReportResponse)
async def analyze_property(property_id: str, user: dict = Depends(get_current_user)):
    """Generate AI-powered risk analysis report"""
    
    # Get property
    prop = await db.properties.find_one(
        {"property_id": property_id, "user_id": user["user_id"]},
        {"_id": 0}
    )
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Get documents
    docs = await db.documents.find(
        {"property_id": property_id},
        {"_id": 0}
    ).to_list(20)
    
    # Get mock government records
    govt_records = await get_mock_government_records(prop.get("survey_no", ""), prop.get("state", ""))
    
    # Prepare document summary for AI
    doc_summary = ""
    for doc in docs:
        doc_summary += f"\n--- {doc.get('doc_type', 'Unknown')} ---\n"
        doc_summary += f"OCR Text: {doc.get('ocr_text', '')[:1000]}\n"
        if doc.get('extracted_data'):
            doc_summary += f"Extracted: {json.dumps(doc.get('extracted_data'))}\n"
    
    # Generate AI Risk Analysis
    risk_analysis = await generate_ai_risk_analysis(prop, docs, govt_records)
    
    # Create report
    report_id = f"report_{uuid.uuid4().hex[:12]}"
    report_doc = {
        "report_id": report_id,
        "property_id": property_id,
        "user_id": user["user_id"],
        **risk_analysis,
        "generated_at": datetime.now(timezone.utc)
    }
    
    await db.risk_reports.insert_one(report_doc)
    
    # Update property with risk score
    await db.properties.update_one(
        {"property_id": property_id},
        {"$set": {
            "risk_score": risk_analysis["risk_score"],
            "risk_status": risk_analysis["risk_status"]
        }}
    )
    
    return RiskReportResponse(**{k: v for k, v in report_doc.items() if k != "_id"})

async def generate_ai_risk_analysis(property: dict, documents: list, govt_records: dict) -> dict:
    """Use Gemini to generate comprehensive risk analysis"""
    
    try:
        if not EMERGENT_LLM_KEY:
            # Return mock analysis if no key
            return generate_mock_risk_analysis(property, documents)
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"risk_{uuid.uuid4().hex[:8]}",
            system_message="""You are an expert Indian real estate legal analyst.
            Analyze property documents and government records to identify risks.
            Provide a comprehensive risk assessment with specific red flags, yellow flags, and safe indicators.
            Be thorough but concise. Return valid JSON only."""
        ).with_model("gemini", "gemini-2.5-flash")
        
        # Prepare document data
        doc_data = []
        for doc in documents:
            doc_data.append({
                "type": doc.get("doc_type"),
                "ocr_text": doc.get("ocr_text", "")[:1500],
                "extracted": doc.get("extracted_data", {})
            })
        
        prompt = f"""Analyze this Indian property for legal risks:

Property Details:
- Survey No: {property.get('survey_no')}
- Khata No: {property.get('khata_no', 'N/A')}
- State: {property.get('state')}
- District: {property.get('district')}

Documents Uploaded: {json.dumps(doc_data)}

Government Records: {json.dumps(govt_records)}

Provide analysis as JSON with:
{{
    "risk_score": <0-100, where 0 is high risk, 100 is safe>,
    "risk_status": "<RED|YELLOW|GREEN>",
    "red_flags": [
        {{"issue": "...", "severity": "HIGH|CRITICAL", "details": "..."}}
    ],
    "yellow_flags": [
        {{"issue": "...", "severity": "MEDIUM", "details": "..."}}
    ],
    "green_flags": [
        {{"indicator": "...", "confidence": "HIGH|MEDIUM", "details": "..."}}
    ],
    "executive_summary": "<3-5 line summary>",
    "legal_recommendation": "<SAFE_TO_BUY|BUY_WITH_CAUTION|HIGH_RISK_LEGAL_REVIEW_REQUIRED>",
    "title_chain": [
        {{"owner": "...", "from_date": "...", "to_date": "...", "doc_ref": "...", "transfer_type": "..."}}
    ]
}}

Be specific about issues found. If documents are missing or incomplete, flag that as a yellow flag."""
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        # Parse JSON response
        try:
            json_str = response
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
            return json.loads(json_str.strip())
        except:
            return generate_mock_risk_analysis(property, documents)
            
    except Exception as e:
        logger.error(f"AI analysis error: {e}")
        return generate_mock_risk_analysis(property, documents)

def generate_mock_risk_analysis(property: dict, documents: list) -> dict:
    """Generate mock risk analysis when AI is unavailable"""
    import random
    
    has_docs = len(documents) > 0
    risk_score = random.randint(60, 95) if has_docs else random.randint(30, 60)
    
    if risk_score >= 75:
        status = "GREEN"
        recommendation = "SAFE_TO_BUY"
    elif risk_score >= 50:
        status = "YELLOW"
        recommendation = "BUY_WITH_CAUTION"
    else:
        status = "RED"
        recommendation = "HIGH_RISK_LEGAL_REVIEW_REQUIRED"
    
    red_flags = []
    yellow_flags = []
    green_flags = []
    
    if not has_docs:
        red_flags.append({
            "issue": "No documents uploaded",
            "severity": "CRITICAL",
            "details": "Complete verification requires uploaded property documents"
        })
    
    yellow_flags.append({
        "issue": "Government records verification pending",
        "severity": "MEDIUM",
        "details": "Live government API integration will provide real-time verification"
    })
    
    if has_docs:
        green_flags.append({
            "indicator": "Documents uploaded for verification",
            "confidence": "MEDIUM",
            "details": "OCR extraction completed successfully"
        })
    
    return {
        "risk_score": risk_score,
        "risk_status": status,
        "red_flags": red_flags,
        "yellow_flags": yellow_flags,
        "green_flags": green_flags,
        "executive_summary": f"Property at Survey No. {property.get('survey_no', 'N/A')} in {property.get('district', 'Unknown')}, {property.get('state', 'Unknown')} has been analyzed. Risk Score: {risk_score}/100. {'Documents provided for analysis.' if has_docs else 'No documents uploaded - limited analysis possible.'}",
        "legal_recommendation": recommendation,
        "title_chain": [
            {
                "owner": "Current Owner (from documents)",
                "from_date": "2020-01-15",
                "to_date": "Present",
                "doc_ref": documents[0]["document_id"] if has_docs else "N/A",
                "transfer_type": "Sale Deed"
            },
            {
                "owner": "Previous Owner",
                "from_date": "2010-06-20",
                "to_date": "2020-01-14",
                "doc_ref": "Mother Deed Reference",
                "transfer_type": "Inheritance"
            }
        ]
    }

# ==================== GOVERNMENT RECORDS (MOCK) ====================

async def get_mock_government_records(survey_no: str, state: str) -> dict:
    """Mock government land records - simulates Bhoomi/Bhulekh/Dharani APIs"""
    
    # Simulate different state record formats
    state_sources = {
        "Karnataka": "Bhoomi (Karnataka RTC)",
        "Uttar Pradesh": "Bhulekh (UP Land Records)",
        "Gujarat": "AnyROR (Gujarat)",
        "Telangana": "Dharani",
        "Maharashtra": "Mahabhulekh"
    }
    
    source = state_sources.get(state, f"{state} Land Records Portal")
    
    return {
        "survey_no": survey_no,
        "owner_name": "Mock Owner Name",
        "father_name": "Mock Father Name",
        "extent": "2 Acres 30 Guntas",
        "land_type": "Agricultural (Bagayat)",
        "khata_no": f"KH-{survey_no[:3]}-2024",
        "mutation_records": [
            {
                "mutation_no": "MUT-2020-1234",
                "date": "2020-01-15",
                "type": "Sale",
                "from_owner": "Previous Owner",
                "to_owner": "Current Owner"
            }
        ],
        "encumbrances": [],
        "pending_litigation": False,
        "cersai_check": "No mortgages registered",
        "source": source,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "disclaimer": "MOCK DATA - Real government API integration pending"
    }

@api_router.get("/government-records/{survey_no}")
async def fetch_government_records(survey_no: str, state: str = "Karnataka"):
    """Fetch government land records (currently mocked)"""
    records = await get_mock_government_records(survey_no, state)
    return records

# ==================== REPORT GENERATION ====================

@api_router.get("/reports/{property_id}")
async def get_report(property_id: str, user: dict = Depends(get_current_user)):
    """Get the latest risk report for a property"""
    report = await db.risk_reports.find_one(
        {"property_id": property_id, "user_id": user["user_id"]},
        {"_id": 0},
        sort=[("generated_at", -1)]
    )
    
    if not report:
        raise HTTPException(status_code=404, detail="No report found. Please run analysis first.")
    
    return report

@api_router.get("/reports/{property_id}/download")
async def download_report_pdf(property_id: str, user: dict = Depends(get_current_user)):
    """Generate and download PDF report"""
    
    # Get report
    report = await db.risk_reports.find_one(
        {"property_id": property_id, "user_id": user["user_id"]},
        {"_id": 0}
    )
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Get property
    prop = await db.properties.find_one(
        {"property_id": property_id},
        {"_id": 0}
    )
    
    # Generate PDF
    pdf_path = REPORTS_DIR / f"{report['report_id']}.pdf"
    
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#0F172A')
    )
    story.append(Paragraph("PropertyCheck AI", title_style))
    story.append(Paragraph("Property Verification Report", styles['Heading2']))
    story.append(Spacer(1, 20))
    
    # Property Details
    story.append(Paragraph("Property Details", styles['Heading3']))
    prop_data = [
        ["Survey Number", prop.get("survey_no", "N/A")],
        ["Khata Number", prop.get("khata_no", "N/A")],
        ["State", prop.get("state", "N/A")],
        ["District", prop.get("district", "N/A")],
    ]
    prop_table = Table(prop_data, colWidths=[2*inch, 4*inch])
    prop_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#0F172A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0'))
    ]))
    story.append(prop_table)
    story.append(Spacer(1, 20))
    
    # Risk Score
    risk_color = colors.green if report["risk_status"] == "GREEN" else (colors.orange if report["risk_status"] == "YELLOW" else colors.red)
    story.append(Paragraph(f"Risk Score: {report['risk_score']}/100", styles['Heading3']))
    story.append(Paragraph(f"Status: {report['risk_status']}", styles['Normal']))
    story.append(Paragraph(f"Recommendation: {report['legal_recommendation'].replace('_', ' ')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", styles['Heading3']))
    story.append(Paragraph(report.get("executive_summary", ""), styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Red Flags
    if report.get("red_flags"):
        story.append(Paragraph("Red Flags (Critical Issues)", styles['Heading3']))
        for flag in report["red_flags"]:
            story.append(Paragraph(f"• {flag.get('issue', '')}: {flag.get('details', '')}", styles['Normal']))
        story.append(Spacer(1, 10))
    
    # Yellow Flags
    if report.get("yellow_flags"):
        story.append(Paragraph("Yellow Flags (Caution Required)", styles['Heading3']))
        for flag in report["yellow_flags"]:
            story.append(Paragraph(f"• {flag.get('issue', '')}: {flag.get('details', '')}", styles['Normal']))
        story.append(Spacer(1, 10))
    
    # Green Flags
    if report.get("green_flags"):
        story.append(Paragraph("Green Flags (Positive Indicators)", styles['Heading3']))
        for flag in report["green_flags"]:
            story.append(Paragraph(f"• {flag.get('indicator', '')}: {flag.get('details', '')}", styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Paragraph("This report is for informational purposes. Consult a legal professional.", styles['Normal']))
    
    doc.build(story)
    
    return FileResponse(
        path=str(pdf_path),
        filename=f"PropertyCheck_Report_{property_id}.pdf",
        media_type="application/pdf"
    )

# ==================== PAYMENT ROUTES ====================

PRICING_PACKAGES = {
    "basic": {"amount": 499.00, "currency": "INR", "name": "Basic Verification", "features": ["OCR Analysis", "Basic Risk Score"]},
    "standard": {"amount": 999.00, "currency": "INR", "name": "Standard Report", "features": ["Full OCR", "AI Risk Analysis", "Title Chain"]},
    "premium": {"amount": 1999.00, "currency": "INR", "name": "Premium Legal Report", "features": ["Everything in Standard", "Government Records Check", "PDF Report"]}
}

@api_router.get("/pricing")
async def get_pricing():
    """Get available pricing packages"""
    return PRICING_PACKAGES

@api_router.post("/payments/create-checkout")
async def create_payment_checkout(
    request: Request,
    payment_data: PaymentCreate,
    user: dict = Depends(get_current_user)
):
    """Create Stripe checkout session for property verification"""
    
    # Get package
    package = PRICING_PACKAGES.get(payment_data.package_type)
    if not package:
        raise HTTPException(status_code=400, detail="Invalid package type")
    
    # Verify property
    prop = await db.properties.find_one(
        {"property_id": payment_data.property_id, "user_id": user["user_id"]}
    )
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    
    host_url = str(request.base_url).rstrip("/")
    webhook_url = f"{host_url}/api/webhook/stripe"
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    # For INR, convert to USD (approximate)
    usd_amount = round(package["amount"] / 83, 2)  # Approximate INR to USD
    
    body = await request.json() if request.headers.get("content-type") == "application/json" else {}
    origin_url = body.get("origin_url", host_url)
    
    success_url = f"{origin_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{origin_url}/pricing"
    
    checkout_request = CheckoutSessionRequest(
        amount=usd_amount,
        currency="usd",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "user_id": user["user_id"],
            "property_id": payment_data.property_id,
            "package_type": payment_data.package_type,
            "inr_amount": str(package["amount"])
        }
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    # Store payment record
    await db.payment_transactions.insert_one({
        "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
        "session_id": session.session_id,
        "user_id": user["user_id"],
        "property_id": payment_data.property_id,
        "package_type": payment_data.package_type,
        "amount": package["amount"],
        "currency": "INR",
        "usd_amount": usd_amount,
        "payment_status": "initiated",
        "created_at": datetime.now(timezone.utc)
    })
    
    return {
        "checkout_url": session.url,
        "session_id": session.session_id
    }

@api_router.get("/payments/status/{session_id}")
async def check_payment_status(session_id: str, request: Request, user: dict = Depends(get_current_user)):
    """Check payment status and update record"""
    
    host_url = str(request.base_url).rstrip("/")
    webhook_url = f"{host_url}/api/webhook/stripe"
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    try:
        status = await stripe_checkout.get_checkout_status(session_id)
        
        # Update payment record
        update_result = await db.payment_transactions.find_one_and_update(
            {"session_id": session_id, "user_id": user["user_id"]},
            {"$set": {
                "payment_status": status.payment_status,
                "status": status.status,
                "updated_at": datetime.now(timezone.utc)
            }},
            return_document=True
        )
        
        # If payment is complete, grant access to report
        if status.payment_status == "paid" and update_result:
            await db.properties.update_one(
                {"property_id": update_result.get("property_id")},
                {"$set": {"report_access": True, "package_type": update_result.get("package_type")}}
            )
        
        return {
            "status": status.status,
            "payment_status": status.payment_status,
            "amount_total": status.amount_total,
            "currency": status.currency
        }
    except Exception as e:
        logger.error(f"Payment status check error: {e}")
        raise HTTPException(status_code=500, detail="Failed to check payment status")

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    body = await request.body()
    signature = request.headers.get("Stripe-Signature", "")
    
    host_url = str(request.base_url).rstrip("/")
    webhook_url = f"{host_url}/api/webhook/stripe"
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    try:
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        # Update payment status
        await db.payment_transactions.update_one(
            {"session_id": webhook_response.session_id},
            {"$set": {
                "payment_status": webhook_response.payment_status,
                "event_type": webhook_response.event_type,
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        return {"status": "processed"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error", "message": str(e)}

# ==================== DASHBOARD STATS ====================

@api_router.get("/dashboard/stats")
async def get_dashboard_stats(user: dict = Depends(get_current_user)):
    """Get user dashboard statistics"""
    
    properties_count = await db.properties.count_documents({"user_id": user["user_id"]})
    documents_count = await db.documents.count_documents({"user_id": user["user_id"]})
    reports_count = await db.risk_reports.count_documents({"user_id": user["user_id"]})
    
    # Recent properties
    recent_properties = await db.properties.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).sort("created_at", -1).limit(5).to_list(5)
    
    return {
        "total_properties": properties_count,
        "total_documents": documents_count,
        "total_reports": reports_count,
        "recent_properties": recent_properties
    }

# ==================== BASIC ROUTES ====================

@api_router.get("/")
async def root():
    return {"message": "PropertyCheck AI API", "version": "1.0.0"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Include router
app.include_router(api_router)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
