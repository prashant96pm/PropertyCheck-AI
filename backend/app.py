"""PropertyCheck AI - Main Application Entry Point"""
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import os

from config import client, logger

# Create app
app = FastAPI(title="PropertyCheck AI API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and mount all route modules
from routes.auth import router as auth_router
from routes.properties import router as properties_router
from routes.search import router as search_router
from routes.intelligence import router as intelligence_router
from routes.reports import router as reports_router
from routes.payments import router as payments_router
from routes.admin import router as admin_router
from routes.enterprise import router as enterprise_router
from routes.jobs import router as jobs_router
from modules.gov_data_bridge.routes.gov_routes import router as gov_router
from routes.fraud import router as fraud_router
from routes.alerts import router as alerts_router

app.include_router(auth_router, prefix="/api")
app.include_router(properties_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(intelligence_router, prefix="/api")
app.include_router(reports_router, prefix="/api")
app.include_router(payments_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(enterprise_router, prefix="/api")
app.include_router(jobs_router, prefix="/api")
app.include_router(gov_router, prefix="/api")
app.include_router(fraud_router, prefix="/api")
app.include_router(alerts_router, prefix="/api")

# Health & root
from datetime import datetime, timezone

@app.get("/api/")
async def root():
    return {"name": "PropertyCheck AI API", "version": "2.0", "status": "running"}

@app.get("/api/health")
async def health_check():
    health = {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}
    try:
        await client.admin.command('ping')
        health["database"] = "connected"
    except Exception:
        health["database"] = "connecting"
    return health

@app.on_event("startup")
async def startup_db_client():
    try:
        await client.admin.command('ping')
        logger.info("MongoDB connection verified successfully")
    except Exception as e:
        logger.warning(f"MongoDB initial ping failed (will retry on demand): {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
