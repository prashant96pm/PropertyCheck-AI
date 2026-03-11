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
import Profile from './pages/Profile';
import Settings from './pages/Settings';
import PrivacyPolicy from './pages/PrivacyPolicy';
import TermsOfService from './pages/TermsOfService';
import DPDPCompliance from './pages/DPDPCompliance';
import SharedReport from './pages/SharedReport';
import AdminPanel from './pages/AdminPanel';
import ApiDocs from './pages/ApiDocs';

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
      <Route path="/privacy-policy" element={<PrivacyPolicy />} />
      <Route path="/terms-of-service" element={<TermsOfService />} />
      <Route path="/dpdp-compliance" element={<DPDPCompliance />} />
      <Route path="/shared-report/:shareToken" element={<SharedReport />} />
      <Route path="/developer" element={<ApiDocs />} />
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
      <Route path="/report/:propertyId" element={
        <ProtectedRoute>
          <PropertyDetail />
        </ProtectedRoute>
      } />
      <Route path="/profile" element={
        <ProtectedRoute>
          <Profile />
        </ProtectedRoute>
      } />
      <Route path="/settings" element={
        <ProtectedRoute>
          <Settings />
        </ProtectedRoute>
      } />
      <Route path="/payment/success" element={
        <ProtectedRoute>
          <PaymentSuccess />
        </ProtectedRoute>
      } />
      <Route path="/admin" element={
        <ProtectedRoute>
          <AdminPanel />
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
