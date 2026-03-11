import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Loader2, CheckCircle2, Clock, AlertTriangle, Play, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const JOB_TYPES = {
  risk_analysis: { label: 'AI Risk Analysis', color: 'cyan' },
  document_ocr: { label: 'Document OCR', color: 'amber' },
  govt_data_retrieval: { label: 'Govt Data Retrieval', color: 'violet' },
  title_verification: { label: 'Title Verification', color: 'emerald' },
  valuation_report: { label: 'Valuation Report', color: 'pink' },
};

const BackgroundJobs = ({ propertyId }) => {
  const { isAuthenticated } = useAuth();
  const [jobs, setJobs] = useState([]);
  const [submitting, setSubmitting] = useState(null);
  const pollingRef = useRef({});

  useEffect(() => {
    if (isAuthenticated) fetchJobs();
    return () => Object.values(pollingRef.current).forEach(clearInterval);
  }, [isAuthenticated]);

  const fetchJobs = async () => {
    try {
      const res = await axios.get(`${API}/jobs/list`, { withCredentials: true });
      setJobs(res.data.jobs || []);
      res.data.jobs?.forEach(j => {
        if (j.status === 'processing' || j.status === 'queued') startPolling(j.job_id);
      });
    } catch (err) { /* ignore */ }
  };

  const submitJob = async (jobType) => {
    setSubmitting(jobType);
    try {
      const res = await axios.post(`${API}/jobs/submit`, {
        job_type: jobType,
        property_id: propertyId,
      }, { withCredentials: true });
      toast.success(`${JOB_TYPES[jobType].label} job submitted`);
      setJobs(prev => [{ ...res.data, job_type: jobType, property_id: propertyId, progress: 0, steps: [], status: 'queued', created_at: new Date().toISOString() }, ...prev]);
      startPolling(res.data.job_id);
    } catch (err) {
      toast.error('Failed to submit job');
    } finally {
      setSubmitting(null);
    }
  };

  const startPolling = (jobId) => {
    if (pollingRef.current[jobId]) return;
    pollingRef.current[jobId] = setInterval(async () => {
      try {
        const res = await axios.get(`${API}/jobs/status/${jobId}`, { withCredentials: true });
        setJobs(prev => prev.map(j => j.job_id === jobId ? res.data : j));
        if (res.data.status === 'completed' || res.data.status === 'failed') {
          clearInterval(pollingRef.current[jobId]);
          delete pollingRef.current[jobId];
          if (res.data.status === 'completed') toast.success(`Job completed: ${JOB_TYPES[res.data.job_type]?.label}`);
        }
      } catch (err) {
        clearInterval(pollingRef.current[jobId]);
        delete pollingRef.current[jobId];
      }
    }, 2000);
  };

  const statusIcon = (status) => {
    if (status === 'completed') return <CheckCircle2 className="h-4 w-4 text-emerald-400" />;
    if (status === 'failed') return <AlertTriangle className="h-4 w-4 text-red-400" />;
    if (status === 'processing') return <Loader2 className="h-4 w-4 text-cyan-400 animate-spin" />;
    return <Clock className="h-4 w-4 text-slate-400" />;
  };

  const propertyJobs = jobs.filter(j => j.property_id === propertyId);

  return (
    <div data-testid="background-jobs-panel">
      {/* Submit Buttons */}
      <div className="flex flex-wrap gap-2 mb-6">
        {Object.entries(JOB_TYPES).map(([type, info]) => (
          <Button
            key={type}
            data-testid={`submit-job-${type}`}
            variant="outline"
            size="sm"
            className={`border-slate-700 text-slate-300 hover:text-white hover:bg-${info.color}-500/10`}
            onClick={() => submitJob(type)}
            disabled={!!submitting}
          >
            {submitting === type ? <Loader2 className="h-3 w-3 mr-1.5 animate-spin" /> : <Play className="h-3 w-3 mr-1.5" />}
            {info.label}
          </Button>
        ))}
      </div>

      {/* Job List */}
      {propertyJobs.length > 0 ? (
        <div className="space-y-3">
          {propertyJobs.map(job => (
            <div key={job.job_id} className="p-4 bg-slate-800/50 rounded-lg border border-slate-700/50" data-testid={`job-${job.job_id}`}>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  {statusIcon(job.status)}
                  <span className="text-sm font-medium text-white">{JOB_TYPES[job.job_type]?.label || job.job_type}</span>
                </div>
                <Badge className={`text-xs ${
                  job.status === 'completed' ? 'bg-emerald-500/20 text-emerald-400' :
                  job.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                  job.status === 'processing' ? 'bg-cyan-500/20 text-cyan-400' :
                  'bg-slate-700 text-slate-300'
                }`}>{job.status}</Badge>
              </div>

              {/* Progress Bar */}
              <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden mb-2">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    job.status === 'completed' ? 'bg-emerald-400' :
                    job.status === 'failed' ? 'bg-red-400' : 'bg-cyan-400'
                  }`}
                  style={{ width: `${job.progress || 0}%` }}
                />
              </div>

              <div className="flex items-center justify-between text-xs text-slate-500">
                <span>{job.current_step || 'Waiting...'}</span>
                <span>{job.progress || 0}%</span>
              </div>

              {/* Steps */}
              {job.steps?.length > 0 && job.status !== 'completed' && (
                <div className="mt-2 space-y-1">
                  {job.steps.slice(-3).map((step, i) => (
                    <div key={i} className="flex items-center gap-1.5 text-xs">
                      <CheckCircle2 className="h-3 w-3 text-emerald-400" />
                      <span className="text-slate-400">{step.name}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8">
          <Clock className="h-10 w-10 text-slate-600 mx-auto mb-3" />
          <p className="text-sm text-slate-400">No background jobs for this property</p>
          <p className="text-xs text-slate-500 mt-1">Submit a job above to start processing</p>
        </div>
      )}
    </div>
  );
};

export default BackgroundJobs;
