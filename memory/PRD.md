# PropertyCheck AI - Product Requirements Document

## Original Problem Statement
Build a production-grade SaaS application called **PropertyCheck AI** — an AI-Powered Property Intelligence & Verification Platform for India. Combines Landeed (land record discovery), Zillow (property intelligence), Palantir (multi-source data integration), and AI Legal Copilot (automated due diligence).

## Tech Stack
- **Frontend**: React + TailwindCSS + ShadCN UI (Glassmorphism dark theme)
- **Backend**: FastAPI (Python) - Modular APIRouter architecture (9 route modules)
- **Database**: MongoDB (Atlas-ready)
- **AI/ML**: Gemini via Emergent LLM Key, Tesseract OCR
- **Auth**: JWT + Google OAuth (Emergent-managed)
- **Payments**: Stripe + Razorpay (dual gateway)
- **Visualization**: D3.js (Knowledge Graph + Title Chain), Leaflet.js (Maps)

## Completed Features

### Core MVP
- [x] User Auth (JWT + Google OAuth), Property CRUD, Document Upload + OCR
- [x] AI Risk Analysis (Gemini-powered, deterministic mock fallback)
- [x] PDF Report Generation
- [x] Glassmorphism dark theme, Pulsing Risk Meter

### Universal Property Search
- [x] Smart Search (Gemini NLP + regex fallback), Advanced Filters
- [x] Property 360 Profile page, Sample Registry

### P0 Intelligence Features
- [x] Title Chain Reconstruction, AI Legal Copilot, Property Valuation
- [x] Government Data Retrieval Agents, Enhanced Report Generator
- [x] Enhanced PropertyDetail: 11 intelligence tabs

### P1 - Backend Refactor
- [x] Modular Architecture: 9 route modules (auth, properties, search, intelligence, reports, payments, admin, enterprise, jobs)

### P2 - Strategic Features
- [x] Property Knowledge Graph (D3.js force-directed graph)
- [x] Map Integration (Leaflet.js with CartoDB dark tiles)
- [x] Enterprise API Documentation & Key Management at /developer
- [x] Admin Panel at /admin (role-gated)

### P3 - Advanced Features (Mar 2026)
- [x] **D3.js Title Chain Visualization**: Animated horizontal ownership flow with gap/anomaly highlighting, clickable nodes, transfer type labels, verification status icons
- [x] **Background Jobs**: 5 job types (risk_analysis, document_ocr, govt_data_retrieval, title_verification, valuation_report) with real-time progress polling, step tracking, async simulation
- [x] **Mobile Responsiveness**: Hamburger menu, touch-friendly tabs, responsive grids, mobile-optimized map/graph, tablet breakpoints
- [x] **State Land Record Databases**: 17 Indian state registries (Bhoomi, Bhulekh, Dharani, Meebhoomi, etc.) with portal URLs, digitization %, record types, coverage info
- [x] **Payment Activation (Stripe + Razorpay)**: Dual payment gateway with method selector, Stripe checkout flow, Razorpay inline checkout with signature verification, payment status tracking

## Architecture
```
/app/backend/
  app.py              # Entry point
  config.py           # Shared config
  models/schemas.py   # Pydantic models
  utils/auth.py       # Auth helpers
  routes/
    auth.py, properties.py, search.py, intelligence.py,
    reports.py, payments.py, admin.py, enterprise.py, jobs.py

/app/frontend/src/
  components/
    KnowledgeGraph.js, PropertyMap.js, TitleChainVisualization.js,
    BackgroundJobs.js, LandRegistries.js, MobileNav.js, RiskMeter.js
  pages/
    AdminPanel.js, ApiDocs.js, PropertyDetail.js (11 tabs),
    Dashboard.js, Landing.js, Pricing.js, PaymentSuccess.js, etc.
```

## Routes
| Route | Page | Auth |
|-------|------|------|
| / | Landing | No |
| /search | Universal Search | No |
| /pricing | Pricing (Stripe+Razorpay) | No |
| /developer | Enterprise API Docs | No |
| /dashboard | Dashboard | Yes |
| /property/:id | Property Intelligence (11 tabs) | Yes |
| /admin | Admin Panel | Yes (Admin) |

## Prioritized Backlog
- [ ] AI Fraud Detection Engine
- [ ] Light mode theme
- [ ] Real Government API Integration (replace mocks with live data)
- [ ] Email notifications for job completion
- [ ] Multi-language support (Hindi, Kannada)

## Test Reports
- iteration_6.json: P1 Backend Refactor (36/36 passed)
- iteration_7.json: P2 Features (Backend 91% + Frontend 100%)
- iteration_8.json: P3 Features (Backend 100% 12/12 + Frontend 100%)
