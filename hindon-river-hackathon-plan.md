# Hindon River Cleaning-Drive Monitoring: Hackathon Project Plan

> **How to use this file:** Paste it into a Claude chat (or attach it) and ask questions or request changes, for example "we're only 3 people, adjust the plan", "write the ticket JSON schema", or "make the Source Investigator simpler". Claude will have the full project context below.

---

## 1. Project brief

**Goal:** Build a hackathon project for monitoring and patrolling a river-cleaning drive on the **Hindon river** (Uttar Pradesh), inspired by cases where IAS officers revived rivers that had turned into sewers.

**Requirements from the team:**
- A multi-agent, agentic AI system that is genuinely implemented, not a formality.
- It should stand out from typical hackathon projects.
- It must be feasible within a 24-hour hackathon.

**Core insight:** River revivals led by a single officer often fade because evidence is patchy and follow-up is manual. This project is a **command center for the drive**: it detects problems, traces them to a source, dispatches someone, and then **verifies the problem was actually fixed**. The verification step is what most projects skip.

**Feasibility verdict:** Doable if scoped as a *monitoring and accountability system*, not a "clean the river" system. Software cannot clean the river, but it can keep a drive honest and sustained.

---

## 2. Data sources

| Source | Notes |
|---|---|
| Citizen and volunteer reports | Geotagged photos via a Telegram/WhatsApp bot or a simple PWA |
| Patrol app | GPS-tracked routes for volunteers and officials (the "patrol" part) |
| Satellite | Sentinel-2 (free, via Google Earth Engine or Copernicus): turbidity and algal-bloom proxies, bank encroachment, dumping hotspots. 10 m resolution, so it works on wider stretches but not narrow ones |
| Context data | Rainfall/weather (Open-Meteo), drain and outfall locations (OpenStreetMap plus manual pins), CPCB/UPPCB station data if accessible. **Unverified:** many stations report monthly rather than in real time, so check availability early |
| Optional IoT node | ESP32 with pH, turbidity, TDS and temperature sensors, publishing over MQTT |

---

## 3. The agents

| Agent | Job | Tools |
|---|---|---|
| **Triage** | Reads a photo and classifies it (garbage, sewage outfall, foam, burning, encroachment), scores severity, removes duplicates | Vision model, EXIF/GPS check |
| **Water Sentinel** | Detects anomalies in sensor and satellite readings; filters out rain-driven false alarms | Anomaly detection, weather API |
| **Source Investigator** | When a spike appears, uses flow direction and the drain map to produce ranked source hypotheses with evidence | GIS queries, sensor history |
| **Dispatcher** | Assigns each ticket to the right department (Nagar Nigam, UPPCB, Jal Nigam, Irrigation) and plans patrol routes by priority | OR-Tools routing, ticket DB |
| **Verifier** | Requires before/after photos, compares them, rechecks sensors and the next satellite pass, closes or reopens the ticket | Vision model, sensor data |
| **Briefing** | Writes a daily summary for the officer (English, plus Hindi if time allows), flags overdue tickets, builds an evidence pack for escalation | Report generation |

An **orchestrator** routes events between agents through a shared ticket database and an event bus (MQTT or SQS). Escalations and enforcement notices need **human approval**.

### What makes it real rather than a formality
- Every agent has a defined input, tool calls, a structured JSON output, and a metric.
  - Triage: accuracy on about 100 labeled photos.
  - Source Investigator: how often its top-3 hypotheses contain the true source in simulated incidents.
- The Source Investigator and the closed verification loop are the genuinely agentic parts (multi-step reasoning over tools).
- The demo is a **replay scenario**: sensor spike, traced to a drain, ticket raised, patrol dispatched, before/after photo submitted, ticket closed or reopened.

---

## 4. Honest limits and risks

- BOD and dissolved oxygen cannot be measured cheaply. pH, turbidity, TDS and temperature are only **indicative**; label them that way.
- If sensor data is simulated for the demo, **say so**. Judges respect honesty.
- Source attribution is a *hypothesis for human review*, never an accusation against a factory.
- Crowdsourcing invites spam: verify with GPS and EXIF checks and duplicate detection.
- Don't cover the whole river. Pick one stretch (the Ghaziabad section) and do it properly.
- Photo privacy: avoid capturing identifiable people.

---

## 5. Suggested stack

- **Backend:** Python (Flask or FastAPI) with Postgres/PostGIS or SQLite
- **Agents:** Claude API with tool use, or LangGraph for orchestration
- **Messaging:** Mosquitto (MQTT)
- **Frontend:** React with a Leaflet map (tickets, patrol routes, sensor readings)
- **Deployment:** Docker Compose (on Windows, run through WSL2 to avoid environment mismatches)
- **Optional AWS angle:** IoT Core, Lambda, S3, Bedrock

---

## 6. Team roles (assumes 4 people; if 3, merge D into the others)

