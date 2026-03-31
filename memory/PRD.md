# PropertyCheck AI - Product Requirements Document

## Original Problem Statement
Build a production-grade SaaS application called **PropertyCheck AI** — an AI-Powered Property Intelligence & Verification Platform for India. Combines Landeed, Zillow, Palantir, and AI Legal Copilot.

## Tech Stack
- **Frontend**: React + TailwindCSS + ShadCN UI (Glassmorphism dark theme)
- **Backend**: FastAPI (Python) - Modular APIRouter (10 route modules)
- **Database**: MongoDB (Atlas-ready)
- **AI/ML**: Gemini via Emergent LLM Key, Tesseract OCR
- **Auth**: JWT + Google OAuth (Emergent-managed)
- **Payments**: Stripe + Razorpay (dual gateway)
- **Visualization**: D3.js (Knowledge Graph + Title Chain), Leaflet.js (Maps)
- **GovDataBridge**: httpx + BeautifulSoup4 + pytesseract + boto3 (20 state scrapers)

## Architecture
```
/app/backend/
  app.py                    # Entry point (10 routers)
  config.py                 # Shared config
  models/schemas.py         # Pydantic models
  utils/auth.py             # Auth helpers
  routes/                   # 9 route modules
    auth.py, properties.py, search.py, intelligence.py,
    reports.py, payments.py, admin.py, enterprise.py, jobs.py
  modules/
    gov_data_bridge/        # GovDataBridge Module
      config/portals_config.py     # 20 state portal configs
      scrapers/                     # 20 state scrapers
        base/base_scraper.py       # Abstract base class
        karnataka/bhoomi_scraper.py
        telangana/dharani_scraper.py
        tamilnadu/tnregnet_scraper.py
        maharashtra/mahabhumi_scraper.py
        ... (16 more state scrapers)
      captcha/captcha_solver.py    # OCR + mock CAPTCHA solver
      queue/job_processor.py       # Async job processing
      storage/document_storage.py  # S3 + local PDF storage
      parsers/parsers.py           # HTML/PDF parsing + normalizer
      models/gov_record.py         # MongoDB models
      routes/gov_routes.py         # REST API endpoints
      utils/helpers.py             # Rate limiter, portal health

/app/frontend/src/
  components/
    GovDataBridge.js           # Live record fetching UI
    KnowledgeGraph.js, PropertyMap.js, TitleChainVisualization.js,
    BackgroundJobs.js, LandRegistries.js, MobileNav.js
  pages/
    AdminPanel.js, ApiDocs.js, PropertyDetail.js (11+ tabs),
    Dashboard.js, Landing.js, Pricing.js, etc.
```

## Completed Features

### Core MVP + P0 Intelligence (COMPLETE)
- [x] Auth, Property CRUD, Document Upload+OCR, AI Risk Analysis, PDF Reports
- [x] Title Chain, AI Legal Copilot, Valuation, Govt Data Agents, Universal Search

### P1 Backend Refactor (COMPLETE)
- [x] 9 modular route modules, shared config, auth utils, Pydantic models

### P2 Strategic Features (COMPLETE)
- [x] Knowledge Graph (D3.js), Map (Leaflet.js), Enterprise API Docs, Admin Panel

### P3 Advanced Features (COMPLETE)
- [x] D3.js Title Chain Viz, Background Jobs, Mobile Responsiveness
- [x] 17 State Land Record Databases, Stripe+Razorpay dual payments

### GovDataBridge Module (COMPLETE - Mar 2026)
- [x] **20 State Scrapers**: Karnataka (Bhoomi), Telangana (Dharani), Tamil Nadu (TNREGINET), Maharashtra (MahaBhumi), AP (Meebhoomi), UP (Bhulekh), Rajasthan (Apna Khata), MP (Bhu-Abhilekh), Gujarat (AnyROR), Haryana (Jamabandi), Punjab (PLRS), WB (Banglarbhumi), Kerala (E-Revenue), Odisha (Bhunaksha), Bihar (Bhu-Lekh), Jharkhand (JharBhoomi), Chhattisgarh (Bhuiyan), HP (HimBhoomi), Uttarakhand (DevBhoomi), Goa
- [x] **Base Scraper**: Abstract class with httpx, retry (tenacity), rate limiting, mock/live dual mode
- [x] **CAPTCHA Solver**: pytesseract OCR + Pillow preprocessing + mock bypass (GOV_MOCK_MODE)
- [x] **Job Processor**: 9-step async processing with progress tracking via MongoDB
- [x] **S3 Storage**: boto3 with pre-signed URLs + local file fallback
- [x] **24hr Caching**: Cache hit returns instant CACHED response
- [x] **REST API**: /gov/fetch, /gov/fetch-bulk, /gov/job/:id, /gov/states, /gov/portals/status, /gov/records/:propertyId, /gov/jobs/history, /gov/download
- [x] **Frontend**: GovDataBridge component with state selector, doc type selector, real-time job progress, structured data display, PDF download, portal directory grid
- [x] **Parsers**: HTML table parser, PDF parser (pdfplumber), data normalizer

## GovDataBridge API Endpoints
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /api/gov/states | No | List 20 states with docs/inputs |
| GET | /api/gov/portals/status | No | Portal health status |
| POST | /api/gov/fetch | JWT | Submit single fetch job |
| POST | /api/gov/fetch-bulk | JWT | Submit up to 10 jobs |
| GET | /api/gov/job/{job_id} | JWT | Poll job status/progress |
| GET | /api/gov/records/{prop_id} | JWT | Property's fetched records |
| GET | /api/gov/jobs/history | JWT | User's job history |
| GET | /api/gov/document/{rec_id} | No | Get record by ID |
| GET | /api/gov/download/{s}/{d}/{j} | No | Download PDF |

## Prioritized Backlog
- [ ] Live scraper implementation (replace mock with real Playwright/httpx)
- [ ] 2captcha integration for production CAPTCHA solving
- [ ] Real S3 bucket configuration
- [ ] AI Fraud Detection Engine
- [ ] Light mode theme
- [ ] Multi-language support

## Test Reports
- iteration_6.json: P1 Backend Refactor (36/36)
- iteration_7.json: P2 Features (100%)
- iteration_8.json: P3 Features (100%)
- iteration_9.json: GovDataBridge Module (Backend 17/17 + Frontend 100%)

## Mocked Services
- 20 state government portal scrapers (GOV_MOCK_MODE=true)
- S3 storage (local fallback)
- CAPTCHA solver (mock bypass)
- Stripe/Razorpay (test keys)
- AI Legal Copilot (Gemini mock fallback)
