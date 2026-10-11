import React, { useState } from 'react';
import { triggerVerify } from '../api/client';

export default function VerificationModal({ ticket, onClose, onVerified }) {
  if (!ticket) return null;

  const [afterImageUrl, setAfterImageUrl] = useState(
    ticket.after_photo_url ||
    'https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?auto=format&fit=crop&w=800&q=80'
  );
  const [description, setDescription] = useState(
    'Field remediation completed. Solid waste piles cleared by earthmovers; water edge restored.'
  );
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(ticket.verification || null);

  const handleVerify = async (forcePass) => {
    setLoading(true);
    try {
      const res = await triggerVerify(ticket.id, {
        after_image_url: afterImageUrl,
        after_description: description,
        force_pass: forcePass
      });
      setResult(res.verification);
      onVerified && onVerified();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const beforeScore = ticket.before_photo_analysis?.cleanliness_score || 20;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="glass-panel"
        style={{
          width: '880px',
          maxWidth: '95vw',
          maxHeight: '90vh',
          overflowY: 'auto',
          padding: '28px',
          background: '#0d1527',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          boxShadow: '0 20px 50px rgba(0,0,0,0.7)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="badge badge-closed">Closed-Loop Verification</span>
              <span style={{ fontSize: '0.8rem', color: '#64748b' }}>{ticket.id}</span>
            </div>
            <h2 style={{ fontSize: '1.3rem', fontWeight: 700, color: '#f8fafc', marginTop: '4px' }}>
              {ticket.title}
            </h2>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              color: '#94a3b8',
              fontSize: '1.2rem',
              cursor: 'pointer'
            }}
          >
            ✕
          </button>
        </div>

        {/* Side by side Before & After photos */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
          {/* Before */}
          <div style={{
            background: 'rgba(0,0,0,0.3)',
            borderRadius: '12px',
            border: '1px solid rgba(255,255,255,0.08)',
            padding: '12px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <strong style={{ fontSize: '0.82rem', color: '#f43f5e' }}>BEFORE (Initial State)</strong>
              <span className="badge badge-critical">{beforeScore}% Clean</span>
            </div>
            <img
              src={ticket.before_photo_url || "https://images.unsplash.com/photo-1618477461853-cf6ed80faba5?auto=format&fit=crop&w=800&q=80"}
              alt="Before Remediation"
              style={{
                width: '100%',
                height: '210px',
                objectFit: 'cover',
                borderRadius: '8px',
                border: '1px solid rgba(255,255,255,0.06)'
              }}
            />
            <div style={{ marginTop: '8px', fontSize: '0.75rem', color: '#94a3b8' }}>
              Detected: {ticket.before_photo_analysis?.detected_objects?.join(', ') || 'Severe debris & contamination'}
            </div>
          </div>

          {/* After */}
          <div style={{
            background: 'rgba(0,0,0,0.3)',
            borderRadius: '12px',
            border: '1px solid rgba(255,255,255,0.08)',
            padding: '12px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <strong style={{ fontSize: '0.82rem', color: '#10b981' }}>AFTER (Field Remediation Proof)</strong>
              {result && (
                <span className={`badge ${result.verified ? 'badge-closed' : 'badge-reopened'}`}>
                  {result.after_cleanliness}% Clean
                </span>
              )}
            </div>
            <img
              src={afterImageUrl}
              alt="After Remediation"
              style={{
                width: '100%',
                height: '210px',
                objectFit: 'cover',
                borderRadius: '8px',
                border: '1px solid rgba(255,255,255,0.06)'
              }}
            />
            <div style={{ marginTop: '8px' }}>
              <input
                type="text"
                value={afterImageUrl}
                onChange={(e) => setAfterImageUrl(e.target.value)}
                placeholder="After Image URL"
                style={{
                  width: '100%',
                  background: 'rgba(0,0,0,0.5)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '6px',
                  padding: '5px 8px',
                  fontSize: '0.72rem',
                  color: '#e2e8f0'
                }}
              />
            </div>
          </div>
        </div>

        {/* Verification Inspector Form */}
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', fontSize: '0.78rem', color: '#cbd5e1', marginBottom: '6px' }}>
            Field Inspector Notes / Observations
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={2}
            style={{
              width: '100%',
              background: 'rgba(0,0,0,0.4)',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: '8px',
              padding: '8px 12px',
              color: '#fff',
              fontSize: '0.85rem'
            }}
          />
        </div>

        {/* Action Decision Buttons */}
        <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
          <button
            onClick={() => handleVerify(true)}
            disabled={loading}
            className="btn btn-success"
            style={{ flex: 1, padding: '12px' }}
          >
            ✓ Verify Resolution (Pass & Close Ticket)
          </button>
          <button
            onClick={() => handleVerify(false)}
            disabled={loading}
            className="btn btn-danger"
            style={{ flex: 1, padding: '12px' }}
          >
            ✗ Reject Cleanup (Reopen Ticket with Notice)
          </button>
        </div>

        {/* Verification Report Result */}
        {result && (
          <div style={{
            background: result.verified ? 'rgba(16, 185, 129, 0.1)' : 'rgba(244, 63, 94, 0.1)',
            border: `1px solid ${result.verified ? 'rgba(16, 185, 129, 0.3)' : 'rgba(244, 63, 94, 0.3)'}`,
            borderRadius: '12px',
            padding: '16px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{
                fontWeight: 700,
                fontSize: '0.95rem',
                color: result.verified ? '#34d399' : '#f87171'
              }}>
                {result.verified ? 'AUDIT PASSED — TICKET VERIFIED & CLOSED' : 'AUDIT FAILED — TICKET REOPENED'}
              </span>
              <span className="badge badge-medium">
                +{result.improvement_percentage}% Improvement
              </span>
            </div>
            <p style={{ fontSize: '0.85rem', color: '#e2e8f0', lineHeight: 1.5, margin: 0 }}>
              {result.notes}
            </p>
            {result.rejection_reasons?.length > 0 && (
              <ul style={{ marginTop: '8px', paddingLeft: '20px', color: '#fda4af', fontSize: '0.8rem' }}>
                {result.rejection_reasons.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
