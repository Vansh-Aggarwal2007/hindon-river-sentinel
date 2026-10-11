import React, { useState, useEffect } from 'react';
import { fetchAgentLogs } from '../api/client';

export default function AgentTerminal() {
  const [logs, setLogs] = useState([]);
  const [filterAgent, setFilterAgent] = useState('ALL');
  const [loading, setLoading] = useState(false);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const data = await fetchAgentLogs();
      setLogs(data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
    const interval = setInterval(loadLogs, 6000);
    return () => clearInterval(interval);
  }, []);

  const agentNames = [
    'ALL',
    'Triage Agent',
    'Water Sentinel',
    'Source Investigator',
    'Dispatcher',
    'Verifier',
    'Briefing Agent',
    'System Orchestrator'
  ];

  const filteredLogs = filterAgent === 'ALL'
    ? logs
    : logs.filter((l) => l.agent_name === filterAgent);

  return (
    <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#38bdf8', textTransform: 'uppercase' }}>
            Telemetry & Execution Trace
          </span>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc', margin: '2px 0 0' }}>
            Multi-Agent Reasoning & Tool Calls Log
          </h3>
        </div>
        <button
          onClick={loadLogs}
          disabled={loading}
          className="btn btn-secondary"
          style={{ fontSize: '0.78rem', padding: '6px 12px' }}
        >
          {loading ? 'Refreshing...' : '↺ Refresh Trace'}
        </button>
      </div>

      {/* Filter pills */}
      <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
        {agentNames.map((agent) => (
          <button
            key={agent}
            onClick={() => setFilterAgent(agent)}
            style={{
              padding: '5px 10px',
              borderRadius: '6px',
              fontSize: '0.72rem',
              fontWeight: filterAgent === agent ? 600 : 500,
              background: filterAgent === agent ? 'rgba(6, 182, 212, 0.2)' : 'rgba(255, 255, 255, 0.04)',
              border: filterAgent === agent ? '1px solid #06b6d4' : '1px solid rgba(255, 255, 255, 0.08)',
              color: filterAgent === agent ? '#38bdf8' : '#94a3b8',
              cursor: 'pointer'
            }}
          >
            {agent}
          </button>
        ))}
      </div>

      {/* Terminal logs list */}
      <div style={{
        background: '#090d16',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        borderRadius: '12px',
        padding: '16px',
        maxHeight: '520px',
        overflowY: 'auto',
        fontFamily: 'var(--font-mono)',
        fontSize: '0.78rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '10px'
      }}>
        {filteredLogs.length === 0 ? (
          <div style={{ color: '#64748b', textAlign: 'center', padding: '20px' }}>
            No telemetry logs recorded yet.
          </div>
        ) : (
          filteredLogs.map((log, idx) => {
            let color = '#38bdf8';
            if (log.agent_name === 'Water Sentinel') color = '#10b981';
            else if (log.agent_name === 'Source Investigator') color = '#f59e0b';
            else if (log.agent_name === 'Dispatcher') color = '#8b5cf6';
            else if (log.agent_name === 'Verifier') color = '#34d399';
            else if (log.agent_name === 'Briefing Agent') color = '#ec4899';

            return (
              <div
                key={idx}
                style={{
                  background: 'rgba(255, 255, 255, 0.02)',
                  borderLeft: `3px solid ${color}`,
                  padding: '8px 12px',
                  borderRadius: '0 6px 6px 0'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ color, fontWeight: 700 }}>{log.agent_name}</span>
                    <span style={{
                      color: '#cbd5e1',
                      fontSize: '0.7rem',
                      background: 'rgba(255, 255, 255, 0.06)',
                      padding: '1px 6px',
                      borderRadius: '4px'
                    }}>
                      {log.action}
                    </span>
                  </div>
                  <span style={{ color: '#64748b', fontSize: '0.68rem' }}>
                    {log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : ''}
                  </span>
                </div>

                <div style={{ color: '#94a3b8', fontSize: '0.74rem' }}>
                  {typeof log.details === 'string' ? log.details : JSON.stringify(log.details)}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
