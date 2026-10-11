import React, { useState, useEffect } from 'react';
import { fetchBriefing, approveEscalation } from '../api/client';

export default function OfficerBriefing({ tickets, onRefreshData }) {
  const [briefing, setBriefing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lang, setLang] = useState('en'); // 'en' or 'hi'
  const [escalatingId, setEscalatingId] = useState(null);
  const [escalateSuccess, setEscalateSuccess] = useState('');

  const loadBriefing = async () => {
    try {
      const data = await fetchBriefing();
      setBriefing(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBriefing();
  }, [tickets]);

  const handleApproveEscalation = async (ticketId) => {
    setEscalatingId(ticketId);
    try {
      const res = await approveEscalation(
        ticketId,
        'Approved by District Magistrate for immediate UPPCB statutory show-cause notice under Section 33A Water Act.'
      );
      setEscalateSuccess(`Directive issued for ${ticketId}. Show cause notice dispatched to UPPCB.`);
      loadBriefing();
      onRefreshData && onRefreshData();
    } catch (err) {
      console.error(err);
    } finally {
      setEscalatingId(null);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: '#64748b' }}>
        Synthesizing Executive Command Dossier...
      </div>
    );
  }

  const stats = briefing?.stats || {};
  const criticalTickets = stats.critical_tickets || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: 'rgba(15, 23, 42, 0.65)',
        padding: '16px 20px',
        borderRadius: '14px',
        border: '1px solid rgba(255, 255, 255, 0.08)'
      }}>
        <div>
          <span style={{
            fontSize: '0.72rem',
            fontWeight: 700,
            color: '#38bdf8',
            letterSpacing: '0.05em',
            textTransform: 'uppercase'
          }}>
            District Administration Command Portal
          </span>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc', margin: '2px 0 0' }}>
            IAS Officer Daily Intelligence Briefing
          </h2>
        </div>

        {/* Language switch button */}
        <div style={{ display: 'flex', gap: '6px', background: 'rgba(0,0,0,0.4)', padding: '4px', borderRadius: '8px' }}>
          <button
            onClick={() => setLang('en')}
            style={{
              padding: '6px 14px',
              borderRadius: '6px',
              border: 'none',
              background: lang === 'en' ? '#06b6d4' : 'transparent',
              color: lang === 'en' ? '#fff' : '#94a3b8',
              fontWeight: 600,
              fontSize: '0.8rem',
              cursor: 'pointer'
            }}
          >
            English
          </button>
          <button
            onClick={() => setLang('hi')}
            style={{
              padding: '6px 14px',
              borderRadius: '6px',
              border: 'none',
              background: lang === 'hi' ? '#06b6d4' : 'transparent',
              color: lang === 'hi' ? '#fff' : '#94a3b8',
              fontWeight: 600,
              fontSize: '0.8rem',
              cursor: 'pointer'
            }}
          >
            हिंदी (Hindi)
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap: '14px'
      }}>
        <div className="glass-panel" style={{ padding: '16px' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 600, color: '#94a3b8' }}>TOTAL INCIDENTS</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#f8fafc', marginTop: '4px' }}>
            {stats.total_tickets || 0}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>Logged across sector</div>
        </div>

        <div className="glass-panel" style={{ padding: '16px' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 600, color: '#94a3b8' }}>VERIFIED RESOLVED</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#34d399', marginTop: '4px' }}>
            {stats.closed_count || 0}
            <span style={{ fontSize: '0.9rem', color: '#6ee7b7', marginLeft: '6px' }}>
              ({stats.resolution_rate_percent}%)
            </span>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>Closed-loop verified</div>
        </div>

        <div className="glass-panel" style={{ padding: '16px' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 600, color: '#94a3b8' }}>ACTIVE PATROLS</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#fbbf24', marginTop: '4px' }}>
            {stats.dispatched_count || 0}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>Field units deployed</div>
        </div>

        <div className="glass-panel" style={{ padding: '16px' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 600, color: '#94a3b8' }}>SENSOR ALARMS</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#f87171', marginTop: '4px' }}>
            {stats.active_sensor_anomalies?.length || 0}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>Unresolved spikes</div>
        </div>

        <div className="glass-panel" style={{ padding: '16px' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 600, color: '#94a3b8' }}>REOPENED (AUDIT FAIL)</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#f472b6', marginTop: '4px' }}>
            {stats.reopened_count || 0}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>Incomplete cleanups</div>
        </div>
      </div>

      {/* Main Briefing Text */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{
          whiteSpace: 'pre-wrap',
          fontFamily: lang === 'hi' ? 'inherit' : 'var(--font-body)',
          fontSize: '0.9rem',
          lineHeight: 1.7,
          color: '#e2e8f0'
        }}>
          {lang === 'hi' ? briefing?.hindi_summary : briefing?.english_dossier}
        </div>
      </div>

      {/* Critical Red Flag Action Center */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
          <span className="pulse-indicator pulse-rose"></span>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f87171', margin: 0 }}>
            Critical Enforcement & Statutory Directives
          </h3>
        </div>

        {escalateSuccess && (
          <div style={{
            background: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            color: '#6ee7b7',
            padding: '10px 14px',
            borderRadius: '8px',
            fontSize: '0.85rem',
            marginBottom: '16px'
          }}>
            ✓ {escalateSuccess}
          </div>
        )}

        {criticalTickets.length === 0 ? (
          <p style={{ color: '#64748b', fontSize: '0.85rem', margin: 0 }}>
            No critical unaddressed breaches require executive sign-off at this time.
          </p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {criticalTickets.map((ct) => (
              <div
                key={ct.id}
                style={{
                  background: 'rgba(0, 0, 0, 0.3)',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  borderRadius: '10px',
                  padding: '16px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: '16px'
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <span style={{ color: '#38bdf8', fontWeight: 700, fontSize: '0.8rem' }}>{ct.id}</span>
                    <span className="badge badge-critical">{ct.severity}</span>
                    <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Reach {ct.location.reach_km} km</span>
                  </div>
                  <div style={{ fontWeight: 600, color: '#f8fafc', fontSize: '0.9rem' }}>
                    {ct.title}
                  </div>
                  <p style={{ fontSize: '0.78rem', color: '#94a3b8', margin: '4px 0 0' }}>
                    Dept: {ct.assigned_department || 'UPPCB'} | Source Hypothesis: {ct.source_hypotheses?.[0]?.name || 'Industrial Conduit'}
                  </p>
                </div>

                <div>
                  {ct.escalation_approved ? (
                    <span style={{
                      padding: '6px 12px',
                      background: 'rgba(16, 185, 129, 0.15)',
                      color: '#34d399',
                      border: '1px solid rgba(16, 185, 129, 0.3)',
                      borderRadius: '6px',
                      fontSize: '0.78rem',
                      fontWeight: 600
                    }}>
                      ✓ Section 33A Notice Dispatched
                    </span>
                  ) : (
                    <button
                      onClick={() => handleApproveEscalation(ct.id)}
                      disabled={escalatingId === ct.id}
                      className="btn btn-danger"
                      style={{ fontSize: '0.8rem', padding: '8px 14px' }}
                    >
                      {escalatingId === ct.id ? 'Issuing Notice...' : 'Approve & Issue Directive'}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
