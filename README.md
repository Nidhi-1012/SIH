# NER-LINK AI (SIH26002)

### Smart Logistics & Accessibility Intelligence Platform for North Eastern Region (NER)
**AI-Based Early Warning, Landslide Risk Monitoring & Safe Route Navigation System**

---

## Overview

NER-LINK AI is a comprehensive disaster-resilient navigation, road risk monitoring, and logistics management platform specifically engineered for the challenging topography of North East India.

The system continuously monitors landslide vulnerability, rainfall intensity, flood risks, and road blockages across critical NER highway corridors (e.g. NH-6 Guwahati–Shillong–Silchar, NH-37 Guwahati–Jorhat, NH-13 Sela Pass–Tawang). It calculates multi-factor dynamic risk scores and guides drivers, truck operators, emergency responders, and citizens onto the **safest practical routes**.

---

## Key Features

1. **AI Safe-Route Engine (Safety Over Speed)**
   - Evaluates routes across 4 critical risk factors: Landslide Probability, Rain/Weather Intensity, Flood Inundation Risk, and Road Condition.
   - Dynamic prioritization (P0 Emergency/Medical, P1 Perishables, P2 General Freight, P3 Passenger).
   - Real-time adaptive re-routing warnings with single-tap route switching.

2. **Mobile-First Responsive Web Application (`/mobile`)**
   - 100% vector SVG icons (clean, high-contrast, scalable, zero emoji dependencies).
   - Designed for Android smartphones used by drivers, villagers, and transport operators.
   - Turn-by-turn navigation with audio voice guidance via Web Speech API.
   - Emergency SOS modal (112 / 1070 disaster helpline, WhatsApp / SMS GPS sharing).
   - 2-tap crowd-sourced road hazard reporting with offline sync queue.
   - Multilingual support (English, Hindi, Assamese).

3. **High-Performance FastAPI Backend**
   - SQLite / PostgreSQL with SQLAlchemy ORM.
   - Open-Meteo live rainfall and weather sync engine.
   - Random Forest Risk Classifier with SHAP explainability.
   - Field incident logging with automated road state transitions (Open, Caution, Degraded, Blocked).
   - Real-time alert engine with 15-minute hysteresis cooldown.

4. **React Command Center Dashboard**
   - Interactive Leaflet live corridor map.
   - Active road segment condition monitoring.
   - Incident management and alert dispatch control.

---

## Project Structure

```
SIH/
├── backend/                  # FastAPI REST API & ML services
│   ├── app/
│   │   ├── main.py           # Application entrypoint & routes
│   │   ├── models.py         # SQLAlchemy ORM models
│   │   ├── schemas.py        # Pydantic data schemas
│   │   └── services/         # Weather, Routing, Risk ML services
│   └── requirements.txt
├── frontend/                 # React + Vite + TypeScript Command Center
│   ├── src/
│   │   ├── App.tsx           # Dashboard layout & live map
│   │   └── components/       # Metric cards, alert streams
│   └── public/
│       └── mobile/           # Mobile SafeRoute PWA
├── mobile/                   # Standalone Mobile PWA (app.html / index.html)
├── ml/                       # Machine Learning models, training & benchmarks
│   ├── benchmark_replay.py   # Baseline vs NER-LINK comparative benchmark
│   └── artifacts/            # Evaluation metrics and benchmark results
└── data/                     # Corridor GeoJSON & demo pitch scenarios
```

---

## Quick Start

### 1. Backend Service
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows (or source venv/bin/activate on Linux/Mac)
pip install -r requirements.txt
uvicorn app.main:app --port 8000 --reload
```
* API Documentation: `http://127.0.0.1:8000/docs`
* Mobile Application (served standalone by the backend): `http://127.0.0.1:8000/mobile/`

### 2. Frontend Command Center
```bash
cd frontend
npm install
npm run dev
```
* Dashboard: `http://localhost:3000`

---

## Machine Learning & Benchmark Evidence

Computed by `ml/benchmark_replay.py` (run it yourself: `python ml/benchmark_replay.py`
from the repo root) — it calls the same routing and risk-scoring code the live
API uses, against the real pilot-corridor segments, under two simulated
weather scenarios. Full per-pair results in `ml/artifacts/benchmark_results.json`.
These are not hand-typed figures.

**Scenario 1 — Severe Monsoon Closure** (a segment pushed fully Blocked):
* A naive shortest-distance router (no live road-condition awareness) drives
  straight through the confirmed closure on **83.3%** of the benchmark's
  origin-destination pairs. Any closure-aware router — ours included —
  strands on **0%**.

**Scenario 2 — Elevated Risk Advisory** (a segment pushed to Caution, but
still technically open — the case a purely reactive, closure-only system
can't see): this is the genuine "AI picks the safer route before the road
fails" comparison, made possible by a real alternate bypass
(`SEG-NH6-06-ALT` in `data/pilot_corridor.json`) added around the corridor's
highest-risk segment specifically so this comparison exists.
* A naive router and a purely reactive closure-avoider both still drive
  through the elevated-risk segment on 5 of 6 test routes — neither has any
  concept of "risky but open."
* NER-LINK AI's risk-weighted routing reroutes around it on 2 of those 5,
  cutting average risk exposure by **30.4%** — proactively, before any
  closure is confirmed.

**Known limitation, stated plainly:** this differentiation currently exists
at exactly one point in the pilot corridor (the bypass added around
`SEG-NH6-06`). Other high-risk segments in the dataset (e.g. the
Nongpoh–Umiam stretch) still have no alternate route, so a closure there
still means "no route," not a smart detour, for every strategy alike.
Extending real alternate routes to more of the corridor is the next step
toward a fully general safe-routing claim, not a solved problem yet.
