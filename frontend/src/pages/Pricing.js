import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { 
  Shield, 
  CheckCircle2, 
  ArrowLeft,
  Loader2,
  CreditCard,
  Sparkles,
  Zap
} from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Pricing = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [pricing, setPricing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processingPayment, setProcessingPayment] = useState(false);

  const propertyId = searchParams.get('property_id');

  useEffect(() => {
    fetchPricing();
  }, []);

  const fetchPricing = async () => {
    try {
      const response = await axios.get(`${API}/pricing`);
      setPricing(response.data);
    } catch (error) {
      console.error('Failed to fetch pricing:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePurchase = async (packageType) => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    if (!propertyId) {
      toast.error('Please select a property first');
      navigate('/dashboard');
      return;
    }

    setProcessingPayment(true);

    try {
      const response = await axios.post(
        `${API}/payments/create-checkout`,
        {
          property_id: propertyId,
          package_type: packageType,
          origin_url: window.location.origin
        },
        { withCredentials: true }
      );

      window.location.href = response.data.checkout_url;
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to initiate payment');
      setProcessingPayment(false);
    }
  };

  const packages = pricing ? [
    {
      key: 'basic',
      name: pricing.basic.name,
      price: `₹${pricing.basic.amount}`,
      features: pricing.basic.features,
      popular: false,
      icon: <FileText className="h-6 w-6" />
    },
    {
      key: 'standard',
      name: pricing.standard.name,
      price: `₹${pricing.standard.amount}`,
      features: pricing.standard.features,
      popular: true,
      icon: <Sparkles className="h-6 w-6" />
    },
    {
      key: 'premium',
      name: pricing.premium.name,
      price: `₹${pricing.premium.amount}`,
      features: pricing.premium.features,
      popular: false,
      icon: <Zap className="h-6 w-6" />
    }
  ] : [];

  return (
    <div className="min-h-screen gradient-bg">
      <div className="fixed inset-0 grid-bg opacity-30 pointer-events-none" />
      
      {/* Navigation */}
      <nav className="glass-header sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-4">
              <Link to={isAuthenticated ? "/dashboard" : "/"} className="text-slate-400 hover:text-white transition-colors">
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <Link to="/" className="flex items-center gap-2">
                <Shield className="h-8 w-8 text-cyan-400" />
                <span className="text-xl font-semibold text-white" style={{ fontFamily: 'Playfair Display' }}>
                  PropertyCheck AI
                </span>
              </Link>
            </div>
            
            {!isAuthenticated && (
              <div className="flex items-center gap-4">
                <Link to="/login">
                  <Button variant="ghost" className="text-slate-300 hover:text-white">Sign In</Button>
                </Link>
                <Link to="/register">
                  <Button className="btn-primary">Get Started</Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16 relative z-10">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4 text-white" style={{ fontFamily: 'Playfair Display' }}>
            Choose Your <span className="text-gradient">Plan</span>
          </h1>
          <p className="text-lg text-slate-400 max-w-2xl mx-auto">
            Select the verification package that best fits your needs. All plans include AI-powered document analysis.
          </p>
          {propertyId && (
            <Badge variant="outline" className="mt-4 border-cyan-500/30 text-cyan-400">
              Purchasing for property: {propertyId}
            </Badge>
          )}
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-cyan-400" />
          </div>
        ) : (
          <div className="grid md:grid-cols-3 gap-8">
            {packages.map((plan) => (
              <div 
                key={plan.key} 
                className={`${plan.popular ? 'glass-card-blue' : 'glass-card'} relative`}
              >
                {plan.popular && (
                  <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-cyan-500 text-white border-0">
                    Most Popular
                  </Badge>
                )}
                <div className="text-center mb-6">
                  <div className={`h-14 w-14 rounded-xl mx-auto mb-4 flex items-center justify-center ${
                    plan.popular ? 'bg-cyan-500/20 text-cyan-400' : 'bg-slate-700 text-slate-400'
                  }`}>
                    {plan.icon}
                  </div>
                  <h3 className="text-xl font-semibold text-white">{plan.name}</h3>
                  <div className="mt-4">
                    <span className="text-4xl font-bold text-gradient">{plan.price}</span>
                    <span className="text-slate-400"> / property</span>
                  </div>
                </div>
                
                <ul className="space-y-3 mb-6">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-center gap-2 text-sm text-slate-300">
                      <CheckCircle2 className="h-4 w-4 text-cyan-400 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
                
                <Button
                  data-testid={`purchase-${plan.key}-btn`}
                  className={`w-full ${plan.popular ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => handlePurchase(plan.key)}
                  disabled={processingPayment}
                >
                  {processingPayment ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <CreditCard className="h-4 w-4 mr-2" />
                      Purchase
                    </>
                  )}
                </Button>
              </div>
            ))}
          </div>
        )}

        {/* Features Comparison */}
        <div className="mt-16">
          <h2 className="text-2xl font-semibold text-center text-white mb-8" style={{ fontFamily: 'Playfair Display' }}>
            What's <span className="text-gradient">Included</span>
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { title: "OCR Extraction", desc: "AI-powered text extraction from scanned documents" },
              { title: "Risk Analysis", desc: "Comprehensive risk scoring with detailed flags" },
              { title: "Title Chain", desc: "30-year ownership history reconstruction" },
              { title: "PDF Reports", desc: "Lawyer-ready downloadable reports" }
            ].map((item, index) => (
              <div key={index} className="glass-card">
                <h3 className="font-medium text-white mb-2">{item.title}</h3>
                <p className="text-sm text-slate-400">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Trust Badges */}
        <div className="mt-16 text-center">
          <p className="text-sm text-slate-500 mb-4">Trusted by thousands of property buyers across India</p>
          <div className="flex items-center justify-center gap-8 text-slate-400">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              <span className="text-sm">Secure Payments</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              <span className="text-sm">256-bit Encryption</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              <span className="text-sm">DPDP Compliant</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

// Missing import
const FileText = ({ className }) => (
  <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
    <polyline points="14 2 14 8 20 8"/>
    <line x1="16" x2="8" y1="13" y2="13"/>
    <line x1="16" x2="8" y1="17" y2="17"/>
    <line x1="10" x2="8" y1="9" y2="9"/>
  </svg>
);

export default Pricing;
