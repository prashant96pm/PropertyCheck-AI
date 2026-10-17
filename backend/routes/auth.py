from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.responses import RedirectResponse
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode
import os
import secrets
import uuid
import httpx
from config import db, JWT_EXPIRATION_HOURS, logger, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, BACKEND_PUBLIC_URL, FRONTEND_URL
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

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"
OAUTH_STATE_TTL = timedelta(minutes=10)
OAUTH_SESSION_TTL = timedelta(minutes=5)


def _google_redirect_uri(request: Request) -> str:
    base = BACKEND_PUBLIC_URL or str(request.base_url).rstrip("/")
    return f"{base}/api/auth/google/callback"


def _allowed_frontend_origins() -> set:
    origins = {o.strip().rstrip("/") for o in os.environ.get("CORS_ORIGINS", "").split(",") if o.strip() and o.strip() != "*"}
    if FRONTEND_URL:
        origins.add(FRONTEND_URL)
    return origins


@router.get("/auth/google/login")
async def google_login(request: Request, redirect: str = ""):
    """Start the Google OAuth flow. `redirect` is the frontend origin to return to."""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=503, detail="Google sign-in is not configured")
    frontend = redirect.rstrip("/")
    if frontend not in _allowed_frontend_origins():
        frontend = FRONTEND_URL
    if not frontend:
        raise HTTPException(status_code=400, detail="Invalid redirect")
    state = secrets.token_urlsafe(32)
    await db.oauth_states.insert_one({"state": state, "frontend": frontend, "created_at": datetime.now(timezone.utc)})
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": _google_redirect_uri(request),
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "prompt": "select_account",
    }
    return RedirectResponse(f"{GOOGLE_AUTH_URL}?{urlencode(params)}")


@router.get("/auth/google/callback")
async def google_callback(request: Request, code: str = "", state: str = "", error: str = ""):
    """Google redirects here. Exchange the code, then hand the frontend a one-time session_id."""
    state_doc = await db.oauth_states.find_one_and_delete({"state": state}) if state else None
    if not state_doc:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")
    frontend = state_doc["frontend"]
    created = state_doc["created_at"]
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    if error or not code or datetime.now(timezone.utc) - created > OAUTH_STATE_TTL:
        return RedirectResponse(f"{frontend}/login")
    try:
        async with httpx.AsyncClient(timeout=15) as client_http:
            token_resp = await client_http.post(GOOGLE_TOKEN_URL, data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": _google_redirect_uri(request),
                "grant_type": "authorization_code",
            })
            token_resp.raise_for_status()
            access_token = token_resp.json()["access_token"]
            info_resp = await client_http.get(GOOGLE_USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"})
            info_resp.raise_for_status()
            info = info_resp.json()
    except Exception as e:
        logger.error(f"Google OAuth exchange failed: {e}")
        return RedirectResponse(f"{frontend}/login")
    if not info.get("email") or not info.get("email_verified", False):
        return RedirectResponse(f"{frontend}/login")
    session_id = secrets.token_urlsafe(32)
    await db.oauth_sessions.insert_one({
        "session_id": session_id,
        "email": info["email"],
        "name": info.get("name") or info["email"].split("@")[0],
        "picture": info.get("picture"),
        "created_at": datetime.now(timezone.utc),
    })
    return RedirectResponse(f"{frontend}/auth/callback#session_id={session_id}")


@router.post("/auth/session")
async def process_oauth_session(request: Request, response: Response):
    body = await request.json()
    session_id = body.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    oauth_data = await db.oauth_sessions.find_one_and_delete({"session_id": session_id}, {"_id": 0})
    if not oauth_data:
        raise HTTPException(status_code=401, detail="Invalid session")
    created = oauth_data["created_at"]
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) - created > OAUTH_SESSION_TTL:
        raise HTTPException(status_code=401, detail="Session expired")
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
