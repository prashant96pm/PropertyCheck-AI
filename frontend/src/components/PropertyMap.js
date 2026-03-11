import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix Leaflet default marker icon issue with bundlers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const createIcon = (color) => new L.DivIcon({
  html: `<div style="background:${color};width:12px;height:12px;border-radius:50%;border:2px solid white;box-shadow:0 0 6px ${color}"></div>`,
  className: '',
  iconSize: [12, 12],
  iconAnchor: [6, 6],
});

const PropertyMap = ({ property, valuation }) => {
  // Use property coordinates or generate deterministic ones based on district
  const districtCoords = {
    'Bengaluru Urban': [12.9716, 77.5946],
    'Bengaluru Rural': [13.1986, 77.3834],
    'Mumbai': [19.0760, 72.8777],
    'Hyderabad': [17.3850, 78.4867],
    'Chennai': [13.0827, 80.2707],
    'Pune': [18.5204, 73.8567],
    'Ahmedabad': [23.0225, 72.5714],
    'Delhi': [28.7041, 77.1025],
    'Kolkata': [22.5726, 88.3639],
    'Jaipur': [26.9124, 75.7873],
  };

  const district = property?.district || 'Bengaluru Urban';
  const baseCoords = districtCoords[district] || [12.9716, 77.5946];

  // Slight offset based on property_id for uniqueness
  const seed = property?.property_id ? [...property.property_id].reduce((a, c) => a + c.charCodeAt(0), 0) : 0;
  const lat = baseCoords[0] + ((seed % 100) - 50) * 0.001;
  const lng = baseCoords[1] + ((seed % 80) - 40) * 0.001;

  const infrastructure = valuation?.infrastructure || {};

  // Generate infrastructure marker positions around the property
  const infraMarkers = Object.entries(infrastructure).map(([key, val], i) => {
    const angle = (i / Object.keys(infrastructure).length) * 2 * Math.PI;
    const dist = parseFloat(val.distance) || 2;
    const scaledDist = Math.min(dist * 0.005, 0.03);
    return {
      key,
      name: val.name,
      distance: val.distance,
      position: [lat + Math.cos(angle) * scaledDist, lng + Math.sin(angle) * scaledDist],
    };
  });

  return (
    <div data-testid="property-map-container" className="rounded-lg overflow-hidden border border-slate-700/50">
      <MapContainer
        center={[lat, lng]}
        zoom={14}
        style={{ height: '400px', width: '100%', background: '#0f172a' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        {/* Property marker */}
        <Marker position={[lat, lng]}>
          <Popup>
            <div style={{ color: '#0f172a', fontFamily: 'system-ui' }}>
              <strong>Survey No. {property?.survey_no}</strong>
              <br />
              {property?.owner_name && <span>Owner: {property.owner_name}<br /></span>}
              {property?.extent && <span>Extent: {property.extent}<br /></span>}
              <span>{property?.district}, {property?.state}</span>
            </div>
          </Popup>
        </Marker>

        {/* Property boundary circle */}
        <Circle
          center={[lat, lng]}
          radius={150}
          pathOptions={{ color: '#06b6d4', fillColor: '#06b6d4', fillOpacity: 0.1, weight: 2, dashArray: '5,5' }}
        />

        {/* Infrastructure markers */}
        {infraMarkers.map(m => (
          <Marker key={m.key} position={m.position} icon={createIcon('#f59e0b')}>
            <Popup>
              <div style={{ color: '#0f172a', fontFamily: 'system-ui' }}>
                <strong>{m.name}</strong>
                <br />
                <span>{m.distance}</span>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      {/* Infrastructure legend */}
      <div className="p-3 bg-slate-800/80 border-t border-slate-700/50">
        <div className="flex flex-wrap gap-3">
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <div className="w-2.5 h-2.5 rounded-full bg-cyan-400" />
            Property
          </div>
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <div className="w-2.5 h-2.5 rounded-full bg-amber-400" />
            Infrastructure
          </div>
          {Object.entries(infrastructure).slice(0, 4).map(([k, v]) => (
            <span key={k} className="text-xs text-slate-500">{v.name} ({v.distance})</span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PropertyMap;
