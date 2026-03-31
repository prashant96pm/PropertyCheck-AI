# PropertyCheck AI - Product Requirements Document

## Original Problem Statement
Build a production-grade SaaS web application called **PropertyCheck AI**, an AI-powered property intelligence and verification platform for India. The platform combines features from Landeed (land record discovery), Zillow (property intelligence), and Palantir (data integration).

## Tech Stack
- **Frontend**: React, TailwindCSS, ShadCN UI, D3.js, Leaflet.js, react-i18next
- **Backend**: FastAPI, Python, motor (async MongoDB), emergentintegrations (Gemini LLM)
- **Database**: MongoDB
- **Auth**: JWT + Emergent Google OAuth
- **Integrations**: Gemini LLM (Emergent key), Stripe, Razorpay, Playwright (scrapers)

## What's Been Implemented (Complete)

### P0 - Core MVP
- Universal Property Search (keyword + advanced)
- Property 360 Dashboard & Detail pages
- Document upload & management
- Risk Score Engine (deterministic, 0-100)
- AI Legal Copilot (Gemini mock/live)
- Property Valuation estimates
- Shareable public report pages
- User auth (JWT + Google OAuth)
- Profile, Settings, Legal pages

### P1 - Backend Refactor (DONE)
- Monolithic server.py → modular APIRouter architecture
- Routes: auth, properties, search, intelligence, reports, payments, admin, enterprise, jobs, fraud, alerts
- Models, utils, config separated

### P1 - Advanced Features (DONE)
- Knowledge Graph (D3.js interactive visualization)
- Map Integration (Leaflet.js)
- Enterprise API Layer + API Docs page
- Admin Panel (admin-role users)
- Title Chain Visualization (D3.js timeline)
- Razorpay & Stripe payment integration
- Background Jobs (async processing)

### P1 - GovDataBridge Module (DONE)
- Full module: `/app/backend/modules/gov_data_bridge/`
- Mock scrapers for ALL 20 Indian states
- Live scrapers for 20 states (httpx + bs4 with auto mock fallback)
- 3-tier CAPTCHA solving: 2Captcha API → OCR (pytesseract) → Mock
- S3 storage with auto local fallback (boto3 → local file)
- Job processor (async background tasks)
- Frontend GovDataBridge component

### P1 - AI Fraud Detection Engine (DONE - March 2026)
- POST /api/fraud/analyze/{property_id} - Gemini LLM analysis
- Rule-based fallback if LLM unavailable
- Returns: fraud_score (0-100), risk_level, findings[], recommended_actions[]
- Results stored in MongoDB fraud_reports collection
- GET /api/fraud/report/{property_id} for retrieval

### P1 - Record Alert Subscriptions (DONE - March 2026)
- POST /api/alerts/subscribe - Create alert subscription
- GET /api/alerts/subscriptions - List user subscriptions
- PUT/DELETE /api/alerts/subscription/{sub_id} - Manage subscriptions
- POST /api/alerts/check-now/{sub_id} - Manual check trigger
- GET /api/alerts/notifications - Get notifications
- Background task simulates record detection

### P1 - Light/Dark Mode (DONE - March 2026)
- CSS variables for both themes in index.css
- ThemeContext with localStorage persistence
- Dark (default), Light, System mode options
- Glass-card light mode overrides

### P1 - Multi-language i18n (DONE - March 2026)
- 23 languages: English + 22 Scheduled Indian languages
- Priority 1: Hindi, Kannada, Tamil, Telugu, Marathi (full translations)
- Priority 2: Bengali, Gujarati, Malayalam, Odia, Punjabi, Assamese, Urdu
- Priority 3: Sindhi, Nepali, Sanskrit, Konkani, Maithili, Dogri, Manipuri, Santali, Bodo, Kashmiri
- Language persisted to localStorage
- Settings page with expandable language picker

## Current Mocked Services
- Government portal scrapers (GOV_MOCK_MODE=true, live attempted first with fallback)
- 2Captcha (no API key → falls back to OCR/mock)
- S3 (no AWS keys → falls back to local storage)
- AI Legal Copilot & Fraud Detection use real Gemini LLM when key available

## Architecture
```
/app
├── backend/
│   ├── app.py (main entry)
│   ├── config.py
│   ├── modules/gov_data_bridge/ (scrapers, captcha, storage)
│   ├── routes/ (auth, properties, search, intelligence, reports, payments, admin, enterprise, jobs, fraud, alerts)
│   ├── models/
│   └── utils/
├── frontend/
│   ├── src/
│   │   ├── i18n/ (23 language files)
│   │   ├── contexts/ (Auth, Theme)
│   │   ├── components/
│   │   └── pages/
```

## Remaining Future Tasks
- Mobile responsiveness improvements (P3)
- Live Government API integration (when portals support it) (P3)
- Real-time WebSocket notifications for alerts (P3)
