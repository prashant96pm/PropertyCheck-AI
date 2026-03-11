"""Payments - Pricing, Stripe Checkout"""
from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime, timezone
import uuid
from config import db, STRIPE_API_KEY, logger
from utils.auth import get_current_user

try:
    from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
except ImportError:
    StripeCheckout = None

router = APIRouter()

PRICING = {
    "basic": {"name": "Basic Verification", "amount": 499.0, "currency": "INR", "features": ["AI Risk Score", "Basic Title Check", "Document OCR", "PDF Report"]},
    "standard": {"name": "Standard Due Diligence", "amount": 1499.0, "currency": "INR", "features": ["Everything in Basic", "30-Year Title Chain", "Encumbrance Check", "Legal Copilot Analysis", "Government Records Check", "PDF Report"]},
    "premium": {"name": "Premium Intelligence", "amount": 2999.0, "currency": "INR", "features": ["Everything in Standard", "AI Legal Opinion", "Property Valuation", "Market Intelligence", "Shareable Report Link", "Priority Support"]},
}


@router.get("/pricing")
async def get_pricing():
    return PRICING


@router.post("/payments/create-checkout")
async def create_checkout(request: Request, user: dict = Depends(get_current_user)):
    body = await request.json()
    property_id = body.get("property_id")
    package_type = body.get("package_type", "basic")
    origin_url = body.get("origin_url", "")
    if package_type not in PRICING:
        raise HTTPException(status_code=400, detail="Invalid package type")
    package = PRICING[package_type]
    if STRIPE_API_KEY and StripeCheckout:
        try:
            checkout = StripeCheckout(api_key=STRIPE_API_KEY)
            session = await checkout.create_session(CheckoutSessionRequest(
                product_name=package["name"], unit_amount=int(package["amount"] * 100), currency=package["currency"].lower(),
                success_url=f"{origin_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}&property_id={property_id}",
                cancel_url=f"{origin_url}/pricing?property_id={property_id}",
                metadata={"property_id": property_id, "user_id": user["user_id"], "package_type": package_type}
            ))
            return {"checkout_url": session.url, "session_id": session.id}
        except Exception as e:
            logger.error(f"Stripe error: {e}")
            raise HTTPException(status_code=500, detail="Payment processing error")
    return {"checkout_url": f"{origin_url}/payment/success?property_id={property_id}", "session_id": "mock_session"}


@router.get("/payments/status/{session_id}")
async def check_payment_status(session_id: str, request: Request, user: dict = Depends(get_current_user)):
    """Check payment status"""
    txn = await db.payment_transactions.find_one({"session_id": session_id, "user_id": user["user_id"]}, {"_id": 0})
    if not txn:
        return {"status": "not_found", "payment_status": "unknown"}
    if STRIPE_API_KEY and StripeCheckout:
        try:
            checkout = StripeCheckout(api_key=STRIPE_API_KEY)
            status = await checkout.get_checkout_status(session_id)
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {"$set": {"payment_status": status.payment_status, "updated_at": datetime.now(timezone.utc).isoformat()}}
            )
            return {"status": status.status, "payment_status": status.payment_status, "amount_total": status.amount_total}
        except Exception as e:
            logger.error(f"Payment status error: {e}")
    return {"status": "completed", "payment_status": txn.get("payment_status", "initiated")}


@router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    body = await request.body()
    signature = request.headers.get("Stripe-Signature", "")
    if STRIPE_API_KEY and StripeCheckout:
        try:
            checkout = StripeCheckout(api_key=STRIPE_API_KEY)
            webhook_response = await checkout.handle_webhook(body, signature)
            await db.payment_transactions.update_one(
                {"session_id": webhook_response.session_id},
                {"$set": {"payment_status": webhook_response.payment_status, "updated_at": datetime.now(timezone.utc).isoformat()}}
            )
            return {"status": "processed"}
        except Exception as e:
            logger.error(f"Webhook error: {e}")
    return {"status": "ok"}
