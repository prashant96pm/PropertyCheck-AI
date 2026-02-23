import React, { useEffect, useState } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { 
  Building2, 
  CheckCircle2, 
  Loader2,
  ArrowRight
} from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PaymentSuccess = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [status, setStatus] = useState('checking');
  const [paymentDetails, setPaymentDetails] = useState(null);

  const sessionId = searchParams.get('session_id');

  useEffect(() => {
    if (sessionId && isAuthenticated) {
      pollPaymentStatus();
    }
  }, [sessionId, isAuthenticated]);

  const pollPaymentStatus = async (attempts = 0) => {
    const maxAttempts = 10;
    const pollInterval = 2000;

    if (attempts >= maxAttempts) {
      setStatus('timeout');
      toast.error('Payment verification timed out');
      return;
    }

    try {
      const response = await axios.get(
        `${API}/payments/status/${sessionId}`,
        { withCredentials: true }
      );

      if (response.data.payment_status === 'paid') {
        setStatus('success');
        setPaymentDetails(response.data);
        toast.success('Payment successful!');
        return;
      } else if (response.data.status === 'expired') {
        setStatus('expired');
        return;
      }

      // Continue polling
      setTimeout(() => pollPaymentStatus(attempts + 1), pollInterval);
    } catch (error) {
      console.error('Payment status check error:', error);
      setTimeout(() => pollPaymentStatus(attempts + 1), pollInterval);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 noise-texture flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2">
            <Shield className="h-10 w-10 text-primary" />
            <span className="text-2xl font-semibold text-primary" style={{ fontFamily: 'Playfair Display' }}>
              PropertyCheck AI
            </span>
          </Link>
        </div>

        <Card className="card-base shadow-lg">
          <CardContent className="pt-8 pb-8 text-center">
            {status === 'checking' && (
              <>
                <Loader2 className="h-16 w-16 text-accent mx-auto mb-6 animate-spin" />
                <h2 className="text-2xl font-semibold text-primary mb-2" style={{ fontFamily: 'Playfair Display' }}>
                  Verifying Payment
                </h2>
                <p className="text-muted-foreground mb-6">
                  Please wait while we confirm your payment...
                </p>
              </>
            )}

            {status === 'success' && (
              <>
                <div className="h-16 w-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <CheckCircle2 className="h-10 w-10 text-emerald-600" />
                </div>
                <h2 className="text-2xl font-semibold text-primary mb-2" style={{ fontFamily: 'Playfair Display' }}>
                  Payment Successful!
                </h2>
                <p className="text-muted-foreground mb-6">
                  Your property verification report is now available.
                </p>
                {paymentDetails && (
                  <div className="bg-slate-50 p-4 rounded-sm mb-6 text-left">
                    <p className="text-sm text-muted-foreground">Amount Paid</p>
                    <p className="font-mono font-bold text-lg">
                      ${(paymentDetails.amount_total / 100).toFixed(2)} {paymentDetails.currency?.toUpperCase()}
                    </p>
                  </div>
                )}
                <Link to="/dashboard">
                  <Button data-testid="go-to-dashboard-btn" className="w-full btn-primary">
                    Go to Dashboard
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </>
            )}

            {status === 'expired' && (
              <>
                <div className="h-16 w-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <Shield className="h-10 w-10 text-amber-600" />
                </div>
                <h2 className="text-2xl font-semibold text-primary mb-2" style={{ fontFamily: 'Playfair Display' }}>
                  Session Expired
                </h2>
                <p className="text-muted-foreground mb-6">
                  Your payment session has expired. Please try again.
                </p>
                <Link to="/pricing">
                  <Button className="w-full btn-primary">
                    Try Again
                  </Button>
                </Link>
              </>
            )}

            {status === 'timeout' && (
              <>
                <div className="h-16 w-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <Shield className="h-10 w-10 text-amber-600" />
                </div>
                <h2 className="text-2xl font-semibold text-primary mb-2" style={{ fontFamily: 'Playfair Display' }}>
                  Verification Timeout
                </h2>
                <p className="text-muted-foreground mb-6">
                  We couldn't verify your payment. Please contact support if you were charged.
                </p>
                <Link to="/dashboard">
                  <Button className="w-full btn-secondary">
                    Go to Dashboard
                  </Button>
                </Link>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PaymentSuccess;
