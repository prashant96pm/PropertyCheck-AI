import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Building2, ArrowLeft } from 'lucide-react';

const TermsOfService = () => {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen gradient-bg">
      <div className="fixed inset-0 grid-bg opacity-30 pointer-events-none" />
      <nav className="glass-header sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center h-16 gap-4">
            <button onClick={() => navigate(-1)} className="text-slate-400 hover:text-white transition-colors" data-testid="terms-back-btn">
              <ArrowLeft className="h-5 w-5" />
            </button>
            <Link to="/" className="flex items-center gap-2">
              <Building2 className="h-8 w-8 text-cyan-400" />
              <span className="text-xl font-semibold text-white" style={{ fontFamily: 'Playfair Display' }}>PropertyCheck AI</span>
            </Link>
          </div>
        </div>
      </nav>
      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12 relative z-10">
        <h1 className="text-3xl font-bold text-white mb-8" style={{ fontFamily: 'Playfair Display' }}>Terms of <span className="text-gradient">Service</span></h1>
        <div className="glass-card prose prose-invert max-w-none space-y-6">
          <section>
            <h2 className="text-lg font-semibold text-white">1. Acceptance of Terms</h2>
            <p className="text-sm text-slate-400 leading-relaxed">By accessing or using PropertyCheck AI, you agree to be bound by these Terms of Service. If you do not agree, please do not use the platform.</p>
          </section>
          <section>
            <h2 className="text-lg font-semibold text-white">2. Service Description</h2>
            <p className="text-sm text-slate-400 leading-relaxed">PropertyCheck AI provides AI-powered property document verification, risk assessment, title chain reconstruction, and government record lookup services for Indian real estate. Our reports are for informational purposes and do not constitute legal advice.</p>
          </section>
          <section>
            <h2 className="text-lg font-semibold text-white">3. User Accounts</h2>
            <p className="text-sm text-slate-400 leading-relaxed">You must provide accurate information during registration. You are responsible for maintaining the confidentiality of your account credentials. Notify us immediately of any unauthorized access to your account.</p>
          </section>
          <section>
            <h2 className="text-lg font-semibold text-white">4. Document Upload & Processing</h2>
            <p className="text-sm text-slate-400 leading-relaxed">You retain ownership of all documents uploaded. By uploading, you grant us a limited license to process documents for verification purposes. We do not share your documents with other users or third parties beyond what is necessary for verification.</p>
          </section>
          <section>
            <h2 className="text-lg font-semibold text-white">5. Payments & Refunds</h2>
            <p className="text-sm text-slate-400 leading-relaxed">All payments are processed securely through Stripe. Verification reports are non-refundable once generated. If you experience technical issues preventing report generation, contact support for assistance.</p>
          </section>
          <section>
            <h2 className="text-lg font-semibold text-white">6. Limitation of Liability</h2>
            <p className="text-sm text-slate-400 leading-relaxed">PropertyCheck AI provides AI-assisted analysis and should not be used as the sole basis for property transactions. We recommend consulting with legal professionals for final verification. Our liability is limited to the amount paid for the specific service.</p>
          </section>
          <section>
            <h2 className="text-lg font-semibold text-white">7. Governing Law</h2>
            <p className="text-sm text-slate-400 leading-relaxed">These terms shall be governed by the laws of India. Any disputes shall be subject to the exclusive jurisdiction of courts in Bengaluru, Karnataka.</p>
          </section>
          <p className="text-xs text-slate-500 pt-4 border-t border-slate-700/50">Last updated: February 2026</p>
        </div>
      </main>
    </div>
  );
};

export default TermsOfService;
