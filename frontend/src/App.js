import React from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { Toaster } from './components/ui/sonner';

// Pages
import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import UploadProperty from './pages/UploadProperty';
import PropertyDetail from './pages/PropertyDetail';
import Pricing from './pages/Pricing';
import PaymentSuccess from './pages/PaymentSuccess';
import UniversalSearch from './pages/UniversalSearch';
import PropertyProfile from './pages/PropertyProfile';

// Components
import ProtectedRoute from './components/ProtectedRoute';
import AuthCallback from './components/AuthCallback';

import './App.css';

// Router wrapper to handle OAuth callback
function AppRouter() {
  const location = useLocation();
  
  // Check URL fragment for session_id (OAuth callback)
  if (location.hash?.includes('session_id=')) {
    return <AuthCallback />;
  }
  
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/pricing" element={<Pricing />} />
      <Route path="/search" element={<UniversalSearch />} />
      <Route path="/property-profile/:propertyId" element={<PropertyProfile />} />
      <Route path="/auth/callback" element={<AuthCallback />} />
      
      {/* Protected routes */}
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <Dashboard />
        </ProtectedRoute>
      } />
      <Route path="/upload" element={
        <ProtectedRoute>
          <UploadProperty />
        </ProtectedRoute>
      } />
      <Route path="/property/:propertyId" element={
        <ProtectedRoute>
          <PropertyDetail />
        </ProtectedRoute>
      } />
      <Route path="/payment/success" element={
        <ProtectedRoute>
          <PaymentSuccess />
        </ProtectedRoute>
      } />
      
      {/* Fallback */}
      <Route path="*" element={<Landing />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRouter />
        <Toaster 
          position="top-right"
          toastOptions={{
            style: {
              background: 'hsl(222, 47%, 11%)',
              color: 'hsl(210, 40%, 98%)',
              border: '1px solid hsl(217, 33%, 20%)',
            },
          }}
        />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
