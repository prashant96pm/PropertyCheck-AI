import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Building2, ArrowLeft } from 'lucide-react';

const PrivacyPolicy = () => {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen gradient-bg">
      <div className="fixed inset-0 grid-bg opacity-30 pointer-events-none" />
      <nav className="glass-header sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center h-16 gap-4">
            <button onClick={() => navigate(-1)} className="text-slate-400 hover:text-white transition-colors" data-testid="privacy-back-btn">
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
        <h1 className="text-3xl font-bold text-white mb-8" style={{ fontFamily: 'Playfair Display' }}>Privacy <span className="text-gradient">Policy</span></h1>
        <div className="glass-card prose prose-invert max-w-none space-y-6">
          <section>
            <h2 className="text-lg font-semibold text-white">1. Information We Collect</h2>
            <p className="text-sm text-slate-400 leading-relaxed">We collect personal information you provide when registering (name, email), property documents you upload for verification, and usage data to improve our services. We do not collect sensitive personal data beyond what is necessary for property verification.</p>
          </section>
          <section>
            <h2 className="text-lg font-semibold text-white">2. How We Use Your Information</h2>
            <p className="text-sm text-slate-400 leading-relaxed">Your information is used to: perform AI-powered document analysis and OCR, generate risk assessment reports, match property records with government databases, and provide search results. We do not sell your personal data to third parties.</p>
          </section>
          <section>
            <h2 className="text-lg font-semibold text-white">3. Data Security</h2>
            <p className="text-sm text-slate-400 leading-relaxed">All data is encrypted with 256-bit AES encryption in transit and at rest. Documents are processed in secure, isolated environments. Access is restricted on a need-to-know basis with multi-factor authentication for all internal systems.</p>
          </section>
          <section>
            <h2 className="text-lg font-semibold text-white">4. Data Retention</h2>
            <p className="text-sm text-slate-400 leading-relaxed">Uploaded documents are retained for 90 days post-verification unless you request earlier deletion. Risk reports are stored indefinitely in your account. You may request complete data deletion at any time by contacting support.</p>
          </section>
          <section>
            <h2 className="text-lg font-semibold text-white">5. Third-Party Services</h2>
            <p className="text-sm text-slate-400 leading-relaxed">We integrate with government land record portals (Bhoomi, Bhulekh, Dharani, etc.) and payment processors (Stripe). These services have their own privacy policies. We only share minimum necessary data with these providers.</p>
          </section>
          <section>
            <h2 className="text-lg font-semibold text-white">6. Your Rights</h2>
            <p className="text-sm text-slate-400 leading-relaxed">Under applicable data protection laws, you have the right to access, correct, delete, or port your personal data. To exercise these rights, contact us at privacy@propertycheck.ai.</p>
          </section>
          <p className="text-xs text-slate-500 pt-4 border-t border-slate-700/50">Last updated: February 2026</p>
        </div>
      </main>
    </div>
  );
};

export default PrivacyPolicy;
