# Hindon River Sentinel — Project Summary & Architecture Blueprint

> **Autonomous Multi-Agent Command & Accountability Platform for River Rejuvenation**  
> **Target Sector:** Hindon River Corridor, Ghaziabad District, Uttar Pradesh (Karhera to NH-24)  
> **Core Innovation:** Upstream Hydrological Source Tracing + Closed-Loop Photographic & Sensor Verification

---

## 1. Executive Summary & Problem Context

### The Real-World Dilemma
The **Hindon River** in Western Uttar Pradesh (a tributary of the Yamuna) has suffered severe environmental degradation due to untreated municipal sewage, unregulated industrial effluent discharges (from textile, electroplating, and chemical clusters), and illegal solid waste dumping along floodplains. 

Historically, proactive District Magistrates (IAS officers) and municipal commissioners have launched intensive river cleaning and anti-dumping drives. However, these initiatives almost universally lose momentum after initial publicity because:
1. **Patchy Evidence & Manual Follow-Up:** Citizen complaints via WhatsApp groups or informal memos get lost without spatial-temporal tracking.
2. **Missing Source Attribution:** Downstream pollution spikes (e.g., toxic foam or fish mortality) are addressed as cosmetic cleanup without identifying which upstream drain or industrial cluster discharged the effluent.
3. **No Verification Loop (The Critical Failure Point):** Field contractors and junior staff report that an area is "cleaned," but there is no independent, automated verification of whether waste was actually removed or whether water quality rebounded.

### The Solution: An AI Command Center for Accountability
**Hindon River Sentinel** is **not** software that claims to clean the river. Instead, it is an **intelligent operating system for the district administration and patrolling task forces** that bridges the gap between detection, tracing, action, and verification.

---

## 2. Multi-Agent System Architecture

The core of the platform consists of 6 specialized, collaborating agents coordinated by an event orchestrator:

```
[ Citizen Photo Report / Downstream Sensor Spike ]
                       │
                       ▼
            ┌─────────────────────┐
            │    Triage Agent     │ ──► Vision AI: waste/foam classification, GPS check, deduplication (<200m)
            └──────────┬──────────┘
                       │
            ┌──────────┴──────────┐
            │   Water Sentinel    │ ──► Continuous IoT anomaly detection + Rainfall false-alarm filter
            └──────────┬──────────┘
                       │
            ┌──────────┴──────────┐
            │ Source Investigator │ ──► Upstream GIS backtracking + industrial drain chemical fingerprinting
            └──────────┬──────────┘
                       │
            ┌──────────┴──────────┐
            │  Dispatcher Agent   │ ──► Jurisdictional routing (UPPCB, Nagar Nigam, Jal Nigam, Irrigation) + TSP Patrol route
            └──────────┬──────────┘
                       │ (Field patrol executes remediation and uploads "After" photo)
            ┌──────────┴──────────┐
            │   Verifier Agent    │ ──► Closed-loop vision audit (≥80% clean) + sensor delta check -> Closes or Reopens
            └──────────┬──────────┘
                       │
            ┌──────────┴──────────┐
            │   Briefing Agent    │ ──► Daily Executive Dossier for DM/IAS (English + Hindi) & Section 33A notice
            └─────────────────────┘
```

### Deep Dive into the Agents

