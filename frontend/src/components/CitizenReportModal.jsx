import React, { useState } from 'react';
import { createReport } from '../api/client';

export default function CitizenReportModal({ isOpen, onClose, onReportCreated }) {
  if (!isOpen) return null;

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [lat, setLat] = useState('28.6655');
  const [lng, setLng] = useState('77.4168');
  const [imageUrl, setImageUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const presets = [
    {
      label: '🧼 Toxic Chemical Foam',
      title: 'Dense Toxic Foam at Hindon Barrage',
      desc: 'Thick white surfactant foam blanketing the water downstream of the weir. Strong pungent detergent odor.',
      lat: '28.6655',
      lng: '77.4168',
      img: 'https://images.unsplash.com/photo-1621451537084-482c73073a0f?auto=format&fit=crop&w=800&q=80'
    },
    {
      label: '🚜 Plastic Waste Dumping',
      title: 'Tractor Trolley Dumping Municipal Waste',
      desc: 'Commercial tractor emptying plastic bags and vegetable refuse directly on the river embankment near Karhera.',
      lat: '28.6942',
      lng: '77.4085',
      img: 'https://images.unsplash.com/photo-1618477461853-cf6ed80faba5?auto=format&fit=crop&w=800&q=80'
    },
    {
      label: '🏭 Black Chemical Effluent',
      title: 'Untreated Industrial Acid Discharge',
      desc: 'Dark blackened water spilling into the stream with high acidity. Dissolved solids clearly abnormal.',
      lat: '28.6612',
      lng: '77.4110',
      img: 'https://images.unsplash.com/photo-1611273426858-450d8e3c9fce?auto=format&fit=crop&w=800&q=80'
    },
    {
      label: '🏗️ Floodplain Encroachment',
      title: 'Illegal Sheds & Construction Debris',
      desc: 'Temporary sheds erected inside the 100-meter protected river floodplain buffer zone.',
      lat: '28.6520',
      lng: '77.4280',
      img: 'https://images.unsplash.com/photo-1530587191325-3db32d826c18?auto=format&fit=crop&w=800&q=80'
    }
  ];

  const applyPreset = (p) => {
    setTitle(p.title);
    setDescription(p.desc);
    setLat(p.lat);
    setLng(p.lng);
    setImageUrl(p.img);
    setResult(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const res = await createReport({
        title,
        description,
        lat: parseFloat(lat),
        lng: parseFloat(lng),
        image_url: imageUrl
      });
      setResult(res);
      if (!res.is_duplicate) {
        onReportCreated && onReportCreated();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="glass-panel"
        style={{
          width: '680px',
          maxWidth: '95vw',
          maxHeight: '90vh',
          overflowY: 'auto',
          padding: '24px',
          background: '#0d1527',
          border: '1px solid rgba(255, 255, 255, 0.1)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc' }}>
              Citizen Environmental Report
            </h2>
            <p style={{ fontSize: '0.8rem', color: '#94a3b8', margin: 0 }}>
              Submitted reports trigger the Vision Triage Agent for classification & deduplication.
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              color: '#94a3b8',
              fontSize: '1.1rem',
              cursor: 'pointer'
            }}
          >
            ✕
          </button>
        </div>

        {/* Presets */}
        <div style={{ marginBottom: '18px' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', marginBottom: '6px' }}>
            Quick Demo Presets
          </div>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {presets.map((p, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => applyPreset(p)}
                style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '6px',
                  padding: '6px 10px',
                  color: '#cbd5e1',
                  fontSize: '0.75rem',
                  cursor: 'pointer'
                }}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.78rem', color: '#cbd5e1', marginBottom: '4px' }}>
              Incident Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Chemical Foam near Barrage"
              required
              style={{
                width: '100%',
                background: 'rgba(0, 0, 0, 0.4)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                padding: '9px 12px',
                color: '#fff',
                fontSize: '0.85rem'
              }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.78rem', color: '#cbd5e1', marginBottom: '4px' }}>
              Detailed Description & Visual Observations
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              placeholder="Describe color, smell, discharge source or vehicle type..."
              required
              style={{
                width: '100%',
                background: 'rgba(0, 0, 0, 0.4)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                padding: '9px 12px',
                color: '#fff',
                fontSize: '0.85rem'
              }}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.78rem', color: '#cbd5e1', marginBottom: '4px' }}>
                Latitude
              </label>
              <input
                type="number"
                step="0.0001"
                value={lat}
                onChange={(e) => setLat(e.target.value)}
                required
                style={{
                  width: '100%',
                  background: 'rgba(0, 0, 0, 0.4)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '8px',
                  padding: '9px 12px',
                  color: '#fff',
                  fontSize: '0.85rem'
                }}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.78rem', color: '#cbd5e1', marginBottom: '4px' }}>
                Longitude
              </label>
              <input
                type="number"
                step="0.0001"
                value={lng}
                onChange={(e) => setLng(e.target.value)}
                required
                style={{
                  width: '100%',
                  background: 'rgba(0, 0, 0, 0.4)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '8px',
                  padding: '9px 12px',
                  color: '#fff',
                  fontSize: '0.85rem'
                }}
              />
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.78rem', color: '#cbd5e1', marginBottom: '4px' }}>
              Geotagged Photo URL
            </label>
            <input
              type="url"
              value={imageUrl}
              onChange={(e) => setImageUrl(e.target.value)}
              placeholder="https://images.unsplash.com/..."
              style={{
                width: '100%',
                background: 'rgba(0, 0, 0, 0.4)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                padding: '9px 12px',
                color: '#fff',
                fontSize: '0.85rem'
              }}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
            style={{ marginTop: '6px', padding: '10px' }}
          >
            {loading ? 'Processing via Triage Agent...' : 'Submit to AI Command Center'}
          </button>
        </form>

        {/* Result view */}
        {result && (
          <div style={{
            marginTop: '18px',
            background: result.is_duplicate ? 'rgba(245, 158, 11, 0.15)' : 'rgba(16, 185, 129, 0.15)',
            border: `1px solid ${result.is_duplicate ? 'rgba(245, 158, 11, 0.3)' : 'rgba(16, 185, 129, 0.3)'}`,
            borderRadius: '10px',
            padding: '14px'
          }}>
            <div style={{ fontWeight: 700, fontSize: '0.9rem', color: result.is_duplicate ? '#fbbf24' : '#6ee7b7', marginBottom: '4px' }}>
              {result.is_duplicate ? 'Duplicate Report Detected & Merged' : 'Ticket Created & Classified by Triage Agent'}
            </div>
            <p style={{ fontSize: '0.8rem', color: '#cbd5e1', margin: 0 }}>
              {result.message || `Assigned ID: ${result.ticket?.id} | Severity: ${result.ticket?.severity} | Type: ${result.ticket?.incident_type}`}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
