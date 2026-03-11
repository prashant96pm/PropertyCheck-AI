from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: str
    name: str
    email: str
    role: str = "user"
    picture: Optional[str] = None
    auth_provider: str = "email"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class PropertyCreate(BaseModel):
    survey_no: str
    khata_no: Optional[str] = None
    owner_name: Optional[str] = None
    state: str
    district: str
    taluk: Optional[str] = None
    village: Optional[str] = None
    extent: Optional[str] = None
    land_type: Optional[str] = None
    boundaries: Optional[Dict] = None

class PropertyResponse(BaseModel):
    property_id: str
    survey_no: str
    khata_no: Optional[str] = None
    owner_name: Optional[str] = None
    state: str
    district: str
    taluk: Optional[str] = None
    village: Optional[str] = None
    extent: Optional[str] = None
    land_type: Optional[str] = None
    boundaries: Optional[Dict] = None
    risk_score: Optional[int] = None
    risk_status: Optional[str] = None
    user_id: Optional[str] = None
    created_at: Optional[str] = None

class DocumentResponse(BaseModel):
    document_id: str
    property_id: str
    filename: str
    doc_type: str
    ocr_text: Optional[str] = None
    ocr_status: str = "pending"
    extracted_fields: Optional[Dict] = None
    uploaded_at: Optional[str] = None

class RiskReportResponse(BaseModel):
    report_id: str
    property_id: str
    risk_score: int
    risk_status: str
    summary: Optional[str] = None
    executive_summary: Optional[str] = None
    risk_factors: Optional[List[Dict]] = None
    recommendations: Optional[List[str]] = None
    ai_insights: Optional[str] = None
    generated_at: Optional[str] = None

class PaymentCreate(BaseModel):
    property_id: str
    package_type: str

class PropertySearchQuery(BaseModel):
    owner_name: Optional[str] = None
    survey_no: Optional[str] = None
    plot_no: Optional[str] = None
    khata_no: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None
    taluk: Optional[str] = None
    land_type: Optional[str] = None
    page: int = 1
    limit: int = 20

class SmartSearchQuery(BaseModel):
    query: str

class PropertyFullProfile(BaseModel):
    property_id: str
    basic_details: Optional[Dict] = None
    ownership_history: Optional[List[Dict]] = None
    legal_records: Optional[Dict] = None
    documents: Optional[List[Dict]] = None
    geo_spatial: Optional[Dict] = None
    risk_assessment: Optional[Dict] = None
    government_records: Optional[Dict] = None

class OwnerSearchResult(BaseModel):
    property_id: str
    owner_name: str
    survey_no: str
    district: str
    state: str
    match_score: Optional[float] = None
