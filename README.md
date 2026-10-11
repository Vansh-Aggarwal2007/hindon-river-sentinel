# Hindon River Sentinel — AI Command & Accountability Center

An autonomous, multi-agent command and accountability platform for monitoring and patrolling river rejuvenation drives along the **Hindon River** (Uttar Pradesh, Ghaziabad stretch: Karhera to NH-24).

Inspired by case studies where proactive IAS officers revived dying rivers, this platform closes the accountability loop by connecting detection, upstream hydrological source investigation, departmental dispatch, and **verified closed-loop resolution** with before/after vision comparison.

---

## 🌟 Key Architecture & Multi-Agent System

```
[ Citizen Report / Sensor Spike ]
                │
                ▼
       ┌─────────────────┐
       │   Triage Agent  │ ──► Vision AI classifies waste/foam, checks GPS & deduplicates (<200m)
       └────────┬────────┘
                │
       ┌────────┴────────┐
       │ Water Sentinel  │ ──► Rolling baseline anomaly detection + Rainfall false-alarm filter
       └────────┬────────┘
                │
       ┌────────┴────────┐
       │Source Investig. │ ──► GIS river flow backtracking & industrial drain fingerprinting
       └────────┬────────┘
                │
       ┌────────┴────────┐
       │Dispatcher Agent │ ──► Jurisdictional routing (UPPCB, Nagar Nigam, Jal Nigam, Irrigation) + TSP Patrol route
       └────────┬────────┘
                │ (Field team cleans & submits After photo)
       ┌────────┴────────┐
       │ Verifier Agent  │ ──► Vision comparison (>=80% clean) + sensor normalization -> Closes/Reopens
       └────────┬────────┘
                │
       ┌────────┴────────┐
       │ Briefing Agent  │ ──► Bilingual Daily Executive Dossier (English + Hindi) & Section 33A notice
       └─────────────────┘
```

### The 6 Specialized Agents
1. **Triage Agent** ([`backend/app/agents/triage.py`](file:///c:/Users/VANSH/Hackthons-Projects/Environmental-hacks/backend/app/agents/triage.py)):
   - Analyzes photos and descriptions (detects toxic foam, municipal plastic dumping, blackwater, illegal burning, encroachment).
   - Computes severity (LOW / MEDIUM / HIGH / CRITICAL) and cleanliness score.
   - Deduplication tool: suppresses duplicate spam within 200m radius and merges with existing active incidents.
2. **Water Sentinel Agent** ([`backend/app/agents/water_sentinel.py`](file:///c:/Users/VANSH/Hackthons-Projects/Environmental-hacks/backend/app/agents/water_sentinel.py)):
   - Evaluates real-time pH (6.5-8.5), TDS (<1000 ppm), Turbidity (<50 NTU) and temperature.
   - **Rainfall Filter tool**: suppresses false alarms during heavy precipitation (>15mm) when turbidity is elevated by natural sediment runoff with normal/diluted TDS.
3. **Source Investigator Agent** ([`backend/app/agents/source_investigator.py`](file:///c:/Users/VANSH/Hackthons-Projects/Environmental-hacks/backend/app/agents/source_investigator.py)) — *Headline Agentic Feature*:
   - Backtracks upstream along the hydrological gradient (Hindon North-to-South flow in Ghaziabad).
   - Queries GIS outfalls (Sahibabad Industrial Drain, Dasna Tannery Drain, Karhera Outfall, Arthala Drain).
   - Correlates chemical signatures (electroplating acids vs organic sludge) and produces ranked Top-3 hypotheses with transparent evidence.
4. **Dispatcher Agent** ([`backend/app/agents/dispatcher.py`](file:///c:/Users/VANSH/Hackthons-Projects/Environmental-hacks/backend/app/agents/dispatcher.py)):
   - Routes to the correct regulatory jurisdiction:
     - Chemical effluent & foam: `UPPCB (Uttar Pradesh Pollution Control Board)`
     - Municipal solid waste & plastics: `Nagar Nigam Ghaziabad`
     - Sewer trunk line / STP bypass: `UP Jal Nigam`
     - Encroachment & flood plain damage: `UP Irrigation Department`
   - Plans optimized patrol routes using Nearest-Neighbor routing.
5. **Verifier Agent** ([`backend/app/agents/verifier.py`](file:///c:/Users/VANSH/Hackthons-Projects/Environmental-hacks/backend/app/agents/verifier.py)) — *Closed-Loop Accountability*:
   - Compares before & after photos with vision AI.
   - Re-checks downstream IoT sensors for chemical normalization.
   - Autonomous determination: `VERIFIED_CLOSED` (>=80% clean) or `REOPENED` (audit failure with rejection notes).
6. **Briefing Agent** ([`backend/app/agents/briefing.py`](file:///c:/Users/VANSH/Hackthons-Projects/Environmental-hacks/backend/app/agents/briefing.py)):
   - Generates daily executive intelligence dossier for the District Magistrate / IAS Officer.
   - Bilingual: Full English report + Hindi summary (हिंडन नदी स्वच्छता अभियान प्रशासनिक सारांश).
   - Drafts statutory show-cause notices under Section 33A of Water (Prevention & Control of Pollution) Act 1974.

---

## 🚀 How to Run

### 1. Backend (FastAPI)
```bash
# Activate virtual environment
.venv\Scripts\activate

# Run backend API server on port 8000
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation available at: `http://127.0.0.1:8000/docs`

### 2. Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
Dashboard available at: `http://localhost:3000`

### 3. Run Automated Tests
```bash
$env:PYTHONPATH="backend"
.venv\Scripts\pytest backend/tests -v
```
All 24 unit and integration tests cover:
- Triage classification & spatial deduplication
- Water Sentinel anomaly thresholds & rainfall runoff filter
- Source Investigator upstream GIS backtracking
- Dispatcher routing & TSP patrol optimization
- Verifier before/after comparison & reopen logic
- Briefing bilingual synthesis & Section 33A notice drafting
- System Orchestrator end-to-end incident cycle & replay steps

---

## ⏱️ 3-Minute Hackathon Demo Script

1. **Problem & Angle (30s):**
   Show the Hindon river map (Karhera to NH-24). Explain that cleanup drives usually fade because there is no automated accountability or verification.
2. **Citizen Photo Report (30s):**
   Click `Citizen Report`, pick a preset (e.g. *Toxic Chemical Foam*). Watch the **Triage Agent** classify it in real-time, compute severity, and map it.
3. **Sensor Spike & Upstream Investigation (60s):**
   Click `Live Demo Replay`. Execute Step 1: **Water Sentinel** catches a pH/TDS spike. Execute Step 2: **Source Investigator** backtracks upstream to identify Sahibabad Industrial Drain as the top culprit (89% match). Execute Step 3: **Dispatcher** routes the ticket to UPPCB.
4. **Closed-Loop Verification (45s):**
   Execute Step 4: **Verifier Agent** audits before vs after photos (92% clean) and confirms sensor normalization, marking the ticket `VERIFIED_CLOSED`.
5. **IAS Executive Briefing (15s):**
   Show the `IAS Executive Briefing` tab with English and Hindi summaries, and click to approve a statutory Section 33A notice.
