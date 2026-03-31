"""Record Alert Subscription - Notify users when new government records are detected"""
import uuid
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Depends, Request
from config import db, logger
from utils.auth import get_current_user

router = APIRouter(prefix="/alerts")


@router.post("/subscribe")
async def subscribe_alert(request: Request, user: dict = Depends(get_current_user)):
    """Subscribe to record alerts for a property/state combination"""
    body = await request.json()
    property_id = body.get("propertyId") or body.get("property_id", "")
    state = body.get("state", "").lower().replace(" ", "")
    document_types = body.get("documentTypes", [])
    frequency = body.get("frequency", "daily")  # daily, weekly, instant

    if not state:
        raise HTTPException(status_code=400, detail="state is required")

    sub_id = f"alert_{uuid.uuid4().hex[:12]}"
    subscription = {
        "subscription_id": sub_id,
        "user_id": user["user_id"],
        "property_id": property_id,
        "state": state,
        "document_types": document_types,
        "frequency": frequency,
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_checked": datetime.now(timezone.utc).isoformat(),
        "last_notified": None,
        "records_found": 0,
    }
    await db.record_alerts.insert_one(subscription)
    return {"subscription_id": sub_id, "status": "active", "message": f"Alert subscription created for {state}"}


@router.get("/subscriptions")
async def list_subscriptions(user: dict = Depends(get_current_user)):
    """List all active alert subscriptions"""
    subs = await db.record_alerts.find(
        {"user_id": user["user_id"]}, {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    return {"subscriptions": subs, "total": len(subs)}


@router.put("/subscription/{sub_id}")
async def update_subscription(sub_id: str, request: Request, user: dict = Depends(get_current_user)):
    """Update or toggle a subscription"""
    body = await request.json()
    update_fields = {}
    if "active" in body:
        update_fields["active"] = body["active"]
    if "frequency" in body:
        update_fields["frequency"] = body["frequency"]
    if "documentTypes" in body:
        update_fields["document_types"] = body["documentTypes"]

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()
    result = await db.record_alerts.update_one(
        {"subscription_id": sub_id, "user_id": user["user_id"]},
        {"$set": update_fields},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"status": "updated", "subscription_id": sub_id}


@router.delete("/subscription/{sub_id}")
async def delete_subscription(sub_id: str, user: dict = Depends(get_current_user)):
    """Delete a subscription"""
    result = await db.record_alerts.delete_one(
        {"subscription_id": sub_id, "user_id": user["user_id"]}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"status": "deleted", "subscription_id": sub_id}


@router.get("/notifications")
async def get_notifications(user: dict = Depends(get_current_user), limit: int = 20):
    """Get recent alert notifications"""
    notifications = await db.alert_notifications.find(
        {"user_id": user["user_id"]}, {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    return {"notifications": notifications, "total": len(notifications)}


@router.post("/check-now/{sub_id}")
async def manual_check(sub_id: str, user: dict = Depends(get_current_user)):
    """Manually trigger a check for new records"""
    sub = await db.record_alerts.find_one(
        {"subscription_id": sub_id, "user_id": user["user_id"]}, {"_id": 0}
    )
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Simulate checking for new records
    asyncio.create_task(_check_for_new_records(sub, user["user_id"]))
    return {"status": "checking", "message": "Checking for new records..."}


async def _check_for_new_records(sub: dict, user_id: str):
    """Background task to check for new records and create notification"""
    import random
    await asyncio.sleep(2)

    # Simulate finding new records
    has_new = random.random() > 0.6
    now = datetime.now(timezone.utc).isoformat()

    await db.record_alerts.update_one(
        {"subscription_id": sub["subscription_id"]},
        {"$set": {"last_checked": now}},
    )

    if has_new:
        notification = {
            "notification_id": f"notif_{uuid.uuid4().hex[:12]}",
            "user_id": user_id,
            "subscription_id": sub["subscription_id"],
            "state": sub["state"],
            "property_id": sub.get("property_id", ""),
            "message": f"New {sub['state'].title()} land record update detected",
            "details": "A mutation entry was updated in the government portal. Review the latest records.",
            "record_type": "MUTATION",
            "read": False,
            "created_at": now,
        }
        await db.alert_notifications.insert_one(notification)
        await db.record_alerts.update_one(
            {"subscription_id": sub["subscription_id"]},
            {"$set": {"last_notified": now}, "$inc": {"records_found": 1}},
        )
