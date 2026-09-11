# Implementation Plan — Phase 2: Role-Based Access (User / Driver / Officer)

## Companion to `implementation_plan.md` (Phase 1, the 7-day sprint). Read that first for architecture context.

| Field | Value |
|---|---|
| Goal | Turn the existing NER SafeRoute app into a real role-based platform: User, Driver, Officer |
| Driving doc | SIH26002 problem statement (see below) + user's refined ChatGPT plan |
| Constraint | Limited time — fix fundamentals first, reuse everything that already works, do not rebuild |
| Architecture decision | Supabase = auth/identity only. FastAPI + SQLAlchemy stays the single system of record for all domain data (segments, incidents, alerts, telemetry). No parallel Supabase-Postgres data layer. |

---

## 0. Problem statement (plain-language restatement)

NER's terrain and weather regularly cut off the few road corridors that exist. There is no live, predictive picture of which roads are actually usable. Essential cargo (medicine, food, construction material, agri produce) gets delayed or routed into danger. The platform must: monitor road/bridge accessibility, predict disruptions (weather + terrain + field reports), suggest the *safest* route (not fastest), track vehicles by GPS, alert automatically on blockages/delays/high-risk entry, let field staff report hazards from remote low-network areas, and give officers a regional dashboard — multilingual, offline-tolerant.

---

## 1. Two pre-existing problems this phase must fix, not just build around

1. **No login page writes a role.** [`login/user`](../frontend/login/user/index.html), [`login/driver`](../frontend/login/driver/index.html), [`login/officer`](../frontend/login/officer/index.html) all call plain Supabase `signUp`/`signInWithPassword`. Destination is decided by which button was clicked, not by identity.
2. **Backend never checks role.** `verify_admin_user` in `backend/app/main.py` only validates "is this a real Supabase session" — any signed-up user can currently approve/reject hazard reports via the admin gate embedded in `user/index.html`. This must close before anything else ships.

---

## Phase 0 — Fundamentals cleanup (do first, ~2-3 hrs)

Carried over from the prior review; doing this now prevents the same drift from happening again while adding new screens.

- [ ] Delete the 30 root-level `fix_*.py` / `add_*.py` / `enhance_*.py` one-shot patch scripts — already applied, now only a risk if re-run against drifted files.
- [ ] Collapse the 4 duplicate HTML copies (`mobile/app.html`, `mobile/index.html`, `frontend/public/mobile/index.html`, `frontend/user/index.html`) to **one source of truth** (`frontend/user/index.html`); make the others thin redirects, not copies. They have already drifted apart once.
- [ ] Delete the orphaned React app (`frontend/src/`) — Vite's actual entry (`frontend/index.html`) hasn't mounted it since the vanilla-HTML pivot. Keeping it around invites duplicate effort during this phase.
- [ ] Replace the fabricated benchmark numbers in `ml/benchmark_replay.py` / `README.md` with either a real replay or an honest "directional estimate" label.

**Definition of Done:** one app, one frontend stack, no dead code duplicating the screens you're about to modify.

---

## Phase 1 — Google Maps migration (map surface only, ~3-4 hrs)

