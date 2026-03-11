import React, { useState, useEffect, useCallback } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  ArrowLeft, FileText, AlertTriangle, CheckCircle2, XCircle,
  Download, RefreshCw, Loader2, MapPin, Calendar, User, Building2,
  Scale, Clock, Sparkles, TrendingUp, Globe, Gavel, History,
  Share2, ExternalLink, ChevronRight, IndianRupee, Home,
  ShieldCheck, FileSearch, Landmark, Copy
} from 'lucide-react';
import { toast } from 'sonner';
import RiskMeter from '../components/RiskMeter';
import KnowledgeGraph from '../components/KnowledgeGraph';
import PropertyMap from '../components/PropertyMap';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PropertyIntelligence = () => {
  const { propertyId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [property, setProperty] = useState(null);
  const [report, setReport] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [govtRecords, setGovtRecords] = useState(null);
  const [titleChain, setTitleChain] = useState(null);
  const [valuation, setValuation] = useState(null);
  const [govtSources, setGovtSources] = useState(null);
  const [legalCopilot, setLegalCopilot] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [copilotLoading, setCopilotLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  const fetchData = useCallback(async () => {
    try {
      const [propRes, docsRes] = await Promise.all([
        axios.get(`${API}/properties/${propertyId}`, { withCredentials: true }),
        axios.get(`${API}/documents/${propertyId}`, { withCredentials: true }).catch(() => ({ data: [] })),
      ]);
      setProperty(propRes.data);
      setDocuments(Array.isArray(docsRes.data) ? docsRes.data : docsRes.data?.documents || []);

      // Fetch parallel intelligence data
      const [reportRes, govtRes, chainRes, valRes, sourcesRes, copilotRes] = await Promise.allSettled([
        axios.get(`${API}/reports/${propertyId}`, { withCredentials: true }),
        axios.get(`${API}/government-records/${encodeURIComponent(propRes.data.survey_no)}?state=${encodeURIComponent(propRes.data.state)}`, { withCredentials: true }),
        axios.get(`${API}/property/${propertyId}/title-chain`, { withCredentials: true }),
        axios.get(`${API}/property/${propertyId}/valuation`, { withCredentials: true }),
        axios.get(`${API}/property/${propertyId}/government-sources`, { withCredentials: true }),
        axios.get(`${API}/property/${propertyId}/legal-copilot`, { withCredentials: true }),
      ]);

      if (reportRes.status === 'fulfilled') setReport(reportRes.value.data);
      if (govtRes.status === 'fulfilled') setGovtRecords(govtRes.value.data);
      if (chainRes.status === 'fulfilled') setTitleChain(chainRes.value.data);
      if (valRes.status === 'fulfilled') setValuation(valRes.value.data);
      if (sourcesRes.status === 'fulfilled') setGovtSources(sourcesRes.value.data);
      if (copilotRes.status === 'fulfilled' && copilotRes.value.data?.analysis) setLegalCopilot(copilotRes.value.data);
    } catch (err) {
      toast.error('Failed to load property data');
    } finally {
      setLoading(false);
    }
  }, [propertyId]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const runAnalysis = async () => {
    setAnalyzing(true);
    try {
      const res = await axios.post(`${API}/analyze/${propertyId}`, {}, { withCredentials: true });
      setReport(res.data);
      toast.success('AI Risk Analysis complete');
    } catch (err) {
      toast.error('Analysis failed');
    } finally {
      setAnalyzing(false);
    }
  };

  const runLegalCopilot = async () => {
    setCopilotLoading(true);
    try {
      const res = await axios.post(`${API}/property/${propertyId}/legal-copilot`, {}, { withCredentials: true });
      setLegalCopilot(res.data);
      toast.success('Legal analysis generated');
    } catch (err) {
      toast.error('Legal Copilot analysis failed');
    } finally {
      setCopilotLoading(false);
    }
  };

  const shareReport = async () => {
    if (!report) { toast.error('Run analysis first'); return; }
    try {
      const res = await axios.post(`${API}/reports/${propertyId}/share`, {}, { withCredentials: true });
      const link = `${window.location.origin}/shared-report/${res.data.share_token}`;
      await navigator.clipboard.writeText(link);
      toast.success('Shareable link copied to clipboard');
    } catch (err) {
      toast.error('Failed to generate shareable link');
    }
  };

  if (loading) return (
    <div className="min-h-screen gradient-bg flex items-center justify-center">
      <Loader2 className="h-8 w-8 animate-spin text-cyan-400" />
    </div>
  );

  if (!property) return (
    <div className="min-h-screen gradient-bg flex items-center justify-center">
      <div className="glass-card text-center"><p className="text-slate-400">Property not found</p></div>
    </div>
  );

  const riskColor = report?.risk_score >= 80 ? 'emerald' : report?.risk_score >= 50 ? 'amber' : 'red';

  return (
    <div className="min-h-screen gradient-bg">
      <div className="fixed inset-0 grid-bg opacity-30 pointer-events-none" />

      {/* Nav */}
      <nav className="glass-header sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-4">
              <button onClick={() => navigate('/dashboard')} data-testid="back-to-dashboard" className="text-slate-400 hover:text-white transition-colors"><ArrowLeft className="h-5 w-5" /></button>
              <Link to="/" className="flex items-center gap-2">
                <Building2 className="h-8 w-8 text-cyan-400" />
                <span className="text-xl font-semibold text-white" style={{ fontFamily: 'Playfair Display' }}>PropertyCheck AI</span>
              </Link>
            </div>
            <div className="flex items-center gap-3">
              {report && (
                <>
                  <Button data-testid="share-report-btn" variant="ghost" className="text-slate-400 hover:text-white" onClick={shareReport}><Share2 className="h-4 w-4 mr-2" />Share</Button>
                  <Link to={`/report/${propertyId}`}><Button data-testid="download-report-btn" variant="ghost" className="text-slate-400 hover:text-white"><Download className="h-4 w-4 mr-2" />PDF</Button></Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        {/* Property Header */}
        <div className="glass-card mb-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display' }}>
                  Survey No. {property.survey_no}
                </h1>
                {report && (
                  <Badge className={`bg-${riskColor}-500/20 text-${riskColor}-400 border-${riskColor}-500/30`}>
                    {report.risk_score >= 80 ? 'Low Risk' : report.risk_score >= 50 ? 'Medium Risk' : 'High Risk'}
                  </Badge>
                )}
              </div>
              <div className="flex flex-wrap gap-4 text-sm text-slate-400">
                <span className="flex items-center gap-1"><User className="h-3.5 w-3.5" />{property.owner_name || 'Unknown'}</span>
                <span className="flex items-center gap-1"><MapPin className="h-3.5 w-3.5" />{property.district}, {property.state}</span>
                <span className="flex items-center gap-1"><Home className="h-3.5 w-3.5" />{property.land_type || 'Residential'}</span>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {!report ? (
                <Button data-testid="run-analysis-btn" className="btn-primary" onClick={runAnalysis} disabled={analyzing}>
                  {analyzing ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Analyzing...</> : <><Sparkles className="h-4 w-4 mr-2" />Run AI Analysis</>}
                </Button>
              ) : (
                <div className="text-center">
                  <p className="text-xs text-slate-500 mb-1">Risk Score</p>
                  <p className={`text-3xl font-bold font-mono text-${riskColor}-400`}>{report.risk_score}</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Quick Stats Row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="glass-card text-center py-4">
            <p className="text-2xl font-bold text-white font-mono">{titleChain?.total_transfers || '—'}</p>
            <p className="text-xs text-slate-400 mt-1">Ownership Transfers</p>
          </div>
          <div className="glass-card text-center py-4">
            <p className="text-2xl font-bold text-white font-mono">{titleChain?.chain_span_years || '—'}yr</p>
            <p className="text-xs text-slate-400 mt-1">Title History Span</p>
          </div>
          <div className="glass-card text-center py-4">
            <p className="text-2xl font-bold text-white font-mono">{govtSources?.retrieved || '—'}/{govtSources?.total_sources || '—'}</p>
            <p className="text-xs text-slate-400 mt-1">Sources Retrieved</p>
          </div>
          <div className="glass-card text-center py-4">
            <p className="text-2xl font-bold text-cyan-400 font-mono">{valuation?.estimated_value?.formatted || '—'}</p>
            <p className="text-xs text-slate-400 mt-1">Est. Value</p>
          </div>
        </div>

        {/* Main Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="glass-card w-full flex flex-wrap gap-1 p-1">
            {[
              { v: 'overview', l: 'Overview', i: Home },
              { v: 'title-chain', l: 'Title Chain', i: History },
              { v: 'risk', l: 'Risk Report', i: ShieldCheck },
              { v: 'legal-copilot', l: 'Legal Copilot', i: Gavel },
              { v: 'valuation', l: 'Valuation', i: IndianRupee },
              { v: 'documents', l: 'Documents', i: FileText },
              { v: 'government', l: 'Govt Sources', i: Globe },
              { v: 'graph', l: 'Knowledge Graph', i: Globe },
              { v: 'map', l: 'Map', i: MapPin },
            ].map(t => (
              <TabsTrigger key={t.v} value={t.v} className="flex-1 data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400 text-xs sm:text-sm" data-testid={`tab-${t.v}`}>
                <t.i className="h-3.5 w-3.5 mr-1.5 hidden sm:inline" />{t.l}
              </TabsTrigger>
            ))}
          </TabsList>

          {/* OVERVIEW TAB */}
          <TabsContent value="overview">
            <div className="grid md:grid-cols-2 gap-6">
              <div className="glass-card">
                <h3 className="text-lg font-semibold text-white mb-4">Property Details</h3>
                <div className="space-y-3">
                  {[
                    ['Survey No', property.survey_no],
                    ['Owner', property.owner_name],
                    ['Khata No', property.khata_no || 'N/A'],
                    ['Extent', property.extent || 'N/A'],
                    ['Land Type', property.land_type || 'N/A'],
                    ['Village', property.village || 'N/A'],
                    ['Taluk', property.taluk || 'N/A'],
                    ['District', property.district],
                    ['State', property.state],
                  ].map(([k, v]) => (
                    <div key={k} className="flex justify-between py-2 border-b border-slate-700/30">
                      <span className="text-sm text-slate-400">{k}</span>
                      <span className="text-sm text-white font-medium">{v || '—'}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-6">
                {report && (
                  <div className={`glass-card border-${riskColor}-500/30`}>
                    <h3 className="text-lg font-semibold text-white mb-3">AI Risk Assessment</h3>
                    <div className="flex items-center justify-between mb-4">
                      <RiskMeter score={report.risk_score} />
                      <div className="text-right">
                        <p className={`text-2xl font-bold text-${riskColor}-400`}>{report.risk_score}/100</p>
                        <p className={`text-sm text-${riskColor}-400`}>{report.risk_score >= 80 ? 'No Risk' : report.risk_score >= 50 ? 'Medium Risk' : 'High Risk'}</p>
                      </div>
                    </div>
                    <Button variant="ghost" className="w-full text-slate-400 hover:text-white" onClick={() => setActiveTab('risk')}>
                      View Detailed Report <ChevronRight className="h-4 w-4 ml-1" />
                    </Button>
                  </div>
                )}

                {valuation && (
                  <div className="glass-card">
                    <h3 className="text-lg font-semibold text-white mb-3">Market Intelligence</h3>
                    <div className="flex justify-between items-center mb-3">
                      <span className="text-sm text-slate-400">Estimated Value</span>
                      <span className="text-xl font-bold text-cyan-400">{valuation.estimated_value.formatted}</span>
                    </div>
                    <div className="flex justify-between items-center mb-3">
                      <span className="text-sm text-slate-400">Guideline Value</span>
                      <span className="text-sm text-white">{valuation.guideline_value.formatted}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-slate-400">Annual Appreciation</span>
                      <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30">{valuation.price_trends.annual_appreciation}</Badge>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </TabsContent>

          {/* TITLE CHAIN TAB */}
          <TabsContent value="title-chain">
            <div className="glass-card">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-white">Ownership Title Chain</h3>
                {titleChain && (
                  <div className="flex gap-3">
                    <Badge className="bg-cyan-500/20 text-cyan-400">{titleChain.chain_span_years}+ Years</Badge>
                    <Badge className={`${titleChain.completeness_score >= 90 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'}`}>
                      {titleChain.completeness_score}% Complete
                    </Badge>
                  </div>
                )}
              </div>

              {titleChain?.chain?.map((entry, i) => (
                <div key={i} className="relative pl-8 pb-8 last:pb-0">
                  <div className="absolute left-3 top-2 bottom-0 w-px bg-slate-700" />
                  <div className={`absolute left-1 top-2 h-5 w-5 rounded-full flex items-center justify-center ${entry.verified ? 'bg-emerald-500/20 border border-emerald-500/50' : 'bg-amber-500/20 border border-amber-500/50'}`}>
                    {entry.verified ? <CheckCircle2 className="h-3 w-3 text-emerald-400" /> : <AlertTriangle className="h-3 w-3 text-amber-400" />}
                  </div>
                  <div className="glass-card ml-4">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                      <div>
                        <p className="font-semibold text-white">{entry.owner_name}</p>
                        <p className="text-xs text-slate-500">{entry.father_name}</p>
                      </div>
                      <div className="text-right">
                        <Badge variant="outline" className="border-slate-600 text-slate-300">{entry.transfer_type}</Badge>
                        <p className="text-xs text-slate-500 mt-1">{entry.transfer_date}</p>
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-4 text-xs text-slate-400">
                      <span>Doc: {entry.doc_ref}</span>
                      <span>Extent: {entry.extent}</span>
                      {entry.consideration !== 'N/A' && <span>Consideration: {entry.consideration}</span>}
                      <span>Registrar: {entry.registrar}</span>
                    </div>
                  </div>
                </div>
              ))}

              {titleChain?.gaps?.length > 0 && (
                <div className="mt-6 p-4 bg-amber-500/10 border border-amber-500/30 rounded-lg">
                  <h4 className="font-semibold text-amber-400 mb-2 flex items-center gap-2"><AlertTriangle className="h-4 w-4" />Title Chain Gaps Detected</h4>
                  {titleChain.gaps.map((g, i) => (
                    <p key={i} className="text-sm text-amber-300">{g.between}: {g.gap_years} year gap - {g.note}</p>
                  ))}
                </div>
              )}

              {titleChain?.anomalies?.length > 0 && (
                <div className="mt-4 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                  <h4 className="font-semibold text-red-400 mb-2 flex items-center gap-2"><XCircle className="h-4 w-4" />Anomalies</h4>
                  {titleChain.anomalies.map((a, i) => (
                    <p key={i} className="text-sm text-red-300">{a.type}: {a.detail}</p>
                  ))}
                </div>
              )}
            </div>
          </TabsContent>

          {/* RISK REPORT TAB */}
          <TabsContent value="risk">
            {report ? (
              <div className="space-y-6">
                <div className="glass-card">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold text-white">AI Risk Analysis Report</h3>
                    <Button variant="ghost" className="text-slate-400" onClick={runAnalysis} disabled={analyzing}>
                      <RefreshCw className={`h-4 w-4 mr-2 ${analyzing ? 'animate-spin' : ''}`} />Re-analyze
                    </Button>
                  </div>
                  <div className="grid md:grid-cols-3 gap-6 mb-6">
                    <div className="text-center">
                      <RiskMeter score={report.risk_score} />
                      <p className={`mt-2 text-lg font-bold text-${riskColor}-400`}>{report.risk_score}/100</p>
                    </div>
                    <div className="md:col-span-2">
                      <h4 className="font-medium text-white mb-3">Executive Summary</h4>
                      <p className="text-sm text-slate-300 leading-relaxed">{report.summary || report.executive_summary}</p>
                    </div>
                  </div>
                </div>

                {report.risk_factors && (
                  <div className="glass-card">
                    <h4 className="font-semibold text-white mb-4">Risk Factors</h4>
                    <div className="space-y-3">
                      {report.risk_factors.map((f, i) => (
                        <div key={i} className="flex items-start gap-3 p-3 bg-slate-800/50 rounded-lg">
                          {f.severity === 'HIGH' ? <XCircle className="h-5 w-5 text-red-400 flex-shrink-0" /> :
                           f.severity === 'MEDIUM' ? <AlertTriangle className="h-5 w-5 text-amber-400 flex-shrink-0" /> :
                           <CheckCircle2 className="h-5 w-5 text-emerald-400 flex-shrink-0" />}
                          <div>
                            <p className="text-sm font-medium text-white">{f.factor || f.name}</p>
                            <p className="text-xs text-slate-400">{f.detail || f.description}</p>
                          </div>
                          <Badge className={`ml-auto ${f.severity === 'HIGH' ? 'bg-red-500/20 text-red-400' : f.severity === 'MEDIUM' ? 'bg-amber-500/20 text-amber-400' : 'bg-emerald-500/20 text-emerald-400'}`}>{f.severity}</Badge>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {report.recommendations && (
                  <div className="glass-card">
                    <h4 className="font-semibold text-white mb-4">Recommendations</h4>
                    <div className="space-y-2">
                      {report.recommendations.map((r, i) => (
                        <div key={i} className="flex items-start gap-2 text-sm text-slate-300">
                          <ChevronRight className="h-4 w-4 text-cyan-400 flex-shrink-0 mt-0.5" />
                          <span>{r}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="glass-card text-center py-12">
                <Sparkles className="h-12 w-12 text-cyan-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">AI Risk Analysis</h3>
                <p className="text-sm text-slate-400 mb-6">Run AI analysis to generate risk score and detailed verification report</p>
                <Button data-testid="run-analysis-cta" className="btn-primary" onClick={runAnalysis} disabled={analyzing}>
                  {analyzing ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Analyzing...</> : <><Sparkles className="h-4 w-4 mr-2" />Run AI Analysis</>}
                </Button>
              </div>
            )}
          </TabsContent>

          {/* LEGAL COPILOT TAB */}
          <TabsContent value="legal-copilot">
            <div className="glass-card">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                    <Gavel className="h-5 w-5 text-cyan-400" />AI Legal Copilot
                  </h3>
                  <p className="text-xs text-slate-500">AI-powered legal due diligence analysis</p>
                </div>
                <Button data-testid="run-legal-copilot" className="btn-primary" onClick={runLegalCopilot} disabled={copilotLoading}>
                  {copilotLoading ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Generating...</> : <><Sparkles className="h-4 w-4 mr-2" />{legalCopilot ? 'Re-generate' : 'Generate Analysis'}</>}
                </Button>
              </div>

              {legalCopilot?.analysis ? (
                <div className="space-y-4">
                  {legalCopilot.ai_powered && (
                    <Badge className="bg-cyan-500/20 text-cyan-400 border-cyan-500/30">Powered by Gemini AI</Badge>
                  )}
                  <div className="bg-slate-900/50 rounded-lg p-6 border border-slate-700/50 max-h-[600px] overflow-y-auto">
                    <pre className="text-sm text-slate-300 whitespace-pre-wrap font-sans leading-relaxed">{legalCopilot.analysis}</pre>
                  </div>
                  <p className="text-xs text-slate-500">Generated: {new Date(legalCopilot.generated_at).toLocaleString()}</p>
                </div>
              ) : (
                <div className="text-center py-12">
                  <Scale className="h-12 w-12 text-slate-600 mx-auto mb-4" />
                  <p className="text-sm text-slate-400">Click "Generate Analysis" to create a lawyer-style due diligence report for this property</p>
                </div>
              )}
            </div>
          </TabsContent>

          {/* VALUATION TAB */}
          <TabsContent value="valuation">
            {valuation ? (
              <div className="space-y-6">
                <div className="grid md:grid-cols-3 gap-4">
                  <div className="glass-card text-center">
                    <p className="text-sm text-slate-400 mb-1">Estimated Market Value</p>
                    <p className="text-3xl font-bold text-cyan-400">{valuation.estimated_value.formatted}</p>
                    <Badge className="mt-2 bg-cyan-500/20 text-cyan-400">{valuation.estimated_value.confidence} Confidence</Badge>
                  </div>
                  <div className="glass-card text-center">
                    <p className="text-sm text-slate-400 mb-1">Government Guideline Value</p>
                    <p className="text-2xl font-bold text-white">{valuation.guideline_value.formatted}</p>
                    <p className="text-xs text-slate-500 mt-1">{valuation.guideline_value.source}</p>
                  </div>
                  <div className="glass-card text-center">
                    <p className="text-sm text-slate-400 mb-1">Annual Appreciation</p>
                    <p className="text-2xl font-bold text-emerald-400">{valuation.price_trends.annual_appreciation}</p>
                    <Badge className="mt-2 bg-emerald-500/20 text-emerald-400">{valuation.price_trends.trend}</Badge>
                  </div>
                </div>

                {/* Price Trend Chart */}
                <div className="glass-card">
                  <h4 className="font-semibold text-white mb-4 flex items-center gap-2"><TrendingUp className="h-4 w-4 text-cyan-400" />Price Trend ({valuation.price_trends.district})</h4>
                  <div className="flex items-end gap-3 h-48">
                    {valuation.price_trends.data_points.map((dp, i) => {
                      const max = Math.max(...valuation.price_trends.data_points.map(d => d.avg_price_sqft));
                      const pct = (dp.avg_price_sqft / max) * 100;
                      return (
                        <div key={i} className="flex-1 flex flex-col items-center gap-2">
                          <span className="text-xs text-slate-400">{dp.avg_price_sqft}</span>
                          <div className="w-full bg-cyan-500/30 rounded-t" style={{ height: `${pct}%` }}>
                            <div className="w-full h-full bg-gradient-to-t from-cyan-600/80 to-cyan-400/80 rounded-t" />
                          </div>
                          <span className="text-xs text-slate-500">{dp.year}</span>
                        </div>
                      );
                    })}
                  </div>
                  <p className="text-xs text-slate-500 mt-2 text-center">Average Price per Sq.Ft (INR)</p>
                </div>

                {/* Neighborhood */}
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="glass-card">
                    <h4 className="font-semibold text-white mb-4">Neighborhood Scores</h4>
                    {Object.entries(valuation.neighborhood).map(([k, v]) => (
                      <div key={k} className="flex items-center justify-between py-2 border-b border-slate-700/30 last:border-0">
                        <span className="text-sm text-slate-400 capitalize">{k.replace('_', ' ')}</span>
                        <div className="flex items-center gap-2">
                          <div className="w-24 h-2 bg-slate-700 rounded-full overflow-hidden">
                            <div className="h-full bg-cyan-400 rounded-full" style={{ width: `${(v / 5) * 100}%` }} />
                          </div>
                          <span className="text-sm text-white font-mono">{v}/5</span>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="glass-card">
                    <h4 className="font-semibold text-white mb-4">Nearby Infrastructure</h4>
                    <div className="space-y-3">
                      {Object.entries(valuation.infrastructure).map(([k, v]) => (
                        <div key={k} className="flex items-center justify-between py-2 border-b border-slate-700/30 last:border-0">
                          <div>
                            <p className="text-sm text-white">{v.name}</p>
                            <p className="text-xs text-slate-500 capitalize">{k.replace('_', ' ')}</p>
                          </div>
                          <span className="text-sm text-cyan-400">{v.distance}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Nearby Transactions */}
                <div className="glass-card">
                  <h4 className="font-semibold text-white mb-4">Recent Transactions Nearby</h4>
                  <div className="space-y-3">
                    {valuation.nearby_transactions.map((tx, i) => (
                      <div key={i} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                        <div>
                          <p className="text-sm text-white">{tx.address}</p>
                          <p className="text-xs text-slate-500">{tx.date} - {tx.type}</p>
                        </div>
                        <span className="text-sm font-bold text-emerald-400">{tx.amount}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="glass-card text-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-cyan-400 mx-auto mb-4" />
                <p className="text-sm text-slate-400">Loading valuation data...</p>
              </div>
            )}
          </TabsContent>

          {/* DOCUMENTS TAB */}
          <TabsContent value="documents">
            <div className="glass-card">
              <h3 className="text-lg font-semibold text-white mb-4">Property Documents</h3>
              {documents.length > 0 ? (
                <div className="space-y-3 mb-6">
                  {documents.map((doc, i) => (
                    <div key={i} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                      <div className="flex items-center gap-3">
                        <FileText className="h-5 w-5 text-cyan-400" />
                        <div>
                          <p className="text-sm text-white">{doc.filename || doc.doc_type}</p>
                          <p className="text-xs text-slate-500">{doc.doc_type} - {doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleDateString() : 'N/A'}</p>
                        </div>
                      </div>
                      <Badge className={doc.ocr_status === 'completed' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'}>
                        {doc.ocr_status || 'Pending'}
                      </Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-slate-400 mb-4">No documents uploaded yet.</p>
              )}
              <Link to={`/upload?property_id=${propertyId}`}>
                <Button className="btn-secondary"><FileSearch className="h-4 w-4 mr-2" />Upload Documents</Button>
              </Link>
            </div>
          </TabsContent>

          {/* GOVERNMENT SOURCES TAB */}
          <TabsContent value="government">
            {govtSources ? (
              <div className="space-y-6">
                <div className="glass-card">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                      <Globe className="h-5 w-5 text-cyan-400" />Government Data Retrieval Agents
                    </h3>
                    <div className="flex gap-2">
                      <Badge className="bg-emerald-500/20 text-emerald-400">{govtSources.retrieved} Retrieved</Badge>
                      {govtSources.pending > 0 && <Badge className="bg-amber-500/20 text-amber-400">{govtSources.pending} Pending</Badge>}
                    </div>
                  </div>
                  <div className="space-y-3">
                    {govtSources.sources.map((src, i) => (
                      <div key={i} className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
                        <div className="flex items-center gap-3">
                          {src.status === 'RETRIEVED' ? <CheckCircle2 className="h-5 w-5 text-emerald-400" /> : <Clock className="h-5 w-5 text-amber-400 animate-pulse" />}
                          <div>
                            <p className="text-sm font-medium text-white">{src.name}</p>
                            {src.url !== '#' && <p className="text-xs text-slate-500">{src.url}</p>}
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge className={src.status === 'RETRIEVED' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'}>
                            {src.status}
                          </Badge>
                          <p className="text-xs text-slate-500 mt-1">{src.records_found} records</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {govtRecords && (
                  <div className="glass-card">
                    <h4 className="font-semibold text-white mb-4">Retrieved Land Records</h4>
                    <div className="grid md:grid-cols-2 gap-4">
                      {[
                        ['Owner Name', govtRecords.owner_name],
                        ['Father Name', govtRecords.father_name],
                        ['Extent', govtRecords.extent],
                        ['Land Type', govtRecords.land_type],
                        ['Khata No', govtRecords.khata_no],
                        ['CERSAI', govtRecords.cersai_check],
                      ].map(([k, v]) => (
                        <div key={k} className="flex justify-between p-2 border-b border-slate-700/30">
                          <span className="text-sm text-slate-400">{k}</span>
                          <span className="text-sm text-white">{v || '—'}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <p className="text-xs text-amber-400 flex items-center gap-1">
                  <AlertTriangle className="h-3 w-3" />
                  {govtSources.disclaimer}
                </p>
              </div>
            ) : (
              <div className="glass-card text-center py-12"><Loader2 className="h-8 w-8 animate-spin text-cyan-400 mx-auto" /></div>
            )}
          </TabsContent>

          {/* KNOWLEDGE GRAPH TAB */}
          <TabsContent value="graph">
            <div className="glass-card">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Globe className="h-5 w-5 text-cyan-400" />Property Knowledge Graph
              </h3>
              <p className="text-xs text-slate-500 mb-4">Interactive visualization of property relationships — owners, documents, locations, and government records</p>
              <KnowledgeGraph
                propertyId={propertyId}
                titleChain={titleChain}
                property={property}
                documents={documents}
              />
            </div>
          </TabsContent>

          {/* MAP TAB */}
          <TabsContent value="map">
            <div className="glass-card">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <MapPin className="h-5 w-5 text-cyan-400" />Property Location
              </h3>
              <p className="text-xs text-slate-500 mb-4">Property location with nearby infrastructure markers</p>
              <PropertyMap property={property} valuation={valuation} />
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default PropertyIntelligence;
