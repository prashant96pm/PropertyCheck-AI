"""Admin Panel - System stats, user management"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone, timedelta
from config import db
from utils.auth import get_current_user

router = APIRouter(prefix="/admin")


async def require_admin(user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.get("/stats")
async def admin_stats(user: dict = Depends(require_admin)):
    total_users = await db.users.count_documents({})
    total_properties = await db.properties.count_documents({})
    total_reports = await db.risk_reports.count_documents({})
    total_documents = await db.documents.count_documents({})
    total_searches = await db.property_search_index.count_documents({})
    recent_users = await db.users.find({}, {"_id": 0, "password": 0}).sort("created_at", -1).limit(10).to_list(10)
    return {
        "total_users": total_users, "total_properties": total_properties,
        "total_reports": total_reports, "total_documents": total_documents,
        "total_searches": total_searches, "recent_users": recent_users,
    }


@router.get("/users")
async def admin_users(user: dict = Depends(require_admin), limit: int = 50, skip: int = 0):
    users = await db.users.find({}, {"_id": 0, "password": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.users.count_documents({})
    return {"users": users, "total": total}


@router.put("/users/{user_id}/role")
async def update_user_role(user_id: str, role: str, admin: dict = Depends(require_admin)):
    if role not in ["user", "admin", "lawyer", "bank"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    await db.users.update_one({"user_id": user_id}, {"$set": {"role": role}})
    return {"message": f"User role updated to {role}"}


@router.get("/verifications")
async def admin_verifications(user: dict = Depends(require_admin), limit: int = 50):
    reports = await db.risk_reports.find({}, {"_id": 0}).sort("generated_at", -1).limit(limit).to_list(limit)
    return {"verifications": reports, "total": len(reports)}
