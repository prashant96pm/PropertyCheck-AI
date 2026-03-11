# PropertyCheck AI - Product Requirements Document

## Original Problem Statement
Build a production-grade SaaS application called **PropertyCheck AI** — an AI-Powered Property Intelligence & Verification Platform for India. Combines Landeed (land record discovery), Zillow (property intelligence), Palantir (multi-source data integration), and AI Legal Copilot (automated due diligence).

## Tech Stack
- **Frontend**: React + TailwindCSS + ShadCN UI (Glassmorphism dark theme)
- **Backend**: FastAPI (Python) - Modular APIRouter architecture
- **Database**: MongoDB (Atlas-ready)
- **AI/ML**: Gemini via Emergent LLM Key, Tesseract OCR
- **Auth**: JWT + Google OAuth (Emergent-managed)
- **Payments**: Stripe (stubbed)
- **Visualization**: D3.js (Knowledge Graph), Leaflet.js (Maps)

## What's Been Implemented

### Core MVP (COMPLETE)
- [x] User Auth (JWT + Google OAuth), Property CRUD, Document Upload + OCR
- [x] AI Risk Analysis (Gemini-powered, deterministic mock fallback)
- [x] PDF Report Generation, Payment stubs (Stripe)
- [x] Glassmorphism dark theme, Pulsing Risk Meter

### Universal Property Search (COMPLETE)
- [x] Smart Search (Gemini NLP + regex fallback), Advanced Filters
- [x] Property 360 Profile page, Sample Registry (5 demo properties)

### P0 Intelligence Features (COMPLETE - Mar 2026)
- [x] Title Chain Reconstruction, AI Legal Copilot, Property Valuation
- [x] Government Data Retrieval Agents, Enhanced Report Generator
- [x] Enhanced PropertyDetail: 9 intelligence tabs

### P1 - Backend Refactor (COMPLETE - Mar 2026)
- [x] Modular Architecture: 8 route modules
- [x] Shared Config, Auth Utilities, Pydantic Models
- [x] Zero Regressions: 36/36 API tests passed

### P2 - Strategic Features (COMPLETE - Mar 2026)
- [x] **Property Knowledge Graph**: D3.js force-directed interactive graph showing property-owner-document-location-government relationships. Draggable nodes, zoom, click-to-inspect details panel. Color-coded by entity type.
- [x] **Map Integration (Leaflet.js)**: Property location map with CartoDB dark tiles, property marker with popup, boundary circle, infrastructure markers (hospitals, schools, metro). District-based coordinates.
- [x] **Enterprise API Documentation & Key Management**: Full API reference at /developer with 4 endpoint categories, interactive API key generation, copy-to-clipboard cURL examples, authentication docs, rate limit tiers.
- [x] **Admin Panel**: Role-gated admin dashboard at /admin with Overview (system stats), Users (management + role changes), Verifications (risk report monitoring). Accessible from dashboard dropdown for admin users only.

## Architecture

```
/app/backend/
  app.py              # Entry point - imports all routers
  config.py           # Shared config (DB, JWT, API keys)
  models/schemas.py   # Pydantic models
  utils/auth.py       # Auth helpers
  routes/
    auth.py           # Auth, profile, dashboard
    properties.py     # Property CRUD, document upload
    search.py         # Search, full-profile, ownership, legal records
    intelligence.py   # Title chain, legal copilot, valuation, govt sources
    reports.py        # Risk analysis, PDF reports, sharing
    payments.py       # Pricing, Stripe checkout
    admin.py          # Admin panel (role-gated)
    enterprise.py     # Enterprise API (API key auth)

/app/frontend/src/
  components/
    KnowledgeGraph.js  # D3.js force-directed graph
    PropertyMap.js     # Leaflet.js map component
    RiskMeter.js, ShimmerLoader.js, FloatingActionButton.js
  pages/
    AdminPanel.js      # Admin dashboard (overview/users/verifications)
    ApiDocs.js         # Enterprise API docs & key management
    PropertyDetail.js  # 9-tab intelligence view (+ graph + map)
    Dashboard.js, Landing.js, SearchPage.js, etc.
```

## Routes
| Route | Page | Auth |
|-------|------|------|
| / | Landing | No |
| /login, /register | Auth | No |
| /search | Universal Search | No |
| /property-profile/:id | Property 360 | No |
| /pricing | Pricing | No |
| /developer | Enterprise API Docs | No |
| /shared-report/:token | Shared Report | No |
| /dashboard | Dashboard | Yes |
| /upload | Upload Property | Yes |
| /property/:id | Property Intelligence (9 tabs) | Yes |
| /profile, /settings | User Settings | Yes |
| /admin | Admin Panel | Yes (Admin role) |

## Prioritized Backlog

### P3 - Future
- [ ] D3.js Title Chain Visualization enhancements
- [ ] Background Jobs (async processing simulation)
- [ ] Mobile Responsiveness
- [ ] Live Government API Integration
- [ ] Payment activation (Razorpay/Stripe)
- [ ] AI Fraud Detection Engine
- [ ] Light mode theme

## Test Reports
- iteration_1-2.json: MVP
- iteration_3.json: Navigation & Search (100%)
- iteration_4.json: UI/UX Fixes (94-95%)
- iteration_5.json: Property Intelligence P0 (100%)
- iteration_6.json: Backend Refactor P1 (100% - 36/36)
- iteration_7.json: P2 Features (Backend 91% + Frontend 100%)
