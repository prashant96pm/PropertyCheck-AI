import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../components/ui/dropdown-menu';
import ShimmerLoader from '../components/ShimmerLoader';
import FloatingActionButton from '../components/FloatingActionButton';
import RiskMeter from '../components/RiskMeter';
import { 
  Plus, 
  FileText, 
  CheckCircle2, 
  ChevronRight,
  LogOut,
  User,
  Settings,
  Building2,
  Clock,
  TrendingUp,
  AlertTriangle,
  XCircle,
  Search,
  Sparkles
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, propsRes] = await Promise.all([
        axios.get(`${API}/dashboard/stats`, { withCredentials: true }),
        axios.get(`${API}/properties`, { withCredentials: true })
      ]);
      setStats(statsRes.data);
      setProperties(propsRes.data);
    } catch (error) {
      console.error('Dashboard fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const getCardGlowClass = (status) => {
    if (!status) return 'glass-card';
    if (status === 'GREEN') return 'glass-card-green';
    if (status === 'YELLOW') return 'glass-card-orange';
    return 'glass-card-red';
  };

  const getRiskBadge = (status) => {
    if (!status) return null;
    
    const badges = {
      GREEN: <Badge className="badge-risk-low">VERIFIED</Badge>,
      YELLOW: <Badge className="badge-risk-medium">CAUTION</Badge>,
      RED: <Badge className="badge-risk-high">HIGH RISK</Badge>
    };
    return badges[status] || null;
  };

  const getRiskIcon = (status) => {
    if (!status) return <Clock className="h-5 w-5 text-slate-500" />;
    if (status === 'GREEN') return <CheckCircle2 className="h-5 w-5 text-emerald-400" />;
    if (status === 'YELLOW') return <AlertTriangle className="h-5 w-5 text-amber-400" />;
    return <XCircle className="h-5 w-5 text-red-400" />;
  };

  return (
    <div className="min-h-screen gradient-bg">
      {/* Animated Background Grid */}
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
              <Link to="/search">
                <Button data-testid="nav-search-btn" className="btn-secondary">
                  <Search className="h-4 w-4 mr-2" />
                  Search
                </Button>
              </Link>
              <Link to="/upload">
                <Button data-testid="new-property-btn" className="btn-primary">
                  <Plus className="h-4 w-4 mr-2" />
                  New Property
                </Button>
              </Link>
              
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button data-testid="user-menu-btn" variant="ghost" className="relative h-10 w-10 rounded-full">
                    {user?.picture ? (
                      <img src={user.picture} alt={user.name} className="h-10 w-10 rounded-full" />
                    ) : (
                      <div className="h-10 w-10 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center border border-cyan-500/30">
                        {user?.name?.charAt(0) || 'U'}
                      </div>
                    )}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56 bg-slate-900 border-slate-700">
                  <div className="px-2 py-1.5">
                    <p className="text-sm font-medium text-white">{user?.name}</p>
                    <p className="text-xs text-slate-400">{user?.email}</p>
                  </div>
                  <DropdownMenuSeparator className="bg-slate-700" />
                  <DropdownMenuItem data-testid="profile-menu-item" className="text-slate-300 hover:text-white hover:bg-slate-800 cursor-pointer" onClick={() => navigate('/profile')}>
                    <User className="mr-2 h-4 w-4" />
                    Profile
                  </DropdownMenuItem>
                  <DropdownMenuItem data-testid="settings-menu-item" className="text-slate-300 hover:text-white hover:bg-slate-800 cursor-pointer" onClick={() => navigate('/settings')}>
                    <Settings className="mr-2 h-4 w-4" />
                    Settings
                  </DropdownMenuItem>
                  <DropdownMenuSeparator className="bg-slate-700" />
                  <DropdownMenuItem data-testid="logout-menu-item" onClick={handleLogout} className="text-slate-300 hover:text-white hover:bg-slate-800">
                    <LogOut className="mr-2 h-4 w-4" />
                    Log out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white" style={{ fontFamily: 'Playfair Display' }}>
            Welcome back, <span className="text-gradient">{user?.name?.split(' ')[0]}</span>
          </h1>
          <p className="text-slate-400 mt-1">
            Manage your property verifications and reports
          </p>
        </div>

        {/* Quick Search Bar */}
        <div className="glass-card-blue mb-8">
          <div className="flex items-center gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
              <input
                data-testid="dashboard-search-input"
                type="text"
                placeholder="Quick search: owner name, survey number, or location..."
                className="input-glass w-full pl-12 py-3"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && e.target.value.trim()) {
                    navigate(`/search?q=${encodeURIComponent(e.target.value.trim())}`);
                  }
                }}
              />
            </div>
            <Link to="/search">
              <Button data-testid="dashboard-search-go-btn" className="btn-primary whitespace-nowrap">
                <Sparkles className="h-4 w-4 mr-2" />
                Search
              </Button>
            </Link>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {loading ? (
            Array(4).fill(0).map((_, i) => (
              <ShimmerLoader key={i} variant="stat" />
            ))
          ) : (
            <>
              <div className="glass-card-blue">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-400">Total Properties</p>
                    <p className="text-3xl font-bold text-white mt-1 font-mono">
                      {stats?.total_properties || 0}
                    </p>
                  </div>
                  <div className="h-12 w-12 rounded-lg bg-cyan-500/20 flex items-center justify-center">
                    <Building2 className="h-6 w-6 text-cyan-400" />
                  </div>
                </div>
              </div>

              <div className="glass-card">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-400">Documents</p>
                    <p className="text-3xl font-bold text-white mt-1 font-mono">
                      {stats?.total_documents || 0}
                    </p>
                  </div>
                  <div className="h-12 w-12 rounded-lg bg-amber-500/20 flex items-center justify-center">
                    <FileText className="h-6 w-6 text-amber-400" />
                  </div>
                </div>
              </div>

              <div className="glass-card-green">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-400">Reports Generated</p>
                    <p className="text-3xl font-bold text-white mt-1 font-mono">
                      {stats?.total_reports || 0}
                    </p>
                  </div>
                  <div className="h-12 w-12 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                    <CheckCircle2 className="h-6 w-6 text-emerald-400" />
                  </div>
                </div>
              </div>

              <div className="glass-card-orange">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-400">Pending Review</p>
                    <p className="text-3xl font-bold text-white mt-1 font-mono">
                      {properties.filter(p => !p.risk_score).length}
                    </p>
                  </div>
                  <div className="h-12 w-12 rounded-lg bg-orange-500/20 flex items-center justify-center">
                    <Clock className="h-6 w-6 text-orange-400" />
                  </div>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Quick Actions & Properties */}
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Quick Actions */}
          <div className="glass-card lg:col-span-1">
            <h2 className="text-lg font-semibold text-white mb-4" style={{ fontFamily: 'Playfair Display' }}>
              Quick Actions
            </h2>
            <div className="space-y-3">
              <Link to="/search" className="block">
                <Button data-testid="quick-search-btn" className="w-full justify-start btn-secondary">
                  <Search className="mr-2 h-4 w-4 text-cyan-400" />
                  Search Properties
                </Button>
              </Link>
              <Link to="/upload" className="block">
                <Button data-testid="quick-upload-btn" className="w-full justify-start btn-secondary">
                  <Plus className="mr-2 h-4 w-4 text-cyan-400" />
                  Add New Property
                </Button>
              </Link>
              <Link to="/pricing" className="block">
                <Button data-testid="quick-pricing-btn" className="w-full justify-start btn-secondary">
                  <TrendingUp className="mr-2 h-4 w-4 text-cyan-400" />
                  View Pricing
                </Button>
              </Link>
            </div>
          </div>

          {/* Properties List */}
          <div className="glass-card lg:col-span-2">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-white" style={{ fontFamily: 'Playfair Display' }}>
                Your Properties
              </h2>
              <Link to="/upload">
                <Button data-testid="add-property-btn" variant="ghost" size="sm" className="text-cyan-400 hover:text-cyan-300">
                  <Plus className="h-4 w-4 mr-1" />
                  Add
                </Button>
              </Link>
            </div>
            
            {loading ? (
              <ShimmerLoader variant="table" />
            ) : properties.length > 0 ? (
              <div className="space-y-4">
                {properties.map((property) => (
                  <Link 
                    key={property.property_id} 
                    to={`/property/${property.property_id}`}
                    className="block"
                  >
                    <div 
                      data-testid={`property-card-${property.property_id}`}
                      className={`${getCardGlowClass(property.risk_status)} p-4 cursor-pointer hover:scale-[1.01] transition-transform duration-200`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          {getRiskIcon(property.risk_status)}
                          <div>
                            <p className="font-medium text-white">
                              Survey No: {property.survey_no}
                            </p>
                            <p className="text-sm text-slate-400">
                              {property.district}, {property.state}
                              {property.khata_no && ` • Khata: ${property.khata_no}`}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          {property.risk_score && (
                            <div className="text-right">
                              <p className="text-xs text-slate-500">Risk Score</p>
                              <p className={`font-mono font-bold ${
                                property.risk_score >= 75 ? 'text-emerald-400' :
                                property.risk_score >= 50 ? 'text-amber-400' : 'text-red-400'
                              }`}>
                                {property.risk_score}/100
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
              <div className="text-center py-12">
                <Building2 className="h-12 w-12 text-slate-600 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-white mb-2">No properties yet</h3>
                <p className="text-sm text-slate-400 mb-4">
                  Start by adding your first property for verification
                </p>
                <Link to="/upload">
                  <Button data-testid="empty-add-property-btn" className="btn-primary">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Property
                  </Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Floating Action Button */}
      <FloatingActionButton to="/upload" />
    </div>
  );
};

export default Dashboard;
