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
* Mobile Application: `http://127.0.0.1:8000/mobile/app.html`

### 2. Frontend Command Center
```bash
cd frontend
npm install
npm run dev
```
* Dashboard: `http://localhost:3000`

---

## Machine Learning & Benchmark Evidence

* **Risk Reduction:** –79.4% average route hazard reduction compared to traditional shortest-path algorithms (OSM / Google Maps baseline).
* **Stranding Prevention:** 0% stranding rate in monsoon landslide simulation benchmarks.
* **Reliability:** 94.8% on-time delivery reliability under degraded road conditions.
