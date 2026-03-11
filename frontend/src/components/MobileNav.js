import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from './ui/button';
import {
  Building2, Menu, X, Search, Plus, User, Settings,
  LogOut, Shield, Code, CreditCard
} from 'lucide-react';

const MobileNav = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleNav = (path) => {
    setIsOpen(false);
    navigate(path);
  };

  if (!isAuthenticated) return null;

  return (
    <>
      {/* Hamburger Button - visible only on mobile */}
      <button
        data-testid="mobile-menu-btn"
        onClick={() => setIsOpen(!isOpen)}
        className="md:hidden text-slate-400 hover:text-white p-2"
      >
        {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
      </button>

      {/* Mobile Slide-out Menu */}
      {isOpen && (
        <div className="fixed inset-0 z-[100] md:hidden" data-testid="mobile-menu-overlay">
          {/* Backdrop */}
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setIsOpen(false)} />

          {/* Menu Panel */}
          <div className="absolute right-0 top-0 h-full w-72 bg-slate-900 border-l border-slate-700 p-6">
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-2">
                <Building2 className="h-6 w-6 text-cyan-400" />
                <span className="text-lg font-semibold text-white" style={{ fontFamily: 'Playfair Display' }}>Menu</span>
              </div>
              <button onClick={() => setIsOpen(false)} className="text-slate-400 hover:text-white">
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* User Info */}
            <div className="mb-6 p-3 bg-slate-800/50 rounded-lg">
              <p className="text-sm font-medium text-white">{user?.name}</p>
              <p className="text-xs text-slate-400">{user?.email}</p>
            </div>

            {/* Nav Links */}
            <nav className="space-y-1">
              {[
                { path: '/dashboard', label: 'Dashboard', icon: Building2 },
                { path: '/search', label: 'Search Properties', icon: Search },
                { path: '/upload', label: 'Add Property', icon: Plus },
                { path: '/pricing', label: 'Pricing', icon: CreditCard },
                { path: '/developer', label: 'API Documentation', icon: Code },
                { path: '/profile', label: 'Profile', icon: User },
                { path: '/settings', label: 'Settings', icon: Settings },
              ].map(item => (
                <button
                  key={item.path}
                  data-testid={`mobile-nav-${item.path.slice(1)}`}
                  onClick={() => handleNav(item.path)}
                  className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition-colors text-sm"
                >
                  <item.icon className="h-4 w-4 text-cyan-400" />
                  {item.label}
                </button>
              ))}

              {user?.role === 'admin' && (
                <button
                  data-testid="mobile-nav-admin"
                  onClick={() => handleNav('/admin')}
                  className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition-colors text-sm"
                >
                  <Shield className="h-4 w-4 text-red-400" />
                  Admin Panel
                </button>
              )}
            </nav>

            {/* Logout */}
            <div className="absolute bottom-6 left-6 right-6">
              <Button
                data-testid="mobile-logout-btn"
                variant="ghost"
                className="w-full text-slate-400 hover:text-white hover:bg-red-500/10"
                onClick={() => { logout(); setIsOpen(false); }}
              >
                <LogOut className="h-4 w-4 mr-2" />
                Log Out
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default MobileNav;
