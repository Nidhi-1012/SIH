# Implementation Plan

## NER-LINK AI — AI-Based Smart Logistics & Accessibility Intelligence Platform

| Field | Value |
|---|---|
| Companion document | `PRD_NER-LINK_AI.md` (this plan implements it — do not duplicate rationale, only execution) |
| Problem statement | SIH26002 |
| Plan status | v1.0 |
| Prepared | 9 September 2026 |
| Build window | 7-day sprint, scheduled to finish with margin before the 30 Sept 2026 SIH26002 deadline |

---

## 1. How to Use This Document

This is the execution layer under the PRD: concrete tasks, owners, order of operations, environment setup, and Definition of Done per day. Every task references the PRD section it implements, so if a requirement is unclear, go back to the PRD — this document does not re-argue design decisions, it schedules them.

**Before Day 1 starts:** the 7 open decisions in PRD §15 must be closed. Section 2 below turns each into a concrete input this plan needs.

---

## 2. Pre-Sprint Setup (Day 0)

### 2.1 Close the open decisions (PRD §15) — produces these hard inputs

| Decision | Output needed before Day 1 |
|---|---|
| Pilot geography | Bounding box (lat/lon) + list of district names for the OSM extract |
| Routing engine | Confirmed: GraphHopper self-hosted (PRD §6.3/§14.3) unless overridden |
| Weather source | Confirmed: IMD adapter + fallback provider (PRD §14.2) |
| AI target | Confirmed: disruption probability at 6/12/24h + confidence |
| Field-report schema | Confirmed fields: GPS, incident_type, severity, photo, notes, reporter, timestamp |
| Cargo priority classes | Confirmed: medicines, food, agri produce, construction material → P0–P3 |
| Demo scenario | Confirmed: rainfall → field report → risk spike → P0 reroute → alert → ETA update |

### 2.2 Accounts, tokens, repos

