import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import {
  Loader2, CheckCircle2, Clock, AlertTriangle, Download,
  ExternalLink, RefreshCw, Globe, FileText, Search
} from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const STATE_LABELS = {
  karnataka: 'Karnataka', telangana: 'Telangana', tamilnadu: 'Tamil Nadu',
  maharashtra: 'Maharashtra', andhrapradesh: 'Andhra Pradesh', uttarpradesh: 'Uttar Pradesh',
  rajasthan: 'Rajasthan', madhyapradesh: 'Madhya Pradesh', gujarat: 'Gujarat',
  haryana: 'Haryana', punjab: 'Punjab', westbengal: 'West Bengal',
  kerala: 'Kerala', odisha: 'Odisha', bihar: 'Bihar', jharkhand: 'Jharkhand',
  chhattisgarh: 'Chhattisgarh', himachalpradesh: 'Himachal Pradesh',
  uttarakhand: 'Uttarakhand', goa: 'Goa',
};

const GovDataBridge = ({ propertyId, property }) => {
  const { isAuthenticated } = useAuth();
  const [portals, setPortals] = useState(null);
  const [selectedState, setSelectedState] = useState('');
  const [selectedDoc, setSelectedDoc] = useState('');
  const [inputs, setInputs] = useState({});
  const [activeJobs, setActiveJobs] = useState([]);
  const [records, setRecords] = useState([]);
  const [fetching, setFetching] = useState(false);
  const pollRef = useRef({});

  useEffect(() => {
    fetchPortals();
    if (isAuthenticated && propertyId) fetchRecords();
    return () => Object.values(pollRef.current).forEach(clearInterval);
  }, [isAuthenticated, propertyId]);

  // Auto-select state based on property
  useEffect(() => {
    if (property?.state) {
      const key = property.state.toLowerCase().replace(/\s+/g, '');
      const match = Object.keys(STATE_LABELS).find(k => k === key || STATE_LABELS[k].toLowerCase() === property.state.toLowerCase());
      if (match) setSelectedState(match);
    }
  }, [property]);

  const fetchPortals = async () => {
    try {
      const res = await axios.get(`${API}/gov/portals/status`);
      setPortals(res.data.portals);
    } catch (err) { /* ignore */ }
  };

  const fetchRecords = async () => {
    try {
      const res = await axios.get(`${API}/gov/records/${propertyId}`, { withCredentials: true });
      setRecords(res.data.records || []);
    } catch (err) { /* ignore */ }
  };

  const handleFetch = async () => {
    if (!selectedState || !selectedDoc) {
      toast.error('Select a state and document type');
      return;
    }
    setFetching(true);
    try {
      const res = await axios.post(`${API}/gov/fetch`, {
        state: selectedState,
        documentType: selectedDoc,
        inputs: {
          ...inputs,
          district: inputs.district || property?.district || '',
          surveyNumber: inputs.surveyNumber || property?.survey_no || '',
        },
        propertyId,
      }, { withCredentials: true });

      if (res.data.status === 'CACHED') {
        toast.success('Record found in cache!');
        fetchRecords();
      } else if (res.data.job_id) {
        toast.success(`Fetching ${selectedDoc} from ${STATE_LABELS[selectedState]}...`);
        setActiveJobs(prev => [...prev, { ...res.data, state: selectedState, document_type: selectedDoc }]);
        startPolling(res.data.job_id);
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to submit fetch request');
    } finally {
      setFetching(false);
    }
  };

  const startPolling = (jobId) => {
    if (pollRef.current[jobId]) return;
    pollRef.current[jobId] = setInterval(async () => {
      try {
        const res = await axios.get(`${API}/gov/job/${jobId}`, { withCredentials: true });
        setActiveJobs(prev => prev.map(j => j.job_id === jobId ? { ...j, ...res.data } : j));
        if (res.data.status === 'COMPLETED' || res.data.status === 'FAILED') {
          clearInterval(pollRef.current[jobId]);
          delete pollRef.current[jobId];
          if (res.data.status === 'COMPLETED') {
            toast.success('Record fetched successfully!');
            fetchRecords();
          }
        }
      } catch (err) {
        clearInterval(pollRef.current[jobId]);
        delete pollRef.current[jobId];
      }
    }, 3000);
  };

  const portalDocs = selectedState && portals?.[selectedState]?.documents || [];
  const portalInputs = selectedState ? (portals?.[selectedState]?.inputs || []) : [];

  return (
    <div data-testid="gov-data-bridge-panel">
      {/* Fetch Form */}
      <div className="p-4 bg-slate-800/50 rounded-lg border border-slate-700/50 mb-6">
        <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
          <Search className="h-4 w-4 text-cyan-400" />Fetch Live Government Records
        </h4>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-3">
          {/* State Select */}
          <select
            data-testid="gov-state-select"
            value={selectedState}
            onChange={e => { setSelectedState(e.target.value); setSelectedDoc(''); setInputs({}); }}
            className="input-glass text-sm"
          >
            <option value="">Select State</option>
            {Object.entries(STATE_LABELS).map(([k, v]) => (
              <option key={k} value={k}>{v}</option>
            ))}
          </select>

          {/* Document Type Select */}
          <select
            data-testid="gov-doc-select"
            value={selectedDoc}
            onChange={e => setSelectedDoc(e.target.value)}
            className="input-glass text-sm"
            disabled={!selectedState}
          >
            <option value="">Select Document</option>
            {portalDocs.map(d => (
              <option key={d} value={d}>{d.replace(/_/g, ' ')}</option>
            ))}
          </select>

          {/* Survey/Khasra Number */}
          <input
            data-testid="gov-survey-input"
            type="text"
            placeholder="Survey / Khasra No."
            value={inputs.surveyNumber || inputs.khasraNumber || inputs.plotNumber || inputs.gutNumber || ''}
            onChange={e => {
              const key = portalInputs.includes('surveyNumber') ? 'surveyNumber' :
                         portalInputs.includes('khasraNumber') ? 'khasraNumber' :
                         portalInputs.includes('plotNumber') ? 'plotNumber' :
                         portalInputs.includes('gutNumber') ? 'gutNumber' : 'surveyNumber';
              setInputs(prev => ({ ...prev, [key]: e.target.value }));
            }}
            className="input-glass text-sm"
          />
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-3">
          <input data-testid="gov-district-input" type="text" placeholder="District"
            value={inputs.district || ''} onChange={e => setInputs(prev => ({ ...prev, district: e.target.value }))}
            className="input-glass text-sm" />
          <input type="text" placeholder="Taluk / Tehsil / Mandal"
            value={inputs.taluk || inputs.tehsil || inputs.mandal || ''}
            onChange={e => {
              const key = portalInputs.includes('taluk') ? 'taluk' : portalInputs.includes('tehsil') ? 'tehsil' : 'mandal';
              setInputs(prev => ({ ...prev, [key]: e.target.value }));
            }}
            className="input-glass text-sm" />
          <input type="text" placeholder="Village / Mouza"
            value={inputs.village || inputs.mouza || ''}
            onChange={e => {
              const key = portalInputs.includes('mouza') ? 'mouza' : 'village';
              setInputs(prev => ({ ...prev, [key]: e.target.value }));
            }}
            className="input-glass text-sm" />
        </div>

        <Button data-testid="gov-fetch-btn" className="btn-primary" onClick={handleFetch}
          disabled={fetching || !selectedState || !selectedDoc}>
          {fetching ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Globe className="h-4 w-4 mr-2" />}
          Fetch Records
        </Button>

        {selectedState && portals?.[selectedState] && (
          <div className="mt-3 flex items-center gap-2">
            <Badge className={`text-xs ${portals[selectedState].status === 'UP' ? 'bg-emerald-500/20 text-emerald-400' : portals[selectedState].status === 'MOCK' ? 'bg-amber-500/20 text-amber-400' : 'bg-red-500/20 text-red-400'}`}>
              {portals[selectedState].status === 'MOCK' ? 'Mock Mode' : portals[selectedState].status}
            </Badge>
            <span className="text-xs text-slate-500">{portals[selectedState].name}</span>
            <a href={portals[selectedState].url} target="_blank" rel="noopener noreferrer" className="text-xs text-cyan-400 hover:underline flex items-center gap-1">
              <ExternalLink className="h-3 w-3" />Portal
            </a>
          </div>
        )}
      </div>

      {/* Active Jobs */}
      {activeJobs.filter(j => j.status !== 'COMPLETED').length > 0 && (
        <div className="mb-6 space-y-3">
          <h4 className="text-sm font-semibold text-white">Active Fetches</h4>
          {activeJobs.filter(j => j.status !== 'COMPLETED').map(job => (
            <div key={job.job_id} className="p-3 bg-slate-800/50 rounded-lg border border-cyan-500/20" data-testid={`gov-job-${job.job_id}`}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-white">{STATE_LABELS[job.state]} - {job.document_type?.replace(/_/g, ' ')}</span>
                <Badge className="text-xs bg-cyan-500/20 text-cyan-400">{job.status}</Badge>
              </div>
              <div className="w-full h-1.5 bg-slate-700 rounded-full overflow-hidden mb-1">
                <div className="h-full bg-cyan-400 rounded-full transition-all duration-500" style={{ width: `${job.progress || 0}%` }} />
              </div>
              <p className="text-xs text-slate-500">{job.current_step || 'Processing...'} - {job.progress || 0}%</p>
            </div>
          ))}
        </div>
      )}

      {/* Fetched Records */}
      {records.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            <FileText className="h-4 w-4 text-cyan-400" />Fetched Records ({records.length})
          </h4>
          <div className="space-y-3">
            {records.map((rec, i) => (
              <div key={i} className="p-4 bg-slate-800/50 rounded-lg border border-slate-700/50" data-testid={`gov-record-${i}`}>
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <span className="text-sm font-medium text-white">{STATE_LABELS[rec.state] || rec.state} - {rec.document_type?.replace(/_/g, ' ')}</span>
                    <Badge className={`ml-2 text-xs ${rec.source === 'mock' ? 'bg-amber-500/20 text-amber-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                      {rec.source === 'mock' ? 'Mock' : 'Live'}
                    </Badge>
                  </div>
                  {rec.pdf_url && (
                    <a href={rec.pdf_url.startsWith('http') ? rec.pdf_url : `${BACKEND_URL}${rec.pdf_url}`}
                      target="_blank" rel="noopener noreferrer" data-testid={`gov-download-${i}`}>
                      <Button variant="ghost" size="sm" className="text-cyan-400">
                        <Download className="h-4 w-4 mr-1" /> PDF
                      </Button>
                    </a>
                  )}
                </div>

                {/* Structured Data */}
                {rec.structured_data && (
                  <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-2">
                    {Object.entries(rec.structured_data).map(([k, v]) => (
                      <div key={k} className="text-xs">
                        <span className="text-slate-500">{k.replace(/_/g, ' ')}: </span>
                        <span className="text-slate-300">{String(v)}</span>
                      </div>
                    ))}
                  </div>
                )}

                <p className="text-[10px] text-slate-600 mt-2">
                  Fetched: {rec.portal_fetched_at ? new Date(rec.portal_fetched_at).toLocaleString() : 'N/A'}
                  {rec.source_portal && ` from ${rec.source_portal}`}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Portal Directory */}
      {portals && records.length === 0 && activeJobs.length === 0 && (
        <div>
          <h4 className="text-sm font-semibold text-white mb-3">Portal Directory (20 States)</h4>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-2">
            {Object.entries(portals).map(([k, v]) => (
              <div key={k} className="p-2 bg-slate-800/30 rounded border border-slate-700/30 cursor-pointer hover:border-cyan-500/30 transition-colors"
                onClick={() => setSelectedState(k)} data-testid={`portal-${k}`}>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-white">{v.name}</span>
                  <div className={`w-2 h-2 rounded-full ${v.status === 'UP' ? 'bg-emerald-400' : v.status === 'MOCK' ? 'bg-amber-400' : 'bg-red-400'}`} />
                </div>
                <p className="text-[10px] text-slate-500 mt-0.5">{v.documents?.join(', ')}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default GovDataBridge;
