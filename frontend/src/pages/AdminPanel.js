import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import {
  Building2, Users, FileText, CheckCircle2, AlertTriangle,
  ArrowLeft, Shield, Activity, Search, ChevronRight,
  BarChart3, Clock, Loader2
} from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminPanel = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [verifications, setVerifications] = useState([]);
  const [activeSection, setActiveSection] = useState('overview');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.role !== 'admin') {
      toast.error('Admin access required');
      navigate('/dashboard');
      return;
    }
    fetchAdminData();
  }, [user, navigate]);

  const fetchAdminData = async () => {
    try {
      const [statsRes, usersRes, verificationsRes] = await Promise.allSettled([
        axios.get(`${API}/admin/stats`, { withCredentials: true }),
        axios.get(`${API}/admin/users`, { withCredentials: true }),
        axios.get(`${API}/admin/verifications`, { withCredentials: true }),
      ]);
      if (statsRes.status === 'fulfilled') setStats(statsRes.value.data);
      if (usersRes.status === 'fulfilled') setUsers(usersRes.value.data.users || []);
      if (verificationsRes.status === 'fulfilled') setVerifications(verificationsRes.value.data.verifications || []);
    } catch (err) {
      toast.error('Failed to load admin data');
    } finally {
      setLoading(false);
    }
  };

  const updateUserRole = async (userId, newRole) => {
    try {
      await axios.put(`${API}/admin/users/${userId}/role?role=${newRole}`, {}, { withCredentials: true });
      toast.success(`Role updated to ${newRole}`);
      setUsers(prev => prev.map(u => u.user_id === userId ? { ...u, role: newRole } : u));
    } catch (err) {
      toast.error('Failed to update role');
    }
  };

  if (loading) return (
    <div className="min-h-screen gradient-bg flex items-center justify-center">
      <Loader2 className="h-8 w-8 animate-spin text-cyan-400" />
    </div>
  );

  const sections = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'users', label: 'Users', icon: Users },
    { id: 'verifications', label: 'Verifications', icon: Shield },
  ];

  return (
    <div className="min-h-screen gradient-bg" data-testid="admin-panel">
      <div className="fixed inset-0 grid-bg opacity-30 pointer-events-none" />

      <nav className="glass-header sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-4">
              <button onClick={() => navigate('/dashboard')} className="text-slate-400 hover:text-white" data-testid="admin-back-btn">
                <ArrowLeft className="h-5 w-5" />
              </button>
              <Link to="/" className="flex items-center gap-2">
                <Building2 className="h-8 w-8 text-cyan-400" />
                <span className="text-xl font-semibold text-white" style={{ fontFamily: 'Playfair Display' }}>Admin Panel</span>
              </Link>
            </div>
            <Badge className="bg-red-500/20 text-red-400 border-red-500/30">
              <Shield className="h-3 w-3 mr-1" /> Admin
            </Badge>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        {/* Section Tabs */}
        <div className="flex gap-2 mb-8">
          {sections.map(s => (
            <button
              key={s.id}
              data-testid={`admin-tab-${s.id}`}
              onClick={() => setActiveSection(s.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                activeSection === s.id
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
              }`}
            >
              <s.icon className="h-4 w-4" />{s.label}
            </button>
          ))}
        </div>

        {/* Overview Section */}
        {activeSection === 'overview' && stats && (
          <div data-testid="admin-overview">
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
              {[
                { label: 'Total Users', value: stats.total_users, icon: Users, color: 'cyan' },
                { label: 'Properties', value: stats.total_properties, icon: Building2, color: 'emerald' },
                { label: 'Reports', value: stats.total_reports, icon: FileText, color: 'amber' },
                { label: 'Documents', value: stats.total_documents, icon: FileText, color: 'violet' },
                { label: 'Searches', value: stats.total_searches, icon: Search, color: 'pink' },
              ].map(item => (
                <div key={item.label} className="glass-card">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-xs text-slate-400">{item.label}</p>
                      <p className="text-2xl font-bold text-white font-mono mt-1">{item.value || 0}</p>
                    </div>
                    <div className={`h-10 w-10 rounded-lg bg-${item.color}-500/20 flex items-center justify-center`}>
                      <item.icon className={`h-5 w-5 text-${item.color}-400`} />
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Recent Users */}
            <div className="glass-card">
              <h3 className="text-lg font-semibold text-white mb-4" style={{ fontFamily: 'Playfair Display' }}>Recent Users</h3>
              <div className="space-y-3">
                {(stats.recent_users || []).slice(0, 5).map((u, i) => (
                  <div key={i} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="h-8 w-8 rounded-full bg-cyan-500/20 flex items-center justify-center text-cyan-400 text-sm font-bold">
                        {u.name?.charAt(0)?.toUpperCase() || '?'}
                      </div>
                      <div>
                        <p className="text-sm text-white">{u.name || 'N/A'}</p>
                        <p className="text-xs text-slate-500">{u.email}</p>
                      </div>
                    </div>
                    <Badge className={`${u.role === 'admin' ? 'bg-red-500/20 text-red-400' : 'bg-slate-700 text-slate-300'}`}>{u.role || 'user'}</Badge>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Users Section */}
        {activeSection === 'users' && (
          <div data-testid="admin-users-section">
            <div className="glass-card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white" style={{ fontFamily: 'Playfair Display' }}>User Management</h3>
                <p className="text-sm text-slate-400">{users.length} total users</p>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-700/50">
                      <th className="text-left text-xs text-slate-400 pb-3 font-medium">User</th>
                      <th className="text-left text-xs text-slate-400 pb-3 font-medium">Email</th>
                      <th className="text-left text-xs text-slate-400 pb-3 font-medium">Role</th>
                      <th className="text-left text-xs text-slate-400 pb-3 font-medium">Joined</th>
                      <th className="text-right text-xs text-slate-400 pb-3 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((u, i) => (
                      <tr key={i} className="border-b border-slate-800/50" data-testid={`admin-user-row-${i}`}>
                        <td className="py-3">
                          <div className="flex items-center gap-2">
                            <div className="h-7 w-7 rounded-full bg-cyan-500/20 flex items-center justify-center text-cyan-400 text-xs font-bold">
                              {u.name?.charAt(0)?.toUpperCase() || '?'}
                            </div>
                            <span className="text-sm text-white">{u.name || 'N/A'}</span>
                          </div>
                        </td>
                        <td className="py-3 text-sm text-slate-400">{u.email}</td>
                        <td className="py-3">
                          <Badge className={`text-xs ${
                            u.role === 'admin' ? 'bg-red-500/20 text-red-400' :
                            u.role === 'lawyer' ? 'bg-violet-500/20 text-violet-400' :
                            u.role === 'bank' ? 'bg-amber-500/20 text-amber-400' :
                            'bg-slate-700 text-slate-300'
                          }`}>{u.role || 'user'}</Badge>
                        </td>
                        <td className="py-3 text-xs text-slate-500">
                          {u.created_at ? new Date(u.created_at).toLocaleDateString() : 'N/A'}
                        </td>
                        <td className="py-3 text-right">
                          <select
                            data-testid={`role-select-${i}`}
                            value={u.role || 'user'}
                            onChange={(e) => updateUserRole(u.user_id, e.target.value)}
                            className="bg-slate-800 text-slate-300 text-xs rounded px-2 py-1 border border-slate-700"
                          >
                            <option value="user">User</option>
                            <option value="admin">Admin</option>
                            <option value="lawyer">Lawyer</option>
                            <option value="bank">Bank</option>
                          </select>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Verifications Section */}
        {activeSection === 'verifications' && (
          <div data-testid="admin-verifications-section">
            <div className="glass-card">
              <h3 className="text-lg font-semibold text-white mb-4" style={{ fontFamily: 'Playfair Display' }}>Recent Verifications</h3>
              {verifications.length > 0 ? (
                <div className="space-y-3">
                  {verifications.map((v, i) => (
                    <div key={i} className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg border border-slate-700/50" data-testid={`verification-row-${i}`}>
                      <div className="flex items-center gap-3">
                        {v.risk_status === 'GREEN' ? <CheckCircle2 className="h-5 w-5 text-emerald-400" /> :
                         v.risk_status === 'YELLOW' ? <AlertTriangle className="h-5 w-5 text-amber-400" /> :
                         <AlertTriangle className="h-5 w-5 text-red-400" />}
                        <div>
                          <p className="text-sm text-white">Property: {v.property_id}</p>
                          <p className="text-xs text-slate-500">
                            {v.generated_at ? new Date(v.generated_at).toLocaleString() : 'N/A'}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="text-right">
                          <p className={`text-lg font-bold font-mono ${
                            v.risk_score >= 75 ? 'text-emerald-400' : v.risk_score >= 50 ? 'text-amber-400' : 'text-red-400'
                          }`}>{v.risk_score}/100</p>
                        </div>
                        <Badge className={`${
                          v.risk_status === 'GREEN' ? 'bg-emerald-500/20 text-emerald-400' :
                          v.risk_status === 'YELLOW' ? 'bg-amber-500/20 text-amber-400' :
                          'bg-red-500/20 text-red-400'
                        }`}>{v.risk_status}</Badge>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <Activity className="h-12 w-12 text-slate-600 mx-auto mb-3" />
                  <p className="text-sm text-slate-400">No verifications yet</p>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default AdminPanel;