- [ ] Create GitHub org/repo, branch protection on `main`, CI skeleton (GitHub Actions).
- [ ] Register for Bhuvan API access (token expires every 24h — build a refresh script/cron immediately, don't leave it for later; PRD §14.4).
- [ ] Confirm IMD API endpoint access (`api.imd.gov.in`) and cache a sample response for offline dev.
- [ ] Provision cloud VM/container (Docker host) for GraphHopper + Postgres/PostGIS + Redis.
- [ ] Set up object storage bucket for incident photos.
- [ ] Set up Firebase project for FCM (push notifications).
- [ ] Agree on Slack/Discord channel + daily 15-min stand-up time for the 7-day sprint.

### 2.3 Environment skeleton

```text
/backend        FastAPI service (REST + WebSocket)
/ml             training scripts, notebooks, model artifacts, SHAP explainability
/routing        GraphHopper config, custom_model profiles, docker-compose
/frontend       React + TS command dashboard
/mobile         Flutter/React Native field app
/infra          docker-compose.yml, GitHub Actions workflows, seed scripts
/data           OSM extract, historical/synthetic incident data, weather cache
```

- [ ] `docker-compose.yml` brings up: Postgres+PostGIS, Redis, GraphHopper, backend API, frontend dev server — one command (`docker compose up`) for any team member to get a working local stack.
- [ ] Seed script loads pilot-corridor OSM extract into PostGIS.

**Definition of Done for Day 0:** any team member can clone the repo, run one command, and see a blank map of the pilot corridor in the browser.

---

## 3. Day 1 — Foundation (PRD §6.1, §9, §8)

**Goal:** road network + database schema + basic map, end to end.

| Task | Owner | PRD ref |
|---|---|---|
| Finalize pilot corridor OSM extract; clip to bounding box | GIS/Route Engineer | §5 |
| Create Postgres/PostGIS schema: `road_segments`, `users`, `vehicles`, `shipments`, `incidents`, `weather_observations`, `vehicle_telemetry`, `route_predictions`, `alerts` | Backend | §9 |
| Import road geometry into `road_segments`; assign `road_class`, `district`, `bridge_id` where derivable from OSM tags | GIS/Route Engineer | §9 |
| Stand up FastAPI skeleton: health check, DB connection, migrations (Alembic) | Backend | §8 |
| Command Center Map — render base map + road segments (no live logic yet) | Frontend | §6.7 |
| Draft `incidents` API contract (POST/GET) so mobile team can start against a mock | Backend + Mobile | §6.6 |

**Definition of Done:** road segments render on the Command Center map, pulled live from PostGIS via the FastAPI backend, colored by a placeholder status field.

---

## 4. Day 2 — Routing + Incident API (PRD §6.3, §6.6, §14.3)

| Task | Owner | PRD ref |
|---|---|---|
| Stand up GraphHopper self-hosted against the pilot OSM extract; confirm `/route` works | GIS/Route Engineer | §6.3, §14.3 |
| Define a `custom_model` profile skeleton that accepts a per-request risk-weight parameter (even if the weight is a placeholder for now) | GIS/Route Engineer | §6.3, §14.3 |
| `road_status` model: implement the four-state machine (`Open/Caution/Blocked/Unknown`) with confidence + freshness decay logic | Backend | §6.1 |
| Incident API: implement POST `/incidents` (matches field-report schema), attach nearest-segment lookup (PostGIS `ST_ClosestPoint`/`ST_DWithin`) | Backend | §6.6 |
| Incident submission → triggers `road_segments` status recalculation | Backend | §6.1, §6.6 |
| Mobile app skeleton: incident report form (online mode only for now) | Mobile | §6.6 |

**Definition of Done:** submitting an incident via API (or the mobile form) visibly changes a segment's status on the Command Center map on refresh.

---

## 5. Day 3 — Weather Ingestion + Baseline ML (PRD §6.2, §14.2)

| Task | Owner | PRD ref |
|---|---|---|
| Build IMD adapter (provider-abstraction interface, not a hardcoded IMD call) — fetch district rainfall/forecast, normalize into `weather_observations` | Integration/Product | §14.2 |
| Implement fallback weather provider behind the same abstraction | Integration/Product | §14.2 |
| Feature engineering: join rainfall (1h/6h/24h + forecast), historical incident counts per segment, road condition, data freshness into a training table | AI/ML Lead | §6.2 |
| Generate/label historical or synthetic disruption events for the pilot corridor (needed because live historical data won't exist for a new pilot area) | AI/ML Lead | §11, §13.5 |
| Train Phase 1 baseline model (Logistic Regression → Random Forest → XGBoost, pick the best on validation) | AI/ML Lead | §6.2 |
| Wire SHAP (or feature-importance fallback) to produce top-factor explanations per prediction | AI/ML Lead | §6.2 |

**Definition of Done:** calling the risk-scoring function for any pilot segment returns a 0–100 score, a disruption probability, and a top-3 factor breakdown — even if accuracy is still rough.

---

## 6. Day 4 — Risk-Aware Routing + Route Ranking (PRD §6.3)

| Task | Owner | PRD ref |
|---|---|---|
| Wire the risk model's per-segment score into GraphHopper's `custom_model` weighting at query time | GIS/Route Engineer + AI/ML Lead | §6.3, §14.3 |
| Implement `RouteScore = wT·T + wD·D + wR·R + wC·C + wU·U + wP·P` on top of GraphHopper's candidate routes | Backend | §6.3 |
| Implement the two starter weight profiles (P0 emergency vs. P2 routine) and route by shipment priority class | Backend | §6.3, §10 |
| Build the route comparison API response: ETA, distance, risk, reliability %, recommendation label | Backend | §6.3 |
| Route Intelligence screen: comparison table (ETA/distance/risk/reliability/recommendation) | Frontend | §6.7 |
| Hard-constraint pass: exclude/heavily penalize Blocked segments and vehicle-incompatible roads before scoring | Backend | §6.3 |

**Definition of Done:** requesting a route between hub and destination with a Blocked segment on the shortest path returns a ranked list where that route is excluded or marked "Avoid," and an alternate is "Recommended" — matches PRD §6.3 acceptance criteria exactly.

---

## 7. Day 5 — Tracking, GPS Simulator, Alerts (PRD §6.4, §6.5)

| Task | Owner | PRD ref |
|---|---|---|
| `vehicle_telemetry` ingestion endpoint (device GPS or simulator, same contract) | Backend | §6.4 |
| Build a telemetry simulator script that moves a vehicle along an assigned route at a realistic speed, clearly flagged as simulated in all UI | Backend/Mobile | §6.4 |
| Shipment/Vehicle Tracking screen: live position, ETA, route-risk exposure | Frontend | §6.7 |
| Alert engine: implement the 4 triggers from PRD §6.5 (road blocked, high disruption probability, ETA breach, high-risk corridor entry) with severity + cooldown windows | Backend | §6.5 |
| FCM push integration + SMS fallback stub | Backend | §6.5 |
| Alerts Center screen: live feed + acknowledgment state | Frontend | §6.7 |

**Definition of Done:** a moving simulated vehicle that enters a Risk ≥ 61 segment produces exactly one driver alert and one dispatcher alert, visible with timestamps in the Alerts Center — matches PRD §6.5 acceptance criteria.

---

## 8. Day 6 — Field App, Offline Sync, Explainability, Multilingual (PRD §6.6, §6.8)

| Task | Owner | PRD ref |
|---|---|---|
| Mobile: local SQLite queue for incident reports created offline | Mobile | §6.8 |
| Mobile: sync logic with idempotency keys, retry/backoff, image compression | Mobile | §6.8 |
| Mobile: airplane-mode test — create report offline, reconnect, confirm single sync with no duplication | Mobile | §6.8 (acceptance criteria) |
| Explanation panel: clickable risk scores/route scores open a factor breakdown (SHAP output from Day 3) | Frontend | §6.2, §7 |
| Multilingual: implement message-intent → translation layer for at least English + 2 languages relevant to the pilot corridor; standardized short phrases for safety alerts | Integration/Product | §6.8 |
| District Accessibility Dashboard: district-wise connectivity summary + bottlenecks | Frontend | §6.7 |
| Emergency Mode toggle: re-prioritize P0/P1, surface safe corridors, force-reroute at-risk shipments, highlight isolation-risk districts | Frontend + Backend | §6.7.1 |

**Definition of Done:** the full offline-to-sync loop works on a real or emulated device, every risk/status number in the UI is clickable-explainable, and Emergency Mode visibly changes the dashboard state.

---

## 9. Day 7 — Integration, Validation Run, Demo Rehearsal (PRD §12, §13.5)

| Task | Owner | PRD ref |
|---|---|---|
| Run the validation replay: Baseline A (shortest path) vs. Baseline B (route + known-blocked) vs. Our model (route + risk + priority) on the pilot corridor scenario | AI/ML Lead + GIS Engineer | §13.5 |
| Capture actual metrics (ETA error, risk exposure, reroute response time) — replace directional KPI language in the pitch with real numbers | AI/ML Lead | §13 |
| End-to-end rehearsal of the 5-minute demo storyline: normal shipment → weather risk appears → field report → AI reroutes → vehicle tracking updates → Emergency Mode | Whole team | §12, PRD demo storyline |
| Freeze a backup dataset/demo recording in case of live-connectivity failure during the pitch | Integration/Product | §12 |
| Bug bash: fix anything that breaks the demo path; do not chase non-demo-path bugs this late | Whole team | — |
| Finalize pitch deck: problem → architecture → live demo → validation numbers → scalability statement (one corridor now, architected for full NER) | Integration/Product | §3, §5 |

**Definition of Done:** the team can run the full field-to-reroute loop live, twice in a row, without manual intervention, and has real (not invented) numbers to defend the routing decision.

---

## 10. Cross-Cutting Tasks (Ongoing, Not Day-Specific)

- **Security baseline (PRD §7):** RBAC, JWT auth, encrypted transit/at-rest, audit logging on status/route/alert changes, server-side secrets, rate limiting, input validation — start these on Day 1, not as a Day 7 afterthought; retrofitting auth late in a sprint is expensive.
- **Confidence/staleness display (PRD §6.1):** every screen showing a risk or status value must show freshness/confidence, not just the number — build this into the shared UI components from Day 1 so it isn't bolted on later.
- **No fabricated data claims (PRD §11):** anywhere the UI or pitch references weather, road status, or historical data, it must be traceable to IMD/OSM/field-reports/synthetic-and-labeled-as-such — never presented as a live government feed the team doesn't actually have.

---

## 11. Risk Watchlist (Carried from PRD §11/§14, Tracked Daily)

| Risk | Watch for | If it happens |
|---|---|---|
| No live road-status feed | N/A — expected; field-report loop is the mitigation, not a fallback | Lean harder into the field-to-reroute demo story |
| Bhuvan token expiry (24h) | Integration calls failing overnight | Cron-based token refresh, built Day 0 |
| GraphHopper custom_model complexity | Day 2 routing engine stand-up slipping | Fall back to precomputed risk-weighted graph rebuild (OSRM-style) as an interim, keep custom_model as a Day-4 stretch |
| Thin/synthetic training data | Model producing unstable or non-explainable scores | Simplify to Random Forest with fewer, higher-signal features; prioritize explainability over accuracy for the demo |
| Offline sync bugs | Duplicate or lost reports on reconnect | Idempotency keys are mandatory from Day 6, test airplane-mode explicitly before Day 7 |
| Scope creep | Any task not traceable to a PRD section number | Cut it — see PRD §16 "What Not to Build" |

---

## 12. Definition of Done — Whole Sprint

The sprint is complete when, without manual data-fixing between runs, the team can:

1. Show the pilot-corridor Command Center with live segment status and confidence.
2. Submit a field incident report (including offline → sync) that changes a segment's status.
3. Show the AI risk score for that segment with a factor-level explanation.
4. Show a route re-ranking that avoids the newly-Blocked segment and recommends an alternate, with ETA/risk/reliability.
5. Show a driver + dispatcher alert firing from that reroute.
6. Show the vehicle's tracked position and ETA update accordingly.
7. Toggle Emergency Mode and show the dashboard reprioritize around P0/P1 cargo.
8. Present real validation numbers (Baseline A vs. B vs. Our model) from the replay run, not estimated figures.

This sequence **is** the pitch — Day 7 rehearsal should run exactly this checklist, twice.
