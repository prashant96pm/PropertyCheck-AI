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
- [x] **Title Chain Reconstruction**: 5-transfer ownership chain, gap analysis, anomaly detection, 42yr span, completeness score
- [x] **AI Legal Copilot**: Gemini-powered lawyer-style due diligence reports (10-section structured analysis)
- [x] **Property Valuation & Market Intelligence**: Estimated value, guideline value, price trends, neighborhood scores, infrastructure distances, nearby transactions
- [x] **Government Data Retrieval Agents**: 7 multi-source agents (state portals, CERSAI, eCourts, municipal, survey dept) with status tracking
- [x] **Enhanced Report Generator**: Shareable report links with public access
- [x] **Enhanced PropertyDetail**: 7 intelligence tabs (Overview, Title Chain, Risk, Legal Copilot, Valuation, Documents, Govt Sources)

### Navigation & UI (COMPLETE)
- [x] All routes working, Building2 icon, Footer legal links
- [x] Profile page, Settings page, Privacy/Terms/DPDP pages
- [x] Bengaluru (not Bangalore), risk labels (No Risk/High Risk)
- [x] Shared report page for public access

### P1 - Backend Refactor (COMPLETE - Mar 2026)
- [x] **Modular Architecture**: Broke down 2000-line monolithic server.py into 8 route modules
- [x] **Route Modules**: auth.py, properties.py, search.py, intelligence.py, reports.py, payments.py, admin.py, enterprise.py
- [x] **Shared Config**: config.py (DB, JWT, API keys, directories)
- [x] **Auth Utilities**: utils/auth.py (hash_password, verify_password, create_jwt_token, get_current_user)
- [x] **Pydantic Models**: models/schemas.py (UserCreate, UserLogin, TokenResponse, PropertyCreate, etc.)
- [x] **Thin Entry Point**: app.py imports and mounts all routers with /api prefix
- [x] **Zero Regressions**: All 36 API endpoints tested and passing (iteration_6.json)

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
```

## Routes
| Route | Page | Auth |
|-------|------|------|
| / | Landing | No |
| /login, /register | Auth | No |
| /search | Universal Search | No |
| /property-profile/:id | Property 360 | No |
| /pricing | Pricing | No |
| /privacy-policy, /terms-of-service, /dpdp-compliance | Legal | No |
| /shared-report/:token | Shared Report | No |
| /dashboard | Dashboard | Yes |
| /upload | Upload Property | Yes |
| /property/:id, /report/:id | Property Intelligence | Yes |
| /profile, /settings | User Settings | Yes |

## Key API Endpoints
- Auth: register, login, session, me, logout, google
- Properties: CRUD + documents upload
- Intelligence: title-chain, valuation, government-sources, legal-copilot
- Analysis: risk analysis, reports, PDF download
- Search: multi-param search, AI smart search, full-profile
- Social: shared reports (create + public access)
- Profile: get + update
- Admin: stats, users, role management, verifications
- Enterprise: API key management, verify, title-history, risk-score

## Prioritized Backlog

### P2 - Strategic (Next)
- [ ] Property Knowledge Graph (D3.js/React visualization)
- [ ] Map integration (Leaflet.js - user's choice)
- [ ] Enterprise API Layer (documented REST APIs with API key auth)
- [ ] Admin Panel (accessible from dashboard for admin-role users)

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
- iteration_5.json: Property Intelligence P0 (100% backend + frontend)
- iteration_6.json: Backend Refactor P1 (100% - 36/36 tests passed)
