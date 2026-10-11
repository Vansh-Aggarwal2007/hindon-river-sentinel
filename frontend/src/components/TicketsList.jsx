import React, { useState } from 'react';
import { triggerInvestigation, triggerDispatch } from '../api/client';

export default function TicketsList({ tickets, onSelectTicket, onOpenVerify, onRefreshData }) {
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [search, setSearch] = useState('');
  const [actionLoading, setActionLoading] = useState(null);

  const filterOptions = [
    { id: 'ALL', label: 'All Incidents' },
    { id: 'ACTIVE', label: 'Active & Dispatched' },
    { id: 'VERIFIED_CLOSED', label: 'Verified Closed' },
    { id: 'REOPENED', label: 'Reopened (Audit Fail)' },
  ];

  const filtered = tickets.filter((t) => {
    // Search match
    const matchSearch =
      t.title.toLowerCase().includes(search.toLowerCase()) ||
      t.id.toLowerCase().includes(search.toLowerCase()) ||
      t.location.address.toLowerCase().includes(search.toLowerCase());

    if (!matchSearch) return false;

    if (filterStatus === 'ALL') return true;
    if (filterStatus === 'VERIFIED_CLOSED') return t.status === 'VERIFIED_CLOSED';
    if (filterStatus === 'REOPENED') return t.status === 'REOPENED';
    if (filterStatus === 'ACTIVE') {
      return ['OPEN', 'INVESTIGATING', 'DISPATCHED', 'IN_PROGRESS', 'PENDING_VERIFICATION'].includes(t.status);
    }
    return true;
  });

  const handleInvestigate = async (e, tid) => {
    e.stopPropagation();
    setActionLoading(tid);
    try {
      await triggerInvestigation(tid);
      onRefreshData && onRefreshData();
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(null);
    }
  };

  const handleDispatch = async (e, tid) => {
    e.stopPropagation();
    setActionLoading(tid);
    try {
      await triggerDispatch(tid);
      onRefreshData && onRefreshData();
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Search & Filter Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        {/* Filter Pills */}
        <div style={{ display: 'flex', gap: '6px' }}>
          {filterOptions.map((opt) => (
            <button
              key={opt.id}
              onClick={() => setFilterStatus(opt.id)}
              style={{
                padding: '6px 14px',
                borderRadius: '8px',
                fontSize: '0.8rem',
                fontWeight: filterStatus === opt.id ? 600 : 500,
                background: filterStatus === opt.id ? 'rgba(6, 182, 212, 0.2)' : 'rgba(255, 255, 255, 0.04)',
                border: filterStatus === opt.id ? '1px solid #06b6d4' : '1px solid rgba(255, 255, 255, 0.08)',
                color: filterStatus === opt.id ? '#38bdf8' : '#94a3b8',
                cursor: 'pointer'
              }}
            >
              {opt.label}
            </button>
          ))}
        </div>

        {/* Search Input */}
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by ticket ID, location or pollutant..."
          style={{
            minWidth: '280px',
            background: 'rgba(0, 0, 0, 0.4)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '8px',
            padding: '8px 12px',
            color: '#fff',
            fontSize: '0.82rem'
          }}
        />
      </div>

      {/* Incidents Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))',
        gap: '16px'
      }}>
        {filtered.map((t) => {
          const isClosed = t.status === 'VERIFIED_CLOSED';
          const isReopened = t.status === 'REOPENED';
          const isCritical = t.severity === 'CRITICAL';

          let statusBadge = 'badge-medium';
          if (isClosed) statusBadge = 'badge-closed';
          else if (isReopened) statusBadge = 'badge-reopened';
          else if (isCritical) statusBadge = 'badge-critical';

          return (
            <div
              key={t.id}
              onClick={() => onSelectTicket(t)}
              className="glass-panel glass-panel-interactive"
              style={{
                padding: '18px',
                cursor: 'pointer',
                display: 'flex',
                flexDirection: 'column',
                gap: '12px'
              }}
            >
              {/* Card top */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#38bdf8' }}>{t.id}</span>
                    <span className={`badge ${statusBadge}`}>{t.status.replace('_', ' ')}</span>
                  </div>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#f8fafc', margin: 0 }}>
                    {t.title}
                  </h4>
                </div>

                <span className="badge badge-medium">{t.severity}</span>
              </div>

              {/* Photo preview + details */}
              <div style={{ display: 'flex', gap: '12px' }}>
                <img
                  src={t.before_photo_url || "https://images.unsplash.com/photo-1618477461853-cf6ed80faba5?auto=format&fit=crop&w=800&q=80"}
                  alt="Incident Photo"
                  style={{
                    width: '90px',
                    height: '90px',
                    objectFit: 'cover',
                    borderRadius: '8px',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    flexShrink: 0
                  }}
                />

                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '0.75rem', color: '#94a3b8' }}>
                  <div>
                    <strong>Type:</strong> <span style={{ color: '#e2e8f0' }}>{t.incident_type.replace('_', ' ')}</span>
                  </div>
                  <div>
                    <strong>Reach:</strong> <span style={{ color: '#e2e8f0' }}>{t.location?.reach_km} km</span> ({t.location?.address?.slice(0, 32)}...)
                  </div>
                  <div>
                    <strong>Dept:</strong> <span style={{ color: '#38bdf8' }}>{t.assigned_department || 'Pending'}</span>
                  </div>
                  {t.source_hypotheses?.length > 0 && (
                    <div style={{ color: '#fbbf24' }}>
                      <strong>Culprit:</strong> {t.source_hypotheses[0].name.slice(0, 24)}...
                    </div>
                  )}
                </div>
              </div>

              {/* Card Actions */}
              <div style={{ display: 'flex', gap: '8px', marginTop: 'auto', paddingTop: '8px', borderTop: '1px solid rgba(255, 255, 255, 0.06)' }}>
                {(!t.source_hypotheses || t.source_hypotheses.length === 0) && (
                  <button
                    onClick={(e) => handleInvestigate(e, t.id)}
                    disabled={actionLoading === t.id}
                    className="btn btn-secondary"
                    style={{ flex: 1, fontSize: '0.72rem', padding: '5px' }}
                  >
                    Investigate
                  </button>
                )}

                {t.status === 'OPEN' && (
                  <button
                    onClick={(e) => handleDispatch(e, t.id)}
                    disabled={actionLoading === t.id}
                    className="btn btn-secondary"
                    style={{ flex: 1, fontSize: '0.72rem', padding: '5px' }}
                  >
                    Dispatch
                  </button>
                )}

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onOpenVerify(t);
                  }}
                  className="btn btn-primary"
                  style={{ flex: 1, fontSize: '0.72rem', padding: '5px' }}
                >
                  {isClosed ? 'View Audit Proof' : 'Verify & Close'}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
