import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { 
  Shield, 
  FileSearch, 
  AlertTriangle, 
  CheckCircle2, 
  Building2, 
  Scale, 
  FileText,
  ArrowRight,
  Star,
  Users,
  Clock,
  Languages
} from 'lucide-react';

const Landing = () => {
  const { isAuthenticated } = useAuth();

  const features = [
    {
      icon: <FileSearch className="h-6 w-6" />,
      title: "AI-Powered OCR",
      description: "Extract data from Sale Deeds, EC, RTC, Khata documents in multiple Indian languages"
    },
    {
      icon: <Shield className="h-6 w-6" />,
      title: "Risk Detection",
      description: "Identify fraud, double registration, and ownership discrepancies instantly"
    },
    {
      icon: <Scale className="h-6 w-6" />,
      title: "Legal Risk Score",
      description: "Get 0-100 risk score with RED/YELLOW/GREEN status indicators"
    },
    {
      icon: <FileText className="h-6 w-6" />,
      title: "Lawyer-Ready Reports",
      description: "Download comprehensive PDF reports for legal due diligence"
    }
  ];

  const stats = [
    { value: "50,000+", label: "Properties Verified" },
    { value: "99.2%", label: "Accuracy Rate" },
    { value: "< 2 min", label: "Average Report Time" },
    { value: "12", label: "Indian Languages" }
  ];

  const pricing = [
    {
      name: "Basic",
      price: "₹499",
      features: ["OCR Document Analysis", "Basic Risk Score", "Email Support"],
      popular: false
    },
    {
      name: "Standard",
      price: "₹999",
      features: ["Full OCR Extraction", "AI Risk Analysis", "30-Year Title Chain", "PDF Report"],
      popular: true
    },
    {
      name: "Premium",
      price: "₹1,999",
      features: ["Everything in Standard", "Government Records Check", "Priority Support", "Legal Consultation"],
      popular: false
    }
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Navigation */}
      <nav className="glass-header sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <Shield className="h-8 w-8 text-primary" />
              <span className="text-xl font-semibold text-primary" style={{ fontFamily: 'Playfair Display' }}>
                PropertyCheck AI
              </span>
            </div>
            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-sm text-muted-foreground hover:text-primary transition-colors">Features</a>
              <a href="#how-it-works" className="text-sm text-muted-foreground hover:text-primary transition-colors">How it Works</a>
              <a href="#pricing" className="text-sm text-muted-foreground hover:text-primary transition-colors">Pricing</a>
            </div>
            <div className="flex items-center gap-4">
              {isAuthenticated ? (
                <Link to="/dashboard">
                  <Button data-testid="dashboard-btn" className="btn-primary">
                    Dashboard
                  </Button>
                </Link>
              ) : (
                <>
                  <Link to="/login">
                    <Button data-testid="login-btn" variant="ghost" className="text-sm">
                      Sign In
                    </Button>
                  </Link>
                  <Link to="/register">
                    <Button data-testid="get-started-btn" className="btn-primary">
                      Get Started
                    </Button>
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero-gradient noise-texture py-24 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-12 gap-12 items-center">
            <div className="lg:col-span-7">
              <Badge className="mb-6 bg-accent/10 text-accent border-accent/20 hover:bg-accent/10">
                <Star className="h-3 w-3 mr-1" /> Trusted by 10,000+ Property Buyers
              </Badge>
              <h1 className="text-5xl md:text-7xl font-bold text-primary tracking-tight mb-6" style={{ fontFamily: 'Playfair Display' }}>
                Verify Land Ownership with AI Precision
              </h1>
              <p className="text-lg md:text-xl text-muted-foreground leading-relaxed mb-8 max-w-2xl">
                PropertyCheck AI instantly validates property documents, detects fraud, reconstructs 30-year title chains, and generates lawyer-ready risk reports for Indian real estate.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link to="/register">
                  <Button data-testid="hero-cta-btn" size="lg" className="btn-primary text-base">
                    Start Free Verification
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </Link>
                <Button data-testid="hero-demo-btn" size="lg" variant="outline" className="btn-secondary text-base">
                  View Sample Report
                </Button>
              </div>
              
              {/* Trust Indicators */}
              <div className="mt-12 flex flex-wrap gap-6 text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                  DPDP Act Compliant
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                  256-bit Encryption
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                  CERSAI Integrated
                </div>
              </div>
            </div>
            
            <div className="lg:col-span-5">
              <div className="relative">
                <img 
                  src="https://images.unsplash.com/photo-1764686630524-2d399d87fa2d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1NTJ8MHwxfHNlYXJjaHw0fHxtb2Rlcm4lMjBpbmRpYW4lMjBob3VzZSUyMGV4dGVyaW9yJTIwYXJjaGl0ZWN0dXJlfGVufDB8fHx8MTc3MTc0OTE1OXww&ixlib=rb-4.1.0&q=85"
                  alt="Modern Architecture"
                  className="rounded-sm shadow-xl w-full"
                />
                {/* Floating Risk Card */}
                <Card className="absolute -bottom-6 -left-6 shadow-lg animate-fade-in">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="h-12 w-12 rounded-sm bg-emerald-100 flex items-center justify-center">
                        <span className="text-emerald-700 font-bold font-mono">87</span>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Risk Score</p>
                        <p className="text-sm font-semibold text-emerald-700">SAFE TO BUY</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-12 bg-primary text-primary-foreground">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <p className="text-3xl md:text-4xl font-bold font-mono">{stat.value}</p>
                <p className="text-sm text-slate-300 mt-1">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-semibold text-primary tracking-tight mb-4" style={{ fontFamily: 'Playfair Display' }}>
              AI-Powered Due Diligence
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Comprehensive property verification powered by advanced AI and integrated with government land records
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <Card key={index} className="card-base card-interactive group">
                <CardContent className="p-6">
                  <div className="h-12 w-12 rounded-sm bg-accent/10 text-accent flex items-center justify-center mb-4 group-hover:bg-accent group-hover:text-white transition-colors duration-200">
                    {feature.icon}
                  </div>
                  <h3 className="text-lg font-semibold text-primary mb-2">{feature.title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How it Works Section */}
      <section id="how-it-works" className="py-24 bg-slate-50 noise-texture">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-semibold text-primary tracking-tight mb-4" style={{ fontFamily: 'Playfair Display' }}>
              How It Works
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Three simple steps to comprehensive property verification
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: "01", title: "Upload Documents", desc: "Upload Sale Deed, EC, RTC, Khata, or any land document in PDF or image format" },
              { step: "02", title: "AI Analysis", desc: "Our AI extracts data, verifies against government records, and detects anomalies" },
              { step: "03", title: "Get Report", desc: "Download lawyer-ready PDF report with risk score and legal recommendations" }
            ].map((item, index) => (
              <div key={index} className="relative">
                <div className="text-8xl font-bold text-slate-200 absolute -top-4 left-0" style={{ fontFamily: 'Playfair Display' }}>
                  {item.step}
                </div>
                <div className="relative z-10 pt-12">
                  <h3 className="text-xl font-semibold text-primary mb-3">{item.title}</h3>
                  <p className="text-muted-foreground">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-16">
            <img 
              src="https://images.pexels.com/photos/7841450/pexels-photo-7841450.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
              alt="Document Review Process"
              className="rounded-sm shadow-xl w-full max-w-4xl mx-auto"
            />
          </div>
        </div>
      </section>

      {/* Supported Documents */}
      <section className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-5xl font-semibold text-primary tracking-tight mb-6" style={{ fontFamily: 'Playfair Display' }}>
                Supports All Indian Land Documents
              </h2>
              <p className="text-lg text-muted-foreground mb-8">
                Our AI understands documents across 12 Indian languages and all state-specific formats
              </p>
              
              <div className="grid grid-cols-2 gap-4">
                {["Sale Deed", "Mother Deed", "EC Certificate", "RTC / Pahani", "7/12 Extract", "Khata Certificate", "Mutation Records", "NOC Documents"].map((doc, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-accent" />
                    <span className="text-sm">{doc}</span>
                  </div>
                ))}
              </div>
              
              <div className="mt-8 flex items-center gap-2 text-sm text-muted-foreground">
                <Languages className="h-4 w-4" />
                Supports: Kannada, Hindi, Tamil, Telugu, Marathi, Gujarati, Bengali, Malayalam & more
              </div>
            </div>
            
            <div>
              <img 
                src="https://images.pexels.com/photos/7841462/pexels-photo-7841462.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
                alt="Legal Professionals"
                className="rounded-sm shadow-xl"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-24 bg-slate-50 noise-texture">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-semibold text-primary tracking-tight mb-4" style={{ fontFamily: 'Playfair Display' }}>
              Simple, Transparent Pricing
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Pay per property verification. No subscriptions, no hidden fees.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {pricing.map((plan, index) => (
              <Card key={index} className={`card-base relative ${plan.popular ? 'border-accent shadow-lg' : ''}`}>
                {plan.popular && (
                  <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-accent text-white">
                    Most Popular
                  </Badge>
                )}
                <CardContent className="p-6">
                  <h3 className="text-xl font-semibold text-primary mb-2">{plan.name}</h3>
                  <div className="mb-6">
                    <span className="text-4xl font-bold text-primary">{plan.price}</span>
                    <span className="text-muted-foreground"> / property</span>
                  </div>
                  <ul className="space-y-3 mb-6">
                    {plan.features.map((feature, fIndex) => (
                      <li key={fIndex} className="flex items-center gap-2 text-sm">
                        <CheckCircle2 className="h-4 w-4 text-accent" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                  <Link to="/register">
                    <Button 
                      data-testid={`pricing-${plan.name.toLowerCase()}-btn`}
                      className={`w-full ${plan.popular ? 'btn-primary' : 'btn-secondary'}`}
                    >
                      Get Started
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-primary text-primary-foreground">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-5xl font-semibold tracking-tight mb-6" style={{ fontFamily: 'Playfair Display' }}>
            Ready to Verify Your Property?
          </h2>
          <p className="text-lg text-slate-300 mb-8 max-w-2xl mx-auto">
            Join thousands of property buyers, developers, and legal professionals who trust PropertyCheck AI for due diligence.
          </p>
          <Link to="/register">
            <Button data-testid="cta-start-btn" size="lg" variant="secondary" className="bg-white text-primary hover:bg-slate-100">
              Start Free Verification
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-slate-900 text-slate-400">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Shield className="h-6 w-6 text-white" />
                <span className="text-lg font-semibold text-white" style={{ fontFamily: 'Playfair Display' }}>
                  PropertyCheck AI
                </span>
              </div>
              <p className="text-sm">
                AI-powered land verification platform for Indian real estate.
              </p>
            </div>
            
            <div>
              <h4 className="text-white font-medium mb-4">Product</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#features" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="#pricing" className="hover:text-white transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition-colors">API Access</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-white font-medium mb-4">Company</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white transition-colors">About Us</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-white font-medium mb-4">Legal</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Terms of Service</a></li>
                <li><a href="#" className="hover:text-white transition-colors">DPDP Compliance</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-slate-800 mt-12 pt-8 text-sm text-center">
            <p>© 2024 PropertyCheck AI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
