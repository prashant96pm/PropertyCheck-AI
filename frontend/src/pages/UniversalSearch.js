import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import ShimmerLoader from '../components/ShimmerLoader';
import RiskMeter from '../components/RiskMeter';
import { 
  Search, 
  User, 
  MapPin, 
  FileText,
  Building2,
  Loader2,
  ArrowRight,
  Sparkles,
  Filter,
  ChevronRight,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Globe,
  Zap
} from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const INDIAN_STATES = [
  "Karnataka", "Maharashtra", "Telangana", "Tamil Nadu", "Gujarat",
  "Rajasthan", "Uttar Pradesh", "Madhya Pradesh", "Andhra Pradesh", "Kerala"
];

const UniversalSearch = () => {
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  
  const [searchMode, setSearchMode] = useState('smart'); // smart, advanced
  const [smartQuery, setSmartQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [totalResults, setTotalResults] = useState(0);
  const [searchType, setSearchType] = useState('');
  
  // Advanced search fields
  const [advancedFilters, setAdvancedFilters] = useState({
    owner_name: '',
    survey_no: '',
    plot_no: '',
    khata_no: '',
    registration_no: '',
    district: '',
    state: '',
    village: '',
    taluk: '',
    land_type: ''
  });

  useEffect(() => {
    const q = searchParams.get('q');
    if (q) {
      setSmartQuery(q);
      setSearchMode('smart');
      // Auto-trigger search with query param
      performSmartSearch(q);
    } else {
      loadSampleProperties();
    }
  }, []);

  const performSmartSearch = async (query) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/property/ai-smart-search`, {
        query
      }, { withCredentials: true });
      
      setResults(response.data.results || []);
      setTotalResults(response.data.total || 0);
      setSearchType('ai_smart_search');
      
      if (response.data.note) {
        toast.info(response.data.note);
      } else if (response.data.results?.length === 0) {
        toast.info('No properties found matching your query');
      } else {
        toast.success(`Found ${response.data.total} properties`);
      }
    } catch (error) {
      // On any error, fall back to showing sample registry
      toast.info('Showing sample properties for review');
      await loadSampleProperties();
    } finally {
      setLoading(false);
    }
  };

  const loadSampleProperties = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/property/search`, {
        withCredentials: true
      });
      setResults(response.data.results || []);
      setTotalResults(response.data.total || 0);
      setSearchType(response.data.search_type || 'sample');
    } catch (error) {
      console.error('Failed to load properties:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSmartSearch = async () => {
    if (!smartQuery.trim()) {
      toast.error('Please enter a search query');
      return;
    }
    await performSmartSearch(smartQuery);
  };

  const handleAdvancedSearch = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      Object.entries(advancedFilters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
      
      const response = await axios.get(`${API}/property/search?${params.toString()}`, {
        withCredentials: true
      });
      
      setResults(response.data.results || []);
      setTotalResults(response.data.total || 0);
      setSearchType('multi_parameter');
      
      if (response.data.results?.length === 0) {
        toast.info('No properties found with these filters');
      } else {
        toast.success(`Found ${response.data.total} properties`);
      }
    } catch (error) {
      toast.error('Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getRiskBadge = (status) => {
    if (!status) return <Badge className="badge-risk-medium">PENDING</Badge>;
    if (status === 'GREEN') return <Badge className="badge-risk-low">VERIFIED</Badge>;
    if (status === 'YELLOW') return <Badge className="badge-risk-medium">CAUTION</Badge>;
    return <Badge className="badge-risk-high">HIGH RISK</Badge>;
  };

  const getCardGlowClass = (status) => {
    if (!status) return 'glass-card';
    if (status === 'GREEN') return 'glass-card-green';
    if (status === 'YELLOW') return 'glass-card-orange';
    return 'glass-card-red';
  };

  return (
    <div className="min-h-screen gradient-bg">
      <div className="fixed inset-0 grid-bg opacity-30 pointer-events-none" />
      
      {/* Navigation */}
      <nav className="glass-header sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="flex items-center gap-2">
              <Building2 className="h-8 w-8 text-cyan-400" />
              <span className="text-xl font-semibold text-white" style={{ fontFamily: 'Playfair Display' }}>
                PropertyCheck AI
              </span>
            </Link>
            
            <div className="flex items-center gap-4">
              {isAuthenticated ? (
                <Link to="/dashboard">
                  <Button className="btn-secondary">Dashboard</Button>
                </Link>
              ) : (
                <Link to="/login">
                  <Button className="btn-primary">Sign In</Button>
                </Link>
              )}
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4" style={{ fontFamily: 'Playfair Display' }}>
            Universal <span className="text-gradient">Property Search</span>
          </h1>
          <p className="text-lg text-slate-400 max-w-2xl mx-auto">
            Search any property across India using owner name, survey number, plot number, or natural language queries
          </p>
        </div>

        {/* Search Modes */}
        <div className="glass-card-blue mb-8">
          <Tabs value={searchMode} onValueChange={setSearchMode} className="w-full">
            <TabsList className="bg-slate-800/50 border border-slate-700 mb-6">
              <TabsTrigger 
                value="smart" 
                className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400"
              >
                <Sparkles className="h-4 w-4 mr-2" />
                Smart Search
              </TabsTrigger>
              <TabsTrigger 
                value="advanced"
                className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400"
              >
                <Filter className="h-4 w-4 mr-2" />
                Advanced Filters
              </TabsTrigger>
            </TabsList>

            {/* Smart Search */}
            <TabsContent value="smart">
              <div className="space-y-4">
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
                  <Input
                    data-testid="smart-search-input"
                    placeholder="e.g., 'Land owned by Ramesh in Bangalore' or 'Survey 123/4 Karnataka'"
                    value={smartQuery}
                    onChange={(e) => setSmartQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSmartSearch()}
                    className="pl-12 py-6 text-lg input-glass"
                  />
                </div>
                
                <div className="flex flex-wrap gap-2 text-xs text-slate-500">
                  <span>Try:</span>
                  <button 
                    onClick={() => setSmartQuery('Properties in Bangalore Urban')}
                    className="text-cyan-400 hover:underline"
                  >
                    "Properties in Bangalore Urban"
                  </button>
                  <span>•</span>
                  <button 
                    onClick={() => setSmartQuery('Survey 123 Karnataka')}
                    className="text-cyan-400 hover:underline"
                  >
                    "Survey 123 Karnataka"
                  </button>
                  <span>•</span>
                  <button 
                    onClick={() => setSmartQuery('Agricultural land in Telangana')}
                    className="text-cyan-400 hover:underline"
                  >
                    "Agricultural land in Telangana"
                  </button>
                </div>
                
                <Button 
                  data-testid="smart-search-btn"
                  onClick={handleSmartSearch} 
                  disabled={loading}
                  className="btn-primary w-full md:w-auto"
                >
                  {loading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Searching...
                    </>
                  ) : (
                    <>
                      <Zap className="h-4 w-4 mr-2" />
                      Search with AI
                    </>
                  )}
                </Button>
              </div>
            </TabsContent>

            {/* Advanced Search */}
            <TabsContent value="advanced">
              <div className="grid md:grid-cols-3 gap-4 mb-6">
                <div className="space-y-2">
                  <Label className="text-slate-300">Owner Name</Label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                    <Input
                      data-testid="owner-name-input"
                      placeholder="e.g., Ramesh Kumar"
                      value={advancedFilters.owner_name}
                      onChange={(e) => setAdvancedFilters(prev => ({ ...prev, owner_name: e.target.value }))}
                      className="pl-10 input-glass"
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label className="text-slate-300">Survey Number</Label>
                  <Input
                    data-testid="survey-no-search-input"
                    placeholder="e.g., 123/4"
                    value={advancedFilters.survey_no}
                    onChange={(e) => setAdvancedFilters(prev => ({ ...prev, survey_no: e.target.value }))}
                    className="input-glass"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label className="text-slate-300">Plot Number</Label>
                  <Input
                    placeholder="e.g., 45"
                    value={advancedFilters.plot_no}
                    onChange={(e) => setAdvancedFilters(prev => ({ ...prev, plot_no: e.target.value }))}
                    className="input-glass"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label className="text-slate-300">Khata Number</Label>
                  <Input
                    placeholder="e.g., KH-2024-001"
                    value={advancedFilters.khata_no}
                    onChange={(e) => setAdvancedFilters(prev => ({ ...prev, khata_no: e.target.value }))}
                    className="input-glass"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label className="text-slate-300">State</Label>
                  <Select 
                    value={advancedFilters.state}
                    onValueChange={(value) => setAdvancedFilters(prev => ({ ...prev, state: value }))}
                  >
                    <SelectTrigger className="input-glass">
                      <SelectValue placeholder="Select state" />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-900 border-slate-700">
                      {INDIAN_STATES.map(state => (
                        <SelectItem key={state} value={state} className="text-slate-300 hover:bg-slate-800">
                          {state}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label className="text-slate-300">District</Label>
                  <Input
                    placeholder="e.g., Bangalore Urban"
                    value={advancedFilters.district}
                    onChange={(e) => setAdvancedFilters(prev => ({ ...prev, district: e.target.value }))}
                    className="input-glass"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label className="text-slate-300">Village</Label>
                  <Input
                    placeholder="e.g., Sarjapur"
                    value={advancedFilters.village}
                    onChange={(e) => setAdvancedFilters(prev => ({ ...prev, village: e.target.value }))}
                    className="input-glass"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label className="text-slate-300">Taluk</Label>
                  <Input
                    placeholder="e.g., Anekal"
                    value={advancedFilters.taluk}
                    onChange={(e) => setAdvancedFilters(prev => ({ ...prev, taluk: e.target.value }))}
                    className="input-glass"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label className="text-slate-300">Land Type</Label>
                  <Select 
                    value={advancedFilters.land_type}
                    onValueChange={(value) => setAdvancedFilters(prev => ({ ...prev, land_type: value }))}
                  >
                    <SelectTrigger className="input-glass">
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-900 border-slate-700">
                      <SelectItem value="Agricultural" className="text-slate-300">Agricultural</SelectItem>
                      <SelectItem value="Residential" className="text-slate-300">Residential</SelectItem>
                      <SelectItem value="Commercial" className="text-slate-300">Commercial</SelectItem>
                      <SelectItem value="Industrial" className="text-slate-300">Industrial</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="flex gap-4">
                <Button 
                  data-testid="advanced-search-btn"
                  onClick={handleAdvancedSearch} 
                  disabled={loading}
                  className="btn-primary"
                >
                  {loading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Searching...
                    </>
                  ) : (
                    <>
                      <Search className="h-4 w-4 mr-2" />
                      Search Properties
                    </>
                  )}
                </Button>
                
                <Button 
                  variant="outline"
                  onClick={() => setAdvancedFilters({
                    owner_name: '', survey_no: '', plot_no: '', khata_no: '',
                    registration_no: '', district: '', state: '', village: '', taluk: '', land_type: ''
                  })}
                  className="btn-secondary"
                >
                  Clear Filters
                </Button>
              </div>
            </TabsContent>
          </Tabs>
        </div>

        {/* Results */}
        <div className="glass-card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-white" style={{ fontFamily: 'Playfair Display' }}>
              {searchType === 'sample_registry' ? 'Property Registry' : 'Search Results'}
              <span className="text-sm font-normal text-slate-400 ml-2">
                ({totalResults} properties)
              </span>
            </h2>
            
            {searchType && searchType !== 'sample_registry' && (
              <Badge variant="outline" className="border-cyan-500/30 text-cyan-400">
                {searchType === 'ai_smart_search' ? 'Smart Search' : 'Filtered'}
              </Badge>
            )}
          </div>
          
          {loading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4].map(i => (
                <ShimmerLoader key={i} variant="card" />
              ))}
            </div>
          ) : results.length > 0 ? (
            <div className="space-y-4">
              {results.map((property, index) => (
                <Link 
                  key={property.property_id || index}
                  to={`/property-profile/${property.property_id}`}
                  className="block"
                >
                  <div 
                    data-testid={`search-result-${index}`}
                    className={`${getCardGlowClass(property.risk_status)} p-5 cursor-pointer hover:scale-[1.01] transition-transform duration-200`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <Building2 className="h-5 w-5 text-cyan-400" />
                          <h3 className="font-semibold text-white text-lg">
                            Survey No: {property.survey_no}
                            {property.plot_no && ` • Plot ${property.plot_no}`}
                          </h3>
                          {property.match_confidence && (
                            <Badge variant="outline" className="border-emerald-500/30 text-emerald-400 text-xs">
                              {property.match_confidence}% match
                            </Badge>
                          )}
                        </div>
                        
                        <div className="grid md:grid-cols-3 gap-4 mt-3">
                          <div>
                            <p className="text-xs text-slate-500 uppercase tracking-wider">Owner</p>
                            <p className="text-sm text-slate-300 flex items-center gap-1">
                              <User className="h-3 w-3" />
                              {property.owner_name || 'Not Available'}
                            </p>
                          </div>
                          
                          <div>
                            <p className="text-xs text-slate-500 uppercase tracking-wider">Location</p>
                            <p className="text-sm text-slate-300 flex items-center gap-1">
                              <MapPin className="h-3 w-3" />
                              {property.district}, {property.state}
                            </p>
                          </div>
                          
                          <div>
                            <p className="text-xs text-slate-500 uppercase tracking-wider">Land Type</p>
                            <p className="text-sm text-slate-300">
                              {property.land_type || 'Not specified'}
                              {property.extent && ` • ${property.extent}`}
                            </p>
                          </div>
                        </div>
                        
                        {property.khata_no && (
                          <p className="text-xs text-slate-500 mt-2">
                            Khata: {property.khata_no}
                          </p>
                        )}
                      </div>
                      
                      <div className="flex flex-col items-end gap-2 ml-4">
                        {property.risk_score && (
                          <div className="text-right">
                            <p className="text-xs text-slate-500">Risk Score</p>
                            <p className={`font-mono font-bold text-lg ${
                              property.risk_score >= 75 ? 'text-emerald-400' :
                              property.risk_score >= 50 ? 'text-amber-400' : 'text-red-400'
                            }`}>
                              {property.risk_score}
                            </p>
                          </div>
                        )}
                        {getRiskBadge(property.risk_status)}
                        <ChevronRight className="h-5 w-5 text-slate-500" />
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="text-center py-16">
              <Globe className="h-16 w-16 text-slate-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">No properties found</h3>
              <p className="text-slate-400 mb-6 max-w-md mx-auto">
                Try adjusting your search criteria or use the AI smart search for natural language queries
              </p>
              <Button onClick={loadSampleProperties} className="btn-secondary">
                View Sample Registry
              </Button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default UniversalSearch;
