# PropertyCheck AI - Product Requirements Document

## Original Problem Statement
Build a production-grade SaaS application called **PropertyCheck AI** — an AI-Powered Property Intelligence & Verification Platform for India. Combines Landeed (land record discovery), Zillow (property intelligence), Palantir (multi-source data integration), and AI Legal Copilot (automated due diligence).

## Tech Stack
- **Frontend**: React + TailwindCSS + ShadCN UI (Glassmorphism dark theme)
- **Backend**: FastAPI (Python)
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

## Prioritized Backlog

### P1 - Stability
- [ ] Backend refactor into modular APIRouters
- [ ] MongoDB schema cleanup
- [ ] Light mode theme

### P2 - Strategic
- [ ] Live government API integration
- [ ] Map integration (Mapbox/Google Maps)
- [ ] AI Fraud Detection Engine
- [ ] Payment activation (Razorpay/Stripe)
- [ ] Property Knowledge Graph (Neo4j-style)
- [ ] Enterprise API Layer
- [ ] Admin Panel

### P3 - Future
- [ ] D3.js title chain visualization
- [ ] Celery + Redis background jobs
- [ ] Mobile app (Flutter)
- [ ] Elasticsearch, PostgreSQL + PostGIS

## Test Reports
- iteration_1-2.json: MVP
- iteration_3.json: Navigation & Search (100%)
- iteration_4.json: UI/UX Fixes (94-95%)
- iteration_5.json: Property Intelligence P0 (100% backend + frontend)
