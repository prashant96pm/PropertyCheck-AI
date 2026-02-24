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
- [x] AI Smart Search (natural language queries via Gemini, fallback to sample data)
- [x] Advanced Filters (owner name, survey no, plot no, khata no, state, district, village, taluk, land type)
- [x] Sample Property Registry (auto-seeded 5 demo properties, "Review Only" badge)
- [x] Fuzzy name matching (rapidfuzz)
- [x] Property 360 Profile page (`/property-profile/:id`)

### P0 - Navigation & UI Fixes (COMPLETE - Feb 2026)
- [x] All routes configured and working
- [x] Building2 icon replaced Shield icon across all pages
- [x] Footer links: Product, Account, Legal sections all navigable
- [x] Privacy Policy, Terms of Service, DPDP Compliance pages created
- [x] Profile page with editable first/last name, gender, date joined
- [x] Settings page with dark/light/system mode options
- [x] "Bangalore" → "Bengaluru" corrected globally (frontend + backend + DB)
- [x] Smart Search fallback: shows sample data instead of error
- [x] Risk score labels: "No Risk" (green, >=80), "High Risk" (red, <80)
- [x] Government Records: downloadable documents placeholder section
- [x] Toned down blinking/pulsing animations
- [x] User avatar icon visibility improved
- [x] Copyright year updated to 2026
- [x] Deterministic risk scores (re-analysis gives same result)

## Routes
| Route | Page | Auth Required |
|-------|------|---------------|
| / | Landing | No |
| /login | Login | No |
| /register | Register | No |
| /search | Universal Search | No |
| /property-profile/:id | Property 360 Profile | No |
| /pricing | Pricing | No |
| /privacy-policy | Privacy Policy | No |
| /terms-of-service | Terms of Service | No |
| /dpdp-compliance | DPDP Compliance | No |
| /dashboard | Dashboard | Yes |
| /upload | Upload Property | Yes |
| /property/:id | Property Detail | Yes |
| /report/:id | Property Detail (alias) | Yes |
| /profile | User Profile | Yes |
| /settings | Settings | Yes |
| /payment/success | Payment Success | Yes |

## Key API Endpoints
- Auth: POST /api/auth/register, /api/auth/login, /api/auth/session, GET /api/auth/me, POST /api/auth/logout
- Properties: POST /api/properties, GET /api/properties, GET /api/properties/:id
- Documents: POST /api/documents/upload, GET /api/documents/:property_id
- Analysis: POST /api/analyze/:property_id
- Reports: GET /api/reports/:property_id, GET /api/reports/:property_id/download
- Search: GET /api/property/search, POST /api/property/ai-smart-search
- Profile: GET /api/property/full-profile/:id, GET /api/profile, PUT /api/profile
- Govt: GET /api/government-records/:survey_no
- Dashboard: GET /api/dashboard/stats
- Pricing: GET /api/pricing
- Payments: POST /api/payments/create-checkout

## Mocked Components
- Government Records APIs (Bhoomi, Bhulekh, Dharani etc.)
- AI Risk Analysis (falls back to mock when LLM unavailable)
- AI Smart Search (falls back to regex parser + sample data)
- Payment processing (Stripe stubs)

## Prioritized Backlog

### P1 - Stability & Scalability
- [ ] Backend refactor: Break server.py into modular APIRouters
- [ ] MongoDB schema cleanup
- [ ] Error handling + loading states improvements
- [ ] Light mode theme implementation

### P2 - Strategic Features
- [ ] Government land records API integration (Bhoomi, Bhulekh, Dharani)
- [ ] Map integration (Google Maps / Mapbox) for Geo-Spatial validation
- [ ] AI Fraud Detection Engine
- [ ] Payment integration activation (Razorpay/Stripe)
- [ ] Admin Panel for verification monitoring

### P3 - Future
- [ ] Title Chain Reconstruction with D3.js
- [ ] Celery + Redis for background jobs
- [ ] Mobile app (Flutter)
- [ ] Elasticsearch for full-text property search
- [ ] PostgreSQL + PostGIS migration

## Test Reports
- /app/test_reports/iteration_1.json (MVP)
- /app/test_reports/iteration_2.json (MVP round 2)
- /app/test_reports/iteration_3.json (P0 Navigation & Search - 100% pass)
- /app/test_reports/iteration_4.json (UI/UX Fixes Batch - 94-95% pass)
