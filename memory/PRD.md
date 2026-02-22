# PropertyCheck AI - Product Requirements Document

## Original Problem Statement
Build a production-grade SaaS web application called **PropertyCheck AI** - an AI-Powered Land & Real Estate Verification Platform for India. The platform helps property buyers, developers, and legal professionals verify land ownership, detect fraud, reconstruct title chains, and generate lawyer-ready risk reports.

## Tech Stack
- **Frontend**: React + TailwindCSS + ShadCN UI (Glassmorphism dark theme)
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **AI/ML**: Gemini via Emergent LLM Key, Tesseract OCR
- **Auth**: JWT + Google OAuth (Emergent-managed)
- **Payments**: Stripe (stubbed)

## What's Been Implemented

### P0 - Core MVP (COMPLETE)
- [x] User Authentication (JWT + Google OAuth via Emergent)
- [x] Property CRUD (create, list, detail)
- [x] Document Upload with OCR (Tesseract, supports Indian languages)
- [x] AI Risk Analysis (Gemini-powered, with mock fallback)
- [x] PDF Report Generation (lawyer-ready format)
- [x] Payment Integration (Stripe stubs)
- [x] Glassmorphism Dark Theme UI
- [x] Pulsing Risk Meter component

### P0 - Universal Property Search (COMPLETE - Feb 2026)
- [x] Universal Property Search page (`/search`)
- [x] AI Smart Search (natural language queries via Gemini)
- [x] Advanced Filters (owner name, survey no, plot no, khata no, state, district, village, taluk, land type)
- [x] Sample Property Registry (auto-seeded 5 demo properties)
- [x] Fuzzy name matching (rapidfuzz)
- [x] Property 360 Profile page (`/property-profile/:id`)
  - [x] Overview tab with property details & boundaries
  - [x] 30+ Year Ownership History with timeline
  - [x] Legal Records (CERSAI, eCourts, encumbrances)
  - [x] Documents (uploaded + government registry)
  - [x] Geo-Spatial data (coordinates, nearby infrastructure)
  - [x] Government Records (state-specific sources)

### P0 - Navigation (COMPLETE - Feb 2026)
- [x] All routes configured in App.js: /, /login, /register, /dashboard, /upload, /search, /property/:id, /property-profile/:id, /report/:id, /pricing, /payment/success
- [x] Landing page: "Search Properties" in nav + hero CTA
- [x] Dashboard: Search bar, Search nav button, Search quick action
- [x] Dashboard search bar → /search?q= (auto-triggers AI search)
- [x] Search results → Property 360 Profile navigation
- [x] Property Profile → Back to search
- [x] Upload flow → Property Detail
- [x] Logout flow working

## Routes
| Route | Page | Auth Required |
|-------|------|---------------|
| / | Landing | No |
| /login | Login | No |
| /register | Register | No |
| /search | Universal Search | No |
| /property-profile/:id | Property 360 Profile | No |
| /pricing | Pricing | No |
| /dashboard | Dashboard | Yes |
| /upload | Upload Property | Yes |
| /property/:id | Property Detail | Yes |
| /report/:id | Property Detail (alias) | Yes |
| /payment/success | Payment Success | Yes |

## Key API Endpoints
- `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/session`
- `GET /api/auth/me`, `POST /api/auth/logout`
- `POST /api/properties`, `GET /api/properties`, `GET /api/properties/:id`
- `POST /api/documents/upload`, `GET /api/documents/:property_id`
- `POST /api/analyze/:property_id`
- `GET /api/reports/:property_id`, `GET /api/reports/:property_id/download`
- `GET /api/property/search` (multi-parameter)
- `POST /api/property/ai-smart-search` (NLP)
- `GET /api/property/full-profile/:id` (360 profile)
- `GET /api/government-records/:survey_no` (mock)
- `GET /api/dashboard/stats`
- `GET /api/pricing`
- `POST /api/payments/create-checkout`

## Mocked Components
- Government Records APIs (Bhoomi, Bhulekh, Dharani etc.)
- AI Risk Analysis (falls back to mock when LLM unavailable)
- AI Smart Search (falls back to regex parser)
- Ownership History (mock 3-entry chain)
- Payment processing (Stripe stubs)

## Prioritized Backlog

### P1 - Stability & Scalability
- [ ] Backend refactor: Break server.py into modular APIRouters (auth, property, search, documents, risk)
- [ ] MongoDB schema cleanup (Property, Owner, Documents, RiskReport collections)
- [ ] Error handling + loading states (production feel)
- [ ] Input validation improvements

### P2 - Strategic Features
- [ ] Government land records API integration (Bhoomi, Bhulekh, Dharani)
- [ ] Map integration (Google Maps / Mapbox) for Geo-Spatial validation
- [ ] AI Fraud Detection Engine
- [ ] Payment integration activation (Razorpay/Stripe for property reports)
- [ ] Admin Panel for verification monitoring

### P3 - Future
- [ ] Title Chain Reconstruction with D3.js visualization
- [ ] Celery + Redis for background jobs
- [ ] Mobile app (Flutter)
- [ ] Elasticsearch for full-text property search
- [ ] PostgreSQL + PostGIS migration
- [ ] Vector DB for document embeddings

## Test Reports
- /app/test_reports/iteration_1.json (MVP)
- /app/test_reports/iteration_2.json (MVP round 2)
- /app/test_reports/iteration_3.json (P0 Navigation & Search - 100% pass)
