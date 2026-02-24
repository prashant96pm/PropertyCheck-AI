import React, { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Progress } from '../components/ui/progress';
import RiskMeter from '../components/RiskMeter';
import ShimmerLoader from '../components/ShimmerLoader';
import FloatingActionButton from '../components/FloatingActionButton';
import { 
  ArrowLeft, 
  FileText, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle,
  Download,
  RefreshCw,
  Loader2,
  MapPin,
  Calendar,
  User,
  Building2,
  Scale,
  Clock,
  Sparkles
} from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PropertyDetail = () => {
  const { propertyId } = useParams();
  const navigate = useNavigate();
  
  const [property, setProperty] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [report, setReport] = useState(null);
  const [govtRecords, setGovtRecords] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    fetchPropertyData();
  }, [propertyId]);

  const fetchPropertyData = async () => {
    try {
      const [propRes, docsRes] = await Promise.all([
        axios.get(`${API}/properties/${propertyId}`, { withCredentials: true }),
        axios.get(`${API}/documents/${propertyId}`, { withCredentials: true })
      ]);
      
      setProperty(propRes.data);
      setDocuments(docsRes.data);
      
      try {
        const reportRes = await axios.get(`${API}/reports/${propertyId}`, { withCredentials: true });
        setReport(reportRes.data);
      } catch (e) {}
      
      if (propRes.data.survey_no) {
        const govtRes = await axios.get(
          `${API}/government-records/${encodeURIComponent(propRes.data.survey_no)}?state=${encodeURIComponent(propRes.data.state)}`,
          { withCredentials: true }
        );
        setGovtRecords(govtRes.data);
      }
    } catch (error) {
      toast.error('Failed to load property data');
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const runAnalysis = async () => {
    setAnalyzing(true);
    try {
      const response = await axios.post(
        `${API}/analyze/${propertyId}`,
        {},
        { withCredentials: true }
      );
      setReport(response.data);
      setProperty(prev => ({
        ...prev,
        risk_score: response.data.risk_score,
        risk_status: response.data.risk_status
      }));
      toast.success('Analysis completed');
    } catch (error) {
      toast.error('Analysis failed. Please try again.');
    } finally {
      setAnalyzing(false);
    }
  };

  const downloadReport = async () => {
    try {
      const response = await axios.get(
        `${API}/reports/${propertyId}/download`,
        { 
          withCredentials: true,
          responseType: 'blob'
        }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `PropertyCheck_Report_${propertyId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success('Report downloaded');
    } catch (error) {
      toast.error('Failed to download report');
    }
  };

  const getCardGlowClass = (status) => {
    if (!status) return 'glass-card';
    if (status === 'GREEN') return 'glass-card-green';
    if (status === 'YELLOW') return 'glass-card-orange';
    return 'glass-card-red';
  };

  if (loading) {
    return (
      <div className="min-h-screen gradient-bg">
        <div className="fixed inset-0 grid-bg opacity-30 pointer-events-none" />
        <nav className="glass-header sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center h-16">
              <ShimmerLoader className="h-8 w-8 rounded-lg mr-2" />
              <ShimmerLoader className="h-6 w-40" />
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <ShimmerLoader className="h-8 w-64 mb-4" />
          <div className="grid lg:grid-cols-3 gap-6">
            <ShimmerLoader variant="card" />
            <ShimmerLoader variant="card" />
            <ShimmerLoader variant="risk-meter" />
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen gradient-bg">
      <div className="fixed inset-0 grid-bg opacity-30 pointer-events-none" />
      
      {/* Navigation */}
      <nav className="glass-header sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-4">
              <Link to="/dashboard" className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors">
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <Link to="/" className="flex items-center gap-2">
                <Building2 className="h-8 w-8 text-cyan-400" />
                <span className="text-xl font-semibold text-white" style={{ fontFamily: 'Playfair Display' }}>
                  PropertyCheck AI
                </span>
              </Link>
            </div>
            
            <div className="flex items-center gap-3">
              {report && (
                <Button 
                  data-testid="download-report-btn"
                  className="btn-secondary"
                  onClick={downloadReport}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download PDF
                </Button>
              )}
              <Button
                data-testid="run-analysis-btn"
                onClick={runAnalysis}
                disabled={analyzing}
                className="btn-primary"
              >
                {analyzing ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : report ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Re-analyze
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4 mr-2" />
                    Run AI Analysis
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white" style={{ fontFamily: 'Playfair Display' }}>
                Survey No: <span className="text-gradient">{property?.survey_no}</span>
              </h1>
              <p className="text-slate-400 mt-1 flex items-center gap-2">
                <MapPin className="h-4 w-4" />
                {property?.district}, {property?.state}
                {property?.taluk && ` • ${property.taluk}`}
              </p>
            </div>
            
            {/* Risk Meter */}
            {property?.risk_score && (
              <RiskMeter score={property.risk_score} size={160} />
            )}
          </div>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="bg-slate-800/50 border border-slate-700">
            <TabsTrigger data-testid="tab-overview" value="overview" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">
              Overview
            </TabsTrigger>
            <TabsTrigger data-testid="tab-documents" value="documents" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">
              Documents ({documents.length})
            </TabsTrigger>
            <TabsTrigger data-testid="tab-risk" value="risk" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">
              Risk Report
            </TabsTrigger>
            <TabsTrigger data-testid="tab-govt" value="govt" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">
              Government Records
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview">
            <div className="grid lg:grid-cols-3 gap-6">
              <div className={`${getCardGlowClass(property?.risk_status)} lg:col-span-2`}>
                <h2 className="text-lg font-semibold text-white mb-4">Property Details</h2>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-4">
                    <div>
                      <p className="text-xs text-slate-500 uppercase tracking-wider">Survey Number</p>
                      <p className="font-mono font-medium text-white">{property?.survey_no}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 uppercase tracking-wider">Khata Number</p>
                      <p className="font-mono font-medium text-white">{property?.khata_no || 'Not provided'}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 uppercase tracking-wider">State</p>
                      <p className="font-medium text-white">{property?.state}</p>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <p className="text-xs text-slate-500 uppercase tracking-wider">District</p>
                      <p className="font-medium text-white">{property?.district}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 uppercase tracking-wider">Taluk</p>
                      <p className="font-medium text-white">{property?.taluk || 'Not provided'}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 uppercase tracking-wider">Village</p>
                      <p className="font-medium text-white">{property?.village || 'Not provided'}</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-6">
                <div className="glass-card-blue">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-lg bg-cyan-500/20 flex items-center justify-center">
                      <FileText className="h-5 w-5 text-cyan-400" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold font-mono text-white">{documents.length}</p>
                      <p className="text-xs text-slate-400">Documents Uploaded</p>
                    </div>
                  </div>
                </div>

                <div className={report ? 'glass-card-green' : 'glass-card-orange'}>
                  <div className="flex items-center gap-3">
                    <div className={`h-10 w-10 rounded-lg flex items-center justify-center ${
                      report ? 'bg-emerald-500/20' : 'bg-amber-500/20'
                    }`}>
                      {report ? (
                        <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                      ) : (
                        <Clock className="h-5 w-5 text-amber-400" />
                      )}
                    </div>
                    <div>
                      <p className="font-medium text-white">{report ? 'Analysis Complete' : 'Pending Analysis'}</p>
                      <p className="text-xs text-slate-400">
                        {report ? 'Report generated' : 'Click "Run AI Analysis"'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>

          {/* Documents Tab */}
          <TabsContent value="documents">
            <div className="glass-card">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-white">Uploaded Documents</h2>
                <Link to="/upload">
                  <Button className="btn-secondary" size="sm">Add More</Button>
                </Link>
              </div>
              
              {documents.length > 0 ? (
                <div className="space-y-4">
                  {documents.map((doc) => (
                    <div key={doc.document_id} className="p-4 bg-slate-800/50 rounded-lg border border-slate-700">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <FileText className="h-5 w-5 text-cyan-400" />
                          <div>
                            <p className="font-medium text-white">{doc.filename}</p>
                            <p className="text-xs text-slate-500 capitalize">
                              {doc.doc_type.replace(/_/g, ' ')}
                            </p>
                          </div>
                        </div>
                        <Badge className="badge-risk-low">
                          <CheckCircle2 className="h-3 w-3 mr-1" />
                          Processed
                        </Badge>
                      </div>
                      
                      {doc.ocr_text && (
                        <div className="mt-3">
                          <p className="text-xs text-slate-500 mb-2">OCR Extracted Text (Preview)</p>
                          <div className="bg-slate-900/50 p-3 rounded-lg text-xs font-mono text-slate-400 max-h-32 overflow-auto">
                            {doc.ocr_text.substring(0, 500)}
                            {doc.ocr_text.length > 500 && '...'}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <FileText className="h-12 w-12 text-slate-600 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-white mb-2">No documents uploaded</h3>
                  <p className="text-sm text-slate-400 mb-4">
                    Upload property documents for AI analysis
                  </p>
                  <Link to="/upload">
                    <Button className="btn-primary">Upload Documents</Button>
                  </Link>
                </div>
              )}
            </div>
          </TabsContent>

          {/* Risk Report Tab */}
          <TabsContent value="risk">
            {report ? (
              <div className="space-y-6">
                {/* Risk Score Card */}
                <div className={getCardGlowClass(report.risk_status)}>
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-white mb-2">Overall Risk Assessment</h3>
                      <p className="text-slate-400 max-w-2xl">
                        {report.executive_summary}
                      </p>
                      
                      {/* Progress Bar */}
                      <div className="mt-6">
                        <div className="flex justify-between text-xs text-slate-500 mb-2">
                          <span>High Risk</span>
                          <span>Low Risk</span>
                        </div>
                        <div className="h-3 bg-slate-700 rounded-full overflow-hidden">
                          <div 
                            className={`h-full rounded-full transition-all duration-1000 ${
                              report.risk_score >= 75 ? 'bg-emerald-500 shadow-lg shadow-emerald-500/30' :
                              report.risk_score >= 50 ? 'bg-amber-500 shadow-lg shadow-amber-500/30' : 
                              'bg-red-500 shadow-lg shadow-red-500/30'
                            }`}
                            style={{ width: `${report.risk_score}%` }}
                          />
                        </div>
                      </div>
                      
                      {/* Recommendation */}
                      <div className="mt-6 p-4 bg-slate-800/50 rounded-lg">
                        <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Legal Recommendation</p>
                        <p className={`text-lg font-semibold ${
                          report.legal_recommendation === 'SAFE_TO_BUY' ? 'text-emerald-400' :
                          report.legal_recommendation === 'BUY_WITH_CAUTION' ? 'text-amber-400' : 'text-red-400'
                        }`}>
                          {report.legal_recommendation.replace(/_/g, ' ')}
                        </p>
                      </div>
                    </div>
                    <div className="ml-8">
                      <RiskMeter score={report.risk_score} size={180} />
                    </div>
                  </div>
                </div>

                {/* Flags Grid */}
                <div className="grid md:grid-cols-3 gap-6">
                  {/* Red Flags */}
                  <div className="glass-card-red">
                    <h3 className="text-red-400 flex items-center gap-2 font-semibold mb-4">
                      <XCircle className="h-5 w-5" />
                      Red Flags ({report.red_flags?.length || 0})
                    </h3>
                    <p className="text-xs text-slate-500 mb-4">Critical issues requiring attention</p>
                    {report.red_flags?.length > 0 ? (
                      <div className="space-y-3">
                        {report.red_flags.map((flag, index) => (
                          <div key={index} className="p-3 bg-red-500/10 rounded-lg border border-red-500/20">
                            <p className="font-medium text-sm text-red-300">{flag.issue}</p>
                            <p className="text-xs text-red-400/70 mt-1">{flag.details}</p>
                            <Badge className="mt-2 badge-risk-high">{flag.severity}</Badge>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-slate-500">No critical issues found</p>
                    )}
                  </div>

                  {/* Yellow Flags */}
                  <div className="glass-card-orange">
                    <h3 className="text-amber-400 flex items-center gap-2 font-semibold mb-4">
                      <AlertTriangle className="h-5 w-5" />
                      Yellow Flags ({report.yellow_flags?.length || 0})
                    </h3>
                    <p className="text-xs text-slate-500 mb-4">Issues requiring caution</p>
                    {report.yellow_flags?.length > 0 ? (
                      <div className="space-y-3">
                        {report.yellow_flags.map((flag, index) => (
                          <div key={index} className="p-3 bg-amber-500/10 rounded-lg border border-amber-500/20">
                            <p className="font-medium text-sm text-amber-300">{flag.issue}</p>
                            <p className="text-xs text-amber-400/70 mt-1">{flag.details}</p>
                            <Badge className="mt-2 badge-risk-medium">{flag.severity}</Badge>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-slate-500">No warnings found</p>
                    )}
                  </div>

                  {/* Green Flags */}
                  <div className="glass-card-green">
                    <h3 className="text-emerald-400 flex items-center gap-2 font-semibold mb-4">
                      <CheckCircle2 className="h-5 w-5" />
                      Green Flags ({report.green_flags?.length || 0})
                    </h3>
                    <p className="text-xs text-slate-500 mb-4">Positive indicators</p>
                    {report.green_flags?.length > 0 ? (
                      <div className="space-y-3">
                        {report.green_flags.map((flag, index) => (
                          <div key={index} className="p-3 bg-emerald-500/10 rounded-lg border border-emerald-500/20">
                            <p className="font-medium text-sm text-emerald-300">{flag.indicator}</p>
                            <p className="text-xs text-emerald-400/70 mt-1">{flag.details}</p>
                            <Badge className="mt-2 badge-risk-low">{flag.confidence}</Badge>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-slate-500">Upload more documents for verification</p>
                    )}
                  </div>
                </div>

                {/* Title Chain */}
                {report.title_chain?.length > 0 && (
                  <div className="glass-card">
                    <h2 className="text-lg font-semibold text-white mb-4">Title Chain History</h2>
                    <p className="text-sm text-slate-500 mb-6">Ownership transfer timeline</p>
                    <div className="relative">
                      <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gradient-to-b from-cyan-500 via-cyan-500/50 to-transparent" />
                      <div className="space-y-6">
                        {report.title_chain.map((entry, index) => (
                          <div key={index} className="relative pl-10">
                            <div className="absolute left-2 top-1 h-4 w-4 rounded-full bg-cyan-500 border-2 border-slate-900 shadow-lg shadow-cyan-500/30" />
                            <div className="p-4 bg-slate-800/50 rounded-lg border border-slate-700">
                              <div className="flex items-center gap-2 mb-2">
                                <User className="h-4 w-4 text-cyan-400" />
                                <p className="font-medium text-white">{entry.owner}</p>
                              </div>
                              <div className="flex items-center gap-4 text-xs text-slate-500">
                                <span className="flex items-center gap-1">
                                  <Calendar className="h-3 w-3" />
                                  {entry.from_date} - {entry.to_date}
                                </span>
                                <Badge variant="outline" className="border-slate-600 text-slate-400">
                                  {entry.transfer_type}
                                </Badge>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="glass-card text-center py-12">
                <Scale className="h-12 w-12 text-slate-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">No Risk Report Yet</h3>
                <p className="text-slate-400 mb-6 max-w-md mx-auto">
                  Run AI analysis to generate a comprehensive risk assessment report for this property.
                </p>
                <Button 
                  data-testid="generate-report-btn"
                  onClick={runAnalysis} 
                  disabled={analyzing}
                  className="btn-primary"
                >
                  {analyzing ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4 mr-2" />
                      Generate Risk Report
                    </>
                  )}
                </Button>
              </div>
            )}
          </TabsContent>

          {/* Government Records Tab */}
          <TabsContent value="govt">
            <div className="glass-card">
              <h2 className="text-lg font-semibold text-white mb-2">Government Land Records</h2>
              <p className="text-sm text-slate-500 mb-6">
                Data from {govtRecords?.source || 'government land record portals'}
              </p>
              
              {govtRecords ? (
                <div className="space-y-6">
                  <div className="p-4 bg-amber-500/10 border border-amber-500/30 rounded-lg">
                    <p className="text-sm text-amber-400">
                      <AlertTriangle className="h-4 w-4 inline mr-2" />
                      {govtRecords.disclaimer}
                    </p>
                  </div>
                  
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div>
                        <p className="text-xs text-slate-500 uppercase tracking-wider">Owner Name</p>
                        <p className="font-medium text-white">{govtRecords.owner_name}</p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-500 uppercase tracking-wider">Father's Name</p>
                        <p className="font-medium text-white">{govtRecords.father_name || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-500 uppercase tracking-wider">Khata Number</p>
                        <p className="font-mono text-white">{govtRecords.khata_no}</p>
                      </div>
                    </div>
                    <div className="space-y-4">
                      <div>
                        <p className="text-xs text-slate-500 uppercase tracking-wider">Extent</p>
                        <p className="font-medium text-white">{govtRecords.extent}</p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-500 uppercase tracking-wider">Land Type</p>
                        <p className="font-medium text-white">{govtRecords.land_type}</p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-500 uppercase tracking-wider">CERSAI Status</p>
                        <p className="font-medium text-emerald-400">{govtRecords.cersai_check}</p>
                      </div>
                    </div>
                  </div>
                  
                  {govtRecords.mutation_records?.length > 0 && (
                    <div>
                      <h4 className="font-medium text-white mb-3">Mutation Records</h4>
                      <div className="space-y-2">
                        {govtRecords.mutation_records.map((mut, index) => (
                          <div key={index} className="p-3 bg-slate-800/50 rounded-lg flex items-center justify-between border border-slate-700">
                            <div>
                              <p className="text-sm font-medium text-white">{mut.mutation_no}</p>
                              <p className="text-xs text-slate-500">
                                {mut.from_owner} → {mut.to_owner}
                              </p>
                            </div>
                            <div className="text-right">
                              <p className="text-xs text-slate-500">{mut.date}</p>
                              <Badge variant="outline" className="border-slate-600 text-slate-400">{mut.type}</Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Government Documents Available for Download */}
                  <div>
                    <h4 className="font-medium text-white mb-3">Government Documents</h4>
                    <p className="text-xs text-slate-500 mb-3">Documents available from government portals (downloadable when live API integration is enabled)</p>
                    <div className="grid md:grid-cols-2 gap-3">
                      {[
                        { name: "RTC / Pahani Extract", source: govtRecords?.source || "Land Records Portal" },
                        { name: "Encumbrance Certificate (EC)", source: "Sub-Registrar Office" },
                        { name: "Khata Certificate", source: "BBMP / Municipal Records" },
                        { name: "Mutation Register Extract", source: govtRecords?.source || "Taluk Office" },
                        { name: "Survey Sketch / Map", source: "Survey Department" },
                        { name: "CERSAI Report", source: "CERSAI Portal" }
                      ].map((doc, i) => (
                        <div key={i} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                          <div className="flex items-center gap-2">
                            <FileText className="h-4 w-4 text-cyan-400" />
                            <div>
                              <p className="text-sm text-white">{doc.name}</p>
                              <p className="text-xs text-slate-500">{doc.source}</p>
                            </div>
                          </div>
                          <Button variant="ghost" size="sm" className="text-slate-500 hover:text-cyan-400" disabled>
                            <Download className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                    <p className="text-xs text-amber-400 mt-3">
                      <AlertTriangle className="h-3 w-3 inline mr-1" />
                      Live download requires government API integration (coming soon)
                    </p>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <Building2 className="h-12 w-12 text-slate-600 mx-auto mb-4" />
                  <p className="text-slate-400">Government records not available</p>
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </main>

      <FloatingActionButton to="/upload" />
    </div>
  );
};

export default PropertyDetail;
