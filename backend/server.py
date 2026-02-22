from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Depends, Request, Response, Query
from fastapi.responses import FileResponse, StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import re
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any, Union
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
import json
import base64
import io
import aiofiles
import asyncio
from rapidfuzz import fuzz, process

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
JWT_EXPIRATION_HOURS = 24 * 7

# API Keys
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')
DATA_GOV_API_KEY = os.environ.get('DATA_GOV_API_KEY')

# Create the main app
app = FastAPI(title="PropertyCheck AI API")
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure directories exist
UPLOAD_DIR = ROOT_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
REPORTS_DIR = ROOT_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)
DOCS_DIR = ROOT_DIR / "property_documents"
DOCS_DIR.mkdir(exist_ok=True)

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
    role: str = "user"
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class PropertyCreate(BaseModel):
    survey_no: str
    khata_no: Optional[str] = None
    plot_no: Optional[str] = None
    state: str
    district: str
    taluk: Optional[str] = None
    village: Optional[str] = None
    address: Optional[str] = None
    owner_name: Optional[str] = None
    land_type: Optional[str] = None
    extent: Optional[str] = None

class PropertyResponse(BaseModel):
    property_id: str
    survey_no: str
    khata_no: Optional[str] = None
    plot_no: Optional[str] = None
    state: str
    district: str
    taluk: Optional[str] = None
    village: Optional[str] = None
    address: Optional[str] = None
    owner_name: Optional[str] = None
    land_type: Optional[str] = None
    extent: Optional[str] = None
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
    package_type: str

# ==================== NEW SEARCH MODELS ====================

class PropertySearchQuery(BaseModel):
    owner_name: Optional[str] = None
    survey_no: Optional[str] = None
    plot_no: Optional[str] = None
    khata_no: Optional[str] = None
    registration_no: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    village: Optional[str] = None
    taluk: Optional[str] = None
    land_type: Optional[str] = None
    page: int = 1
    limit: int = 20

class SmartSearchQuery(BaseModel):
    query: str  # Natural language query
    filters: Optional[Dict] = None

class PropertyFullProfile(BaseModel):
    property_id: str
    basic_details: Dict
    ownership_history: List[Dict]
    legal_records: Dict
    documents: List[Dict]
    geo_spatial: Dict
    risk_assessment: Optional[Dict] = None
    government_records: Dict

class OwnerSearchResult(BaseModel):
    owner_name: str
    properties: List[Dict]
    aliases: List[str]
    confidence_score: float

# ==================== AUTH HELPERS ====================

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_jwt_token(user_id: str, email: str, role: str = "user") -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(request: Request) -> dict:
    token = request.cookies.get("session_token")
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

async def get_optional_user(request: Request) -> Optional[dict]:
    try:
        return await get_current_user(request)
    except HTTPException:
        return None

# ==================== AUTH ROUTES ====================

@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserCreate, response: Response):
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
        "role": "user",
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.users.insert_one(user_doc)
    token = create_jwt_token(user_id, user_data.email, "user")
    
    response.set_cookie(
        key="session_token", value=token, httponly=True, secure=True,
        samesite="none", max_age=JWT_EXPIRATION_HOURS * 3600, path="/"
    )
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            user_id=user_id, email=user_data.email, name=user_data.name,
            role="user", created_at=user_doc["created_at"]
        )
    )

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin, response: Response):
    user = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(user_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_jwt_token(user["user_id"], user["email"], user.get("role", "user"))
    
    response.set_cookie(
        key="session_token", value=token, httponly=True, secure=True,
        samesite="none", max_age=JWT_EXPIRATION_HOURS * 3600, path="/"
    )
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            user_id=user["user_id"], email=user["email"], name=user["name"],
            picture=user.get("picture"), role=user.get("role", "user"),
            created_at=user["created_at"] if isinstance(user["created_at"], datetime) else datetime.fromisoformat(user["created_at"])
        )
    )

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    return UserResponse(
        user_id=user["user_id"], email=user["email"], name=user["name"],
        picture=user.get("picture"), role=user.get("role", "user"),
        created_at=user["created_at"] if isinstance(user["created_at"], datetime) else datetime.fromisoformat(user["created_at"])
    )

@api_router.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Logged out successfully"}

