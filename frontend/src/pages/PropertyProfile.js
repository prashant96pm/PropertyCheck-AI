import React, { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import RiskMeter from '../components/RiskMeter';
import ShimmerLoader from '../components/ShimmerLoader';
import { 
  ArrowLeft, 
  FileText, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle,
  Download,
  Loader2,
  MapPin,
  Calendar,
  User,
  Building2,
  Scale,
  Clock,
  Globe,
  Map,
  FileSearch,
  History,
  Gavel,
  Landmark,
  ExternalLink
} from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PropertyProfile = () => {
  const { propertyId } = useParams();
  const navigate = useNavigate();
  
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPropertyProfile();
  }, [propertyId]);

  const fetchPropertyProfile = async () => {
    try {
      const response = await axios.get(`${API}/property/full-profile/${propertyId}`, {
        withCredentials: true
      });
      setProfile(response.data);
    } catch (error) {
      toast.error('Failed to load property profile');
      navigate('/search');
    } finally {
      setLoading(false);
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
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center">
            <ShimmerLoader className="h-8 w-48" />
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid lg:grid-cols-3 gap-6">
            <ShimmerLoader variant="card" className="lg:col-span-2" />
            <ShimmerLoader variant="risk-meter" />
          </div>
        </main>
      </div>
    );
  }

  const basic = profile?.basic_details || {};
  const riskAssessment = profile?.risk_assessment;

  return (
    <div className="min-h-screen gradient-bg">
      <div className="fixed inset-0 grid-bg opacity-30 pointer-events-none" />
      
      {/* Navigation */}
      <nav className="glass-header sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-4">
              <Link to="/search" className="text-slate-400 hover:text-white transition-colors">
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <Link to="/" className="flex items-center gap-2">
                <Building2 className="h-8 w-8 text-cyan-400" />
                <span className="text-xl font-semibold text-white" style={{ fontFamily: 'Playfair Display' }}>
                  PropertyCheck AI
                </span>
              </Link>
            </div>
            
            <Badge variant="outline" className="border-cyan-500/30 text-cyan-400">
              360° Intelligence
            </Badge>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        {/* Header with Risk Meter */}
        <div className="grid lg:grid-cols-3 gap-6 mb-8">
          <div className={`${getCardGlowClass(riskAssessment?.risk_status)} lg:col-span-2`}>
            <div className="flex items-start justify-between">
              <div>
                <Badge className="mb-4 bg-cyan-500/20 text-cyan-400 border-cyan-500/30">
                  Property 360° Profile
                </Badge>
                <h1 className="text-3xl font-bold text-white mb-2" style={{ fontFamily: 'Playfair Display' }}>
                  Survey No: <span className="text-gradient">{basic.survey_no}</span>
                </h1>
                <p className="text-slate-400 flex items-center gap-2">
                  <MapPin className="h-4 w-4" />
                  {basic.village && `${basic.village}, `}{basic.taluk && `${basic.taluk}, `}{basic.district}, {basic.state}
                </p>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                  <div>
                    <p className="text-xs text-slate-500 uppercase tracking-wider">Owner</p>
                    <p className="text-white font-medium">{basic.owner_name || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 uppercase tracking-wider">Khata No</p>
                    <p className="text-white font-mono">{basic.khata_no || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 uppercase tracking-wider">Extent</p>
                    <p className="text-white">{basic.extent || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 uppercase tracking-wider">Land Type</p>
                    <p className="text-white">{basic.land_type || 'N/A'}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Risk Meter */}
          <div className="glass-card flex flex-col items-center justify-center">
            {riskAssessment ? (
              <>
                <p className="text-sm text-slate-400 mb-2">Risk Assessment</p>
                <RiskMeter score={riskAssessment.risk_score} size={180} />
              </>
            ) : (
              <div className="text-center">
                <Scale className="h-12 w-12 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400">Analysis Pending</p>
                <p className="text-xs text-slate-500">Run verification to get risk score</p>
              </div>
            )}
          </div>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="bg-slate-800/50 border border-slate-700 flex-wrap">
            <TabsTrigger value="overview" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">
              <Building2 className="h-4 w-4 mr-2" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="ownership" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">
              <History className="h-4 w-4 mr-2" />
              Ownership History
            </TabsTrigger>
            <TabsTrigger value="legal" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">
              <Gavel className="h-4 w-4 mr-2" />
              Legal Records
            </TabsTrigger>
            <TabsTrigger value="documents" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">
              <FileText className="h-4 w-4 mr-2" />
              Documents
            </TabsTrigger>
            <TabsTrigger value="geo" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">
              <Map className="h-4 w-4 mr-2" />
              Geo-Spatial
            </TabsTrigger>
            <TabsTrigger value="govt" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">
              <Landmark className="h-4 w-4 mr-2" />
              Govt Records
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview">
            <div className="grid lg:grid-cols-2 gap-6">
              {/* Basic Details */}
              <div className="glass-card">
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Building2 className="h-5 w-5 text-cyan-400" />
                  Property Details
                </h2>
                <div className="space-y-4">
                  {[
                    { label: 'Survey Number', value: basic.survey_no },
                    { label: 'Plot Number', value: basic.plot_no || 'N/A' },
                    { label: 'Khata Number', value: basic.khata_no || 'N/A' },
                    { label: 'Extent', value: basic.extent },
                    { label: 'Land Type', value: basic.land_type },
                    { label: 'Zoning', value: basic.zoning },
                    { label: 'Village', value: basic.village || 'N/A' },
                    { label: 'Taluk', value: basic.taluk || 'N/A' },
                    { label: 'District', value: basic.district },
                    { label: 'State', value: basic.state }
                  ].map((item, index) => (
                    <div key={index} className="flex justify-between py-2 border-b border-slate-700/50 last:border-0">
                      <span className="text-slate-400">{item.label}</span>
                      <span className="text-white font-medium">{item.value || 'N/A'}</span>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Boundaries */}
              <div className="glass-card">
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Map className="h-5 w-5 text-cyan-400" />
                  Boundaries
                </h2>
                <div className="grid grid-cols-2 gap-4">
                  {['North', 'South', 'East', 'West'].map((direction) => (
                    <div key={direction} className="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                      <p className="text-xs text-slate-500 uppercase tracking-wider">{direction}</p>
                      <p className="text-white mt-1">
                        {profile?.geo_spatial?.boundaries?.[direction.toLowerCase()] || 'Not specified'}
                      </p>
                    </div>
                  ))}
                </div>
                
                {/* Quick Stats */}
                <div className="mt-6 grid grid-cols-2 gap-4">
                  <div className="bg-emerald-500/10 p-4 rounded-lg border border-emerald-500/20">
                    <p className="text-xs text-slate-400">Documents</p>
                    <p className="text-2xl font-bold text-emerald-400">
                      {profile?.documents?.length || 0}
                    </p>
                  </div>
                  <div className="bg-cyan-500/10 p-4 rounded-lg border border-cyan-500/20">
                    <p className="text-xs text-slate-400">Ownership Changes</p>
                    <p className="text-2xl font-bold text-cyan-400">
                      {profile?.ownership_history?.length || 0}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>

          {/* Ownership History Tab */}
          <TabsContent value="ownership">
            <div className="glass-card">
              <h2 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
                <History className="h-5 w-5 text-cyan-400" />
                30+ Year Ownership History
              </h2>
              
              {profile?.ownership_history?.length > 0 ? (
                <div className="relative">
                  <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gradient-to-b from-cyan-500 via-cyan-500/50 to-transparent" />
                  <div className="space-y-6">
                    {profile.ownership_history.map((entry, index) => (
                      <div key={index} className="relative pl-10">
                        <div className="absolute left-2 top-1 h-4 w-4 rounded-full bg-cyan-500 border-2 border-slate-900 shadow-lg shadow-cyan-500/30" />
                        <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                          <div className="flex items-start justify-between">
                            <div>
                              <div className="flex items-center gap-2 mb-2">
                                <User className="h-4 w-4 text-cyan-400" />
                                <p className="font-medium text-white">{entry.owner_name}</p>
                              </div>
                              {entry.father_name && entry.father_name !== 'N/A' && (
                                <p className="text-xs text-slate-500">S/o {entry.father_name}</p>
                              )}
                            </div>
                            <Badge variant="outline" className="border-slate-600 text-slate-400">
                              {entry.transfer_type}
                            </Badge>
                          </div>
                          
                          <div className="mt-3 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                            <div>
                              <p className="text-xs text-slate-500">From</p>
                              <p className="text-slate-300">{entry.transfer_date || entry.from_date}</p>
                            </div>
                            <div>
                              <p className="text-xs text-slate-500">To</p>
                              <p className="text-slate-300">{entry.to_date || 'Present'}</p>
                            </div>
                            <div>
                              <p className="text-xs text-slate-500">Document Ref</p>
                              <p className="text-slate-300 font-mono text-xs">{entry.doc_reference || entry.doc_ref}</p>
                            </div>
                            {entry.consideration && (
                              <div>
                                <p className="text-xs text-slate-500">Consideration</p>
                                <p className="text-slate-300">{entry.consideration}</p>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <History className="h-12 w-12 text-slate-600 mx-auto mb-4" />
                  <p className="text-slate-400">No ownership history available</p>
                </div>
              )}
            </div>
          </TabsContent>

          {/* Legal Records Tab */}
          <TabsContent value="legal">
            <div className="grid lg:grid-cols-2 gap-6">
              <div className="glass-card">
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Gavel className="h-5 w-5 text-cyan-400" />
                  Legal Status
                </h2>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-emerald-500/10 rounded-lg border border-emerald-500/20">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                      <span className="text-slate-300">CERSAI Check</span>
                    </div>
                    <span className="text-emerald-400">{profile?.legal_records?.cersai_status}</span>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-emerald-500/10 rounded-lg border border-emerald-500/20">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                      <span className="text-slate-300">eCourts Check</span>
                    </div>
                    <span className="text-emerald-400">{profile?.legal_records?.ecourts_check}</span>
                  </div>
                  
                  <div className={`flex items-center justify-between p-3 rounded-lg border ${
                    profile?.legal_records?.pending_litigation 
                      ? 'bg-red-500/10 border-red-500/20' 
                      : 'bg-emerald-500/10 border-emerald-500/20'
                  }`}>
                    <div className="flex items-center gap-2">
                      {profile?.legal_records?.pending_litigation ? (
                        <XCircle className="h-5 w-5 text-red-400" />
                      ) : (
                        <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                      )}
                      <span className="text-slate-300">Pending Litigation</span>
                    </div>
                    <span className={profile?.legal_records?.pending_litigation ? 'text-red-400' : 'text-emerald-400'}>
                      {profile?.legal_records?.pending_litigation ? 'Yes' : 'No'}
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="glass-card">
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-amber-400" />
                  Encumbrances & Liens
                </h2>
                
                {profile?.legal_records?.encumbrances?.length > 0 ? (
                  <div className="space-y-3">
                    {profile.legal_records.encumbrances.map((enc, index) => (
                      <div key={index} className="p-3 bg-amber-500/10 rounded-lg border border-amber-500/20">
                        <p className="text-white">{enc.type}</p>
                        <p className="text-xs text-slate-400">{enc.details}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 bg-emerald-500/10 rounded-lg border border-emerald-500/20">
                    <CheckCircle2 className="h-8 w-8 text-emerald-400 mx-auto mb-2" />
                    <p className="text-emerald-400">No encumbrances found</p>
                    <p className="text-xs text-slate-500">Property is free from mortgages and liens</p>
                  </div>
                )}
              </div>
            </div>
          </TabsContent>

          {/* Documents Tab */}
          <TabsContent value="documents">
            <div className="grid lg:grid-cols-2 gap-6">
              {/* Uploaded Documents */}
              <div className="glass-card">
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <FileText className="h-5 w-5 text-cyan-400" />
                  Uploaded Documents
                </h2>
                
                {profile?.documents?.length > 0 ? (
                  <div className="space-y-3">
                    {profile.documents.map((doc, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                        <div className="flex items-center gap-3">
                          <FileText className="h-5 w-5 text-cyan-400" />
                          <div>
                            <p className="text-white text-sm">{doc.filename || doc.doc_type}</p>
                            <p className="text-xs text-slate-500 capitalize">{doc.doc_type?.replace(/_/g, ' ')}</p>
                          </div>
                        </div>
                        {doc.is_verified && (
                          <Badge className="badge-risk-low">Verified</Badge>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <FileText className="h-8 w-8 text-slate-600 mx-auto mb-2" />
                    <p className="text-slate-400">No documents uploaded</p>
                  </div>
                )}
              </div>
              
              {/* Registry Documents */}
              <div className="glass-card">
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Landmark className="h-5 w-5 text-cyan-400" />
                  Government Registry Documents
                </h2>
                
                <div className="space-y-3">
                  {[
                    { name: 'Encumbrance Certificate (EC)', source: 'Sub-Registrar', available: true },
                    { name: 'RTC / Pahani', source: 'Bhoomi Portal', available: true },
                    { name: 'Khata Certificate', source: 'Municipality', available: true },
                    { name: 'Cadastral Map', source: 'Survey Dept', available: true },
                    { name: 'Mutation Records', source: 'Revenue Dept', available: true }
                  ].map((doc, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                      <div>
                        <p className="text-white text-sm">{doc.name}</p>
                        <p className="text-xs text-slate-500">{doc.source}</p>
                      </div>
                      {doc.available ? (
                        <Button variant="ghost" size="sm" className="text-cyan-400 hover:text-cyan-300">
                          <ExternalLink className="h-4 w-4" />
                        </Button>
                      ) : (
                        <Badge variant="outline" className="text-slate-500">Unavailable</Badge>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </TabsContent>

          {/* Geo-Spatial Tab */}
          <TabsContent value="geo">
            <div className="grid lg:grid-cols-2 gap-6">
              <div className="glass-card">
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Globe className="h-5 w-5 text-cyan-400" />
                  Location & Coordinates
                </h2>
                
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-slate-800/50 p-4 rounded-lg">
                      <p className="text-xs text-slate-500">Latitude</p>
                      <p className="text-white font-mono">{profile?.geo_spatial?.coordinates?.latitude || 'N/A'}</p>
                    </div>
                    <div className="bg-slate-800/50 p-4 rounded-lg">
                      <p className="text-xs text-slate-500">Longitude</p>
                      <p className="text-white font-mono">{profile?.geo_spatial?.coordinates?.longitude || 'N/A'}</p>
                    </div>
                  </div>
                  
                  <div className="bg-slate-800/50 p-4 rounded-lg">
                    <p className="text-xs text-slate-500 mb-2">Zoning Classification</p>
                    <p className="text-white">{profile?.geo_spatial?.zoning_classification || 'Residential'}</p>
                  </div>
                  
                  <div className={`p-4 rounded-lg border ${
                    profile?.geo_spatial?.encroachment_detected 
                      ? 'bg-red-500/10 border-red-500/20' 
                      : 'bg-emerald-500/10 border-emerald-500/20'
                  }`}>
                    <div className="flex items-center gap-2">
                      {profile?.geo_spatial?.encroachment_detected ? (
                        <XCircle className="h-5 w-5 text-red-400" />
                      ) : (
                        <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                      )}
                      <span className={profile?.geo_spatial?.encroachment_detected ? 'text-red-400' : 'text-emerald-400'}>
                        {profile?.geo_spatial?.encroachment_detected ? 'Encroachment Detected' : 'No Encroachment Detected'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="glass-card">
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Map className="h-5 w-5 text-cyan-400" />
                  Nearby Infrastructure
                </h2>
                
                <div className="space-y-3">
                  {['roads', 'lakes', 'highways'].map((type) => (
                    <div key={type}>
                      <p className="text-xs text-slate-500 uppercase tracking-wider mb-2">{type}</p>
                      <div className="flex flex-wrap gap-2">
                        {profile?.geo_spatial?.nearby_infrastructure?.[type]?.map((item, index) => (
                          <Badge key={index} variant="outline" className="border-slate-600 text-slate-300">
                            {item}
                          </Badge>
                        )) || (
                          <span className="text-slate-500 text-sm">No data</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
                
                {/* Map Placeholder */}
                <div className="mt-6 h-48 bg-slate-800/50 rounded-lg border border-slate-700 flex items-center justify-center">
                  <div className="text-center">
                    <Map className="h-8 w-8 text-slate-600 mx-auto mb-2" />
                    <p className="text-slate-500 text-sm">Satellite Map</p>
                    <p className="text-xs text-slate-600">Integration Coming Soon</p>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>

          {/* Government Records Tab */}
          <TabsContent value="govt">
            <div className="glass-card">
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Landmark className="h-5 w-5 text-cyan-400" />
                Government Land Records
              </h2>
              <p className="text-sm text-slate-500 mb-6">
                Source: {profile?.government_records?.source}
              </p>
              
              {profile?.government_records?.disclaimer && (
                <div className="p-4 bg-amber-500/10 border border-amber-500/30 rounded-lg mb-6">
                  <p className="text-sm text-amber-400">
                    <AlertTriangle className="h-4 w-4 inline mr-2" />
                    {profile.government_records.disclaimer}
                  </p>
                </div>
              )}
              
              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <p className="text-xs text-slate-500 uppercase tracking-wider">Registered Owner</p>
                    <p className="text-white font-medium">{profile?.government_records?.owner_name}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 uppercase tracking-wider">Father's Name</p>
                    <p className="text-white">{profile?.government_records?.father_name}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 uppercase tracking-wider">Khata Number</p>
                    <p className="text-white font-mono">{profile?.government_records?.khata_no}</p>
                  </div>
                </div>
                <div className="space-y-4">
                  <div>
                    <p className="text-xs text-slate-500 uppercase tracking-wider">Extent</p>
                    <p className="text-white">{profile?.government_records?.extent}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 uppercase tracking-wider">Land Type</p>
                    <p className="text-white">{profile?.government_records?.land_type}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 uppercase tracking-wider">CERSAI Status</p>
                    <p className="text-emerald-400">{profile?.government_records?.cersai_check}</p>
                  </div>
                </div>
              </div>
              
              {/* Mutation Records */}
              {profile?.government_records?.mutation_records?.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-white font-medium mb-3">Mutation Records</h3>
                  <div className="space-y-2">
                    {profile.government_records.mutation_records.map((mut, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                        <div>
                          <p className="text-white text-sm">{mut.mutation_no}</p>
                          <p className="text-xs text-slate-500">{mut.from_owner} → {mut.to_owner}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-xs text-slate-500">{mut.date}</p>
                          <Badge variant="outline" className="text-slate-400">{mut.type}</Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default PropertyProfile;
