import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Separator } from '../components/ui/separator';
import { Shield, Loader2, Mail, Lock, User, AlertCircle, CheckCircle2 } from 'lucide-react';

const Register = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { register, loginWithGoogle } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);

    try {
      await register(name, email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const features = [
    "AI-powered document verification",
    "30-year title chain reconstruction",
    "Real-time risk assessment",
    "Lawyer-ready PDF reports"
  ];

  return (
    <div className="min-h-screen bg-slate-50 noise-texture flex">
      {/* Left Panel - Features */}
      <div className="hidden lg:flex lg:w-1/2 bg-primary text-primary-foreground p-12 flex-col justify-between">
        <div>
          <Link to="/" className="inline-flex items-center gap-2 mb-12">
            <Shield className="h-10 w-10" />
            <span className="text-2xl font-semibold" style={{ fontFamily: 'Playfair Display' }}>
              PropertyCheck AI
            </span>
          </Link>
          
          <h1 className="text-4xl font-bold mb-6" style={{ fontFamily: 'Playfair Display' }}>
            Verify land ownership with confidence
          </h1>
          <p className="text-slate-300 text-lg mb-8">
            Join thousands of property buyers, developers, and legal professionals who trust PropertyCheck AI.
          </p>
          
          <ul className="space-y-4">
            {features.map((feature, index) => (
              <li key={index} className="flex items-center gap-3">
                <CheckCircle2 className="h-5 w-5 text-accent" />
                <span>{feature}</span>
              </li>
            ))}
          </ul>
        </div>
        
        <div className="text-sm text-slate-400">
          <p>Trusted by 10,000+ users across India</p>
        </div>
      </div>

      {/* Right Panel - Form */}
      <div className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          {/* Mobile Logo */}
          <div className="text-center mb-8 lg:hidden">
            <Link to="/" className="inline-flex items-center gap-2">
              <Shield className="h-10 w-10 text-primary" />
              <span className="text-2xl font-semibold text-primary" style={{ fontFamily: 'Playfair Display' }}>
                PropertyCheck AI
              </span>
            </Link>
          </div>

          <Card className="card-base shadow-lg">
            <CardHeader className="space-y-1">
              <CardTitle className="text-2xl" style={{ fontFamily: 'Playfair Display' }}>
                Create an account
              </CardTitle>
              <CardDescription>
                Get started with your free property verification
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* Google OAuth Button */}
              <Button
                data-testid="google-register-btn"
                type="button"
                variant="outline"
                className="w-full mb-4"
                onClick={loginWithGoogle}
              >
                <svg className="h-5 w-5 mr-2" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Continue with Google
              </Button>

              <div className="relative my-6">
                <Separator />
                <span className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-card px-2 text-xs text-muted-foreground">
                  or register with email
                </span>
              </div>

              {/* Error Message */}
              {error && (
                <div className="mb-4 p-3 rounded-sm bg-red-50 border border-red-200 flex items-center gap-2 text-sm text-red-700">
                  <AlertCircle className="h-4 w-4" />
                  {error}
                </div>
              )}

              {/* Registration Form */}
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Full Name</Label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="name"
                      data-testid="register-name-input"
                      type="text"
                      placeholder="John Doe"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="pl-10"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="email"
                      data-testid="register-email-input"
                      type="email"
                      placeholder="name@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="pl-10"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="password"
                      data-testid="register-password-input"
                      type="password"
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="pl-10"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Confirm Password</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="confirmPassword"
                      data-testid="register-confirm-password-input"
                      type="password"
                      placeholder="••••••••"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className="pl-10"
                      required
                    />
                  </div>
                </div>

                <Button
                  data-testid="register-submit-btn"
                  type="submit"
                  className="w-full btn-primary"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Creating account...
                    </>
                  ) : (
                    'Create Account'
                  )}
                </Button>
              </form>

              <p className="mt-6 text-center text-sm text-muted-foreground">
                Already have an account?{' '}
                <Link to="/login" className="text-accent hover:underline font-medium">
                  Sign in
                </Link>
              </p>
            </CardContent>
          </Card>

          <p className="mt-6 text-center text-xs text-muted-foreground">
            By creating an account, you agree to our{' '}
            <a href="#" className="underline">Terms of Service</a> and{' '}
            <a href="#" className="underline">Privacy Policy</a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
