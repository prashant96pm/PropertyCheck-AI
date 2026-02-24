import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { 
  Building2, 
  ArrowLeft, 
  User, 
  Mail, 
  Calendar,
  Save,
  Loader2
} from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Profile = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ first_name: '', last_name: '', gender: '' });

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const res = await axios.get(`${API}/profile`, { withCredentials: true });
      setProfile(res.data);
      setForm({
        first_name: res.data.first_name || '',
        last_name: res.data.last_name || '',
        gender: res.data.gender || ''
      });
    } catch (err) {
      toast.error('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await axios.put(`${API}/profile`, form, { withCredentials: true });
      toast.success('Profile updated successfully');
    } catch (err) {
      toast.error('Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    try { return new Date(dateStr).toLocaleDateString('en-IN', { year: 'numeric', month: 'long', day: 'numeric' }); }
    catch { return 'N/A'; }
  };

  return (
    <div className="min-h-screen gradient-bg">
      <div className="fixed inset-0 grid-bg opacity-30 pointer-events-none" />
      <nav className="glass-header sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-4">
              <button onClick={() => navigate('/dashboard')} className="text-slate-400 hover:text-white transition-colors" data-testid="profile-back-btn">
                <ArrowLeft className="h-5 w-5" />
              </button>
              <Link to="/" className="flex items-center gap-2">
                <Building2 className="h-8 w-8 text-cyan-400" />
                <span className="text-xl font-semibold text-white" style={{ fontFamily: 'Playfair Display' }}>PropertyCheck AI</span>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12 relative z-10">
        <h1 className="text-3xl font-bold text-white mb-8" style={{ fontFamily: 'Playfair Display' }}>
          Your <span className="text-gradient">Profile</span>
        </h1>

        {loading ? (
          <div className="flex justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-cyan-400" /></div>
        ) : (
          <div className="glass-card space-y-6">
            <div className="flex items-center gap-4 pb-6 border-b border-slate-700/50">
              <div className="h-16 w-16 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center text-2xl font-bold border-2 border-cyan-500/30">
                {form.first_name?.charAt(0) || user?.name?.charAt(0) || 'U'}
              </div>
              <div>
                <p className="text-lg font-semibold text-white">{form.first_name} {form.last_name}</p>
                <p className="text-sm text-slate-400">{profile?.email}</p>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <Label className="text-slate-300 mb-2 block">First Name</Label>
                <Input
                  data-testid="profile-first-name"
                  className="input-glass"
                  value={form.first_name}
                  onChange={(e) => setForm({ ...form, first_name: e.target.value })}
                  placeholder="First Name"
                />
              </div>
              <div>
                <Label className="text-slate-300 mb-2 block">Last Name</Label>
                <Input
                  data-testid="profile-last-name"
                  className="input-glass"
                  value={form.last_name}
                  onChange={(e) => setForm({ ...form, last_name: e.target.value })}
                  placeholder="Last Name"
                />
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <Label className="text-slate-300 mb-2 block">Email</Label>
                <div className="flex items-center gap-2 p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                  <Mail className="h-4 w-4 text-slate-500" />
                  <span className="text-sm text-slate-400">{profile?.email}</span>
                </div>
              </div>
              <div>
                <Label className="text-slate-300 mb-2 block">Gender</Label>
                <Select value={form.gender} onValueChange={(val) => setForm({ ...form, gender: val })}>
                  <SelectTrigger data-testid="profile-gender" className="input-glass">
                    <SelectValue placeholder="Select Gender" />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-900 border-slate-700">
                    <SelectItem value="male">Male</SelectItem>
                    <SelectItem value="female">Female</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                    <SelectItem value="prefer_not_to_say">Prefer not to say</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <Label className="text-slate-300 mb-2 block">Date Joined</Label>
              <div className="flex items-center gap-2 p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                <Calendar className="h-4 w-4 text-slate-500" />
                <span className="text-sm text-slate-400">{formatDate(profile?.date_joined)}</span>
              </div>
            </div>

            <Button data-testid="profile-save-btn" className="btn-primary w-full" onClick={handleSave} disabled={saving}>
              {saving ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Saving...</> : <><Save className="h-4 w-4 mr-2" />Save Changes</>}
            </Button>
          </div>
        )}
      </main>
    </div>
  );
};

export default Profile;
