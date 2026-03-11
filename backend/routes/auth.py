from fastapi import APIRouter, HTTPException, Depends, Request, Response
from datetime import datetime, timezone
import uuid
from config import db, JWT_EXPIRATION_HOURS, logger
from utils.auth import hash_password, verify_password, create_jwt_token, get_current_user
from models.schemas import UserCreate, UserLogin, UserResponse, TokenResponse

router = APIRouter()

@router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserCreate, response: Response):
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    hashed_pw = hash_password(user_data.password)
    user_doc = {
        "user_id": user_id, "email": user_data.email, "name": user_data.name,
        "password": hashed_pw, "picture": None, "role": "user",
        "created_at": datetime.now(timezone.utc).isoformat(), "auth_provider": "email"
    }
    await db.users.insert_one(user_doc)
    token = create_jwt_token(user_id, user_data.email, "user")
    response.set_cookie(key="session_token", value=token, httponly=True, secure=True, samesite="none", max_age=JWT_EXPIRATION_HOURS * 3600, path="/")
    return TokenResponse(access_token=token, user=UserResponse(user_id=user_id, email=user_data.email, name=user_data.name, role="user"))

@router.post("/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin, response: Response):
    user = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(user_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_jwt_token(user["user_id"], user["email"], user.get("role", "user"))
    response.set_cookie(key="session_token", value=token, httponly=True, secure=True, samesite="none", max_age=JWT_EXPIRATION_HOURS * 3600, path="/")
    return TokenResponse(access_token=token, user=UserResponse(user_id=user["user_id"], email=user["email"], name=user["name"], picture=user.get("picture"), role=user.get("role", "user")))

@router.get("/auth/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    return UserResponse(user_id=user["user_id"], email=user["email"], name=user["name"], picture=user.get("picture"), role=user.get("role", "user"), auth_provider=user.get("auth_provider", "email"))

@router.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Logged out successfully"}

@router.post("/auth/session")
async def process_oauth_session(request: Request, response: Response):
    import httpx
    body = await request.json()
    session_id = body.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    async with httpx.AsyncClient() as client_http:
        resp = await client_http.get("https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data", headers={"X-Session-ID": session_id})
    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid session")
    oauth_data = resp.json()
    existing_user = await db.users.find_one({"email": oauth_data["email"]}, {"_id": 0})
    if existing_user:
        user_id = existing_user["user_id"]
        await db.users.update_one({"user_id": user_id}, {"$set": {"name": oauth_data["name"], "picture": oauth_data.get("picture")}})
    else:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        await db.users.insert_one({"user_id": user_id, "email": oauth_data["email"], "name": oauth_data["name"], "picture": oauth_data.get("picture"), "password": None, "role": "user", "created_at": datetime.now(timezone.utc).isoformat(), "auth_provider": "google"})
    token = create_jwt_token(user_id, oauth_data["email"], "user")
    response.set_cookie(key="session_token", value=token, httponly=True, secure=True, samesite="none", max_age=JWT_EXPIRATION_HOURS * 3600, path="/")
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    return {"user_id": user_id, "email": user["email"], "name": user["name"], "picture": user.get("picture"), "access_token": token}

@router.get("/profile")
async def get_profile(user: dict = Depends(get_current_user)):
    user_doc = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "user_id": user_doc.get("user_id"), "email": user_doc.get("email"),
        "first_name": user_doc.get("first_name", user_doc.get("name", "").split(" ")[0] if user_doc.get("name") else ""),
        "last_name": user_doc.get("last_name", " ".join(user_doc.get("name", "").split(" ")[1:]) if user_doc.get("name") else ""),
        "gender": user_doc.get("gender", ""), "date_joined": user_doc.get("created_at", ""),
        "picture": user_doc.get("picture", ""), "auth_provider": user_doc.get("auth_provider", "email"),
    }

@router.put("/profile")
async def update_profile(request: Request, user: dict = Depends(get_current_user)):
    body = await request.json()
    update_fields = {}
    for f in ["first_name", "last_name", "gender"]:
        if f in body:
            update_fields[f] = body[f]
    if update_fields:
        if "first_name" in update_fields or "last_name" in update_fields:
            current = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
            fn = update_fields.get("first_name", current.get("first_name", ""))
            ln = update_fields.get("last_name", current.get("last_name", ""))
            update_fields["name"] = f"{fn} {ln}".strip()
        await db.users.update_one({"user_id": user["user_id"]}, {"$set": update_fields})
    return {"message": "Profile updated successfully"}

@router.get("/dashboard/stats")
async def get_dashboard_stats(user: dict = Depends(get_current_user)):
    properties_count = await db.properties.count_documents({"user_id": user["user_id"]})
    documents_count = await db.documents.count_documents({"user_id": user["user_id"]})
    reports_count = await db.risk_reports.count_documents({"user_id": user["user_id"]})
    recent_properties = await db.properties.find({"user_id": user["user_id"]}, {"_id": 0}).sort("created_at", -1).limit(5).to_list(5)
    return {"total_properties": properties_count, "total_documents": documents_count, "total_reports": reports_count, "recent_properties": recent_properties}