- **A:** backend and orchestrator (API, ticket DB, agent wiring)
- **B:** frontend (map, patrol view, ticket UI)
- **C:** AI and data (vision prompts, sensor and satellite data, Source Investigator)
- **D:** glue, demo and pitch (bot/upload form, dataset collection, evals, slides, README)

---

## 7. 24-hour build plan

Hour 0 is the start of the hackathon. The principle: get one end-to-end slice working by hour 12, then deepen it.

| Hours | Goal | What exists at the end |
|---|---|---|
| **0-1** | Lock scope: one stretch (Ghaziabad), the demo scenario, the ticket JSON schema, API endpoints. Create the repo, `docker-compose.yml` (API, Mosquitto, DB), and API keys | A shared contract everyone codes against |
| **1-3** | In parallel. A: `/report` and `/tickets` endpoints. B: map with dummy pins. C: test the vision prompt on sample photos. D: Telegram bot or web upload form, and start collecting 50+ labeled photos (garbage, foam, drains, clean banks) | Running skeleton, with a map showing fake tickets |
| **3-6** | **Triage agent:** photo, then structured JSON (type, severity, confidence), then duplicate check by location and time, then a ticket on the map. In parallel, C builds a simulated sensor publisher over MQTT, and D pulls drain and outfall locations from OSM plus manual pins | **Milestone 1:** photo in, ticket on map |
| **6-9** | **Dispatcher agent:** rules route tickets to departments, with the LLM handling ambiguous cases. Basic patrol route via OR-Tools. B builds the patrol view. C starts the satellite layer (Sentinel-2 turbidity and algae indices, exported as an overlay) | Tickets get assigned and routed |
| **9-12** | **Water Sentinel:** rolling-baseline anomaly detection on sensor data with a rainfall filter. Alerts go onto the event bus and show as map markers | **Milestone 2:** end-to-end slice works. Commit and eat |
| **12-15** | **Source Investigator:** tools such as `get_upstream_outfalls(point)`, `get_sensor_history`, `get_land_use`. Outputs ranked hypotheses with evidence. Test on 3 scripted incidents | The headline agentic feature |
| **15-17** | **Verifier:** requires a before/after photo, compares them with the vision model, rechecks sensors, closes or reopens the ticket | The loop is closed |
| **17-19** | **Briefing agent:** daily summary (English, Hindi if time allows), overdue-ticket escalation, human approval button. Optionally a PDF evidence pack | Feature-complete product |
| **19-20** | **Feature freeze.** Run evals: Triage accuracy on a held-out photo set, Investigator top-3 hit rate on scripted incidents | Real numbers for the pitch |
| **20-22** | Bug bash, UI polish, seed demo data, architecture diagram, README. Cache the LLM responses used in the demo so a rate limit can't break it | A stable build |
| **22-23** | Slides (5-7), backup demo video (screen capture), deployment check | Pitch material and a fallback |
| **23-24** | Two full rehearsals, submit with buffer, **no new code** | Submitted |

### Practical notes
- **Sleep:** each person takes a 2-3 hour nap somewhere in hours 12-17, staggered so one person is always awake on the main branch.
- **Git:** commit at every milestone; merge to main only when the demo still runs.

### Cut list if behind (drop in this order)
1. Hindi briefing
2. PDF evidence pack (output markdown instead)
3. OR-Tools routing (use nearest-neighbor ordering)
4. Live satellite pipeline (use a static overlay image)
5. Telegram bot (use a web form)

**Never cut the Source Investigator or the Verifier.** They are what make the project stand out.

---

## 8. 3-minute demo script

1. **Problem and angle (30s):** drives fade without follow-up.
2. **Live photo report (30s):** it becomes a ticket on the map.
3. **Sensor spike (60s):** the Investigator traces it upstream and the Dispatcher assigns a patrol.
4. **Verification (45s):** before/after photos close the ticket, or reopen it.
5. **Eval numbers and roadmap (15s).**

---

## 9. Open decisions for the team

Fill these in and bring them back to Claude when modifying the plan:

- [ ] Final team size and who takes each role
- [ ] Exact river stretch to cover
- [ ] Real sensor hardware or simulated data? (If simulated, plan to label it clearly in the demo)
- [ ] Which departments to include in the Dispatcher's routing rules
- [ ] Whether to include Hindi output
- [ ] Hackathon rules: allowed APIs, data restrictions, judging criteria
- [ ] Which LLM/vision provider and who holds the API keys

## 10. Useful follow-up requests to ask Claude

- "Write the ticket JSON schema and API contract for hour 0."
- "Draw the architecture diagram."
- "Write the Triage agent's vision prompt and output schema."
- "Design the 3 scripted incidents for the Source Investigator eval."
- "Adjust the 24-hour plan for a team of 3 / a team of 5."
- "Write the pitch deck outline."
