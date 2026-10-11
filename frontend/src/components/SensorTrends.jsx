import React, { useState } from 'react';
import { postSensorReading, setRainfall } from '../api/client';

export default function SensorTrends({ sensors, onRefreshData }) {
  const [rainMm, setRainMm] = useState(0);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleRainChange = async (val) => {
    setRainMm(val);
    try {
      await setRainfall(val);
      setMessage(`Rainfall simulation set to ${val} mm.`);
      onRefreshData && onRefreshData();
    } catch (err) {
      console.error(err);
    }
  };

  const triggerSpike = async (nodeId) => {
    setLoading(true);
    try {
      await postSensorReading(nodeId, {
        ph: 5.2,
        turbidity_ntu: 195.0,
        tds_ppm: 2450.0,
        temp_c: 28.5
      });
      setMessage(`Triggered chemical anomaly on ${nodeId}. Sentinel alerted!`);
      onRefreshData && onRefreshData();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const resetSensor = async (nodeId) => {
    setLoading(true);
    try {
      await postSensorReading(nodeId, {
        ph: 7.3,
        turbidity_ntu: 42.0,
        tds_ppm: 580.0,
        temp_c: 26.0
      });
      setMessage(`Reset ${nodeId} to baseline clean parameters.`);
      onRefreshData && onRefreshData();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Rainfall simulation control bar */}
      <div className="glass-panel" style={{ padding: '20px 24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
          <div>
            <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#38bdf8', textTransform: 'uppercase' }}>
              Meteorological Coupling
            </span>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc', margin: '2px 0 0' }}>
              Precipitation & Stormwater False-Alarm Filter
            </h3>
          </div>
          <span className="badge badge-medium">
            Current: {rainMm} mm precipitation
          </span>
        </div>

        <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '14px' }}>
          Adjust rainfall slider to observe how the <strong>Water Sentinel Agent</strong> dynamically suppresses false alarms when turbidity spikes are caused by natural rainwater runoff rather than industrial discharge.
        </p>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <input
            type="range"
            min="0"
            max="50"
            step="5"
            value={rainMm}
            onChange={(e) => handleRainChange(parseFloat(e.target.value))}
            style={{ flex: 1, accentColor: '#06b6d4', cursor: 'pointer' }}
          />
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={() => handleRainChange(0)}
              className="btn btn-secondary"
              style={{ fontSize: '0.75rem', padding: '5px 10px' }}
            >
              ☀️ Dry (0mm)
            </button>
            <button
              onClick={() => handleRainChange(25)}
              className="btn btn-secondary"
              style={{ fontSize: '0.75rem', padding: '5px 10px' }}
            >
              🌧️ Heavy Rain (25mm)
            </button>
          </div>
        </div>

        {message && (
          <div style={{ marginTop: '10px', fontSize: '0.8rem', color: '#38bdf8' }}>
            ℹ️ {message}
          </div>
        )}
      </div>

      {/* Sensor Node Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '16px'
      }}>
        {sensors?.map((s) => {
          const isAnomaly = s.current?.is_anomaly;
          const ph = s.current?.ph?.toFixed(1) || '7.0';
          const tds = s.current?.tds_ppm?.toFixed(0) || '500';
          const turb = s.current?.turbidity_ntu?.toFixed(0) || '40';
          const temp = s.current?.temp_c?.toFixed(1) || '26.0';

          return (
            <div
              key={s.node_id}
              className="glass-panel"
              style={{
                padding: '20px',
                border: isAnomaly ? '1px solid rgba(244, 63, 94, 0.4)' : '1px solid rgba(255, 255, 255, 0.08)',
                boxShadow: isAnomaly ? '0 0 20px rgba(244, 63, 94, 0.2)' : 'none'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.72rem', color: '#64748b', fontWeight: 700 }}>
                  {s.node_id}
                </span>
                <span className={`badge ${isAnomaly ? 'badge-critical' : 'badge-closed'}`}>
                  {isAnomaly ? 'ANOMALY DETECTED' : 'NORMAL'}
                </span>
              </div>

              <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#f8fafc', marginBottom: '2px' }}>
                {s.node_name}
              </h4>
              <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '14px' }}>
                Reach {s.reach_km} km | {s.description}
              </p>

              {/* Metric meters */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '14px' }}>
                <div style={{ background: 'rgba(0,0,0,0.35)', padding: '10px', borderRadius: '8px' }}>
                  <div style={{ fontSize: '0.68rem', color: '#64748b' }}>pH Reading</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: ph < 6.0 || ph > 9.0 ? '#f43f5e' : '#34d399' }}>
                    {ph}
                  </div>
                  <div style={{ fontSize: '0.65rem', color: '#94a3b8' }}>Norm: 6.5 - 8.5</div>
                </div>

                <div style={{ background: 'rgba(0,0,0,0.35)', padding: '10px', borderRadius: '8px' }}>
                  <div style={{ fontSize: '0.68rem', color: '#64748b' }}>TDS Concentration</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: tds > 1500 ? '#f43f5e' : '#fbbf24' }}>
                    {tds} <span style={{ fontSize: '0.7rem' }}>ppm</span>
                  </div>
                  <div style={{ fontSize: '0.65rem', color: '#94a3b8' }}>Norm: &lt; 1000 ppm</div>
                </div>

                <div style={{ background: 'rgba(0,0,0,0.35)', padding: '10px', borderRadius: '8px' }}>
                  <div style={{ fontSize: '0.68rem', color: '#64748b' }}>Turbidity</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 700, color: turb > 120 ? '#fbbf24' : '#e2e8f0' }}>
                    {turb} <span style={{ fontSize: '0.7rem' }}>NTU</span>
                  </div>
                  <div style={{ fontSize: '0.65rem', color: '#94a3b8' }}>Norm: &lt; 50 NTU</div>
                </div>

                <div style={{ background: 'rgba(0,0,0,0.35)', padding: '10px', borderRadius: '8px' }}>
                  <div style={{ fontSize: '0.68rem', color: '#64748b' }}>Water Temp</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#e2e8f0' }}>
                    {temp} <span style={{ fontSize: '0.7rem' }}>°C</span>
                  </div>
                  <div style={{ fontSize: '0.65rem', color: '#94a3b8' }}>Seasonal avg</div>
                </div>
              </div>

              {isAnomaly && (
                <div style={{
                  background: 'rgba(244, 63, 94, 0.15)',
                  border: '1px solid rgba(244, 63, 94, 0.3)',
                  padding: '8px 10px',
                  borderRadius: '6px',
                  fontSize: '0.75rem',
                  color: '#fda4af',
                  marginBottom: '12px'
                }}>
                  ⚠️ {s.current?.anomaly_reason}
                </div>
              )}

              {/* Simulation buttons */}
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  onClick={() => triggerSpike(s.node_id)}
                  disabled={loading}
                  className="btn btn-secondary"
                  style={{ flex: 1, fontSize: '0.72rem', padding: '6px' }}
                >
                  ⚡ Simulate Spike
                </button>
                <button
                  onClick={() => resetSensor(s.node_id)}
                  disabled={loading}
                  className="btn btn-secondary"
                  style={{ flex: 1, fontSize: '0.72rem', padding: '6px' }}
                >
                  ↺ Reset Baseline
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
