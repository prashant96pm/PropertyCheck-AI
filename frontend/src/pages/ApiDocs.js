import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import {
  Building2, ArrowLeft, Key, Copy, Code, Globe, Lock,
  CheckCircle2, ChevronRight, Loader2, AlertTriangle, Zap
} from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const API_ENDPOINTS = [
  {
    category: 'Property Verification',
    endpoints: [
      { method: 'GET', path: '/api/enterprise/v1/verify/{property_id}', desc: 'Quick property verification with risk score', auth: 'API Key' },
      { method: 'GET', path: '/api/enterprise/v1/title-history/{property_id}', desc: 'Complete title chain with gap analysis', auth: 'API Key' },
      { method: 'GET', path: '/api/enterprise/v1/risk-score/{property_id}', desc: 'Risk score retrieval', auth: 'API Key' },
    ]
  },
  {
    category: 'Property Search',
    endpoints: [
      { method: 'GET', path: '/api/property/search', desc: 'Multi-parameter property search', auth: 'None', params: 'owner_name, survey_no, district, state, village, taluk' },
      { method: 'POST', path: '/api/property/ai-smart-search', desc: 'AI-powered natural language search', auth: 'None', body: '{ "query": "Land owned by Ramesh in Bengaluru" }' },
      { method: 'GET', path: '/api/property/full-profile/{property_id}', desc: '360-degree property profile', auth: 'None' },
    ]
  },
  {
    category: 'Intelligence',
    endpoints: [
      { method: 'GET', path: '/api/property/{id}/title-chain', desc: 'Title chain reconstruction with gap analysis', auth: 'None' },
      { method: 'GET', path: '/api/property/{id}/valuation', desc: 'Property valuation and market intelligence', auth: 'None' },
      { method: 'GET', path: '/api/property/{id}/government-sources', desc: 'Government data retrieval status', auth: 'None' },
      { method: 'POST', path: '/api/property/{id}/legal-copilot', desc: 'AI legal due diligence report', auth: 'Bearer Token' },
    ]
  },
  {
    category: 'Risk Analysis',
    endpoints: [
      { method: 'POST', path: '/api/analyze/{property_id}', desc: 'Run AI risk analysis', auth: 'Bearer Token' },
      { method: 'GET', path: '/api/reports/{property_id}', desc: 'Get risk report', auth: 'Bearer Token' },
      { method: 'GET', path: '/api/reports/{property_id}/download', desc: 'Download PDF report', auth: 'Bearer Token' },
      { method: 'POST', path: '/api/reports/{property_id}/share', desc: 'Generate shareable report link', auth: 'Bearer Token' },
    ]
  },
];

