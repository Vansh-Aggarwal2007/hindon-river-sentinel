/**
 * API client for Hindon River Monitoring Command Center.
 */
const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export async function fetchHealth() {
  const res = await fetch(`${BASE_URL}/health`);
  return res.json();
}

export async function fetchTickets() {
  const res = await fetch(`${BASE_URL}/tickets`);
  return res.json();
}

export async function fetchTicket(id) {
  const res = await fetch(`${BASE_URL}/tickets/${id}`);
  return res.json();
}

export async function createReport(data) {
  const res = await fetch(`${BASE_URL}/tickets`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function fetchSensors() {
  const res = await fetch(`${BASE_URL}/sensors`);
  return res.json();
}

export async function postSensorReading(nodeId, data) {
  const res = await fetch(`${BASE_URL}/sensors/${nodeId}/reading`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function setRainfall(mm) {
  const res = await fetch(`${BASE_URL}/sensors/set-rain`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ rainfall_mm: mm }),
  });
  return res.json();
}

export async function fetchDrains() {
  const res = await fetch(`${BASE_URL}/drains`);
  return res.json();
}

export async function fetchRiverCoords() {
  const res = await fetch(`${BASE_URL}/river-coords`);
  return res.json();
}

export async function triggerInvestigation(ticketId) {
  const res = await fetch(`${BASE_URL}/agents/investigate/${ticketId}`, {
    method: 'POST',
  });
  return res.json();
}

export async function triggerDispatch(ticketId) {
  const res = await fetch(`${BASE_URL}/agents/dispatch/${ticketId}`, {
    method: 'POST',
  });
  return res.json();
}

export async function triggerVerify(ticketId, data) {
  const res = await fetch(`${BASE_URL}/agents/verify/${ticketId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function fetchAgentLogs() {
  const res = await fetch(`${BASE_URL}/agents/logs`);
  return res.json();
}

export async function resetDatabase() {
  const res = await fetch(`${BASE_URL}/agents/reset`, {
    method: 'POST',
  });
  return res.json();
}

export async function fetchBriefing() {
  const res = await fetch(`${BASE_URL}/briefing`);
  return res.json();
}

export async function approveEscalation(ticketId, officerNotes) {
  const res = await fetch(`${BASE_URL}/briefing/escalate/${ticketId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ officer_notes: officerNotes }),
  });
  return res.json();
}

export async function executeDemoStep(scenarioId, stepIndex) {
  const res = await fetch(`${BASE_URL}/demo/step`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scenario_id: scenarioId, step_index: stepIndex }),
  });
  return res.json();
}
