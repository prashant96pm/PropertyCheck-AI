import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Skeleton } from '../components/ui/skeleton';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../components/ui/dropdown-menu';
import { 
  Shield, 
  Plus, 
  FileText, 
  AlertTriangle, 
  CheckCircle2, 
  ChevronRight,
  LogOut,
  User,
  Settings,
  Building2,
  Clock,
  TrendingUp
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

  const getRiskBadge = (status) => {
    if (!status) return null;
    
    const badges = {
      GREEN: <Badge className="badge-risk-low">SAFE</Badge>,
      YELLOW: <Badge className="badge-risk-medium">CAUTION</Badge>,
      RED: <Badge className="badge-risk-high">HIGH RISK</Badge>
    };
    return badges[status] || null;
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Navigation */}
      <nav className="glass-header sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="flex items-center gap-2">
              <Shield className="h-8 w-8 text-primary" />
              <span className="text-xl font-semibold text-primary" style={{ fontFamily: 'Playfair Display' }}>
                PropertyCheck AI
              </span>
            </Link>
            
            <div className="flex items-center gap-4">
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
                      <div className="h-10 w-10 rounded-full bg-primary text-primary-foreground flex items-center justify-center">
                        {user?.name?.charAt(0) || 'U'}
                      </div>
                    )}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <div className="px-2 py-1.5">
                    <p className="text-sm font-medium">{user?.name}</p>
                    <p className="text-xs text-muted-foreground">{user?.email}</p>
                  </div>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem data-testid="profile-menu-item">
                    <User className="mr-2 h-4 w-4" />
                    Profile
                  </DropdownMenuItem>
                  <DropdownMenuItem data-testid="settings-menu-item">
                    <Settings className="mr-2 h-4 w-4" />
                    Settings
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem data-testid="logout-menu-item" onClick={handleLogout}>
                    <LogOut className="mr-2 h-4 w-4" />
                    Log out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-primary" style={{ fontFamily: 'Playfair Display' }}>
            Welcome back, {user?.name?.split(' ')[0]}
          </h1>
          <p className="text-muted-foreground mt-1">
            Manage your property verifications and reports
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {loading ? (
            Array(4).fill(0).map((_, i) => (
              <Card key={i} className="card-base">
                <CardContent className="p-6">
                  <Skeleton className="h-4 w-20 mb-2" />
                  <Skeleton className="h-8 w-16" />
                </CardContent>
              </Card>
            ))
          ) : (
            <>
              <Card className="card-base">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Total Properties</p>
                      <p className="text-3xl font-bold text-primary mt-1 font-mono">
                        {stats?.total_properties || 0}
                      </p>
                    </div>
                    <div className="h-12 w-12 rounded-sm bg-accent/10 flex items-center justify-center">
                      <Building2 className="h-6 w-6 text-accent" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="card-base">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Documents</p>
                      <p className="text-3xl font-bold text-primary mt-1 font-mono">
                        {stats?.total_documents || 0}
                      </p>
                    </div>
                    <div className="h-12 w-12 rounded-sm bg-amber-100 flex items-center justify-center">
                      <FileText className="h-6 w-6 text-amber-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="card-base">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Reports Generated</p>
                      <p className="text-3xl font-bold text-primary mt-1 font-mono">
                        {stats?.total_reports || 0}
                      </p>
                    </div>
                    <div className="h-12 w-12 rounded-sm bg-emerald-100 flex items-center justify-center">
                      <CheckCircle2 className="h-6 w-6 text-emerald-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="card-base">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Pending Review</p>
                      <p className="text-3xl font-bold text-primary mt-1 font-mono">
                        {properties.filter(p => !p.risk_score).length}
                      </p>
                    </div>
                    <div className="h-12 w-12 rounded-sm bg-red-100 flex items-center justify-center">
                      <Clock className="h-6 w-6 text-red-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </div>

        {/* Quick Actions & Properties */}
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Quick Actions */}
          <Card className="card-base lg:col-span-1">
            <CardHeader>
              <CardTitle className="text-lg" style={{ fontFamily: 'Playfair Display' }}>
                Quick Actions
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Link to="/upload" className="block">
                <Button data-testid="quick-upload-btn" variant="outline" className="w-full justify-start">
                  <Plus className="mr-2 h-4 w-4" />
                  Add New Property
                </Button>
              </Link>
              <Link to="/pricing" className="block">
                <Button data-testid="quick-pricing-btn" variant="outline" className="w-full justify-start">
                  <TrendingUp className="mr-2 h-4 w-4" />
                  View Pricing
                </Button>
              </Link>
              <Button data-testid="quick-help-btn" variant="outline" className="w-full justify-start">
                <FileText className="mr-2 h-4 w-4" />
                Sample Report
              </Button>
            </CardContent>
          </Card>

          {/* Properties List */}
          <Card className="card-base lg:col-span-2">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-lg" style={{ fontFamily: 'Playfair Display' }}>
                Your Properties
              </CardTitle>
              <Link to="/upload">
                <Button data-testid="add-property-btn" variant="ghost" size="sm">
                  <Plus className="h-4 w-4 mr-1" />
                  Add
                </Button>
              </Link>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-4">
                  {Array(3).fill(0).map((_, i) => (
                    <div key={i} className="flex items-center justify-between p-4 border rounded-sm">
                      <div className="space-y-2">
                        <Skeleton className="h-4 w-32" />
                        <Skeleton className="h-3 w-48" />
                      </div>
                      <Skeleton className="h-6 w-16" />
                    </div>
                  ))}
                </div>
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
                        className="flex items-center justify-between p-4 border rounded-sm hover:border-accent/50 transition-colors cursor-pointer"
                      >
                        <div>
                          <p className="font-medium text-primary">
                            Survey No: {property.survey_no}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            {property.district}, {property.state}
                            {property.khata_no && ` • Khata: ${property.khata_no}`}
                          </p>
                        </div>
                        <div className="flex items-center gap-3">
                          {property.risk_score && (
                            <div className="text-right">
                              <p className="text-xs text-muted-foreground">Risk Score</p>
                              <p className={`font-mono font-bold ${
                                property.risk_score >= 75 ? 'text-emerald-600' :
                                property.risk_score >= 50 ? 'text-amber-600' : 'text-red-600'
                              }`}>
                                {property.risk_score}/100
                              </p>
                            </div>
                          )}
                          {getRiskBadge(property.risk_status)}
                          <ChevronRight className="h-5 w-5 text-muted-foreground" />
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <Building2 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-primary mb-2">No properties yet</h3>
                  <p className="text-sm text-muted-foreground mb-4">
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
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