const ApiDocs = () => {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [apiKey, setApiKey] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [orgName, setOrgName] = useState('');
  const [contactEmail, setContactEmail] = useState('');
  const [expandedEndpoint, setExpandedEndpoint] = useState(null);

  const generateApiKey = async () => {
    if (!orgName.trim()) { toast.error('Organization name required'); return; }
    setGenerating(true);
    try {
      const res = await axios.post(`${API}/enterprise/v1/api-keys?org_name=${encodeURIComponent(orgName)}&contact_email=${encodeURIComponent(contactEmail || user?.email || '')}`, {});
      setApiKey(res.data);
      toast.success('API key generated');
    } catch (err) {
      toast.error('Failed to generate API key');
    } finally {
      setGenerating(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };

  const methodColor = {
    GET: 'bg-emerald-500/20 text-emerald-400',
    POST: 'bg-cyan-500/20 text-cyan-400',
    PUT: 'bg-amber-500/20 text-amber-400',
    DELETE: 'bg-red-500/20 text-red-400',
  };

  return (
    <div className="min-h-screen gradient-bg" data-testid="api-docs-page">
      <div className="fixed inset-0 grid-bg opacity-30 pointer-events-none" />

      <nav className="glass-header sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-4">
              <button onClick={() => navigate(-1)} className="text-slate-400 hover:text-white" data-testid="api-docs-back-btn">
                <ArrowLeft className="h-5 w-5" />
              </button>
              <Link to="/" className="flex items-center gap-2">
                <Building2 className="h-8 w-8 text-cyan-400" />
                <span className="text-xl font-semibold text-white" style={{ fontFamily: 'Playfair Display' }}>API Documentation</span>
              </Link>
            </div>
            <Badge className="bg-cyan-500/20 text-cyan-400 border-cyan-500/30">
              <Code className="h-3 w-3 mr-1" /> Enterprise API v1
            </Badge>
          </div>
        </div>
      </nav>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        {/* Hero */}
        <div className="glass-card mb-8">
          <div className="flex items-start gap-4">
            <div className="h-12 w-12 rounded-lg bg-cyan-500/20 flex items-center justify-center flex-shrink-0">
              <Zap className="h-6 w-6 text-cyan-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display' }}>
                PropertyCheck AI Enterprise API
              </h1>
              <p className="text-sm text-slate-400 mt-1">
                Integrate property verification, risk scoring, and intelligence into your applications.
                RESTful API with JSON responses, designed for banks, NBFCs, and PropTech platforms.
              </p>
              <div className="flex gap-2 mt-3">
                <Badge className="bg-emerald-500/20 text-emerald-400">REST API</Badge>
                <Badge className="bg-cyan-500/20 text-cyan-400">JSON</Badge>
                <Badge className="bg-violet-500/20 text-violet-400">Rate Limited</Badge>
              </div>
            </div>
          </div>
        </div>

        {/* API Key Generation */}
        <div className="glass-card mb-8" data-testid="api-key-section">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Key className="h-5 w-5 text-cyan-400" />API Key Management
          </h2>

          {apiKey ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-slate-800/80 rounded-lg border border-emerald-500/30">
                <div>
                  <p className="text-xs text-slate-400">Your API Key</p>
                  <code className="text-sm text-emerald-400 font-mono">{apiKey.api_key}</code>
                </div>
                <Button variant="ghost" size="sm" className="text-slate-400" onClick={() => copyToClipboard(apiKey.api_key)} data-testid="copy-api-key-btn">
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex gap-4 text-xs text-slate-400">
                <span>Org: {apiKey.org_name}</span>
                <span>Plan: {apiKey.plan}</span>
                <span>Rate Limit: {apiKey.rate_limit}</span>
              </div>
              <div className="p-3 bg-slate-800/50 rounded-lg">
                <p className="text-xs text-slate-400 mb-1">Usage example:</p>
                <code className="text-xs text-cyan-400 font-mono block">
                  curl -H "X-API-Key: {apiKey.api_key}" {BACKEND_URL}/api/enterprise/v1/verify/PROPERTY_ID
                </code>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <p className="text-sm text-slate-400">Generate an API key to access enterprise endpoints.</p>
              <div className="grid md:grid-cols-2 gap-3">
                <input
                  data-testid="org-name-input"
                  type="text" placeholder="Organization Name *"
                  value={orgName} onChange={e => setOrgName(e.target.value)}
                  className="input-glass"
                />
                <input
                  data-testid="contact-email-input"
                  type="email" placeholder="Contact Email"
                  value={contactEmail} onChange={e => setContactEmail(e.target.value)}
                  className="input-glass"
                />
              </div>
              <Button data-testid="generate-api-key-btn" className="btn-primary" onClick={generateApiKey} disabled={generating}>
                {generating ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Key className="h-4 w-4 mr-2" />}
                Generate API Key
              </Button>
            </div>
          )}
        </div>

        {/* Authentication Info */}
        <div className="glass-card mb-8">
          <h2 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
            <Lock className="h-5 w-5 text-cyan-400" />Authentication
          </h2>
          <div className="space-y-3 text-sm text-slate-300">
            <div className="p-3 bg-slate-800/50 rounded-lg">
              <p className="font-medium text-white mb-1">Enterprise API (X-API-Key)</p>
              <code className="text-xs text-cyan-400 font-mono">Header: X-API-Key: pck_your_api_key_here</code>
            </div>
            <div className="p-3 bg-slate-800/50 rounded-lg">
              <p className="font-medium text-white mb-1">User API (Bearer Token)</p>
              <code className="text-xs text-cyan-400 font-mono">Header: Authorization: Bearer your_jwt_token</code>
            </div>
          </div>
        </div>

        {/* Endpoints */}
        {API_ENDPOINTS.map((category, ci) => (
          <div key={ci} className="glass-card mb-6" data-testid={`api-category-${ci}`}>
            <h2 className="text-lg font-semibold text-white mb-4">{category.category}</h2>
            <div className="space-y-2">
              {category.endpoints.map((ep, ei) => {
                const key = `${ci}-${ei}`;
                const isExpanded = expandedEndpoint === key;
                return (
                  <div key={ei} className="border border-slate-700/50 rounded-lg overflow-hidden">
                    <button
                      data-testid={`endpoint-${ci}-${ei}`}
                      onClick={() => setExpandedEndpoint(isExpanded ? null : key)}
                      className="w-full flex items-center gap-3 p-3 hover:bg-slate-800/50 transition-colors text-left"
                    >
                      <Badge className={`${methodColor[ep.method]} text-xs font-mono px-2`}>{ep.method}</Badge>
                      <code className="text-sm text-white font-mono flex-1">{ep.path}</code>
                      <span className="text-xs text-slate-500 hidden md:block">{ep.auth}</span>
                      <ChevronRight className={`h-4 w-4 text-slate-500 transition-transform ${isExpanded ? 'rotate-90' : ''}`} />
                    </button>
                    {isExpanded && (
                      <div className="px-3 pb-3 border-t border-slate-700/50 pt-3 space-y-2">
                        <p className="text-sm text-slate-300">{ep.desc}</p>
                        <div className="flex gap-2">
                          <Badge variant="outline" className="text-xs border-slate-600 text-slate-400">Auth: {ep.auth}</Badge>
                        </div>
                        {ep.params && <p className="text-xs text-slate-500">Query params: {ep.params}</p>}
                        {ep.body && (
                          <div className="p-2 bg-slate-900/50 rounded text-xs font-mono text-cyan-400">
                            {ep.body}
                          </div>
                        )}
                        <Button
                          variant="ghost" size="sm" className="text-slate-400 text-xs"
                          onClick={() => copyToClipboard(`curl ${ep.method === 'GET' ? '' : '-X POST '}${BACKEND_URL}${ep.path.replace('{property_id}', 'PROP_ID').replace('{id}', 'PROP_ID')}${ep.auth === 'API Key' ? ' -H "X-API-Key: YOUR_KEY"' : ep.auth === 'Bearer Token' ? ' -H "Authorization: Bearer YOUR_TOKEN"' : ''}`)}
                        >
                          <Copy className="h-3 w-3 mr-1" /> Copy cURL
                        </Button>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))}

        {/* Rate Limits */}
        <div className="glass-card">
          <h2 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-amber-400" />Rate Limits & Pricing
          </h2>
          <div className="grid md:grid-cols-3 gap-4">
            {[
              { plan: 'Trial', limit: '100 req/day', price: 'Free', features: ['Basic verification', 'Risk score access'] },
              { plan: 'Professional', limit: '10,000 req/day', price: '$299/mo', features: ['Full title chain', 'Valuation data', 'Priority support'] },
              { plan: 'Enterprise', limit: 'Unlimited', price: 'Custom', features: ['All features', 'Dedicated support', 'Custom integrations', 'SLA guarantee'] },
            ].map(tier => (
              <div key={tier.plan} className="p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
                <h3 className="font-semibold text-white">{tier.plan}</h3>
                <p className="text-xs text-slate-400 mb-2">{tier.limit}</p>
                <p className="text-lg font-bold text-cyan-400 mb-3">{tier.price}</p>
                <ul className="space-y-1">
                  {tier.features.map((f, i) => (
                    <li key={i} className="flex items-center gap-1.5 text-xs text-slate-400">
                      <CheckCircle2 className="h-3 w-3 text-emerald-400" />{f}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
};

export default ApiDocs;