**Decision:** keep GraphHopper/OSRM as the risk-aware routing engine (it's the only setup that lets you weight routes by your own risk score — Google Directions API has no hook for that). Google Maps JS API replaces only the **map rendering surface** — tiles, pan/zoom feel, markers, and optionally Places Autocomplete for the origin/destination search box. The risk-colored route line is still computed by GraphHopper and drawn as an overlay on top of the Google base map.

- [ ] GCP setup: enable billing on the project (required even for the free tier), enable **Maps JavaScript API** + **Places API**, restrict the key by HTTP referrer (your domain + `localhost`) before it goes live client-side.
- [ ] Swap the script includes in `frontend/user/index.html` (and the 3 redirect stubs from Phase 0) from Leaflet/leaflet-routing-machine CDN tags to `<script src="https://maps.googleapis.com/maps/api/js?key=...&libraries=places&callback=initMap" async defer>`.
- [ ] Convert the ~28 Leaflet call sites to Google Maps JS API equivalents: `L.map()` → `new google.maps.Map()`, `L.marker()` → `google.maps.Marker`, `L.polyline()` → `google.maps.Polyline`, `L.popup()`/`.bindPopup()` → `google.maps.InfoWindow`, `.setView()`/`fitBounds()` → `map.setCenter()`/`map.fitBounds()`. Contained enough to do as direct edits rather than an abstraction layer.
- [ ] Drop `leaflet-routing-machine` entirely — render turn-by-turn from the `turn_instructions` your own `routing_service.py` already returns from GraphHopper, instead of a third-party widget.
- [ ] (Optional, same phase since it's the search box you're touching anyway) Wire Places Autocomplete onto the origin/destination inputs for a real address-search feel, still resolving down to lat/lon that gets handed to GraphHopper as before.

**Definition of Done:** the map renders on Google's tiles with smooth pan/zoom, the risk-colored route line still comes from your own routing engine and still changes when a segment gets Blocked, and turn-by-turn instructions still display without the old routing-machine widget.

---

## Phase 2 — Identity & RBAC (the actual missing piece, ~2-3 hrs)

This is the highest-priority phase — it's a security gap, not a feature gap.

- [ ] **Role must be set server-side, not by the client.** Add a small backend endpoint `POST /api/v1/auth/register` that takes `{email, password, role}`, creates the Supabase user via the **service-role key** (server-side only, never shipped to frontend), and writes `role` into `app_metadata` (not `user_metadata` — `user_metadata` is client-editable and must never be trusted for authorization).
  - `role` ∈ `user | driver | officer`. Officer accounts should not be self-service signup — either an allowlist of officer emails, an invite code, or manual provisioning; do not let the public create officer accounts the same way as user/driver.
- [ ] Update the three login pages to call this endpoint on signup instead of `supabase.auth.signUp` directly, passing the role implied by which page they're on.
- [ ] Backend: replace `verify_admin_user` with a general `get_current_user()` dependency that returns `{id, email, role}` from the verified JWT's `app_metadata.role`, plus a `require_role(*roles)` dependency factory.
- [ ] Apply `require_role("officer")` to: incident approve/reject, `GET /api/v1/officer/drivers` (new, Phase 2), `POST /api/v1/emergency-mode/toggle`.
- [ ] Apply `require_role("driver", "officer")` to the new driver-telemetry POST endpoint (Phase 2).
- [ ] Remove the officer login page's "Bypass (Demo Mode)" button — it's a standing backdoor around the auth you're about to make real.
- [ ] Client-side: each screen reads role from the Supabase session (for UX — hiding buttons) but treat this as decoration only; the server-side check above is what actually protects data.

**Definition of Done:** a `user`-role account that manually navigates to `/user/#admin` and tries to hit an officer endpoint gets a 403 from the API, not just a hidden button.

---

## Phase 3 — Driver GPS tracking + Officer live map (core new capability, ~4-5 hrs)

Reuse what's already there instead of inventing a `driver_locations` table:

- [ ] Extend the existing `VehicleTelemetry` model/endpoint (`backend/app/main.py`, `POST /api/v1/telemetry`) rather than building a parallel table:
  - Require driver auth (`require_role("driver")`) — derive `driver_id` from the authenticated user, don't trust the client-supplied `vehicle_id` default.
  - Add a stable **Driver ID** (e.g. `DRV-001`) assigned once at first driver login — simplest approach: a small `drivers` table (`user_id`, `driver_id`, `created_at`) in the existing FastAPI DB, auto-incrementing.
  - Add `status` derivation server-side from `last_updated`: **Active** (<2 min), **Inactive** (<10 min), **Offline** (>10 min stale), **At Risk** (current nearest segment `risk_score` ≥ threshold — reuse the existing alert-trigger logic in `alert_engine.py`).
- [ ] New endpoint `GET /api/v1/officer/drivers` — latest telemetry row per driver, joined with computed status, current route/destination if set. Officer-only.
- [ ] Driver frontend: on driver-mode load, request geolocation permission, `navigator.geolocation.watchPosition`, throttle posts to the backend (every ~15-30s or on ~50m movement — do not post on every GPS tick). Show **🟢 Location Sharing Active** indicator with a pause toggle.
- [ ] Officer portal: new "Live Driver Tracking" tab in the existing admin portal (same polling pattern already used for alerts/incidents, ~10-15s interval). Markers colored by status, built directly on the Google map from Phase 1; clicking one shows driver ID, status, location, destination, ETA, route risk, last-updated.

**Definition of Done:** open two browser sessions — one as a driver moving on the map, one as an officer — and the driver's marker updates live on the officer's map within ~15s, with correct status color.

---

## Phase 4 — Hazard reporting polish (~1-2 hrs)

- [ ] Expand the hazard-type picker (`frontend/user/index.html`, `pickHazard()`) from its current 3 options to the full 8 from the problem statement: Landslide, Flood, Heavy Rain, Road Blockage, Accident, Damaged Road, Bridge Problem, Other.
- [ ] Add a `Resolved` status alongside the existing `Pending/Verified/Rejected` in the admin portal tabs and backend status enum.
- [ ] Set `reporter` to the authenticated user's email/ID instead of the current free-text default (`"Citizen / Field Reporter"`) when the reporter is logged in.

**Definition of Done:** a hazard reported while logged in shows the real reporter identity in the officer queue, and an officer can move it through Pending → Verified → Resolved.

---

## Phase 5 — Role-restricted UI polish (~1 hr)

- [x] Hide the admin sidebar button/driver-mode controls conditionally based on session role, not just CSS.
- [x] If a non-officer session lands on `/user/#admin`, redirect home instead of showing the login gate as if it were a normal path.

---

## Phase 6 — Stretch, only if time remains

- [ ] Minimal multilingual UI strings (Hindi/Assamese) — backend `translation_service.py` already exists but is wired to 0 frontend surfaces.
- [ ] Offline hazard-report queue (localStorage array + retry on reconnect) — explicitly called out in the original problem statement (§h) and currently entirely absent.

---

## Navigation flow (target end state)

```
Landing page → role card
  → User login    → /user            (map, route safety, report hazard, SOS — no admin access)
  → Driver login   → /driver          (existing app in Driver Mode + GPS sharing indicator)
  → Officer login  → /user/#admin     (existing admin portal + new Live Driver Tracking tab)
```

All three destinations already exist as routes — Phase 1 makes the *server* enforce who's allowed into each, Phase 2 adds the live tracking data officers are currently missing.
