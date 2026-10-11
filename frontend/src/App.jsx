import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import RiverMap from './components/RiverMap';
import TicketsList from './components/TicketsList';
import SensorTrends from './components/SensorTrends';
import OfficerBriefing from './components/OfficerBriefing';
import AgentTerminal from './components/AgentTerminal';
import LiveReplayModal from './components/LiveReplayModal';
import CitizenReportModal from './components/CitizenReportModal';
import VerificationModal from './components/VerificationModal';
import TicketDrawer from './components/TicketDrawer';

import {
  fetchTickets,
  fetchSensors,
  fetchDrains,
  fetchRiverCoords,
  resetDatabase
} from './api/client';

export default function App() {
  const [activeTab, setActiveTab] = useState('map');
  const [tickets, setTickets] = useState([]);
  const [sensors, setSensors] = useState([]);
  const [drains, setDrains] = useState([]);
  const [riverCoords, setRiverCoords] = useState([]);

  // Modals & Drawers state
  const [isReplayOpen, setIsReplayOpen] = useState(false);
  const [isReportOpen, setIsReportOpen] = useState(false);
  const [verifyTicket, setVerifyTicket] = useState(null);
  const [selectedTicket, setSelectedTicket] = useState(null);

  // Load all telemetry
  const loadData = async () => {
    try {
      const [tkts, sens, drns, rvr] = await Promise.all([
        fetchTickets(),
        fetchSensors(),
        fetchDrains(),
        fetchRiverCoords()
      ]);
      setTickets(tkts || []);
      setSensors(sens || []);
      setDrains(drns || []);
      setRiverCoords(rvr || []);
    } catch (err) {
      console.error('Failed to load telemetry:', err);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleReset = async () => {
    if (window.confirm('Reset monitoring system to initial hackathon seed state?')) {
      await resetDatabase();
      loadData();
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenReplay={() => setIsReplayOpen(true)}
        onOpenReport={() => setIsReportOpen(true)}
        onReset={handleReset}
      />

      <main style={{ flex: 1, padding: '24px 28px', maxWidth: '1600px', margin: '0 auto', width: '100%' }}>
        {activeTab === 'map' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gap: '20px', height: 'calc(100vh - 120px)' }}>
            <div className="glass-panel" style={{ padding: '4px', overflow: 'hidden' }}>
              <RiverMap
                tickets={tickets}
                sensors={sensors}
                drains={drains}
                riverCoords={riverCoords}
                onSelectTicket={(t) => setSelectedTicket(t)}
                onVerifyTicket={(t) => setVerifyTicket(t)}
              />
            </div>

            {/* Side summary panel */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', overflowY: 'auto' }}>
              {/* Quick stats widget */}
              <div className="glass-panel" style={{ padding: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
                  <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#f8fafc', margin: 0 }}>
                    Hindon River Sector Telemetry
                  </h3>
                  <span className="pulse-indicator pulse-emerald"></span>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '0.8rem' }}>
                  <div style={{ background: 'rgba(0,0,0,0.3)', padding: '8px', borderRadius: '6px' }}>
                    <span style={{ color: '#64748b', fontSize: '0.7rem' }}>Active Outfalls</span><br/>
                    <strong style={{ color: '#fbbf24' }}>{drains.length} Major Drains</strong>
                  </div>
                  <div style={{ background: 'rgba(0,0,0,0.3)', padding: '8px', borderRadius: '6px' }}>
                    <span style={{ color: '#64748b', fontSize: '0.7rem' }}>IoT Stations</span><br/>
                    <strong style={{ color: '#38bdf8' }}>{sensors.length} River Nodes</strong>
                  </div>
                </div>
              </div>

              {/* Incidents Quick Feed */}
              <div className="glass-panel" style={{ padding: '16px', flex: 1, display: 'flex', flexDirection: 'column' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', margin: 0 }}>
                    Active Incidents Feed
                  </h4>
                  <button
                    onClick={() => setActiveTab('incidents')}
                    style={{ background: 'none', border: 'none', color: '#06b6d4', fontSize: '0.75rem', cursor: 'pointer', fontWeight: 600 }}
                  >
                    View All →
                  </button>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', overflowY: 'auto' }}>
                  {tickets.map((t) => (
                    <div
                      key={t.id}
                      onClick={() => setSelectedTicket(t)}
                      style={{
                        background: 'rgba(255, 255, 255, 0.03)',
                        border: '1px solid rgba(255, 255, 255, 0.06)',
                        borderRadius: '8px',
                        padding: '10px',
                        cursor: 'pointer',
                        transition: 'all 0.2s'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                        <span style={{ fontSize: '0.7rem', fontWeight: 700, color: '#38bdf8' }}>{t.id}</span>
                        <span className={`badge ${t.status === 'VERIFIED_CLOSED' ? 'badge-closed' : 'badge-medium'}`} style={{ fontSize: '0.65rem' }}>
                          {t.status.replace('_', ' ')}
                        </span>
                      </div>
                      <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#f8fafc' }}>
                        {t.title}
                      </div>
                      <div style={{ fontSize: '0.72rem', color: '#94a3b8', marginTop: '2px' }}>
                        Reach {t.location.reach_km} km | Dept: {t.assigned_department || 'Pending'}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'incidents' && (
          <TicketsList
            tickets={tickets}
            onSelectTicket={(t) => setSelectedTicket(t)}
            onOpenVerify={(t) => setVerifyTicket(t)}
            onRefreshData={loadData}
          />
        )}

        {activeTab === 'sensors' && (
          <SensorTrends sensors={sensors} onRefreshData={loadData} />
        )}

        {activeTab === 'briefing' && (
          <OfficerBriefing tickets={tickets} onRefreshData={loadData} />
        )}

        {activeTab === 'agents' && (
          <AgentTerminal />
        )}
      </main>

      {/* Modals & Drawers */}
      <LiveReplayModal
        isOpen={isReplayOpen}
        onClose={() => setIsReplayOpen(false)}
        onRefreshData={loadData}
      />

      <CitizenReportModal
        isOpen={isReportOpen}
        onClose={() => setIsReportOpen(false)}
        onReportCreated={loadData}
      />

      {verifyTicket && (
        <VerificationModal
          ticket={verifyTicket}
          onClose={() => setVerifyTicket(null)}
          onVerified={() => {
            setVerifyTicket(null);
            loadData();
          }}
        />
      )}

      {selectedTicket && (
        <TicketDrawer
          ticket={selectedTicket}
          onClose={() => setSelectedTicket(null)}
          onOpenVerify={(t) => {
            setSelectedTicket(null);
            setVerifyTicket(t);
          }}
          onRefreshData={loadData}
        />
      )}
    </div>
  );
}
