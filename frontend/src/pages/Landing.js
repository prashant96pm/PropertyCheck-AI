import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import RiskMeter from '../components/RiskMeter';
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
  Languages,
  Zap,
  Lock,
  Globe,
  Sparkles
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
      title: "Fraud Detection",
      description: "Identify double registration, forged documents, and ownership discrepancies"
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
    },
    {
      icon: <Globe className="h-6 w-6" />,
      title: "Government Integration",
      description: "Verify against Bhoomi, Bhulekh, Dharani and other land record portals"
    },
    {
      icon: <Zap className="h-6 w-6" />,
      title: "Instant Results",
      description: "Get verification results in under 2 minutes with AI analysis"
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
      popular: false,
      glow: 'glass-card'
    },
    {
      name: "Standard",
      price: "₹999",
      features: ["Full OCR Extraction", "AI Risk Analysis", "30-Year Title Chain", "PDF Report"],
      popular: true,
      glow: 'glass-card-blue'
    },
    {
      name: "Premium",
      price: "₹1,999",
      features: ["Everything in Standard", "Government Records Check", "Priority Support", "Legal Consultation"],
      popular: false,
      glow: 'glass-card'
    }
  ];

  return (
    <div className="min-h-screen gradient-bg relative overflow-hidden">
      {/* Animated Background Grid */}
      <div className="absolute inset-0 grid-bg opacity-50" />
      
      {/* Navigation */}
      <nav className="glass-header sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <Shield className="h-8 w-8 text-cyan-400" />
              <span className="text-xl font-semibold text-white" style={{ fontFamily: 'Playfair Display' }}>
                PropertyCheck AI
              </span>
            </div>
            <div className="hidden md:flex items-center gap-8">
              <Link to="/search" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors">Search Properties</Link>
              <a href="#features" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors">Features</a>
              <a href="#how-it-works" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors">How it Works</a>
              <a href="#pricing" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors">Pricing</a>
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
                    <Button data-testid="login-btn" variant="ghost" className="text-sm text-slate-300 hover:text-white">
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
      <section className="relative py-24 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-12 gap-12 items-center">
            <div className="lg:col-span-7 relative z-10">
              <Badge className="mb-6 bg-cyan-500/20 text-cyan-400 border-cyan-500/30 hover:bg-cyan-500/20">
                <Star className="h-3 w-3 mr-1" /> Trusted by 10,000+ Property Buyers
              </Badge>
              <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6" style={{ fontFamily: 'Playfair Display' }}>
                <span className="text-white">Verify Land</span>
                <br />
                <span className="text-gradient glow-text">Ownership with AI</span>
                <br />
                <span className="text-white">Precision</span>
              </h1>
              <p className="text-lg md:text-xl text-slate-400 leading-relaxed mb-8 max-w-2xl">
                PropertyCheck AI instantly validates property documents, detects fraud, reconstructs 30-year title chains, and generates lawyer-ready risk reports for Indian real estate.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link to="/register">
                  <Button data-testid="hero-cta-btn" size="lg" className="btn-primary text-base">
                    <Sparkles className="mr-2 h-5 w-5" />
                    Start Free Verification
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </Link>
                <Link to="/search">
                  <Button data-testid="hero-search-btn" size="lg" className="btn-secondary text-base">
                    <FileSearch className="mr-2 h-5 w-5" />
                    Search Properties
                  </Button>
                </Link>
              </div>
              
              {/* Trust Indicators */}
              <div className="mt-12 flex flex-wrap gap-6 text-sm text-slate-400">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                  DPDP Act Compliant
                </div>
                <div className="flex items-center gap-2">
                  <Lock className="h-4 w-4 text-emerald-400" />
                  256-bit Encryption
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                  CERSAI Integrated
                </div>
              </div>
            </div>
            
            <div className="lg:col-span-5 flex justify-center">
              {/* Risk Meter Demo */}
              <div className="relative">
                <div className="absolute inset-0 bg-cyan-500/20 blur-3xl rounded-full" />
                <div className="glass-card-blue p-8 relative">
                  <p className="text-sm text-slate-400 text-center mb-4 uppercase tracking-wider">Live Risk Assessment</p>
                  <RiskMeter score={87} size={220} />
                  <div className="mt-6 space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-400">Title Chain</span>
                      <span className="text-emerald-400">✓ Verified</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-400">Government Records</span>
                      <span className="text-emerald-400">✓ Matched</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-400">Encumbrances</span>
                      <span className="text-emerald-400">✓ Clear</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-12 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="glass-card">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              {stats.map((stat, index) => (
                <div key={index} className="text-center">
                  <p className="text-3xl md:text-4xl font-bold font-mono text-gradient">{stat.value}</p>
                  <p className="text-sm text-slate-400 mt-1">{stat.label}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-semibold tracking-tight mb-4 text-white" style={{ fontFamily: 'Playfair Display' }}>
              AI-Powered <span className="text-gradient">Due Diligence</span>
            </h2>
            <p className="text-lg text-slate-400 max-w-2xl mx-auto">
              Comprehensive property verification powered by advanced AI and integrated with government land records
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <div key={index} className="glass-card group hover:border-cyan-500/30 transition-all duration-300 cursor-pointer">
                <div className="h-12 w-12 rounded-lg bg-cyan-500/10 text-cyan-400 flex items-center justify-center mb-4 group-hover:bg-cyan-500/20 group-hover:shadow-lg group-hover:shadow-cyan-500/20 transition-all duration-300">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-sm text-slate-400 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it Works Section */}
      <section id="how-it-works" className="py-24 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-semibold tracking-tight mb-4 text-white" style={{ fontFamily: 'Playfair Display' }}>
              How It <span className="text-gradient">Works</span>
            </h2>
            <p className="text-lg text-slate-400 max-w-2xl mx-auto">
              Three simple steps to comprehensive property verification
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: "01", title: "Upload Documents", desc: "Upload Sale Deed, EC, RTC, Khata, or any land document in PDF or image format", icon: <FileSearch className="h-8 w-8" /> },
              { step: "02", title: "AI Analysis", desc: "Our AI extracts data, verifies against government records, and detects anomalies", icon: <Sparkles className="h-8 w-8" /> },
              { step: "03", title: "Get Report", desc: "Download lawyer-ready PDF report with risk score and legal recommendations", icon: <FileText className="h-8 w-8" /> }
            ].map((item, index) => (
              <div key={index} className="glass-card relative group">
                <div className="absolute -top-4 -left-4 text-7xl font-bold text-cyan-500/10" style={{ fontFamily: 'Playfair Display' }}>
                  {item.step}
                </div>
                <div className="relative z-10">
                  <div className="h-16 w-16 rounded-xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center mb-4">
                    {item.icon}
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-3">{item.title}</h3>
                  <p className="text-slate-400">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Supported Documents */}
      <section className="py-24 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-5xl font-semibold tracking-tight mb-6 text-white" style={{ fontFamily: 'Playfair Display' }}>
                Supports All <span className="text-gradient">Indian Land Documents</span>
              </h2>
              <p className="text-lg text-slate-400 mb-8">
                Our AI understands documents across 12 Indian languages and all state-specific formats
              </p>
              
              <div className="grid grid-cols-2 gap-4">
                {["Sale Deed", "Mother Deed", "EC Certificate", "RTC / Pahani", "7/12 Extract", "Khata Certificate", "Mutation Records", "NOC Documents"].map((doc, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-cyan-400" />
                    <span className="text-sm text-slate-300">{doc}</span>
                  </div>
                ))}
              </div>
              
              <div className="mt-8 flex items-center gap-2 text-sm text-slate-400">
                <Languages className="h-4 w-4 text-cyan-400" />
                Supports: Kannada, Hindi, Tamil, Telugu, Marathi, Gujarati, Bengali, Malayalam & more
              </div>
            </div>
            
            <div className="glass-card-green">
              <img 
                src="https://images.pexels.com/photos/7841462/pexels-photo-7841462.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
                alt="Legal Professionals"
                className="rounded-lg opacity-80"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-24 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-semibold tracking-tight mb-4 text-white" style={{ fontFamily: 'Playfair Display' }}>
              Simple, <span className="text-gradient">Transparent Pricing</span>
            </h2>
            <p className="text-lg text-slate-400 max-w-2xl mx-auto">
              Pay per property verification. No subscriptions, no hidden fees.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {pricing.map((plan, index) => (
              <div key={index} className={`${plan.glow} relative`}>
                {plan.popular && (
                  <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-cyan-500 text-white border-0">
                    Most Popular
                  </Badge>
                )}
                <h3 className="text-xl font-semibold text-white mb-2">{plan.name}</h3>
                <div className="mb-6">
                  <span className="text-4xl font-bold text-gradient">{plan.price}</span>
                  <span className="text-slate-400"> / property</span>
                </div>
                <ul className="space-y-3 mb-6">
                  {plan.features.map((feature, fIndex) => (
                    <li key={fIndex} className="flex items-center gap-2 text-sm text-slate-300">
                      <CheckCircle2 className="h-4 w-4 text-cyan-400" />
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
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 relative">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="glass-card-blue">
            <h2 className="text-3xl md:text-5xl font-semibold tracking-tight mb-6 text-white" style={{ fontFamily: 'Playfair Display' }}>
              Ready to <span className="text-gradient">Verify Your Property?</span>
            </h2>
            <p className="text-lg text-slate-400 mb-8 max-w-2xl mx-auto">
              Join thousands of property buyers, developers, and legal professionals who trust PropertyCheck AI for due diligence.
            </p>
            <Link to="/register">
              <Button data-testid="cta-start-btn" size="lg" className="btn-primary">
                <Sparkles className="mr-2 h-5 w-5" />
                Start Free Verification
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-slate-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Shield className="h-6 w-6 text-cyan-400" />
                <span className="text-lg font-semibold text-white" style={{ fontFamily: 'Playfair Display' }}>
                  PropertyCheck AI
                </span>
              </div>
              <p className="text-sm text-slate-500">
                AI-powered land verification platform for Indian real estate.
              </p>
            </div>
            
            <div>
              <h4 className="text-white font-medium mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-slate-500">
                <li><a href="#features" className="hover:text-cyan-400 transition-colors">Features</a></li>
                <li><a href="#pricing" className="hover:text-cyan-400 transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:text-cyan-400 transition-colors">API Access</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-white font-medium mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-slate-500">
                <li><a href="#" className="hover:text-cyan-400 transition-colors">About Us</a></li>
                <li><a href="#" className="hover:text-cyan-400 transition-colors">Contact</a></li>
                <li><a href="#" className="hover:text-cyan-400 transition-colors">Careers</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-white font-medium mb-4">Legal</h4>
              <ul className="space-y-2 text-sm text-slate-500">
                <li><a href="#" className="hover:text-cyan-400 transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-cyan-400 transition-colors">Terms of Service</a></li>
                <li><a href="#" className="hover:text-cyan-400 transition-colors">DPDP Compliance</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-slate-800/50 mt-12 pt-8 text-sm text-center text-slate-500">
            <p>© 2024 PropertyCheck AI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