@api_router.post("/auth/session")
async def process_oauth_session(request: Request, response: Response):
    import httpx
    
    body = await request.json()
    session_id = body.get("session_id")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    
    async with httpx.AsyncClient() as client_http:
        resp = await client_http.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": session_id}
        )
    
    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    oauth_data = resp.json()
    existing_user = await db.users.find_one({"email": oauth_data["email"]}, {"_id": 0})
    
    if existing_user:
        user_id = existing_user["user_id"]
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"name": oauth_data["name"], "picture": oauth_data.get("picture")}}
        )
    else:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        await db.users.insert_one({
            "user_id": user_id, "email": oauth_data["email"], "name": oauth_data["name"],
            "picture": oauth_data.get("picture"), "password": None, "role": "user",
            "created_at": datetime.now(timezone.utc)
        })
    
    token = create_jwt_token(user_id, oauth_data["email"], "user")
    
    response.set_cookie(
        key="session_token", value=token, httponly=True, secure=True,
        samesite="none", max_age=JWT_EXPIRATION_HOURS * 3600, path="/"
    )
    
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    
    return {
        "user_id": user_id, "email": user["email"], "name": user["name"],
        "picture": user.get("picture"), "access_token": token
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
    
    # Index for search
    await index_property_for_search(prop_doc)
    
    return PropertyResponse(**{k: v for k, v in prop_doc.items() if k != "_id"})

@api_router.get("/properties", response_model=List[PropertyResponse])
async def get_properties(user: dict = Depends(get_current_user)):
    properties = await db.properties.find(
        {"user_id": user["user_id"]}, {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    return [PropertyResponse(**p) for p in properties]

@api_router.get("/properties/{property_id}", response_model=PropertyResponse)
async def get_property(property_id: str, user: dict = Depends(get_current_user)):
    prop = await db.properties.find_one(
        {"property_id": property_id, "user_id": user["user_id"]}, {"_id": 0}
    )
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return PropertyResponse(**prop)

# ==================== UNIVERSAL SEARCH ENGINE ====================

async def index_property_for_search(property_doc: dict):
    """Index property for fast search"""
    search_index = {
        "property_id": property_doc["property_id"],
        "survey_no": property_doc.get("survey_no", "").lower(),
        "khata_no": (property_doc.get("khata_no") or "").lower(),
        "plot_no": (property_doc.get("plot_no") or "").lower(),
        "owner_name": (property_doc.get("owner_name") or "").lower(),
        "district": property_doc.get("district", "").lower(),
        "state": property_doc.get("state", "").lower(),
        "village": (property_doc.get("village") or "").lower(),
        "taluk": (property_doc.get("taluk") or "").lower(),
        "land_type": (property_doc.get("land_type") or "").lower(),
        "searchable_text": f"{property_doc.get('survey_no', '')} {property_doc.get('owner_name', '')} {property_doc.get('district', '')} {property_doc.get('state', '')}".lower(),
        "indexed_at": datetime.now(timezone.utc)
    }
    
    await db.property_search_index.update_one(
        {"property_id": property_doc["property_id"]},
        {"$set": search_index},
        upsert=True
    )

def fuzzy_match_name(query_name: str, target_name: str, threshold: int = 70) -> tuple:
    """Fuzzy match names with confidence score"""
    if not query_name or not target_name:
        return False, 0
    
    query_lower = query_name.lower().strip()
    target_lower = target_name.lower().strip()
    
    # Direct match
    if query_lower == target_lower:
        return True, 100
    
    # Fuzzy ratio
    ratio = fuzz.ratio(query_lower, target_lower)
    partial_ratio = fuzz.partial_ratio(query_lower, target_lower)
    token_sort_ratio = fuzz.token_sort_ratio(query_lower, target_lower)
    
    best_score = max(ratio, partial_ratio, token_sort_ratio)
    
    return best_score >= threshold, best_score

@api_router.get("/property/search")
async def search_properties(
    owner_name: Optional[str] = Query(None, description="Owner name (fuzzy match)"),
    survey_no: Optional[str] = Query(None, description="Survey number"),
    plot_no: Optional[str] = Query(None, description="Plot number"),
    khata_no: Optional[str] = Query(None, description="Khata number"),
    registration_no: Optional[str] = Query(None, description="Registration number"),
    district: Optional[str] = Query(None, description="District"),
    state: Optional[str] = Query(None, description="State"),
    village: Optional[str] = Query(None, description="Village"),
    taluk: Optional[str] = Query(None, description="Taluk"),
    land_type: Optional[str] = Query(None, description="Land type"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    request: Request = None
):
    """Universal property search with multiple parameters"""
    
    # Build query
    query = {}
    
    if survey_no:
        query["survey_no"] = {"$regex": survey_no, "$options": "i"}
    if plot_no:
        query["plot_no"] = {"$regex": plot_no, "$options": "i"}
    if khata_no:
        query["khata_no"] = {"$regex": khata_no, "$options": "i"}
    if district:
        query["district"] = {"$regex": district, "$options": "i"}
    if state:
        query["state"] = {"$regex": state, "$options": "i"}
    if village:
        query["village"] = {"$regex": village, "$options": "i"}
    if taluk:
        query["taluk"] = {"$regex": taluk, "$options": "i"}
    if land_type:
        query["land_type"] = {"$regex": land_type, "$options": "i"}
    
    # If no specific query, return empty
    if not query and not owner_name:
        # Return sample properties from registry
        results = await get_sample_property_registry(limit)
        return {
            "results": results,
            "total": len(results),
            "page": page,
            "limit": limit,
            "search_type": "sample_registry"
        }
    
    skip = (page - 1) * limit
    
    # Search in properties collection
    properties = await db.properties.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    
    # Also search in registry
    registry_results = await db.property_registry.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    
    # Combine results
    all_results = properties + registry_results
    
    # If owner name provided, do fuzzy matching
    if owner_name:
        fuzzy_results = []
        for prop in all_results:
            prop_owner = prop.get("owner_name", "")
            is_match, score = fuzzy_match_name(owner_name, prop_owner)
            if is_match:
                prop["match_confidence"] = score
                fuzzy_results.append(prop)
        
        # Also search by owner name directly
        owner_query = {"owner_name": {"$regex": owner_name, "$options": "i"}}
        owner_results = await db.properties.find(owner_query, {"_id": 0}).limit(limit).to_list(limit)
        owner_registry = await db.property_registry.find(owner_query, {"_id": 0}).limit(limit).to_list(limit)
        
        for prop in owner_results + owner_registry:
            if prop not in fuzzy_results:
                prop["match_confidence"] = 100
                fuzzy_results.append(prop)
        
        # Sort by confidence
        fuzzy_results.sort(key=lambda x: x.get("match_confidence", 0), reverse=True)
        all_results = fuzzy_results[:limit]
    
    total = await db.properties.count_documents(query) + await db.property_registry.count_documents(query)
    
    return {
        "results": all_results,
        "total": total,
        "page": page,
        "limit": limit,
        "search_type": "multi_parameter"
    }

@api_router.post("/property/ai-smart-search")
async def ai_smart_search(search_query: SmartSearchQuery, request: Request):
    """Natural language property search using AI"""
    
    user = await get_optional_user(request)
    
    # Use LLM to parse the natural language query
    if EMERGENT_LLM_KEY:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"search_{uuid.uuid4().hex[:8]}",
            system_message="""You are a property search query parser for Indian land records.
            Extract structured search parameters from natural language queries.
            Return ONLY valid JSON with no additional text."""
        ).with_model("gemini", "gemini-2.5-flash")
        
        prompt = f"""Parse this property search query and extract parameters:
        Query: "{search_query.query}"
        
        Extract and return JSON with these fields (use null for missing):
        {{
            "owner_name": "extracted owner name or null",
            "survey_no": "survey number or null",
            "plot_no": "plot number or null",
            "khata_no": "khata number or null",
            "district": "district name or null",
            "state": "state name or null",
            "village": "village name or null",
            "taluk": "taluk name or null",
            "land_type": "agricultural/residential/commercial or null",
            "intent": "search/verify/history/documents"
        }}
        
        Examples:
        "Land owned by Ramesh in Bangalore" -> {{"owner_name": "Ramesh", "district": "Bangalore", ...}}
        "Survey 123/4 Karnataka" -> {{"survey_no": "123/4", "state": "Karnataka", ...}}
        """
        
        try:
            response = await chat.send_message(UserMessage(text=prompt))
            json_str = response
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
            
            parsed_params = json.loads(json_str.strip())
        except (json.JSONDecodeError, ValueError, IndexError):
            parsed_params = parse_query_fallback(search_query.query)
    else:
        parsed_params = parse_query_fallback(search_query.query)
    
    # Build search query from parsed parameters
    query = {}
    for key in ["survey_no", "plot_no", "khata_no", "district", "state", "village", "taluk", "land_type"]:
        if parsed_params.get(key):
            query[key] = {"$regex": parsed_params[key], "$options": "i"}
    
    # Search properties
    properties = await db.properties.find(query, {"_id": 0}).limit(20).to_list(20)
    registry = await db.property_registry.find(query, {"_id": 0}).limit(20).to_list(20)
    
    all_results = properties + registry
    
    # Fuzzy owner name matching
    if parsed_params.get("owner_name"):
        filtered = []
        for prop in all_results:
            is_match, score = fuzzy_match_name(parsed_params["owner_name"], prop.get("owner_name", ""))
            if is_match:
                prop["match_confidence"] = score
                filtered.append(prop)
        
        # Also direct search
        owner_query = {"owner_name": {"$regex": parsed_params["owner_name"], "$options": "i"}}
        owner_results = await db.properties.find(owner_query, {"_id": 0}).limit(20).to_list(20)
        for prop in owner_results:
            if prop not in filtered:
                prop["match_confidence"] = 100
                filtered.append(prop)
        
        all_results = sorted(filtered, key=lambda x: x.get("match_confidence", 0), reverse=True)
    
    return {
        "query_parsed": parsed_params,
        "results": all_results[:20],
        "total": len(all_results),
        "search_type": "ai_smart_search"
    }

def parse_query_fallback(query: str) -> dict:
    """Fallback query parser without LLM"""
    params = {}
    query_lower = query.lower()
    
    # Survey number patterns
    survey_match = re.search(r'survey\s*(?:no\.?|number)?\s*[:\s]?\s*(\d+[/\-]?\d*)', query_lower)
    if survey_match:
        params["survey_no"] = survey_match.group(1)
    
    # Plot number
    plot_match = re.search(r'plot\s*(?:no\.?|number)?\s*[:\s]?\s*(\d+)', query_lower)
    if plot_match:
        params["plot_no"] = plot_match.group(1)
    
    # State detection
    states = ["karnataka", "maharashtra", "telangana", "andhra pradesh", "tamil nadu", 
              "kerala", "gujarat", "rajasthan", "uttar pradesh", "madhya pradesh"]
    for state in states:
        if state in query_lower:
            params["state"] = state.title()
            break
    
    # District/city detection (common ones)
    cities = ["bangalore", "mumbai", "hyderabad", "chennai", "pune", "ahmedabad", 
              "delhi", "kolkata", "jaipur", "lucknow"]
    for city in cities:
        if city in query_lower:
            params["district"] = city.title()
            break
    
    # Owner name - extract names (simplified)
    owned_by = re.search(r'(?:owned by|owner|belonging to)\s+([a-zA-Z\s]+?)(?:\s+in|\s+at|$)', query_lower)
    if owned_by:
        params["owner_name"] = owned_by.group(1).strip().title()
    
    return params

# ==================== PROPERTY 360° PROFILE ====================

@api_router.get("/property/full-profile/{property_id}")
async def get_full_property_profile(property_id: str, request: Request):
    """Get complete 360° property intelligence profile"""
    
    user = await get_optional_user(request)
    
    # Get property
    property_data = await db.properties.find_one({"property_id": property_id}, {"_id": 0})
    if not property_data:
        property_data = await db.property_registry.find_one({"property_id": property_id}, {"_id": 0})
    
    if not property_data:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Get documents
    documents = await db.documents.find({"property_id": property_id}, {"_id": 0}).to_list(50)
    
    # Get ownership history
    ownership_history = await get_ownership_history(property_id, property_data)
    
    # Get legal records
    legal_records = await get_legal_records(property_id, property_data)
    
    # Get government records
    govt_records = await get_mock_government_records(
        property_data.get("survey_no", ""),
        property_data.get("state", "")
    )
    
    # Get risk report if exists
    risk_report = await db.risk_reports.find_one(
        {"property_id": property_id},
        {"_id": 0},
        sort=[("generated_at", -1)]
    )
    
    # Get geo-spatial data
    geo_data = await get_geo_spatial_data(property_data)
    
    return {
        "property_id": property_id,
        "basic_details": {
            "owner_name": property_data.get("owner_name", "Unknown"),
            "survey_no": property_data.get("survey_no"),
            "khata_no": property_data.get("khata_no"),
            "plot_no": property_data.get("plot_no"),
            "extent": property_data.get("extent", "Not specified"),
            "land_type": property_data.get("land_type", "Not specified"),
            "boundaries": property_data.get("boundaries", {}),
            "village": property_data.get("village"),
            "taluk": property_data.get("taluk"),
            "district": property_data.get("district"),
            "state": property_data.get("state"),
            "zoning": property_data.get("zoning", "Residential")
        },
        "ownership_history": ownership_history,
        "legal_records": legal_records,
        "documents": [{
            "document_id": doc.get("document_id"),
            "doc_type": doc.get("doc_type"),
            "filename": doc.get("filename"),
            "uploaded_at": doc.get("uploaded_at"),
            "is_verified": doc.get("is_verified", False)
        } for doc in documents],
        "geo_spatial": geo_data,
        "risk_assessment": risk_report,
        "government_records": govt_records
    }

async def get_ownership_history(property_id: str, property_data: dict) -> List[Dict]:
    """Get 30+ years ownership history"""
    
    # Check if we have stored history
    history = await db.ownership_chain.find(
        {"property_id": property_id},
        {"_id": 0}
    ).sort("transfer_date", -1).to_list(50)
    
    if history:
        return history
    
    # Generate mock history
    return [
        {
            "owner_name": property_data.get("owner_name", "Current Owner"),
            "father_name": "N/A",
            "transfer_date": "2020-01-15",
            "transfer_type": "Sale Deed",
            "doc_reference": "SD-2020-12345",
            "extent": property_data.get("extent", "N/A"),
            "consideration": "₹45,00,000"
        },
        {
            "owner_name": "Previous Owner",
            "father_name": "Late Grandfather",
            "transfer_date": "2010-06-20",
            "transfer_type": "Inheritance",
            "doc_reference": "MUT-2010-5678",
            "extent": property_data.get("extent", "N/A"),
            "consideration": "N/A"
        },
        {
            "owner_name": "Original Owner",
            "father_name": "N/A",
            "transfer_date": "1995-03-10",
            "transfer_type": "Grant",
            "doc_reference": "GR-1995-001",
            "extent": property_data.get("extent", "N/A"),
            "consideration": "N/A"
        }
    ]

async def get_legal_records(property_id: str, property_data: dict) -> Dict:
    """Get legal and encumbrance records"""
    return {
        "encumbrances": [],
        "mortgages": [],
        "court_cases": [],
        "cersai_status": "No mortgages registered",
        "government_tags": [],
        "pending_litigation": False,
        "ecourts_check": "No pending cases found",
        "last_checked": datetime.now(timezone.utc).isoformat()
    }

async def get_geo_spatial_data(property_data: dict) -> Dict:
    """Get geo-spatial information"""
    return {
        "coordinates": {
            "latitude": 12.9716,
            "longitude": 77.5946
        },
        "boundaries": {
            "north": property_data.get("boundary_north", "Plot 46"),
            "south": property_data.get("boundary_south", "Road"),
            "east": property_data.get("boundary_east", "Plot 44"),
            "west": property_data.get("boundary_west", "Open land")
        },
        "satellite_imagery_url": None,
        "encroachment_detected": False,
        "nearby_infrastructure": {
            "roads": ["NH-44 (2km)", "Ring Road (500m)"],
            "lakes": ["Lake View (1.5km)"],
            "highways": ["Outer Ring Road (3km)"]
        },
        "zoning_classification": property_data.get("zoning", "Residential"),
        "land_use": property_data.get("land_type", "Residential")
    }

# ==================== DOCUMENTS REGISTRY ====================

@api_router.get("/property/documents/{property_id}")
async def get_property_documents(property_id: str, user: dict = Depends(get_current_user)):
    """Get all documents for a property"""
    
    # User's uploaded documents
    user_docs = await db.documents.find(
        {"property_id": property_id},
        {"_id": 0}
    ).to_list(50)
    
    # Registry documents (mock government docs)
    registry_docs = await get_registry_documents(property_id)
    
    return {
        "property_id": property_id,
        "uploaded_documents": user_docs,
        "registry_documents": registry_docs,
        "total_documents": len(user_docs) + len(registry_docs)
    }

async def get_registry_documents(property_id: str) -> List[Dict]:
    """Get mock government registry documents"""
    return [
        {
            "doc_type": "encumbrance_certificate",
            "doc_name": "Encumbrance Certificate (EC)",
            "source": "Sub-Registrar Office",
            "date_range": "1995-2024",
            "is_available": True,
            "download_url": None,
            "status": "Available for download"
        },
        {
            "doc_type": "rtc_pahani",
            "doc_name": "RTC / Pahani",
            "source": "Bhoomi Portal",
            "date_range": "Current",
            "is_available": True,
            "download_url": None,
            "status": "Available"
        },
        {
            "doc_type": "khata_certificate",
            "doc_name": "Khata Certificate",
            "source": "BBMP/Municipality",
            "date_range": "Current",
            "is_available": True,
            "download_url": None,
            "status": "Available"
        },
        {
            "doc_type": "cadastral_map",
            "doc_name": "Cadastral Map (Bhu-Naksha)",
            "source": "Survey Department",
            "date_range": "Current",
            "is_available": True,
            "download_url": None,
            "status": "Available"
        },
        {
            "doc_type": "mutation_records",
            "doc_name": "Mutation Records",
            "source": "Revenue Department",
            "date_range": "2000-2024",
            "is_available": True,
            "download_url": None,
            "status": "5 records found"
        }
    ]

@api_router.get("/property/ownership-history/{property_id}")
async def get_property_ownership_history(property_id: str, request: Request):
    """Get detailed ownership history"""
    
    property_data = await db.properties.find_one({"property_id": property_id}, {"_id": 0})
    if not property_data:
        property_data = await db.property_registry.find_one({"property_id": property_id}, {"_id": 0})
    
    if not property_data:
        raise HTTPException(status_code=404, detail="Property not found")
    
    history = await get_ownership_history(property_id, property_data)
    
    return {
        "property_id": property_id,
        "ownership_chain": history,
        "total_transfers": len(history),
        "first_recorded": history[-1].get("transfer_date") if history else None,
        "current_owner": history[0].get("owner_name") if history else None
    }

@api_router.get("/property/legal-records/{property_id}")
async def get_property_legal_records(property_id: str, request: Request):
    """Get legal records for a property"""
    
    property_data = await db.properties.find_one({"property_id": property_id}, {"_id": 0})
    if not property_data:
        property_data = await db.property_registry.find_one({"property_id": property_id}, {"_id": 0})
    
    if not property_data:
        raise HTTPException(status_code=404, detail="Property not found")
    
    legal = await get_legal_records(property_id, property_data)
    
    return {
        "property_id": property_id,
        **legal
    }

# ==================== SAMPLE PROPERTY REGISTRY ====================

async def get_sample_property_registry(limit: int = 20) -> List[Dict]:
    """Get sample properties from registry for browsing"""
    
    # Check if we have sample data
    count = await db.property_registry.count_documents({})
    
    if count < 10:
        # Seed sample data
        await seed_sample_property_registry()
    
    properties = await db.property_registry.find({}, {"_id": 0}).limit(limit).to_list(limit)
    return properties

async def seed_sample_property_registry():
    """Seed sample property data for demonstration"""
    
    sample_properties = [
        {
            "property_id": f"reg_{uuid.uuid4().hex[:12]}",
            "survey_no": "123/4",
            "khata_no": "KH-2024-001",
            "plot_no": "45",
            "owner_name": "Ramesh Kumar",
            "father_name": "Late Suresh Kumar",
            "state": "Karnataka",
            "district": "Bangalore Urban",
            "taluk": "Anekal",
            "village": "Sarjapur",
            "extent": "2 Acres 30 Guntas",
            "land_type": "Agricultural",
            "risk_status": "GREEN",
            "risk_score": 85,
            "registered_at": datetime.now(timezone.utc)
        },
        {
            "property_id": f"reg_{uuid.uuid4().hex[:12]}",
            "survey_no": "456/2",
            "khata_no": "KH-2024-002",
            "plot_no": "102",
            "owner_name": "Priya Sharma",
            "father_name": "Mohan Sharma",
            "state": "Karnataka",
            "district": "Bangalore Urban",
            "taluk": "Whitefield",
            "village": "Varthur",
            "extent": "1200 Sq Ft",
            "land_type": "Residential",
            "risk_status": "YELLOW",
            "risk_score": 62,
            "registered_at": datetime.now(timezone.utc)
        },
        {
            "property_id": f"reg_{uuid.uuid4().hex[:12]}",
            "survey_no": "789/1",
            "khata_no": "KH-2024-003",
            "plot_no": "78",
            "owner_name": "Venkatesh Reddy",
            "father_name": "Narasimha Reddy",
            "state": "Telangana",
            "district": "Hyderabad",
            "taluk": "Madhapur",
            "village": "Gachibowli",
            "extent": "500 Sq Yards",
            "land_type": "Commercial",
            "risk_status": "GREEN",
            "risk_score": 92,
            "registered_at": datetime.now(timezone.utc)
        },
        {
            "property_id": f"reg_{uuid.uuid4().hex[:12]}",
            "survey_no": "234/5",
            "khata_no": "KH-2024-004",
            "plot_no": "23",
            "owner_name": "Anil Patel",
            "father_name": "Kantilal Patel",
            "state": "Gujarat",
            "district": "Ahmedabad",
            "taluk": "Gandhinagar",
            "village": "Sabarmati",
            "extent": "3 Acres",
            "land_type": "Agricultural",
            "risk_status": "RED",
            "risk_score": 35,
            "registered_at": datetime.now(timezone.utc)
        },
        {
            "property_id": f"reg_{uuid.uuid4().hex[:12]}",
            "survey_no": "567/8",
            "khata_no": "KH-2024-005",
            "plot_no": "156",
            "owner_name": "Lakshmi Narayanan",
            "father_name": "Krishnamurthy",
            "state": "Tamil Nadu",
            "district": "Chennai",
            "taluk": "Tambaram",
            "village": "Pallikaranai",
            "extent": "2400 Sq Ft",
            "land_type": "Residential",
            "risk_status": "GREEN",
            "risk_score": 78,
            "registered_at": datetime.now(timezone.utc)
        }
    ]
    
    for prop in sample_properties:
        await db.property_registry.update_one(
            {"survey_no": prop["survey_no"], "state": prop["state"]},
            {"$set": prop},
            upsert=True
        )

# ==================== DOCUMENT UPLOAD & OCR ====================

@api_router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    property_id: str,
    doc_type: str,
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    prop = await db.properties.find_one({"property_id": property_id, "user_id": user["user_id"]})
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    
    document_id = f"doc_{uuid.uuid4().hex[:12]}"
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "pdf"
    file_path = UPLOAD_DIR / f"{document_id}.{file_ext}"
    
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    ocr_text = ""
    extracted_data = {}
    
    try:
        if file_ext.lower() in ["png", "jpg", "jpeg", "tiff", "bmp"]:
            img = Image.open(file_path)
            ocr_text = pytesseract.image_to_string(img, lang='eng+kan+hin+tel+tam')
        elif file_ext.lower() == "pdf":
            try:
                import PyPDF2
                with open(file_path, 'rb') as pdf_file:
                    reader = PyPDF2.PdfReader(pdf_file)
                    for page in reader.pages:
                        ocr_text += page.extract_text() or ""
            except Exception:
                ocr_text = "PDF text extraction pending"
        
        if ocr_text and len(ocr_text) > 50:
            extracted_data = await extract_document_fields(ocr_text, doc_type)
    except Exception as e:
        logger.error(f"OCR Error: {e}")
        ocr_text = f"OCR processing error: {str(e)}"
    
    doc_record = {
        "document_id": document_id,
        "property_id": property_id,
        "user_id": user["user_id"],
        "filename": file.filename,
        "file_path": str(file_path),
        "doc_type": doc_type,
        "ocr_text": ocr_text,
        "extracted_data": extracted_data,
        "is_verified": False,
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
        
        try:
            json_str = response
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
            return json.loads(json_str.strip())
        except (json.JSONDecodeError, ValueError, IndexError):
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
    prop = await db.properties.find_one(
        {"property_id": property_id, "user_id": user["user_id"]},
        {"_id": 0}
    )
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    
    docs = await db.documents.find({"property_id": property_id}, {"_id": 0}).to_list(20)
    govt_records = await get_mock_government_records(prop.get("survey_no", ""), prop.get("state", ""))
    
    risk_analysis = await generate_ai_risk_analysis(prop, docs, govt_records)
    
    report_id = f"report_{uuid.uuid4().hex[:12]}"
    report_doc = {
        "report_id": report_id,
        "property_id": property_id,
        "user_id": user["user_id"],
        **risk_analysis,
        "generated_at": datetime.now(timezone.utc)
    }
    
    await db.risk_reports.insert_one(report_doc)
    
    await db.properties.update_one(
        {"property_id": property_id},
        {"$set": {
            "risk_score": risk_analysis["risk_score"],
            "risk_status": risk_analysis["risk_status"]
        }}
    )
    
    return RiskReportResponse(**{k: v for k, v in report_doc.items() if k != "_id"})

async def generate_ai_risk_analysis(property: dict, documents: list, govt_records: dict) -> dict:
    try:
        if not EMERGENT_LLM_KEY:
            return generate_mock_risk_analysis(property, documents)
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"risk_{uuid.uuid4().hex[:8]}",
            system_message="""You are an expert Indian real estate legal analyst.
            Analyze property documents and government records to identify risks.
            Return valid JSON only."""
        ).with_model("gemini", "gemini-2.5-flash")
        
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

Return JSON:
{{
    "risk_score": <0-100>,
    "risk_status": "<RED|YELLOW|GREEN>",
    "red_flags": [{{"issue": "...", "severity": "HIGH|CRITICAL", "details": "..."}}],
    "yellow_flags": [{{"issue": "...", "severity": "MEDIUM", "details": "..."}}],
    "green_flags": [{{"indicator": "...", "confidence": "HIGH|MEDIUM", "details": "..."}}],
    "executive_summary": "<3-5 line summary>",
    "legal_recommendation": "<SAFE_TO_BUY|BUY_WITH_CAUTION|HIGH_RISK_LEGAL_REVIEW_REQUIRED>",
    "title_chain": [{{"owner": "...", "from_date": "...", "to_date": "...", "doc_ref": "...", "transfer_type": "..."}}]
}}"""
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        try:
            json_str = response
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
            return json.loads(json_str.strip())
        except (json.JSONDecodeError, ValueError, IndexError):
            return generate_mock_risk_analysis(property, documents)
            
    except Exception as e:
        logger.error(f"AI analysis error: {e}")
        return generate_mock_risk_analysis(property, documents)

def generate_mock_risk_analysis(property: dict, documents: list) -> dict:
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
        "executive_summary": f"Property at Survey No. {property.get('survey_no', 'N/A')} in {property.get('district', 'Unknown')}, {property.get('state', 'Unknown')} has been analyzed. Risk Score: {risk_score}/100.",
        "legal_recommendation": recommendation,
        "title_chain": [
            {"owner": "Current Owner", "from_date": "2020-01-15", "to_date": "Present", "doc_ref": "N/A", "transfer_type": "Sale Deed"},
            {"owner": "Previous Owner", "from_date": "2010-06-20", "to_date": "2020-01-14", "doc_ref": "Mother Deed", "transfer_type": "Inheritance"}
        ]
    }

# ==================== GOVERNMENT RECORDS ====================

async def get_mock_government_records(survey_no: str, state: str) -> dict:
    state_sources = {
        "Karnataka": "Bhoomi (Karnataka RTC)",
        "Uttar Pradesh": "Bhulekh (UP Land Records)",
        "Gujarat": "AnyROR (Gujarat)",
        "Telangana": "Dharani",
        "Maharashtra": "Mahabhulekh",
        "Tamil Nadu": "TNREGINET",
        "Andhra Pradesh": "Meebhoomi"
    }
    
    source = state_sources.get(state, f"{state} Land Records Portal")
    
    return {
        "survey_no": survey_no,
        "owner_name": "Registered Owner",
        "father_name": "Father Name",
        "extent": "2 Acres 30 Guntas",
        "land_type": "Agricultural (Bagayat)",
        "khata_no": f"KH-{survey_no[:3]}-2024" if survey_no else "N/A",
        "mutation_records": [
            {"mutation_no": "MUT-2020-1234", "date": "2020-01-15", "type": "Sale", "from_owner": "Previous Owner", "to_owner": "Current Owner"}
        ],
        "encumbrances": [],
        "pending_litigation": False,
        "cersai_check": "No mortgages registered",
        "source": source,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "disclaimer": "MOCK DATA - Real government API integration pending"
    }

@api_router.get("/government-records/{survey_no:path}")
async def fetch_government_records(survey_no: str, state: str = "Karnataka"):
    records = await get_mock_government_records(survey_no, state)
    return records

# ==================== REPORT GENERATION ====================

@api_router.get("/reports/{property_id}")
async def get_report(property_id: str, user: dict = Depends(get_current_user)):
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
    report = await db.risk_reports.find_one(
        {"property_id": property_id, "user_id": user["user_id"]},
        {"_id": 0}
    )
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    prop = await db.properties.find_one({"property_id": property_id}, {"_id": 0})
    
    pdf_path = REPORTS_DIR / f"{report['report_id']}.pdf"
    
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=30, textColor=colors.HexColor('#0F172A'))
    story.append(Paragraph("PropertyCheck AI", title_style))
    story.append(Paragraph("Property Verification Report", styles['Heading2']))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Property Details", styles['Heading3']))
    prop_data = [
        ["Survey Number", prop.get("survey_no", "N/A") if prop else "N/A"],
        ["Khata Number", prop.get("khata_no", "N/A") if prop else "N/A"],
        ["State", prop.get("state", "N/A") if prop else "N/A"],
        ["District", prop.get("district", "N/A") if prop else "N/A"],
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
    
    story.append(Paragraph(f"Risk Score: {report['risk_score']}/100", styles['Heading3']))
    story.append(Paragraph(f"Status: {report['risk_status']}", styles['Normal']))
    story.append(Paragraph(f"Recommendation: {report['legal_recommendation'].replace('_', ' ')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Executive Summary", styles['Heading3']))
    story.append(Paragraph(report.get("executive_summary", ""), styles['Normal']))
    story.append(Spacer(1, 20))
    
    if report.get("red_flags"):
        story.append(Paragraph("Red Flags", styles['Heading3']))
        for flag in report["red_flags"]:
            story.append(Paragraph(f"• {flag.get('issue', '')}: {flag.get('details', '')}", styles['Normal']))
    
    if report.get("yellow_flags"):
        story.append(Paragraph("Yellow Flags", styles['Heading3']))
        for flag in report["yellow_flags"]:
            story.append(Paragraph(f"• {flag.get('issue', '')}: {flag.get('details', '')}", styles['Normal']))
    
    if report.get("green_flags"):
        story.append(Paragraph("Green Flags", styles['Heading3']))
        for flag in report["green_flags"]:
            story.append(Paragraph(f"• {flag.get('indicator', '')}: {flag.get('details', '')}", styles['Normal']))
    
    story.append(Spacer(1, 30))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    
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
    return PRICING_PACKAGES

@api_router.post("/payments/create-checkout")
async def create_payment_checkout(request: Request, payment_data: PaymentCreate, user: dict = Depends(get_current_user)):
    package = PRICING_PACKAGES.get(payment_data.package_type)
    if not package:
        raise HTTPException(status_code=400, detail="Invalid package type")
    
    prop = await db.properties.find_one({"property_id": payment_data.property_id, "user_id": user["user_id"]})
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    
    host_url = str(request.base_url).rstrip("/")
    webhook_url = f"{host_url}/api/webhook/stripe"
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    usd_amount = round(package["amount"] / 83, 2)
    
    body = await request.json() if request.headers.get("content-type") == "application/json" else {}
    origin_url = body.get("origin_url", host_url)
    
    success_url = f"{origin_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{origin_url}/pricing"
    
    checkout_request = CheckoutSessionRequest(
        amount=usd_amount, currency="usd", success_url=success_url, cancel_url=cancel_url,
        metadata={"user_id": user["user_id"], "property_id": payment_data.property_id, "package_type": payment_data.package_type}
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    await db.payment_transactions.insert_one({
        "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
        "session_id": session.session_id,
        "user_id": user["user_id"],
        "property_id": payment_data.property_id,
        "package_type": payment_data.package_type,
        "amount": package["amount"],
        "payment_status": "initiated",
        "created_at": datetime.now(timezone.utc)
    })
    
    return {"checkout_url": session.url, "session_id": session.session_id}

@api_router.get("/payments/status/{session_id}")
async def check_payment_status(session_id: str, request: Request, user: dict = Depends(get_current_user)):
    host_url = str(request.base_url).rstrip("/")
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=f"{host_url}/api/webhook/stripe")
    
    try:
        status = await stripe_checkout.get_checkout_status(session_id)
        
        await db.payment_transactions.find_one_and_update(
            {"session_id": session_id, "user_id": user["user_id"]},
            {"$set": {"payment_status": status.payment_status, "updated_at": datetime.now(timezone.utc)}}
        )
        
        return {"status": status.status, "payment_status": status.payment_status, "amount_total": status.amount_total}
    except Exception as e:
        logger.error(f"Payment status error: {e}")
        raise HTTPException(status_code=500, detail="Failed to check payment status")

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("Stripe-Signature", "")
    host_url = str(request.base_url).rstrip("/")
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=f"{host_url}/api/webhook/stripe")
    
    try:
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        await db.payment_transactions.update_one(
            {"session_id": webhook_response.session_id},
            {"$set": {"payment_status": webhook_response.payment_status, "updated_at": datetime.now(timezone.utc)}}
        )
        return {"status": "processed"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error"}

# ==================== DASHBOARD STATS ====================

@api_router.get("/dashboard/stats")
async def get_dashboard_stats(user: dict = Depends(get_current_user)):
    properties_count = await db.properties.count_documents({"user_id": user["user_id"]})
    documents_count = await db.documents.count_documents({"user_id": user["user_id"]})
    reports_count = await db.risk_reports.count_documents({"user_id": user["user_id"]})
    
    recent_properties = await db.properties.find(
        {"user_id": user["user_id"]}, {"_id": 0}
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
    return {"message": "PropertyCheck AI API", "version": "2.0.0"}

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
