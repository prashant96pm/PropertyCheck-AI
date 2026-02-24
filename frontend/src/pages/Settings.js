import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Label } from '../components/ui/label';
import { 
  Building2, 
  ArrowLeft, 
  Sun, 
  Moon,
  Monitor
} from 'lucide-react';

const Settings = () => {
  const navigate = useNavigate();
  const [theme, setTheme] = useState('dark');

  const themes = [
    { key: 'dark', label: 'Dark Mode', icon: Moon, desc: 'Dark theme with glassmorphism effects' },
    { key: 'light', label: 'Light Mode', icon: Sun, desc: 'Coming soon - Light theme' },
    { key: 'system', label: 'System', icon: Monitor, desc: 'Coming soon - Follow system preference' },
  ];

  return (
    <div className="min-h-screen gradient-bg">
      <div className="fixed inset-0 grid-bg opacity-30 pointer-events-none" />
      <nav className="glass-header sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-4">
              <button onClick={() => navigate('/dashboard')} className="text-slate-400 hover:text-white transition-colors" data-testid="settings-back-btn">
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
          <span className="text-gradient">Settings</span>
        </h1>

        <div className="glass-card">
          <h2 className="text-lg font-semibold text-white mb-4">Appearance</h2>
          <div className="space-y-3">
            {themes.map((t) => (
              <button
                key={t.key}
                data-testid={`theme-${t.key}-btn`}
                onClick={() => t.key === 'dark' && setTheme(t.key)}
                className={`w-full flex items-center gap-4 p-4 rounded-lg border transition-all ${
                  theme === t.key 
                    ? 'border-cyan-500/50 bg-cyan-500/10' 
                    : 'border-slate-700 bg-slate-800/30 hover:border-slate-600'
                } ${t.key !== 'dark' ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                disabled={t.key !== 'dark'}
              >
                <div className={`h-10 w-10 rounded-lg flex items-center justify-center ${
                  theme === t.key ? 'bg-cyan-500/20 text-cyan-400' : 'bg-slate-700 text-slate-400'
                }`}>
                  <t.icon className="h-5 w-5" />
                </div>
                <div className="text-left">
                  <p className={`font-medium ${theme === t.key ? 'text-cyan-400' : 'text-slate-300'}`}>{t.label}</p>
                  <p className="text-xs text-slate-500">{t.desc}</p>
                </div>
                {theme === t.key && (
                  <div className="ml-auto h-3 w-3 rounded-full bg-cyan-400" />
                )}
              </button>
            ))}
          </div>
        </div>

        <div className="glass-card mt-6">
          <h2 className="text-lg font-semibold text-white mb-4">Notifications</h2>
          <p className="text-sm text-slate-400">Notification preferences coming soon.</p>
        </div>
      </main>
    </div>
  );
};

export default Settings;
