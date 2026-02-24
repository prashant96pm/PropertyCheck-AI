import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Building2, ArrowLeft, CheckCircle2 } from 'lucide-react';

const DPDPCompliance = () => {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen gradient-bg">
      <div className="fixed inset-0 grid-bg opacity-30 pointer-events-none" />
      <nav className="glass-header sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center h-16 gap-4">
            <button onClick={() => navigate(-1)} className="text-slate-400 hover:text-white transition-colors" data-testid="dpdp-back-btn">
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
        <h1 className="text-3xl font-bold text-white mb-8" style={{ fontFamily: 'Playfair Display' }}>DPDP <span className="text-gradient">Compliance</span></h1>
        <div className="glass-card prose prose-invert max-w-none space-y-6">
          <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-lg">
            <p className="text-sm text-emerald-400 flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4" />
              PropertyCheck AI is fully compliant with the Digital Personal Data Protection Act, 2023 (DPDP Act).
            </p>
          </div>
          <section>
            <h2 className="text-lg font-semibold text-white">About DPDP Act</h2>
            <p className="text-sm text-slate-400 leading-relaxed">The Digital Personal Data Protection Act, 2023 is India's comprehensive data protection legislation that governs the processing of digital personal data. PropertyCheck AI adheres to all provisions of this act.</p>
          </section>
          <section>
            <h2 className="text-lg font-semibold text-white">Our Compliance Measures</h2>
            <ul className="space-y-3">
              {[
                "Lawful Purpose: We process personal data only for the legitimate purpose of property verification.",
                "Consent: We obtain explicit consent before processing personal data and documents.",
                "Data Minimization: We collect only the minimum data necessary for verification.",
                "Storage Limitation: Documents are retained only for the required verification period.",
                "Data Principal Rights: Users can access, correct, erase, and port their data.",
                "Data Fiduciary Obligations: We maintain transparency in data processing activities.",
                "Grievance Redressal: We have a designated Data Protection Officer for handling data concerns.",
                "Cross-Border Transfers: Personal data is stored within India unless explicit consent is obtained."
              ].map((item, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-slate-400">
                  <CheckCircle2 className="h-4 w-4 text-cyan-400 flex-shrink-0 mt-0.5" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </section>
          <section>
            <h2 className="text-lg font-semibold text-white">Contact Data Protection Officer</h2>
            <p className="text-sm text-slate-400 leading-relaxed">For any data protection queries or to exercise your rights under the DPDP Act, contact our Data Protection Officer at dpo@propertycheck.ai.</p>
          </section>
          <p className="text-xs text-slate-500 pt-4 border-t border-slate-700/50">Last updated: February 2026</p>
        </div>
      </main>
    </div>
  );
};

export default DPDPCompliance;
