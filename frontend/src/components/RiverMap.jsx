import React, { useEffect, useRef } from 'react';
import L from 'leaflet';

export default function RiverMap({
  tickets,
  sensors,
  drains,
  riverCoords,
  onSelectTicket,
  onVerifyTicket
}) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const layersRef = useRef({
    river: null,
    sensors: null,
    drains: null,
    tickets: null,
    patrol: null
  });

  // Initialize map
  useEffect(() => {
    if (!mapContainerRef.current) return;
    if (mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: [28.660, 77.418],
      zoom: 12,
      zoomControl: true
    });

    // Dark sleek basemap — free, no API key required
    L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>',
      maxZoom: 20
    }).addTo(map);

    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Update River Polyline
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map || !riverCoords || riverCoords.length === 0) return;

    if (layersRef.current.river) {
      map.removeLayer(layersRef.current.river);
    }

    // Outer glow polyline
    const glowLine = L.polyline(riverCoords, {
      color: '#06b6d4',
      weight: 10,
      opacity: 0.35,
      lineCap: 'round'
    });

    // Core water polyline
    const coreLine = L.polyline(riverCoords, {
      color: '#38bdf8',
      weight: 4,
      opacity: 0.9,
      lineCap: 'round'
    });

    const riverGroup = L.layerGroup([glowLine, coreLine]).addTo(map);
    layersRef.current.river = riverGroup;
  }, [riverCoords]);

  // Update Sensors Layer
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map || !sensors) return;

    if (layersRef.current.sensors) {
      map.removeLayer(layersRef.current.sensors);
    }

    const markers = sensors.map((sensor) => {
      const isAnomaly = sensor.current?.is_anomaly;
      const ph = sensor.current?.ph?.toFixed(1) || '7.0';
      const tds = sensor.current?.tds_ppm?.toFixed(0) || '500';
      const turb = sensor.current?.turbidity_ntu?.toFixed(0) || '30';

      const iconHtml = `
        <div style="
          position: relative;
          width: 30px;
          height: 30px;
          display: flex;
          align-items: center;
          justify-content: center;
        ">
          <div style="
            position: absolute;
            width: ${isAnomaly ? '28px' : '20px'};
            height: ${isAnomaly ? '28px' : '20px'};
            border-radius: 50%;
            background: ${isAnomaly ? 'rgba(244, 63, 94, 0.3)' : 'rgba(16, 185, 129, 0.25)'};
            border: 2px solid ${isAnomaly ? '#f43f5e' : '#10b981'};
            box-shadow: 0 0 12px ${isAnomaly ? '#f43f5e' : '#10b981'};
            animation: pulseGlow 1.8s infinite;
          "></div>
          <div style="
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #fff;
            z-index: 2;
          "></div>
        </div>
      `;

      const customIcon = L.divIcon({
        html: iconHtml,
        className: 'sensor-marker-icon',
        iconSize: [30, 30],
        iconAnchor: [15, 15]
      });

      const marker = L.marker([sensor.lat, sensor.lng], { icon: customIcon });
      marker.bindPopup(`
        <div style="font-family: var(--font-body); padding: 4px; min-width: 200px;">
          <div style="font-weight: 700; font-size: 0.9rem; color: #38bdf8; margin-bottom: 2px;">
            ${sensor.node_name}
          </div>
          <div style="font-size: 0.75rem; color: #94a3b8; margin-bottom: 8px;">
            Reach ${sensor.reach_km} km | Node: ${sensor.node_id}
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 0.8rem; margin-bottom: 8px;">
            <div style="background: rgba(255,255,255,0.05); padding: 6px; border-radius: 6px;">
              <span style="color:#64748b; font-size: 0.7rem;">pH Value</span><br/>
              <strong style="color: ${ph < 6.0 || ph > 9.0 ? '#f43f5e' : '#10b981'};">${ph}</strong>
            </div>
            <div style="background: rgba(255,255,255,0.05); padding: 6px; border-radius: 6px;">
              <span style="color:#64748b; font-size: 0.7rem;">TDS (ppm)</span><br/>
              <strong style="color: ${tds > 1500 ? '#f43f5e' : '#f59e0b'};">${tds}</strong>
            </div>
            <div style="background: rgba(255,255,255,0.05); padding: 6px; border-radius: 6px; grid-column: span 2;">
              <span style="color:#64748b; font-size: 0.7rem;">Turbidity</span>: <strong>${turb} NTU</strong>
            </div>
          </div>
          ${isAnomaly ? `
            <div style="background: rgba(244,63,94,0.15); border: 1px solid rgba(244,63,94,0.3); padding: 6px 8px; border-radius: 6px; font-size: 0.75rem; color: #fda4af;">
              ⚠️ ${sensor.current.anomaly_reason || 'Severe Chemical Anomaly Active'}
            </div>
          ` : `
            <div style="font-size: 0.72rem; color: #6ee7b7;">✓ Normal baseline parameters</div>
          `}
        </div>
      `);
      return marker;
    });

    const sensorGroup = L.layerGroup(markers).addTo(map);
    layersRef.current.sensors = sensorGroup;
  }, [sensors]);

  // Update Drains Layer
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map || !drains) return;

    if (layersRef.current.drains) {
      map.removeLayer(layersRef.current.drains);
    }

    const markers = drains.map((drain) => {
      const iconHtml = `
        <div style="
          width: 22px;
          height: 22px;
          background: rgba(245, 158, 11, 0.2);
          border: 1.5px solid #f59e0b;
          border-radius: 6px;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 0 8px rgba(245, 158, 11, 0.4);
        ">
          <span style="font-size: 11px;">🏭</span>
        </div>
      `;

      const customIcon = L.divIcon({
        html: iconHtml,
        className: 'drain-marker-icon',
        iconSize: [22, 22],
        iconAnchor: [11, 11]
      });

      const marker = L.marker([drain.lat, drain.lng], { icon: customIcon });
      marker.bindPopup(`
        <div style="font-family: var(--font-body); padding: 4px; min-width: 210px;">
          <div style="font-weight: 700; font-size: 0.9rem; color: #fbbf24; margin-bottom: 2px;">
            ${drain.name}
          </div>
          <div style="font-size: 0.75rem; color: #94a3b8; margin-bottom: 6px;">
            ${drain.type.replace('_', ' ').toUpperCase()} | ${drain.id}
          </div>
          <div style="font-size: 0.8rem; color: #e2e8f0; margin-bottom: 4px;">
            <strong>Catchment:</strong> ${drain.catchment_area}
          </div>
          <div style="font-size: 0.8rem; color: #e2e8f0; margin-bottom: 6px;">
            <strong>Jurisdiction:</strong> ${drain.regulatory_jurisdiction}
          </div>
          <div style="font-size: 0.75rem; color: #64748b;">
            Typical Pollutants: ${drain.typical_pollutants.join(', ')}
          </div>
        </div>
      `);
      return marker;
    });

    const drainGroup = L.layerGroup(markers).addTo(map);
    layersRef.current.drains = drainGroup;
  }, [drains]);

  // Update Tickets Layer
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map || !tickets) return;

    if (layersRef.current.tickets) {
      map.removeLayer(layersRef.current.tickets);
    }

    const markers = tickets.map((t) => {
      const isClosed = t.status === 'VERIFIED_CLOSED';
      const isCritical = t.severity === 'CRITICAL';
      const isHigh = t.severity === 'HIGH';

      let color = '#3b82f6';
      if (isClosed) color = '#10b981';
      else if (isCritical) color = '#ef4444';
      else if (isHigh) color = '#f59e0b';

      const iconHtml = `
        <div style="
          width: 26px;
          height: 26px;
          border-radius: 50%;
          background: ${color};
          border: 2px solid #ffffff;
          box-shadow: 0 0 10px ${color};
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
        ">
          <div style="width: 8px; height: 8px; border-radius: 50%; background: #fff;"></div>
        </div>
      `;

      const customIcon = L.divIcon({
        html: iconHtml,
        className: 'ticket-marker-icon',
        iconSize: [26, 26],
        iconAnchor: [13, 13]
      });

      const marker = L.marker([t.location.lat, t.location.lng], { icon: customIcon });

      marker.on('click', () => {
        onSelectTicket && onSelectTicket(t);
      });

      marker.bindPopup(`
        <div style="font-family: var(--font-body); padding: 4px; min-width: 220px;">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
            <span style="font-size: 0.7rem; font-weight: 700; color: #38bdf8;">${t.id}</span>
            <span style="font-size: 0.65rem; font-weight: 700; padding: 2px 6px; border-radius: 4px; background: rgba(255,255,255,0.1); color: ${color};">
              ${t.severity}
            </span>
          </div>
          <div style="font-weight: 600; font-size: 0.85rem; color: #f8fafc; margin-bottom: 6px;">
            ${t.title}
          </div>
          <div style="font-size: 0.75rem; color: #94a3b8; margin-bottom: 8px;">
            Status: <strong>${t.status.replace('_', ' ')}</strong><br/>
            Dept: <strong>${t.assigned_department || 'Pending Dispatch'}</strong>
          </div>
          <div style="display: flex; gap: 6px;">
            <button id="view-tkt-btn-${t.id}" style="
              flex: 1;
              background: #06b6d4;
              color: #fff;
              border: none;
              padding: 5px 8px;
              border-radius: 4px;
              font-size: 0.75rem;
              font-weight: 600;
              cursor: pointer;
            ">
              View Evidence
            </button>
          </div>
        </div>
      `);

      marker.on('popupopen', () => {
        const btn = document.getElementById(`view-tkt-btn-${t.id}`);
        if (btn) {
          btn.onclick = () => onSelectTicket && onSelectTicket(t);
        }
      });

      return marker;
    });

    const ticketGroup = L.layerGroup(markers).addTo(map);
    layersRef.current.tickets = ticketGroup;

    // Draw patrol route for dispatched tickets
    if (layersRef.current.patrol) {
      map.removeLayer(layersRef.current.patrol);
    }

    const dispatched = tickets
      .filter((t) => t.status === 'DISPATCHED' && t.patrol_assignment)
      .map((t) => [t.location.lat, t.location.lng]);

    if (dispatched.length > 1) {
      const patrolLine = L.polyline(dispatched, {
        color: '#f59e0b',
        weight: 2.5,
        dashArray: '6, 8',
        opacity: 0.8
      }).addTo(map);
      layersRef.current.patrol = patrolLine;
    }
  }, [tickets, onSelectTicket]);

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', minHeight: '520px' }}>
      <div ref={mapContainerRef} style={{ width: '100%', height: '100%', borderRadius: '16px' }} />

      {/* Map Legend Floating Widget */}
      <div style={{
        position: 'absolute',
        bottom: '20px',
        left: '20px',
        background: 'rgba(15, 23, 42, 0.88)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '12px',
        padding: '12px 16px',
        zIndex: 500,
        boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
        fontSize: '0.75rem',
        color: '#cbd5e1'
      }}>
        <div style={{ fontWeight: 700, fontSize: '0.78rem', color: '#f8fafc', marginBottom: '8px' }}>
          MAP TELEMETRY LAYERS
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '18px', height: '4px', background: '#38bdf8', borderRadius: '2px' }}></div>
            <span>Hindon River Flow Line (Ghaziabad)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#10b981' }}></div>
            <span>IoT Sensor Node (Normal)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#f43f5e', border: '1px solid #fff' }}></div>
            <span>IoT Sensor Node (Spike Anomaly)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '10px', height: '10px', borderRadius: '2px', background: '#f59e0b' }}></div>
            <span>Industrial Drain / Outfall</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '18px', height: '2px', borderTop: '2px dashed #f59e0b' }}></div>
            <span>Active Patrol Route</span>
          </div>
        </div>
      </div>
    </div>
  );
}
