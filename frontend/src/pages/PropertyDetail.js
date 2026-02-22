import React, { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Skeleton } from '../components/ui/skeleton';
import { Progress } from '../components/ui/progress';
import { 
  Shield, 
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
  Clock
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
      
      // Try to fetch existing report
      try {
        const reportRes = await axios.get(`${API}/reports/${propertyId}`, { withCredentials: true });
        setReport(reportRes.data);
      } catch (e) {
        // No report yet
      }
      
      // Fetch mock government records
      if (propRes.data.survey_no) {
        const govtRes = await axios.get(
          `${API}/government-records/${propRes.data.survey_no}?state=${propRes.data.state}`,
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

  const getRiskColor = (score) => {
    if (score >= 75) return 'text-emerald-600';
    if (score >= 50) return 'text-amber-600';
    return 'text-red-600';
  };

  const getRiskBgColor = (score) => {
    if (score >= 75) return 'bg-emerald-100';
    if (score >= 50) return 'bg-amber-100';
    return 'bg-red-100';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50">
        <nav className="glass-header sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center h-16">
              <Skeleton className="h-8 w-8 rounded-sm mr-2" />
              <Skeleton className="h-6 w-40" />
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Skeleton className="h-8 w-64 mb-4" />
          <div className="grid lg:grid-cols-3 gap-6">
            <Skeleton className="h-48" />
            <Skeleton className="h-48" />
            <Skeleton className="h-48" />
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Navigation */}
      <nav className="glass-header sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-4">
              <Link to="/dashboard" className="flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors">
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <Link to="/" className="flex items-center gap-2">
                <Shield className="h-8 w-8 text-primary" />
                <span className="text-xl font-semibold text-primary" style={{ fontFamily: 'Playfair Display' }}>
                  PropertyCheck AI
                </span>
              </Link>
            </div>
            
            <div className="flex items-center gap-3">
              {report && (
                <Button 
                  data-testid="download-report-btn"
                  variant="outline" 
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
                    <Scale className="h-4 w-4 mr-2" />
                    Run AI Analysis
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-primary" style={{ fontFamily: 'Playfair Display' }}>
                Survey No: {property?.survey_no}
              </h1>
              <p className="text-muted-foreground mt-1 flex items-center gap-2">
                <MapPin className="h-4 w-4" />
                {property?.district}, {property?.state}
                {property?.taluk && ` • ${property.taluk}`}
              </p>
            </div>
            
            {/* Risk Score Display */}
            {property?.risk_score && (
              <div className={`text-center p-4 rounded-sm ${getRiskBgColor(property.risk_score)}`}>
                <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Risk Score</p>
                <p className={`text-4xl font-bold font-mono ${getRiskColor(property.risk_score)}`}>
                  {property.risk_score}
                </p>
                <p className="text-xs text-muted-foreground">/100</p>
              </div>
            )}
          </div>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList>
            <TabsTrigger data-testid="tab-overview" value="overview">Overview</TabsTrigger>
            <TabsTrigger data-testid="tab-documents" value="documents">Documents ({documents.length})</TabsTrigger>
            <TabsTrigger data-testid="tab-risk" value="risk">Risk Report</TabsTrigger>
            <TabsTrigger data-testid="tab-govt" value="govt">Government Records</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview">
            <div className="grid lg:grid-cols-3 gap-6">
              {/* Property Details */}
              <Card className="card-base lg:col-span-2">
                <CardHeader>
                  <CardTitle>Property Details</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="space-y-4">
                      <div>
                        <p className="text-xs text-muted-foreground uppercase tracking-wider">Survey Number</p>
                        <p className="font-mono font-medium">{property?.survey_no}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground uppercase tracking-wider">Khata Number</p>
                        <p className="font-mono font-medium">{property?.khata_no || 'Not provided'}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground uppercase tracking-wider">State</p>
                        <p className="font-medium">{property?.state}</p>
                      </div>
                    </div>
                    <div className="space-y-4">
                      <div>
                        <p className="text-xs text-muted-foreground uppercase tracking-wider">District</p>
                        <p className="font-medium">{property?.district}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground uppercase tracking-wider">Taluk</p>
                        <p className="font-medium">{property?.taluk || 'Not provided'}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground uppercase tracking-wider">Village</p>
                        <p className="font-medium">{property?.village || 'Not provided'}</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Quick Stats */}
              <div className="space-y-6">
                <Card className="card-base">
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-sm bg-accent/10 flex items-center justify-center">
                        <FileText className="h-5 w-5 text-accent" />
                      </div>
                      <div>
                        <p className="text-2xl font-bold font-mono">{documents.length}</p>
                        <p className="text-xs text-muted-foreground">Documents Uploaded</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="card-base">
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-3">
                      <div className={`h-10 w-10 rounded-sm flex items-center justify-center ${
                        report ? 'bg-emerald-100' : 'bg-amber-100'
                      }`}>
                        {report ? (
                          <CheckCircle2 className="h-5 w-5 text-emerald-600" />
                        ) : (
                          <Clock className="h-5 w-5 text-amber-600" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium">{report ? 'Analysis Complete' : 'Pending Analysis'}</p>
                        <p className="text-xs text-muted-foreground">
                          {report ? 'Report generated' : 'Click "Run AI Analysis"'}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* Documents Tab */}
          <TabsContent value="documents">
            <Card className="card-base">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Uploaded Documents</CardTitle>
                <Link to="/upload">
                  <Button variant="outline" size="sm">Add More</Button>
                </Link>
              </CardHeader>
              <CardContent>
                {documents.length > 0 ? (
                  <div className="space-y-4">
                    {documents.map((doc) => (
                      <div 
                        key={doc.document_id}
                        className="p-4 border rounded-sm"
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <FileText className="h-5 w-5 text-muted-foreground" />
                            <div>
                              <p className="font-medium">{doc.filename}</p>
                              <p className="text-xs text-muted-foreground capitalize">
                                {doc.doc_type.replace(/_/g, ' ')}
                              </p>
                            </div>
                          </div>
                          <Badge variant="outline">
                            <CheckCircle2 className="h-3 w-3 mr-1" />
                            Processed
                          </Badge>
                        </div>
                        
                        {doc.ocr_text && (
                          <div className="mt-3">
                            <p className="text-xs text-muted-foreground mb-2">OCR Extracted Text (Preview)</p>
                            <div className="bg-slate-100 p-3 rounded-sm text-xs font-mono max-h-32 overflow-auto">
                              {doc.ocr_text.substring(0, 500)}
                              {doc.ocr_text.length > 500 && '...'}
                            </div>
                          </div>
                        )}
                        
                        {doc.extracted_data && Object.keys(doc.extracted_data).length > 0 && (
                          <div className="mt-3">
                            <p className="text-xs text-muted-foreground mb-2">AI Extracted Fields</p>
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                              {Object.entries(doc.extracted_data).slice(0, 6).map(([key, value]) => (
                                <div key={key} className="bg-slate-50 p-2 rounded-sm">
                                  <p className="text-xs text-muted-foreground capitalize">{key.replace(/_/g, ' ')}</p>
                                  <p className="text-sm font-medium truncate">{String(value) || 'N/A'}</p>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-primary mb-2">No documents uploaded</h3>
                    <p className="text-sm text-muted-foreground mb-4">
                      Upload property documents for AI analysis
                    </p>
                    <Link to="/upload">
                      <Button className="btn-primary">Upload Documents</Button>
                    </Link>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Risk Report Tab */}
          <TabsContent value="risk">
            {report ? (
              <div className="space-y-6">
                {/* Risk Score Card */}
                <Card className="card-base">
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-xl font-semibold mb-2">Overall Risk Assessment</h3>
                        <p className="text-muted-foreground max-w-2xl">
                          {report.executive_summary}
                        </p>
                      </div>
                      <div className={`text-center p-6 rounded-sm ${getRiskBgColor(report.risk_score)}`}>
                        <p className={`text-5xl font-bold font-mono ${getRiskColor(report.risk_score)}`}>
                          {report.risk_score}
                        </p>
                        <p className="text-sm text-muted-foreground">/100</p>
                        <Badge className={`mt-2 ${
                          report.risk_status === 'GREEN' ? 'badge-risk-low' :
                          report.risk_status === 'YELLOW' ? 'badge-risk-medium' : 'badge-risk-high'
                        }`}>
                          {report.risk_status}
                        </Badge>
                      </div>
                    </div>
                    
                    {/* Progress Bar */}
                    <div className="mt-6">
                      <div className="flex justify-between text-xs text-muted-foreground mb-2">
                        <span>High Risk</span>
                        <span>Low Risk</span>
                      </div>
                      <Progress value={report.risk_score} className="h-3" />
                    </div>
                    
                    {/* Recommendation */}
                    <div className="mt-6 p-4 bg-slate-50 rounded-sm">
                      <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Legal Recommendation</p>
                      <p className={`text-lg font-semibold ${
                        report.legal_recommendation === 'SAFE_TO_BUY' ? 'text-emerald-600' :
                        report.legal_recommendation === 'BUY_WITH_CAUTION' ? 'text-amber-600' : 'text-red-600'
                      }`}>
                        {report.legal_recommendation.replace(/_/g, ' ')}
                      </p>
                    </div>
                  </CardContent>
                </Card>

                {/* Flags Grid */}
                <div className="grid md:grid-cols-3 gap-6">
                  {/* Red Flags */}
                  <Card className="card-base border-red-200">
                    <CardHeader>
                      <CardTitle className="text-red-600 flex items-center gap-2">
                        <XCircle className="h-5 w-5" />
                        Red Flags ({report.red_flags?.length || 0})
                      </CardTitle>
                      <CardDescription>Critical issues requiring attention</CardDescription>
                    </CardHeader>
                    <CardContent>
                      {report.red_flags?.length > 0 ? (
                        <div className="space-y-3">
                          {report.red_flags.map((flag, index) => (
                            <div key={index} className="p-3 bg-red-50 rounded-sm border border-red-100">
                              <p className="font-medium text-sm text-red-800">{flag.issue}</p>
                              <p className="text-xs text-red-600 mt-1">{flag.details}</p>
                              <Badge variant="outline" className="mt-2 text-xs border-red-200 text-red-600">
                                {flag.severity}
                              </Badge>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-muted-foreground">No critical issues found</p>
                      )}
                    </CardContent>
                  </Card>

                  {/* Yellow Flags */}
                  <Card className="card-base border-amber-200">
                    <CardHeader>
                      <CardTitle className="text-amber-600 flex items-center gap-2">
                        <AlertTriangle className="h-5 w-5" />
                        Yellow Flags ({report.yellow_flags?.length || 0})
                      </CardTitle>
                      <CardDescription>Issues requiring caution</CardDescription>
                    </CardHeader>
                    <CardContent>
                      {report.yellow_flags?.length > 0 ? (
                        <div className="space-y-3">
                          {report.yellow_flags.map((flag, index) => (
                            <div key={index} className="p-3 bg-amber-50 rounded-sm border border-amber-100">
                              <p className="font-medium text-sm text-amber-800">{flag.issue}</p>
                              <p className="text-xs text-amber-600 mt-1">{flag.details}</p>
                              <Badge variant="outline" className="mt-2 text-xs border-amber-200 text-amber-600">
                                {flag.severity}
                              </Badge>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-muted-foreground">No warnings found</p>
                      )}
                    </CardContent>
                  </Card>

                  {/* Green Flags */}
                  <Card className="card-base border-emerald-200">
                    <CardHeader>
                      <CardTitle className="text-emerald-600 flex items-center gap-2">
                        <CheckCircle2 className="h-5 w-5" />
                        Green Flags ({report.green_flags?.length || 0})
                      </CardTitle>
                      <CardDescription>Positive indicators</CardDescription>
                    </CardHeader>
                    <CardContent>
                      {report.green_flags?.length > 0 ? (
                        <div className="space-y-3">
                          {report.green_flags.map((flag, index) => (
                            <div key={index} className="p-3 bg-emerald-50 rounded-sm border border-emerald-100">
                              <p className="font-medium text-sm text-emerald-800">{flag.indicator}</p>
                              <p className="text-xs text-emerald-600 mt-1">{flag.details}</p>
                              <Badge variant="outline" className="mt-2 text-xs border-emerald-200 text-emerald-600">
                                {flag.confidence}
                              </Badge>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-muted-foreground">Upload more documents for verification</p>
                      )}
                    </CardContent>
                  </Card>
                </div>

                {/* Title Chain */}
                {report.title_chain?.length > 0 && (
                  <Card className="card-base">
                    <CardHeader>
                      <CardTitle>Title Chain History</CardTitle>
                      <CardDescription>Ownership transfer timeline</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="relative">
                        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-slate-200" />
                        <div className="space-y-6">
                          {report.title_chain.map((entry, index) => (
                            <div key={index} className="relative pl-10">
                              <div className="absolute left-2 top-1 h-4 w-4 rounded-full bg-accent border-2 border-white shadow" />
                              <div className="p-4 bg-slate-50 rounded-sm">
                                <div className="flex items-center gap-2 mb-2">
                                  <User className="h-4 w-4 text-muted-foreground" />
                                  <p className="font-medium">{entry.owner}</p>
                                </div>
                                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                                  <span className="flex items-center gap-1">
                                    <Calendar className="h-3 w-3" />
                                    {entry.from_date} - {entry.to_date}
                                  </span>
                                  <Badge variant="outline" className="text-xs">
                                    {entry.transfer_type}
                                  </Badge>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            ) : (
              <Card className="card-base">
                <CardContent className="py-12 text-center">
                  <Scale className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-primary mb-2">No Risk Report Yet</h3>
                  <p className="text-muted-foreground mb-6 max-w-md mx-auto">
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
                        <Scale className="h-4 w-4 mr-2" />
                        Generate Risk Report
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Government Records Tab */}
          <TabsContent value="govt">
            <Card className="card-base">
              <CardHeader>
                <CardTitle>Government Land Records</CardTitle>
                <CardDescription>
                  Data from {govtRecords?.source || 'government land record portals'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {govtRecords ? (
                  <div className="space-y-6">
                    <div className="p-4 bg-amber-50 border border-amber-200 rounded-sm">
                      <p className="text-sm text-amber-800">
                        <AlertTriangle className="h-4 w-4 inline mr-2" />
                        {govtRecords.disclaimer}
                      </p>
                    </div>
                    
                    <div className="grid md:grid-cols-2 gap-6">
                      <div className="space-y-4">
                        <div>
                          <p className="text-xs text-muted-foreground uppercase tracking-wider">Owner Name</p>
                          <p className="font-medium">{govtRecords.owner_name}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground uppercase tracking-wider">Father's Name</p>
                          <p className="font-medium">{govtRecords.father_name || 'N/A'}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground uppercase tracking-wider">Khata Number</p>
                          <p className="font-mono">{govtRecords.khata_no}</p>
                        </div>
                      </div>
                      <div className="space-y-4">
                        <div>
                          <p className="text-xs text-muted-foreground uppercase tracking-wider">Extent</p>
                          <p className="font-medium">{govtRecords.extent}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground uppercase tracking-wider">Land Type</p>
                          <p className="font-medium">{govtRecords.land_type}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground uppercase tracking-wider">CERSAI Status</p>
                          <p className="font-medium text-emerald-600">{govtRecords.cersai_check}</p>
                        </div>
                      </div>
                    </div>
                    
                    {/* Mutation Records */}
                    {govtRecords.mutation_records?.length > 0 && (
                      <div>
                        <h4 className="font-medium mb-3">Mutation Records</h4>
                        <div className="space-y-2">
                          {govtRecords.mutation_records.map((mut, index) => (
                            <div key={index} className="p-3 bg-slate-50 rounded-sm flex items-center justify-between">
                              <div>
                                <p className="text-sm font-medium">{mut.mutation_no}</p>
                                <p className="text-xs text-muted-foreground">
                                  {mut.from_owner} → {mut.to_owner}
                                </p>
                              </div>
                              <div className="text-right">
                                <p className="text-xs text-muted-foreground">{mut.date}</p>
                                <Badge variant="outline">{mut.type}</Badge>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <Building2 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">Government records not available</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default PropertyDetail;