| Agent | Responsibility | Key Tools | Primary Metric / Output |
|---|---|---|---|
| **1. Triage Agent** ([`agents/triage.py`](file:///c:/Users/VANSH/Hackthons-Projects/Environmental-hacks/backend/app/agents/triage.py)) | First responder to citizen submissions. Classifies pollution type, computes preliminary severity & cleanliness scores, and suppresses duplicate reports within a 200m radius. | `check_duplicates`<br/>`analyze_image` | Classification accuracy, duplicate suppression rate. |
| **2. Water Sentinel** ([`agents/water_sentinel.py`](file:///c:/Users/VANSH/Hackthons-Projects/Environmental-hacks/backend/app/agents/water_sentinel.py)) | Continuous telemetry monitor. Evaluates pH, TDS, Turbidity, and Temperature against CPCB standards. Employs a **Rainfall Filter tool** to prevent false alarms during heavy rain storms when turbidity rises naturally from silt. | `evaluate_water_parameters`<br/>`get_recent_rainfall`<br/>`filter_rain_runoff` | False alarm suppression rate under rainfall; anomaly detection latency. |
| **3. Source Investigator** ([`agents/source_investigator.py`](file:///c:/Users/VANSH/Hackthons-Projects/Environmental-hacks/backend/app/agents/source_investigator.py)) *(Star Agent)* | Autonomous upstream hydrological investigator. When a spike or dumping is detected, backtracks upstream along river flow vectors, cross-references drain profiles and chemical fingerprints, and generates ranked candidate sources. | `get_upstream_outfalls`<br/>`get_land_use_and_profile`<br/>`evaluate_chemical_match` | Top-3 source hypothesis hit rate with transparent evidence. |
| **4. Dispatcher Agent** ([`agents/dispatcher.py`](file:///c:/Users/VANSH/Hackthons-Projects/Environmental-hacks/backend/app/agents/dispatcher.py)) | Routes incidents to the appropriate regulatory body based on authority domains. Formulates optimal patrol sequences using Travelling Salesperson (TSP) heuristic. | `route_department`<br/>`plan_patrol_route` | Response ETA optimization, 100% correct jurisdictional allocation. |
| **5. Verifier Agent** ([`agents/verifier.py`](file:///c:/Users/VANSH/Hackthons-Projects/Environmental-hacks/backend/app/agents/verifier.py)) *(Closed-Loop)* | The accountability enforcer. Audits "before" vs "after" photos using vision heuristics. Verifies downstream sensor parameters have normalized before marking tickets `VERIFIED_CLOSED`. Reopens tickets if remediation is incomplete. | `compare_before_after`<br/>`check_sensor_normalization` | Remediation audit accuracy; zero false closures. |
| **6. Briefing Agent** ([`agents/briefing.py`](file:///c:/Users/VANSH/Hackthons-Projects/Environmental-hacks/backend/app/agents/briefing.py)) | Synthesizes daily operational intelligence for District Magistrate / IAS leadership. Prepares bilingual summaries (English + Hindi) and drafts statutory show-cause notices under Section 33A of the Water Act 1974. | `aggregate_statistics`<br/>`generate_english_dossier`<br/>`generate_hindi_summary`<br/>`draft_statutory_notice` | Executive clarity; compliance with environmental statute language. |
| **7. System Orchestrator** ([`agents/orchestrator.py`](file:///c:/Users/VANSH/Hackthons-Projects/Environmental-hacks/backend/app/agents/orchestrator.py)) | Coordinates event transitions between agents and manages scripted replay presentation scenarios for live demos. | `run_end_to_end_citizen_report`<br/>`run_sensor_spike_pipeline`<br/>`run_demo_step` | End-to-end pipeline execution time and state consistency. |

---

## 3. Geospatial & Hydrological Foundation (Ghaziabad Stretch)

The system is calibrated to the critical **Ghaziabad stretch** of the Hindon River:

### Monitored River Centerline Coordinates
Flows North-to-South from Karhera (Lat 28.7125, Lng 77.4010) down to NH-24 / Chhijarsi (Lat 28.5820, Lng 77.4380).

### Key Monitored Outfalls & Catchments
1. **DRAIN-01: Sahibabad Industrial Drain** (Lat 28.6612, Lng 77.4110)
   - *Catchment:* Sahibabad Site IV Industrial Belt.
   - *Fingerprint:* Electroplating acids, textile dyes, surfactants, high TDS (>2100 ppm), acidic pH (<5.5).
   - *Jurisdiction:* UPPCB (Uttar Pradesh Pollution Control Board).
2. **DRAIN-02: Dasna Slaughterhouse & Tannery Drain** (Lat 28.6820, Lng 77.4250)
   - *Catchment:* Dasna - Masuri Agro/Tannery Belt.
   - *Fingerprint:* High BOD, organic sludge, pathogens, elevated TDS (~1850 ppm).
   - *Jurisdiction:* UPPCB.
3. **DRAIN-03: Karhera Municipal Outfall** (Lat 28.6945, Lng 77.4095)
   - *Catchment:* Karhera & Nandgram Residential Wards.
   - *Fingerprint:* Domestic blackwater, single-use plastics, embankment dumping corridor.
   - *Jurisdiction:* Nagar Nigam Ghaziabad.
4. **DRAIN-04: Arthala Mixed Drain** (Lat 28.6640, Lng 77.4140)
   - *Catchment:* Arthala & Mohan Nagar Mixed Sector.
   - *Fingerprint:* Domestic detergents, commercial runoff.
   - *Jurisdiction:* UP Jal Nigam.
5. **DRAIN-05: Indirapuram STP Bypass Drain** (Lat 28.6390, Lng 77.4010)
   - *Catchment:* High-density Indirapuram housing societies.
   - *Fingerprint:* Untreated sewage overflow during peak hours.
   - *Jurisdiction:* UP Jal Nigam.
6. **DRAIN-06: Pratap Vihar Flood Plain Dumping Channel** (Lat 28.6520, Lng 77.4280)
   - *Catchment:* Pratap Vihar embankment.
   - *Fingerprint:* Construction debris, illegal floodplain encroachment.
   - *Jurisdiction:* UP Irrigation Department.

### IoT Monitoring Nodes
- `HIN-NODE-01`: Karhera Upstream (Reach 2.5 km) — Baseline reference node.
- `HIN-NODE-02`: Hindon Barrage Central (Reach 7.8 km) — Critical confluence monitoring.
- `HIN-NODE-03`: Kanawani Culvert (Reach 11.2 km) — Downstream Indirapuram reach.
- `HIN-NODE-04`: Chhijarsi Bridge / NH-24 (Reach 14.6 km) — Exit boundary monitoring.

---

## 4. Codebase Architecture & File Structure

```
c:\Users\VANSH\Hackthons-Projects\Environmental-hacks/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI entry point with CORS & router mounts
│   │   ├── models.py                   # Pydantic schemas (Ticket, SensorReading, Hypotheses)
│   │   ├── database.py                 # Thread-safe in-memory cache + SQLite persistence
│   │   ├── seed_data.py                # Ghaziabad GIS coords, drains, nodes, sample tickets
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                 # BaseAgent, Haversine distance, execution logging
│   │   │   ├── triage.py               # Triage Agent (Vision classification & deduplication)
│   │   │   ├── water_sentinel.py       # Water Sentinel Agent (Sensor thresholds & rain filter)
│   │   │   ├── source_investigator.py  # Source Investigator (Upstream GIS backtracking)
│   │   │   ├── dispatcher.py           # Dispatcher Agent (Dept routing & TSP patrol routes)
│   │   │   ├── verifier.py             # Verifier Agent (Before/After audit & sensor checks)
│   │   │   ├── briefing.py             # Briefing Agent (Bilingual reports & legal notices)
│   │   │   └── orchestrator.py         # Pipeline coordination & demo replay runner
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── tickets.py              # CRUD endpoints for incident tickets & reports
│   │       ├── sensors.py              # IoT telemetry, rain simulation, GIS drains
│   │       ├── agents.py               # Direct agent trigger & logs endpoints
│   │       ├── briefing.py             # IAS executive briefing & escalation endpoints
│   │       └── demo.py                 # Live hackathon replay scenario endpoints
│   └── tests/
│       ├── __init__.py
│       ├── test_triage.py              # Unit tests for Triage Agent
│       ├── test_water_sentinel.py      # Unit tests for Water Sentinel & rain filter
│       ├── test_source_investigator.py # Unit tests for Upstream GIS backtracking
│       ├── test_dispatcher.py          # Unit tests for Department routing & patrol TSP
│       ├── test_verifier.py            # Unit tests for Verification & reopen logic
│       ├── test_briefing.py            # Unit tests for English/Hindi briefing & Section 33A
│       ├── test_orchestrator.py        # End-to-end incident cycle & replay steps
│       └── test_api_endpoints.py       # FastAPI REST API endpoint tests
├── frontend/
│   ├── index.html                      # Entry HTML with Leaflet CSS & Google Fonts
│   ├── package.json                    # Dependencies: React 18, Vite 6, Leaflet
│   ├── vite.config.js                  # Vite config with API proxy to localhost:8000
│   └── src/
│       ├── main.jsx                    # React DOM entry point
│       ├── App.jsx                     # Main Command Center UI orchestrator
│       ├── index.css                   # Modern dark design tokens, glassmorphism, animations
│       ├── api/
│       │   └── client.js               # Frontend API client for backend routes
│       └── components/
│           ├── Navbar.jsx              # Header with telemetry status and action triggers
│           ├── RiverMap.jsx            # Interactive Leaflet map (flow lines, nodes, pins)
│           ├── LiveReplayModal.jsx     # 5-step interactive hackathon demo stepper
│           ├── CitizenReportModal.jsx  # Photo upload with quick presets
│           ├── VerificationModal.jsx   # Before vs After photo audit & decision engine
│           ├── TicketDrawer.jsx        # Slide-out drawer with evidence and source ranking
│           ├── TicketsList.jsx         # Incidents list with search, status filters & actions
│           ├── OfficerBriefing.jsx     # IAS dossier view with English/Hindi toggle
│           ├── SensorTrends.jsx        # Telemetry node cards & interactive rainfall slider
│           └── AgentTerminal.jsx       # Real-time multi-agent reasoning trace log
├── .venv/                              # Isolated Python 3.14 virtual environment
├── requirements.txt                    # Frozen Python dependencies
├── hindon-river-hackathon-plan.md      # Original hackathon project plan
├── PROJECT_SUMMARY.md                  # This comprehensive document
└── README.md                           # GitHub README documentation
```

---

## 5. Backend REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check returning status and active agent roster |
| `GET` | `/api/tickets` | Returns all active and resolved incident tickets |
| `POST` | `/api/tickets` | Ingests a new citizen report; runs Triage Agent & deduplication |
| `GET` | `/api/tickets/{id}` | Fetches detailed ticket data including evidence and hypotheses |
| `GET` | `/api/sensors` | Returns telemetry readings from all 4 IoT sensor nodes |
| `POST` | `/api/sensors/{id}/reading`| Submits a sensor reading; runs Water Sentinel anomaly evaluation |
| `POST` | `/api/sensors/set-rain` | Sets simulated precipitation (mm) for the rainfall filter tool |
| `GET` | `/api/drains` | Returns GIS data for all 6 industrial and municipal drains |
| `GET` | `/api/river-coords` | Returns Hindon River centerline coordinates |
| `POST` | `/api/agents/investigate/{id}`| Triggers Source Investigator upstream backtracking on a ticket |
| `POST` | `/api/agents/dispatch/{id}` | Triggers Dispatcher Agent for departmental routing and patrol |
| `POST` | `/api/agents/verify/{id}` | Triggers Verifier Agent with "After" photo and sensor audit |
| `GET` | `/api/agents/logs` | Fetches real-time multi-agent reasoning logs and tool traces |
| `POST` | `/api/agents/reset` | Resets database and telemetry to initial seed state |
| `GET` | `/api/briefing` | Returns executive briefing in English and Hindi |
| `POST` | `/api/briefing/escalate/{id}`| Approves statutory Section 33A notice directive for a ticket |
| `POST` | `/api/demo/step` | Executes atomic step in the replay scenario (Steps 1–5) |

---

## 6. Test Suite & Verification Results

All 24 automated unit and integration tests were executed via pytest:

```
collected 24 items

backend/tests/test_api_endpoints.py::test_health_check_endpoint PASSED   [  4%]
backend/tests/test_api_endpoints.py::test_get_tickets_endpoint PASSED    [  8%]
backend/tests/test_api_endpoints.py::test_post_report_endpoint PASSED    [ 12%]
backend/tests/test_api_endpoints.py::test_sensors_endpoint PASSED        [ 16%]
backend/tests/test_api_endpoints.py::test_drains_endpoint PASSED         [ 20%]
backend/tests/test_api_endpoints.py::test_briefing_endpoint PASSED       [ 25%]
backend/tests/test_api_endpoints.py::test_demo_step_endpoint PASSED      [ 29%]
backend/tests/test_briefing.py::test_briefing_generation PASSED          [ 33%]
backend/tests/test_briefing.py::test_statutory_escalation PASSED         [ 37%]
backend/tests/test_dispatcher.py::test_department_routing_logic PASSED   [ 41%]
backend/tests/test_dispatcher.py::test_dispatch_ticket PASSED            [ 45%]
backend/tests/test_dispatcher.py::test_patrol_route_optimization PASSED  [ 50%]
backend/tests/test_orchestrator.py::test_end_to_end_citizen_report_pipeline PASSED [ 54%]
backend/tests/test_orchestrator.py::test_demo_replay_scenario_steps PASSED [ 58%]
backend/tests/test_source_investigator.py::test_upstream_outfalls_tool PASSED [ 62%]
backend/tests/test_source_investigator.py::test_investigate_barrage_incident PASSED [ 66%]
backend/tests/test_triage.py::test_triage_toxic_foam_classification PASSED [ 70%]
backend/tests/test_triage.py::test_triage_garbage_dumping_classification PASSED [ 75%]
backend/tests/test_triage.py::test_triage_duplicate_detection PASSED     [ 79%]
backend/tests/test_verifier.py::test_verifier_successful_remediation PASSED [ 83%]
backend/tests/test_verifier.py::test_verifier_rejection_and_reopen PASSED [ 87%]
backend/tests/test_water_sentinel.py::test_water_sentinel_normal_reading PASSED [ 91%]
backend/tests/test_water_sentinel.py::test_water_sentinel_chemical_spike_alert PASSED [ 95%]
backend/tests/test_water_sentinel.py::test_water_sentinel_rainfall_false_alarm_filter PASSED [100%]

======================== 24 passed in 3.81s ========================
```

---

## 7. The 3-Minute Hackathon Demo Script (How to Pitch)

1. **Problem Hook (30s):**
   * *Talking Point:* "IAS officers often lead high-energy river revival drives, but the moment they get transferred, the drive fades. Why? Because follow-up is manual, evidence is lost in WhatsApp chats, and nobody verifies if contractors actually cleared the waste. We built Hindon River Sentinel to automate institutional accountability."
2. **Citizen Photo Triage (30s):**
   * *Action:* Click **"Citizen Report"** in the top bar. Click the preset **"Toxic Chemical Foam"** and submit.
   * *Talking Point:* "The Triage Agent immediately runs vision analysis, extracts the severity, checks GPS bounds, and applies duplicate filtering within 200m to prevent spam."
3. **Sensor Spike & Upstream Source Investigation (60s):**
   * *Action:* Open **"Live Demo Replay"** and run **Step 1 (Sensor Spike)**, followed by **Step 2 (Source Trace)**.
   * *Talking Point:* "Downstream at Hindon Barrage, our sensor records a severe pH 5.1 and TDS surge. Instead of just raising a generic alarm, our **Source Investigator Agent** backtracks upstream along the hydrological flow vector. It checks GIS drain profiles and correlates the chemical fingerprint with Sahibabad Site IV industrial cluster (89% match)."
   * *Action:* Click **Step 3 (Dispatch)** to route the ticket to UPPCB Field Rapid Action Unit.
4. **Closed-Loop Verification (45s):**
   * *Action:* Click **Step 4 (Verification)**.
   * *Talking Point:* "Here is what makes our system stand out: the closed verification loop. The field team uploads an 'After' photo. The **Verifier Agent** audits the visual cleanliness (92% clean) and cross-checks downstream sensors. If the work was incomplete, it autonomously reopens the ticket. If verified, it closes it."
5. **IAS Daily Briefing & Legal Escalation (15s):**
   * *Action:* Open the **"IAS Executive Briefing"** tab. Toggle to **"हिंदी (Hindi)"**. Click **"Approve & Issue Directive"** to preview the Section 33A statutory notice under the Water Act 1974.
   * *Talking Point:* "Every evening, the District Magistrate gets a bilingual executive briefing with actionable red flags and statutory legal directives ready for signature."

---

## 8. Current Deployment Status

Both services are running and verified locally:
- **FastAPI Backend:** `http://127.0.0.1:8000` (API Docs: `http://127.0.0.1:8000/docs`)
- **Vite React Frontend:** `http://localhost:3000`
