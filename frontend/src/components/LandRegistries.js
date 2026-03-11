import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Badge } from '../components/ui/badge';
import { CheckCircle2, ExternalLink, Globe, Loader2 } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LandRegistries = ({ propertyId }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRegistries();
  }, [propertyId]);

  const fetchRegistries = async () => {
    try {
      const res = await axios.get(`${API}/property/${propertyId}/land-registries`);
      setData(res.data);
    } catch (err) { /* ignore */ }
    finally { setLoading(false); }
  };

  if (loading) return (
    <div className="text-center py-12"><Loader2 className="h-8 w-8 animate-spin text-cyan-400 mx-auto" /></div>
  );

  if (!data) return <p className="text-sm text-slate-400">Unable to load land registry data</p>;

  return (
    <div data-testid="land-registries-panel">
      {/* Primary State */}
      {data.primary_registry && (
        <div className="glass-card-blue mb-6">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h4 className="font-semibold text-white">{data.primary_registry.name}</h4>
              <p className="text-xs text-slate-400">{data.property_state} - Property's Home State</p>
            </div>
            <Badge className="bg-emerald-500/20 text-emerald-400">{data.primary_registry.digitization} Digital</Badge>
          </div>
          <div className="flex flex-wrap gap-2 mb-3">
            {data.primary_registry.records_available.map(rec => (
              <Badge key={rec} variant="outline" className="border-slate-600 text-slate-300 text-xs">{rec}</Badge>
            ))}
          </div>
          <a href={data.primary_registry.portal_url} target="_blank" rel="noopener noreferrer"
            className="text-xs text-cyan-400 hover:underline flex items-center gap-1">
            <ExternalLink className="h-3 w-3" />{data.primary_registry.portal_url}
          </a>
        </div>
      )}

      {/* All States Grid */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {data.registries.filter(r => !r.is_property_state).map(reg => (
          <div key={reg.state} className="p-3 bg-slate-800/50 rounded-lg border border-slate-700/50" data-testid={`registry-${reg.state}`}>
            <div className="flex items-center justify-between mb-2">
              <h5 className="text-sm font-medium text-white">{reg.state}</h5>
              <Badge className={`text-[10px] ${parseInt(reg.digitization) >= 90 ? 'bg-emerald-500/20 text-emerald-400' : parseInt(reg.digitization) >= 80 ? 'bg-cyan-500/20 text-cyan-400' : 'bg-amber-500/20 text-amber-400'}`}>
                {reg.digitization}
              </Badge>
            </div>
            <p className="text-xs text-slate-400 mb-1">{reg.name}</p>
            <p className="text-[10px] text-slate-500">{reg.coverage} | {reg.records_available.length} record types</p>
            <a href={reg.portal_url} target="_blank" rel="noopener noreferrer"
              className="text-[10px] text-cyan-400 hover:underline flex items-center gap-1 mt-1">
              <ExternalLink className="h-2.5 w-2.5" />Visit Portal
            </a>
          </div>
        ))}
      </div>

      <p className="text-xs text-slate-500 mt-4">{data.data_sources_note}</p>
    </div>
  );
};

export default LandRegistries;
