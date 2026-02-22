import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { 
  Shield, 
  CheckCircle2, 
  ArrowLeft,
  Loader2,
  CreditCard
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

      // Redirect to Stripe checkout
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
      popular: false
    },
    {
      key: 'standard',
      name: pricing.standard.name,
      price: `₹${pricing.standard.amount}`,
      features: pricing.standard.features,
      popular: true
    },
    {
      key: 'premium',
      name: pricing.premium.name,
      price: `₹${pricing.premium.amount}`,
      features: pricing.premium.features,
      popular: false
    }
  ] : [];

  return (
    <div className="min-h-screen bg-slate-50 noise-texture">
      {/* Navigation */}
      <nav className="glass-header sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-4">
              <Link to={isAuthenticated ? "/dashboard" : "/"} className="text-muted-foreground hover:text-primary transition-colors">
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <Link to="/" className="flex items-center gap-2">
                <Shield className="h-8 w-8 text-primary" />
                <span className="text-xl font-semibold text-primary" style={{ fontFamily: 'Playfair Display' }}>
                  PropertyCheck AI
                </span>
              </Link>
            </div>
            
            {!isAuthenticated && (
              <div className="flex items-center gap-4">
                <Link to="/login">
                  <Button variant="ghost">Sign In</Button>
                </Link>
                <Link to="/register">
                  <Button className="btn-primary">Get Started</Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-primary tracking-tight mb-4" style={{ fontFamily: 'Playfair Display' }}>
            Choose Your Plan
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Select the verification package that best fits your needs. All plans include AI-powered document analysis.
          </p>
          {propertyId && (
            <Badge variant="outline" className="mt-4">
              Purchasing for property: {propertyId}
            </Badge>
          )}
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-accent" />
          </div>
        ) : (
          <div className="grid md:grid-cols-3 gap-8">
            {packages.map((plan) => (
              <Card 
                key={plan.key} 
                className={`card-base relative ${plan.popular ? 'border-accent shadow-lg' : ''}`}
              >
                {plan.popular && (
                  <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-accent text-white">
                    Most Popular
                  </Badge>
                )}
                <CardHeader className="text-center">
                  <CardTitle className="text-xl">{plan.name}</CardTitle>
                  <div className="mt-4">
                    <span className="text-4xl font-bold text-primary">{plan.price}</span>
                    <span className="text-muted-foreground"> / property</span>
                  </div>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3 mb-6">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-center gap-2 text-sm">
                        <CheckCircle2 className="h-4 w-4 text-accent flex-shrink-0" />
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
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Features Comparison */}
        <div className="mt-16">
          <h2 className="text-2xl font-semibold text-center mb-8" style={{ fontFamily: 'Playfair Display' }}>
            What's Included
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { title: "OCR Extraction", desc: "AI-powered text extraction from scanned documents" },
              { title: "Risk Analysis", desc: "Comprehensive risk scoring with detailed flags" },
              { title: "Title Chain", desc: "30-year ownership history reconstruction" },
              { title: "PDF Reports", desc: "Lawyer-ready downloadable reports" }
            ].map((item, index) => (
              <Card key={index} className="card-base">
                <CardContent className="pt-6">
                  <h3 className="font-medium mb-2">{item.title}</h3>
                  <p className="text-sm text-muted-foreground">{item.desc}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Trust Badges */}
        <div className="mt-16 text-center">
          <p className="text-sm text-muted-foreground mb-4">Trusted by thousands of property buyers across India</p>
          <div className="flex items-center justify-center gap-8 text-muted-foreground">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
              <span className="text-sm">Secure Payments</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
              <span className="text-sm">256-bit Encryption</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
              <span className="text-sm">DPDP Compliant</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Pricing;
