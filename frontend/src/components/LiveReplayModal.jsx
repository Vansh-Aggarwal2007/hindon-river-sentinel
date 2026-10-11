import React, { useState } from 'react';
import { executeDemoStep } from '../api/client';

export default function LiveReplayModal({ isOpen, onClose, onRefreshData }) {
  if (!isOpen) return null;

  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [stepData, setStepData] = useState(null);
  const [selectedScenario, setSelectedScenario] = useState('chemical_spike');

  const steps = [
    { num: 1, title: '1. Sensor Spike', agent: 'Water Sentinel', desc: 'Detects industrial pH & TDS surge at Hindon Barrage' },
    { num: 2, title: '2. Source Trace', agent: 'Source Investigator', desc: 'Backtracks river gradient to Sahibabad Drain (89% match)' },
    { num: 3, title: '3. Dept Dispatch', agent: 'Dispatcher', desc: 'Routes enforcement order to UPPCB Field Rapid Unit' },
    { num: 4, title: '4. Verification', agent: 'Verifier', desc: 'Before/After vision analysis (92% clean) & sensor normalization' },
    { num: 5, title: '5. IAS Briefing', agent: 'Briefing Agent', desc: 'Compiles DM Executive Summary & Section 33A notice' },
  ];

  const handleRunStep = async (stepNum) => {
    setLoading(true);
    setCurrentStep(stepNum);
    try {
      const res = await executeDemoStep(selectedScenario, stepNum);
      setStepData(res);
      onRefreshData && onRefreshData();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunRainFilter = async () => {
    setLoading(true);
    try {
      const res = await executeDemoStep('rain_runoff', 1);
      setStepData(res);
      onRefreshData && onRefreshData();
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
          width: '840px',
          maxWidth: '95vw',
          maxHeight: '90vh',
          overflowY: 'auto',
          padding: '28px',
          background: '#0d1527',
          border: '1px solid rgba(6, 182, 212, 0.3)',
          boxShadow: '0 20px 50px rgba(0, 0, 0, 0.7)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
          <div>
            <span style={{
              fontSize: '0.72rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              color: '#38bdf8',
              background: 'rgba(6, 182, 212, 0.15)',
              padding: '3px 8px',
              borderRadius: '4px'
            }}>
              Hackathon Presentation Mode
            </span>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#f8fafc', marginTop: '6px' }}>
              Interactive Incident Lifecycle Replay
            </h2>
            <p style={{ fontSize: '0.82rem', color: '#94a3b8', margin: 0 }}>
              Step through the autonomous multi-agent pipeline from initial detection to closed-loop verification.
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'rgba(255,255,255,0.05)',
              border: 'none',
              color: '#94a3b8',
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            ✕
          </button>
        </div>

        {/* Stepper Navigation */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(5, 1fr)',
          gap: '8px',
          marginBottom: '24px',
          background: 'rgba(255, 255, 255, 0.02)',
          padding: '8px',
          borderRadius: '12px',
          border: '1px solid rgba(255, 255, 255, 0.06)'
        }}>
          {steps.map((s) => {
            const isCurrent = currentStep === s.num;
            return (
              <button
                key={s.num}
                onClick={() => handleRunStep(s.num)}
                style={{
                  background: isCurrent ? 'linear-gradient(135deg, rgba(6, 182, 212, 0.25), rgba(59, 130, 246, 0.25))' : 'rgba(255, 255, 255, 0.03)',
                  border: isCurrent ? '1px solid #38bdf8' : '1px solid transparent',
                  borderRadius: '8px',
                  padding: '10px 8px',
                  textAlign: 'left',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
              >
                <div style={{ fontSize: '0.7rem', fontWeight: 700, color: isCurrent ? '#38bdf8' : '#64748b' }}>
                  {s.title}
                </div>
                <div style={{ fontSize: '0.78rem', fontWeight: 600, color: '#f8fafc', marginTop: '2px' }}>
                  {s.agent}
                </div>
              </button>
            );
          })}
        </div>

        {/* Action Controls */}
        <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
          <button
            onClick={() => handleRunStep(currentStep)}
            disabled={loading}
            className="btn btn-primary"
            style={{ flex: 1, padding: '10px' }}
          >
            {loading ? 'Agent Executing...' : `Execute Step ${currentStep}: ${steps[currentStep - 1]?.agent}`}
          </button>

          {currentStep < 5 && (
            <button
              onClick={() => handleRunStep(currentStep + 1)}
              disabled={loading}
              className="btn btn-secondary"
              style={{ padding: '10px 18px' }}
            >
              Next Step →
            </button>
          )}

          <button
            onClick={handleRunRainFilter}
            disabled={loading}
            className="btn btn-secondary"
            title="Demonstrate rainfall false alarm filtering"
            style={{ padding: '10px 14px', fontSize: '0.78rem', color: '#38bdf8' }}
          >
            🌧️ Rain Filter Test
          </button>
        </div>

        {/* Live Step Execution Output Display */}
        {stepData && (
          <div style={{
            background: 'rgba(0, 0, 0, 0.45)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: '12px',
            padding: '18px',
            animation: 'fadeIn 0.3s ease-out'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span className="pulse-indicator pulse-emerald"></span>
                <strong style={{ color: '#38bdf8', fontSize: '0.95rem' }}>{stepData.step_name}</strong>
              </div>
              <span className="badge badge-medium">{stepData.agent}</span>
            </div>

            <p style={{ color: '#e2e8f0', fontSize: '0.85rem', lineHeight: 1.6, marginBottom: '14px' }}>
              {stepData.description}
            </p>

            {/* Structured Telemetry Preview */}
            <div style={{
              background: '#090d16',
              borderRadius: '8px',
              padding: '12px',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.75rem',
              color: '#a5f3fc',
              maxHeight: '220px',
              overflowY: 'auto'
            }}>
              <pre style={{ margin: 0 }}>
                {JSON.stringify(stepData.data, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
