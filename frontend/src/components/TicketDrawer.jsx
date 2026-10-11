import React from 'react';
import { triggerInvestigation, triggerDispatch } from '../api/client';

export default function TicketDrawer({ ticket, onClose, onOpenVerify, onRefreshData }) {
  if (!ticket) return null;

  const isClosed = ticket.status === 'VERIFIED_CLOSED';
  const isCritical = ticket.severity === 'CRITICAL';
  const isHigh = ticket.severity === 'HIGH';

  let statusBadge = 'badge-medium';
  if (isClosed) statusBadge = 'badge-closed';
  else if (ticket.status === 'REOPENED') statusBadge = 'badge-reopened';
  else if (isCritical) statusBadge = 'badge-critical';
  else if (isHigh) statusBadge = 'badge-high';

  const handleInvestigate = async () => {
    try {
      await triggerInvestigation(ticket.id);
      onRefreshData && onRefreshData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDispatch = async () => {
    try {
      await triggerDispatch(ticket.id);
      onRefreshData && onRefreshData();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        right: 0,
        bottom: 0,
        width: '460px',
        maxWidth: '92vw',
        background: 'rgba(11, 15, 25, 0.96)',
        backdropFilter: 'blur(16px)',
        borderLeft: '1px solid rgba(255, 255, 255, 0.1)',
        boxShadow: '-10px 0 35px rgba(0, 0, 0, 0.7)',
        zIndex: 1000,
        padding: '24px',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '20px'
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#38bdf8' }}>{ticket.id}</span>
            <span className={`badge ${statusBadge}`}>{ticket.status.replace('_', ' ')}</span>
            <span className="badge badge-medium">{ticket.severity}</span>
          </div>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#f8fafc', margin: 0 }}>
            {ticket.title}
          </h3>
        </div>
        <button
          onClick={onClose}
          style={{
            background: 'rgba(255, 255, 255, 0.05)',
            border: 'none',
            color: '#94a3b8',
            width: '28px',
            height: '28px',
            borderRadius: '6px',
            cursor: 'pointer'
          }}
        >
          ✕
        </button>
      </div>

      {/* Location & Reach info */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.03)',
        borderRadius: '10px',
        padding: '12px',
        fontSize: '0.8rem',
        color: '#cbd5e1'
      }}>
        <div style={{ marginBottom: '4px' }}>
          <strong>Location:</strong> {ticket.location?.address}
        </div>
        <div style={{ color: '#94a3b8', fontSize: '0.75rem' }}>
          GPS: {ticket.location?.lat?.toFixed(4)}, {ticket.location?.lng?.toFixed(4)} | River Reach: {ticket.location?.reach_km} km
        </div>
      </div>

      {/* Description */}
      <div>
        <h4 style={{ fontSize: '0.82rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', marginBottom: '6px' }}>
          Incident Description
        </h4>
        <p style={{ fontSize: '0.85rem', color: '#e2e8f0', lineHeight: 1.5, margin: 0 }}>
          {ticket.description}
        </p>
      </div>

      {/* Photographic Evidence Before/After */}
      <div>
        <h4 style={{ fontSize: '0.82rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', marginBottom: '8px' }}>
          Photographic Evidence
        </h4>
        <div style={{ display: 'grid', gridTemplateColumns: ticket.after_photo_url ? '1fr 1fr' : '1fr', gap: '10px' }}>
          <div>
            <div style={{ fontSize: '0.7rem', color: '#f43f5e', fontWeight: 700, marginBottom: '4px' }}>
              BEFORE (Initial State)
            </div>
            <img
              src={ticket.before_photo_url || "https://images.unsplash.com/photo-1618477461853-cf6ed80faba5?auto=format&fit=crop&w=800&q=80"}
              alt="Before"
              style={{ width: '100%', height: '140px', objectFit: 'cover', borderRadius: '8px' }}
            />
          </div>
          {ticket.after_photo_url && (
            <div>
              <div style={{ fontSize: '0.7rem', color: '#10b981', fontWeight: 700, marginBottom: '4px' }}>
                AFTER (Verified Resolution)
              </div>
              <img
                src={ticket.after_photo_url}
                alt="After"
                style={{ width: '100%', height: '140px', objectFit: 'cover', borderRadius: '8px' }}
              />
            </div>
          )}
        </div>
      </div>

      {/* Source Investigator Hypotheses */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
          <h4 style={{ fontSize: '0.82rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', margin: 0 }}>
            Source Hypotheses (AI GIS)
          </h4>
          {(!ticket.source_hypotheses || ticket.source_hypotheses.length === 0) && (
            <button
              onClick={handleInvestigate}
              className="btn btn-secondary"
              style={{ fontSize: '0.7rem', padding: '4px 8px' }}
            >
              Run Investigator
            </button>
          )}
        </div>

        {ticket.source_hypotheses?.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {ticket.source_hypotheses.map((hyp, i) => (
              <div
                key={i}
                style={{
                  background: 'rgba(245, 158, 11, 0.08)',
                  border: '1px solid rgba(245, 158, 11, 0.2)',
                  borderRadius: '8px',
                  padding: '10px'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <strong style={{ fontSize: '0.82rem', color: '#fbbf24' }}>{hyp.name}</strong>
                  <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#f59e0b' }}>
                    {Math.round(hyp.confidence * 100)}% Match
                  </span>
                </div>
                <div style={{ fontSize: '0.72rem', color: '#94a3b8', margin: '3px 0' }}>
                  Distance Upstream: {hyp.distance_upstream_m?.toFixed(0)}m | Type: {hyp.type}
                </div>
                {hyp.evidence?.map((ev, eIdx) => (
                  <div key={eIdx} style={{ fontSize: '0.7rem', color: '#cbd5e1' }}>
                    • {ev}
                  </div>
                ))}
              </div>
            ))}
          </div>
        ) : (
          <div style={{ fontSize: '0.78rem', color: '#64748b' }}>
            No upstream source hypotheses computed yet. Click "Run Investigator" to backtrack along the flow vector.
          </div>
        )}
      </div>

      {/* Department & Patrol */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.03)',
        borderRadius: '10px',
        padding: '14px',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>Assigned Department:</span>
          <strong style={{ fontSize: '0.82rem', color: '#38bdf8' }}>
            {ticket.assigned_department || 'Unassigned'}
          </strong>
        </div>

        {ticket.patrol_assignment ? (
          <div>
            <div style={{ fontSize: '0.78rem', color: '#cbd5e1' }}>
              <strong>Patrol Unit:</strong> {ticket.patrol_assignment.patrol_id}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
              Officer: {ticket.patrol_assignment.officer_name}
            </div>
            <div style={{ fontSize: '0.72rem', color: '#fbbf24', marginTop: '2px' }}>
              Target ETA: {new Date(ticket.patrol_assignment.target_eta).toLocaleTimeString()}
            </div>
          </div>
        ) : (
          <button
            onClick={handleDispatch}
            className="btn btn-secondary"
            style={{ width: '100%', fontSize: '0.75rem', padding: '6px' }}
          >
            Dispatch Patrol Team
          </button>
        )}
      </div>

      {/* Action Footer */}
      <div style={{ marginTop: 'auto', display: 'flex', gap: '8px' }}>
        <button
          onClick={() => onOpenVerify && onOpenVerify(ticket)}
          className="btn btn-primary"
          style={{ flex: 1, padding: '10px' }}
        >
          🔍 Review Before/After Verification
        </button>
      </div>
    </div>
  );
}
