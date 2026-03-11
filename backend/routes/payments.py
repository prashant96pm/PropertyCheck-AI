"""Payments - Pricing, Stripe Checkout, Razorpay"""
from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime, timezone
import uuid
import razorpay
from config import db, STRIPE_API_KEY, RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, logger
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
    payment_method = body.get("payment_method", "stripe")

    if package_type not in PRICING:
        raise HTTPException(status_code=400, detail="Invalid package type")

    package = PRICING[package_type]
    amount = package["amount"]

    if payment_method == "razorpay":
        return await _create_razorpay_order(user, property_id, package_type, package, amount, origin_url)

    # Stripe checkout
    if STRIPE_API_KEY and StripeCheckout:
        try:
            host_url = str(request.base_url).rstrip("/")
            webhook_url = f"{host_url}/api/webhook/stripe"
            checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)

            success_url = f"{origin_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}&property_id={property_id}"
            cancel_url = f"{origin_url}/pricing?property_id={property_id}"

            req = CheckoutSessionRequest(
                amount=float(amount),
                currency=package["currency"].lower(),
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={"property_id": property_id, "user_id": user["user_id"], "package_type": package_type}
            )
            session = await checkout.create_checkout_session(req)

            await db.payment_transactions.insert_one({
                "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
                "session_id": session.session_id,
                "user_id": user["user_id"],
                "property_id": property_id,
                "package_type": package_type,
                "amount": amount,
                "currency": package["currency"],
                "payment_method": "stripe",
                "payment_status": "initiated",
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
            return {"checkout_url": session.url, "session_id": session.session_id, "payment_method": "stripe"}
        except Exception as e:
            logger.error(f"Stripe error: {e}")
            raise HTTPException(status_code=500, detail="Payment processing error")

    return {"checkout_url": f"{origin_url}/payment/success?property_id={property_id}", "session_id": "mock_session", "payment_method": "mock"}


async def _create_razorpay_order(user, property_id, package_type, package, amount, origin_url):
    """Create Razorpay order"""
    if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
        try:
            client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
            order = client.order.create({
                "amount": int(amount * 100),
                "currency": package["currency"],
                "payment_capture": 1,
                "notes": {"property_id": property_id, "user_id": user["user_id"], "package_type": package_type}
            })

            await db.payment_transactions.insert_one({
                "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
                "order_id": order["id"],
                "user_id": user["user_id"],
                "property_id": property_id,
                "package_type": package_type,
                "amount": amount,
                "currency": package["currency"],
                "payment_method": "razorpay",
                "payment_status": "initiated",
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
            return {
                "order_id": order["id"],
                "amount": order["amount"],
                "currency": order["currency"],
                "razorpay_key_id": RAZORPAY_KEY_ID,
                "payment_method": "razorpay",
            }
        except Exception as e:
            logger.error(f"Razorpay error: {e}")
            raise HTTPException(status_code=500, detail="Payment processing error")
    raise HTTPException(status_code=500, detail="Razorpay not configured")


@router.post("/payments/razorpay-verify")
async def verify_razorpay(request: Request, user: dict = Depends(get_current_user)):
    """Verify Razorpay payment after completion"""
    body = await request.json()
    order_id = body.get("order_id")
    payment_id = body.get("razorpay_payment_id")
    signature = body.get("razorpay_signature")

    if not all([order_id, payment_id, signature]):
        raise HTTPException(status_code=400, detail="Missing payment details")

    if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
        try:
            client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
            client.utility.verify_payment_signature({
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            })
            await db.payment_transactions.update_one(
                {"order_id": order_id, "user_id": user["user_id"]},
                {"$set": {
                    "payment_id": payment_id,
                    "payment_status": "paid",
                    "signature": signature,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }}
            )
            return {"status": "success", "payment_status": "paid", "payment_id": payment_id}
        except razorpay.errors.SignatureVerificationError:
            await db.payment_transactions.update_one(
                {"order_id": order_id},
                {"$set": {"payment_status": "failed", "updated_at": datetime.now(timezone.utc).isoformat()}}
            )
            raise HTTPException(status_code=400, detail="Payment verification failed")
        except Exception as e:
            logger.error(f"Razorpay verify error: {e}")
            raise HTTPException(status_code=500, detail="Verification error")
    raise HTTPException(status_code=500, detail="Razorpay not configured")


@router.get("/payments/status/{session_id}")
async def check_payment_status(session_id: str, request: Request, user: dict = Depends(get_current_user)):
    """Check Stripe payment status and update DB"""
    txn = await db.payment_transactions.find_one(
        {"session_id": session_id, "user_id": user["user_id"]}, {"_id": 0}
    )
    if not txn:
        return {"status": "not_found", "payment_status": "unknown"}

    if txn.get("payment_status") == "paid":
        return {"status": "complete", "payment_status": "paid", "amount_total": txn.get("amount", 0)}

    if STRIPE_API_KEY and StripeCheckout:
        try:
            checkout = StripeCheckout(api_key=STRIPE_API_KEY)
            status = await checkout.get_checkout_status(session_id)
            new_status = status.payment_status
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {"$set": {"payment_status": new_status, "updated_at": datetime.now(timezone.utc).isoformat()}}
            )
            return {"status": status.status, "payment_status": new_status, "amount_total": status.amount_total, "currency": status.currency}
        except Exception as e:
            logger.error(f"Payment status error: {e}")

    return {"status": "pending", "payment_status": txn.get("payment_status", "initiated")}


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
                {"$set": {
                    "payment_status": webhook_response.payment_status,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }}
            )
            return {"status": "processed"}
        except Exception as e:
            logger.error(f"Webhook error: {e}")
    return {"status": "ok"}
