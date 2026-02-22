import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const checkAuth = useCallback(async () => {
    // CRITICAL: If returning from OAuth callback, skip the /me check.
    // AuthCallback will exchange the session_id and establish the session first.
    if (window.location.hash?.includes('session_id=')) {
      setLoading(false);
      return;
    }
    
    try {
      const response = await axios.get(`${API}/auth/me`, {
        withCredentials: true
      });
      setUser(response.data);
    } catch (err) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = async (email, password) => {
    try {
      setError(null);
      const response = await axios.post(`${API}/auth/login`, 
        { email, password },
        { withCredentials: true }
      );
      setUser(response.data.user);
      localStorage.setItem('token', response.data.access_token);
      return response.data;
    } catch (err) {
      const message = err.response?.data?.detail || 'Login failed';
      setError(message);
      throw new Error(message);
    }
  };

  const register = async (name, email, password) => {
    try {
      setError(null);
      const response = await axios.post(`${API}/auth/register`,
        { name, email, password },
        { withCredentials: true }
      );
      setUser(response.data.user);
      localStorage.setItem('token', response.data.access_token);
      return response.data;
    } catch (err) {
      const message = err.response?.data?.detail || 'Registration failed';
      setError(message);
      throw new Error(message);
    }
  };

  const loginWithGoogle = () => {
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    const redirectUrl = window.location.origin + '/auth/callback';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  const processOAuthSession = async (sessionId) => {
    try {
      const response = await axios.post(`${API}/auth/session`,
        { session_id: sessionId },
        { withCredentials: true }
      );
      setUser({
        user_id: response.data.user_id,
        email: response.data.email,
        name: response.data.name,
        picture: response.data.picture
      });
      localStorage.setItem('token', response.data.access_token);
      return response.data;
    } catch (err) {
      throw new Error('OAuth session processing failed');
    }
  };

  const logout = async () => {
    try {
      await axios.post(`${API}/auth/logout`, {}, { withCredentials: true });
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      setUser(null);
      localStorage.removeItem('token');
    }
  };

  const value = {
    user,
    loading,
    error,
    login,
    register,
    loginWithGoogle,
    processOAuthSession,
    logout,
    checkAuth,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
