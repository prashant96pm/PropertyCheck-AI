# PropertyCheck AI - Product Requirements Document

## Overview
AI-Powered Land & Real Estate Verification Platform for India

## Original Problem Statement
Build a production-grade SaaS web application called PropertyCheck AI that verifies land/real estate ownership, detects fraud, reconstructs 30-year title chains, and generates lawyer-ready risk reports using AI, OCR, and government land record integrations in India.

## Architecture
- **Frontend**: React 19 with TailwindCSS, Shadcn UI components
- **Backend**: FastAPI (Python) with async architecture
- **Database**: MongoDB (document storage, user data, reports)
- **AI/ML**: Google Gemini 3 Flash via Emergent LLM Key
- **OCR**: Tesseract (with mock Google Document AI)
- **Payments**: Stripe (integrated, Razorpay ready)
- **Auth**: JWT + Emergent Google OAuth

## User Personas
1. **Property Buyers** - Individual buyers verifying land before purchase
2. **Real Estate Developers** - Bulk property verification for projects
3. **Banks & NBFCs** - Mortgage verification and fraud detection
4. **Legal Firms** - Due diligence for property transactions
5. **Government & Land Consultants** - Land record validation

## Core Requirements (Static)
- Document upload (PDF, images) with OCR extraction
- AI-powered risk scoring (0-100 scale)
- 30-year title chain reconstruction
- Fraud detection (red/yellow/green flags)
- Lawyer-ready PDF reports
- Multi-language support (Indian languages)
- Secure document storage
- DPDP Act compliance

## What's Been Implemented (Jan 22, 2026)

### MVP Complete ✅
- [x] **Glassmorphism Dark Theme** - Deep navy to charcoal gradient background
- [x] **Pulsing Risk Meter** - Circular gauge with neon glow effects (green/orange/red)
- [x] **Glowing Border Cards** - Green (verified), Orange (caution), Red (high risk)
- [x] **Shimmer Loading Animations** - Skeleton loaders for smooth UX
- [x] **Floating Action Button** - Quick "Scan Document" access
- [x] Landing page with hero, features, pricing sections
- [x] User authentication (email/password + Google OAuth)
- [x] Protected dashboard with property management
- [x] Multi-step property creation (survey no, state, district, etc.)
- [x] Document upload with drag-and-drop
- [x] Tesseract OCR text extraction
- [x] Gemini AI document field extraction
- [x] AI Risk Analysis with score, flags, recommendations
- [x] Title chain visualization with timeline
- [x] PDF report generation and download
- [x] Government records integration (MOCKED)
- [x] Pricing page with packages (₹499, ₹999, ₹1999)
- [x] Stripe payment integration

### UI/UX Features
- Dark glassmorphism theme with blur effects
- Animated grid background
- Neon text gradients and glowing effects
- Interactive hover states with glow intensification
- Responsive design for all screen sizes

## Prioritized Backlog

### P0 - Critical (Next Sprint)
- [ ] Live government API integration (Bhoomi, Bhulekh, Dharani)
- [ ] Razorpay payment gateway activation
- [ ] Document fraud detection AI model
- [ ] User subscription management

### P1 - High Priority
- [ ] Batch property upload for enterprise users
- [ ] API access for B2B clients
- [ ] Enhanced multilingual OCR (Kannada, Hindi, Tamil, Telugu)
- [ ] Admin dashboard for monitoring
- [ ] Email notifications for report completion

### P2 - Medium Priority
- [ ] Satellite imagery integration (Google Earth Engine)
- [ ] Map-based property visualization (Mapbox)
- [ ] Mobile app (Flutter)
- [ ] Encroachment detection AI
- [ ] CERSAI live integration

### P3 - Nice to Have
- [ ] Document comparison tool
- [ ] Historical price trend analysis
- [ ] Legal expert marketplace
- [ ] White-label solution for partners

## Environment Variables
- EMERGENT_LLM_KEY: Gemini AI integration
- STRIPE_API_KEY: Payment processing
- DATA_GOV_API_KEY: Government data access (579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b)
- JWT_SECRET_KEY: Session management

## Next Tasks List
1. Integrate live Bhoomi API for Karnataka RTC records
2. Add Razorpay payment option with INR pricing
3. Implement document tampering detection
4. Add user email verification
5. Build admin monitoring dashboard
