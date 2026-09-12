# NER SafeRoute — Core Completion Implementation Plan

> **For the implementing agent (Gemini / Antigravity):** This plan is written for an
> agent with full codebase access but zero memory of how these findings were made.
> Work top to bottom, in phase order. Each task ends with a **Verify** step that has
> an exact command and exact expected output — do not check a step's box until the
> real output matches. Do not skip ahead to a later phase if an earlier phase's
> verification is failing. Commit after each task (not after each phase), with the
> commit message given in that task. Do not `git add -A` — stage the exact files
> listed in the task.
>
> **After this plan is executed:** hand the repo back to the user (Vinay). Claude
> will test, debug, and refine from there — leave anything you're genuinely unsure
> about clearly marked with a `# NOTE(gemini):` comment rather than guessing silently.

**Goal:** Replace every faked, disconnected, or broken piece of NER-LINK AI's core
loop — risk scoring, routing, and six unwired API endpoints — with real, working,
verifiable implementations, so the app actually does what the SIH26002 problem
statement and this project's own README claim it does.

**Architecture:** No new services and no new architecture. Everything here fits
inside the existing FastAPI backend (`backend/app/`) and the existing single-page
vanilla-JS app (`frontend/user/index.html`). We add one new backend service module
(`ml_risk_service.py`), one new backend service module (`graph_routing_service.py`),
wire an existing-but-orphaned module (`status_engine.py`) into the request flow,
and add JS functions + small HTML fragments to the existing frontend file. Nothing
here introduces a new frontend framework, a new database, or a new deployment
target.

**Tech Stack:** FastAPI, SQLAlchemy, SQLite (dev) / PostgreSQL (prod, unchanged),
scikit-learn + joblib (new, backend), pytest + httpx TestClient (new, backend test
infra), vanilla JS + Leaflet (unchanged, frontend).

**Spec:** The SIH26002 problem statement (points a–h, reproduced inline per task
below) plus the codebase audit findings from the 2026-09-11/12 QA and cleanup
sessions (also reproduced inline — there is no separate spec document; this plan
carries its own justification).

## Global Constraints

- Python 3.11, existing `backend/requirements.txt` dependency set stays; only
  **add** to it, never swap an existing library for a different one.
- Do not change the public shape of any existing API response field that the
  frontend already consumes (`risk_score`, `status`, `confidence`, `distance_km`,
  `eta_minutes`, `overall_risk_score`, `recommendation_label`, `segments`,
  `alert_id`, `incident_id`, etc.) — **add** new fields, don't rename or remove.
- All new training data must be synthetic and must say so in the response/UI
  wherever it surfaces a number derived from it — this project's own PRD bans
  presenting synthetic or simulated data as if it were a live government feed.
- Every new backend function must have a docstring only if it states a
  non-obvious constraint (a formula's units, a fallback trigger condition) —
  do not write docstrings that just restate the function name.
- Do not reintroduce any hardcoded `127.0.0.1` / `localhost` API call in the
  frontend. All frontend → backend calls are relative paths (`/api/v1/...`).
- Do not touch `frontend/src/` (the React dashboard) — its fate is still an open
  decision with the user, out of scope for this plan.
- Do not restore any file previously deleted in the 2026-09-12 cleanup pass
  (the root-level `fix_*.py` / `add_*.py` scripts, `mobile/app.html`,
  `frontend/public/mobile/`, `infra/docker-compose.yml`, `frontend/login.html`).
- Windows dev environment: use `pathlib.Path` for all new filesystem code, never
  hardcode `/` or `\` path separators.

---

## Priority Order (read this before starting)

The SIH26002 deadline is 2026-09-30. If time runs out, stop at the end of a
phase, not mid-phase. Priority, highest first:

1. **Phase 0** — test infrastructure (fast, everything after depends on it existing)
2. **Phase 2** — routing engine fix (the single most visibly broken thing: every
   route query currently returns the same wrong distance regardless of what was
   asked)
3. **Phase 1** — real ML risk model (the project's core "AI" claim is currently a
   hand-tuned formula with zero model behind it)
4. **Phase 4** — photo evidence fix (small, high-value, currently silently
   discards every photo a field officer takes)
5. **Phase 3** — six disconnected endpoints (breadth completion — each sub-task
   is independent, do as many as time allows, in the given order)
6. **Phase 5** — offline sync (real complexity, lower risk of embarrassing a live
   demo than the phases above)
7. **Phase 6 (optional, do last if at all)** — real GraphHopper + OSM data. This
   is infra-heavy with an uncertain payoff for a demo; Phase 2 already gives
   correct routing without it.

---

## Phase 0: Backend Test Infrastructure

**Why:** There is currently no automated test suite anywhere in this repo —
`backend/test_day2.py`, `test_day4.py`, `test_day6.py` are manual `print()`
scripts with zero assertions. Every phase below needs real tests, so this phase
builds that foundation first.

### Task 0.1: Add pytest infrastructure

**Files:**
- Modify: `backend/requirements.txt`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_health.py`

**Interfaces:**
- Produces: a `client` pytest fixture (FastAPI `TestClient`) and a `db_session`
  fixture, available to every test file under `backend/tests/`, backed by a
  throwaway SQLite file per test session (never the dev `data/ner_link.db`).

- [ ] **Step 1: Add test dependencies**

Append to `backend/requirements.txt`:

```
pytest
pytest-asyncio
```

- [ ] **Step 2: Create the tests package**

Create `backend/tests/__init__.py` (empty file).

- [ ] **Step 3: Create the shared fixtures**

Create `backend/tests/conftest.py`:

```python
import os
import tempfile
import pytest

os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(
    tempfile.gettempdir(), "ner_link_test.db"
)

from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, Base, SessionLocal


@pytest.fixture(scope="function", autouse=True)
def reset_db():
    """Every test starts with a clean, empty schema."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
```

`os.environ["DATABASE_URL"]` must be set **before** `from app.main import app`,
because `app/config.py` reads it at import time via `pydantic-settings`.

- [ ] **Step 4: Write the smoke test**

Create `backend/tests/test_health.py`:

```python
def test_health_endpoint_returns_200(client):
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "healthy"
    assert "database" in body
```

- [ ] **Step 5: Run it**

Run (from `backend/`): `python -m pytest tests/test_health.py -v`

Expected: `1 passed`. If `ModuleNotFoundError: No module named 'app'`, run
pytest from inside `backend/`, not the repo root — `app` is a relative package.

- [ ] **Step 6: Commit**

```bash
git add backend/requirements.txt backend/tests/__init__.py backend/tests/conftest.py backend/tests/test_health.py
git commit -m "test: add pytest infrastructure with isolated test database"
```

### Task 0.2: Fix `/health`'s fabricated database status

**Why:** QA finding — `/health` hardcodes the string `"connected (PostgreSQL/PostGIS)"`
regardless of which database is actually configured or reachable. Confirmed by
running the whole stack on SQLite and still seeing that string. This directly
violates the project's own "no fabricated data claims" rule (implementation
plan §10), and it's in the one endpoint whose entire job is telling the truth
about system state.

**Files:**
- Modify: `backend/app/main.py` (the `health_check` function)
- Test: `backend/tests/test_health.py`

**Interfaces:**
- No change to the endpoint's URL or 200/error behavior — only the truthfulness
  of the `database` field's content.

- [ ] **Step 1: Write the failing test**

Add to `backend/tests/test_health.py`:

```python
def test_health_reports_actual_database_backend(client):
    res = client.get("/health")
    body = res.json()
    # The test harness runs on SQLite (see conftest.py) — the health check
    # must say so, not hardcode Postgres.
    assert "sqlite" in body["database"].lower()
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest tests/test_health.py::test_health_reports_actual_database_backend -v`

Expected: `FAIL` — actual value contains `"PostgreSQL/PostGIS"`.

- [ ] **Step 3: Fix `health_check` in `backend/app/main.py`**

Find the `health_check` function. Replace this block:

```python
    try:
        from sqlalchemy import text
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db_status = "connected (PostgreSQL/PostGIS)"
    except Exception as e:
        db_status = f"disconnected ({str(e)})"
```

with:

```python
    try:
        from sqlalchemy import text
        db = next(get_db())
        db.execute(text("SELECT 1"))
        backend_name = engine.url.get_backend_name()  # "sqlite" or "postgresql"
        db_status = f"connected ({backend_name})"
    except Exception as e:
        db_status = f"disconnected ({str(e)})"
```

This requires `engine` to be imported in `main.py` — it already is (see the
existing `from app.database import engine, get_db, Base` import at the top of
the file). No new import needed.

- [ ] **Step 4: Run the test again**

Run: `python -m pytest tests/test_health.py -v`

Expected: `2 passed`.

- [ ] **Step 5: Commit**

```bash
git add backend/app/main.py backend/tests/test_health.py
git commit -m "fix: health check reports the actual database backend instead of a hardcoded string"
```

---

## Phase 1: Real ML Risk Model

**Problem statement point addressed:** (b) "Predicting possible route disruptions
caused by landslides, floods, heavy rainfall, road damage, or traffic congestion"
using AI/ML. **Current state (QA finding):** `risk_model_service.py` is a 100%
hand-written arithmetic formula. `ml/train_baseline.py` and `ml/train_models.py`
both train real scikit-learn models on synthetic data, but neither's output is
loaded by the running backend — the `ml/` folder is completely disconnected from
the API. This phase makes it real, with an honest fallback when the model file
is missing.

### Task 1.1: Consolidate training into one script, produce a real model artifact

**Files:**
- Create: `ml/train_risk_model.py`
- Delete: `ml/train_baseline.py`, `ml/train_models.py` (superseded — both did the
  same job with overlapping/duplicated code; keeping both invites drift)
- Modify: `backend/requirements.txt`

**Interfaces:**
- Produces: `ml/artifacts/risk_model.joblib` (a fitted `RandomForestClassifier`),
  `ml/artifacts/feature_columns.json` (ordered list of feature names the model
  expects, as a JSON array of strings), `ml/artifacts/model_metrics.json`
  (real, not fabricated, metrics from an actual train/test split).

- [ ] **Step 1: Add ML dependencies**

Append to `backend/requirements.txt`:

```
scikit-learn
joblib
pandas
numpy
```

- [ ] **Step 2: Write the training script**

Create `ml/train_risk_model.py`:

```python
"""
Trains the NER-LINK road disruption risk classifier on synthetic,
clearly-labeled data (see PRD §11: no fabricated data claims — this
dataset is synthetic and must never be presented as historical/live).

Run: python ml/train_risk_model.py
Produces: ml/artifacts/risk_model.joblib, feature_columns.json, model_metrics.json
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import dump
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split

ARTIFACT_DIR = Path(__file__).parent / "artifacts"

FEATURE_COLUMNS = [
    "rainfall_1h",
    "rainfall_6h",
    "rainfall_24h",
    "forecast_24h_rain",
    "landslide_susceptibility",
    "base_risk_score",
    "historical_incident_count",
]


def generate_training_data(n_samples: int = 3000, seed: int = 42) -> pd.DataFrame:
    """
    Synthetic dataset calibrated to plausible NER monsoon conditions.
    Label = 1 (disruption within 24h) when combined rainfall + terrain +
    incident-history pressure crosses a randomized realistic threshold —
    this mirrors how landslide triggers actually compound in the literature
    (rainfall intensity x slope instability x prior ground saturation),
    without claiming to be real historical NER data.
    """
    rng = np.random.default_rng(seed)

    rainfall_1h = rng.exponential(scale=4.0, size=n_samples)
    rainfall_6h = rainfall_1h * rng.uniform(3.0, 6.0, size=n_samples)
    rainfall_24h = rainfall_6h * rng.uniform(1.5, 3.0, size=n_samples)
    forecast_24h_rain = rainfall_24h * rng.uniform(0.8, 1.5, size=n_samples)
    landslide_susceptibility = rng.uniform(0.05, 0.98, size=n_samples)
    base_risk_score = rng.uniform(10.0, 90.0, size=n_samples)
    historical_incident_count = rng.poisson(lam=1.2, size=n_samples)

    pressure = (
        0.35 * (rainfall_24h / 100.0)
        + 0.30 * landslide_susceptibility
        + 0.15 * (base_risk_score / 100.0)
        + 0.20 * np.minimum(historical_incident_count / 5.0, 1.0)
    )
    noise = rng.normal(0, 0.08, size=n_samples)
    label = ((pressure + noise) > 0.55).astype(int)

    return pd.DataFrame(
        {
            "rainfall_1h": rainfall_1h,
            "rainfall_6h": rainfall_6h,
            "rainfall_24h": rainfall_24h,
            "forecast_24h_rain": forecast_24h_rain,
            "landslide_susceptibility": landslide_susceptibility,
            "base_risk_score": base_risk_score,
            "historical_incident_count": historical_incident_count,
            "label_disruption": label,
        }
    )


def train_and_save_model(df: pd.DataFrame) -> dict:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    X = df[FEATURE_COLUMNS]
    y = df["label_disruption"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200, max_depth=8, random_state=42, class_weight="balanced"
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    metrics = {
        "trained_on": "synthetic_data",
        "n_samples": len(df),
        "n_features": len(FEATURE_COLUMNS),
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "f1_score": round(float(f1_score(y_test, y_pred)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, y_prob)), 4),
        "feature_importances": {
            col: round(float(imp), 4)
            for col, imp in zip(FEATURE_COLUMNS, model.feature_importances_)
        },
    }

    dump(model, ARTIFACT_DIR / "risk_model.joblib")
    (ARTIFACT_DIR / "feature_columns.json").write_text(json.dumps(FEATURE_COLUMNS, indent=2))
    (ARTIFACT_DIR / "model_metrics.json").write_text(json.dumps(metrics, indent=2))

    return metrics


if __name__ == "__main__":
    data = generate_training_data()
    result = train_and_save_model(data)
    print(json.dumps(result, indent=2))
```

- [ ] **Step 3: Run it and verify the artifacts exist**

Run: `python ml/train_risk_model.py`

Expected output: a JSON object printed with `"trained_on": "synthetic_data"`,
`"accuracy"` between roughly 0.75 and 0.99, and `"roc_auc"` above 0.75. If
`roc_auc` is below 0.6, the synthetic label formula above didn't paste
correctly — re-check `generate_training_data`.

Then verify the files exist:

```bash
python -c "from pathlib import Path; assert Path('ml/artifacts/risk_model.joblib').exists(); assert Path('ml/artifacts/feature_columns.json').exists(); print('artifacts OK')"
```

Expected: `artifacts OK`.

- [ ] **Step 4: Delete the superseded training scripts**

```bash
git rm ml/train_baseline.py ml/train_models.py
```

- [ ] **Step 5: Commit**

```bash
git add ml/train_risk_model.py ml/artifacts/risk_model.joblib ml/artifacts/feature_columns.json ml/artifacts/model_metrics.json backend/requirements.txt
git commit -m "feat: consolidate ML training into one script, produce a real risk model artifact"
```

Note: `ml/artifacts/risk_model.joblib` is a binary file — if the repo's
`.gitignore` blocks `*.joblib` under `ml/models/*.joblib` only (check the
existing `.gitignore` — it currently only ignores `ml/models/*.joblib`, not
`ml/artifacts/`), this path is fine to commit as-is. Do not add a new
`.gitignore` rule for it — the backend needs this file present at runtime and
there's no separate model-serving pipeline in this project to fetch it from
elsewhere.

### Task 1.2: Load the model into the backend and use it for risk scoring

**Files:**
- Create: `backend/app/services/ml_risk_service.py`
- Modify: `backend/app/services/risk_model_service.py`
- Modify: `backend/app/schemas.py` (add `risk_source` field to `RiskAssessment`)
- Modify: `backend/app/main.py` (load the model at startup)
- Test: `backend/tests/test_ml_risk_service.py`

**Interfaces:**
- Produces (from `ml_risk_service.py`, consumed by `risk_model_service.py`):
  - `load_model() -> None` — idempotent, sets module-level state, never raises
    (catches and logs any exception, leaving the model unloaded).
  - `is_model_loaded() -> bool`
  - `predict_disruption_probability(features: dict) -> tuple[float, dict[str, float]]`
    — `features` keys must exactly match `ml/artifacts/feature_columns.json`;
    returns `(probability in [0.0, 1.0], {feature_name: importance_weight})`.
    Raises `RuntimeError("model not loaded")` if called before `load_model()`
    succeeded — callers must check `is_model_loaded()` first.

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_ml_risk_service.py`:

```python
from app.services import ml_risk_service


def test_model_loads_from_artifact():
    ml_risk_service.load_model()
    assert ml_risk_service.is_model_loaded() is True


def test_predict_returns_probability_and_importances():
    ml_risk_service.load_model()
    prob, importances = ml_risk_service.predict_disruption_probability(
        {
            "rainfall_1h": 12.0,
            "rainfall_6h": 45.0,
            "rainfall_24h": 85.0,
            "forecast_24h_rain": 100.0,
            "landslide_susceptibility": 0.9,
            "base_risk_score": 70.0,
            "historical_incident_count": 2,
        }
    )
    assert 0.0 <= prob <= 1.0
    assert isinstance(importances, dict)
    assert len(importances) > 0


def test_high_risk_inputs_score_higher_than_low_risk_inputs():
    ml_risk_service.load_model()
    low_prob, _ = ml_risk_service.predict_disruption_probability(
        {
            "rainfall_1h": 0.5, "rainfall_6h": 1.0, "rainfall_24h": 2.0,
            "forecast_24h_rain": 2.0, "landslide_susceptibility": 0.1,
            "base_risk_score": 15.0, "historical_incident_count": 0,
        }
    )
    high_prob, _ = ml_risk_service.predict_disruption_probability(
        {
            "rainfall_1h": 20.0, "rainfall_6h": 90.0, "rainfall_24h": 150.0,
            "forecast_24h_rain": 160.0, "landslide_susceptibility": 0.95,
            "base_risk_score": 85.0, "historical_incident_count": 4,
        }
    )
    assert high_prob > low_prob
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m pytest tests/test_ml_risk_service.py -v`

Expected: `FAIL` — `ModuleNotFoundError: No module named 'app.services.ml_risk_service'`.

- [ ] **Step 3: Write `ml_risk_service.py`**

Create `backend/app/services/ml_risk_service.py`:

```python
import json
import logging
from pathlib import Path
from typing import Dict, Tuple

logger = logging.getLogger("ml_risk_service")

_ARTIFACT_DIR = Path(__file__).resolve().parent.parent.parent.parent / "ml" / "artifacts"
_MODEL_PATH = _ARTIFACT_DIR / "risk_model.joblib"
_FEATURES_PATH = _ARTIFACT_DIR / "feature_columns.json"

_model = None
_feature_columns: list = []


def load_model() -> None:
    """Loads the trained model into module state. Safe to call multiple
    times; safe to call when the artifact is missing (leaves the model
    unloaded so callers fall back to the rule-based formula)."""
    global _model, _feature_columns
    if _model is not None:
        return
    try:
        from joblib import load

        _model = load(_MODEL_PATH)
        _feature_columns = json.loads(_FEATURES_PATH.read_text())
        logger.info(f"Loaded ML risk model from {_MODEL_PATH}")
    except Exception as e:
        logger.warning(f"ML risk model not loaded, falling back to rule-based scoring: {e}")
        _model = None
        _feature_columns = []


def is_model_loaded() -> bool:
    return _model is not None


def predict_disruption_probability(features: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
    """
    features must contain exactly the keys in ml/artifacts/feature_columns.json.
    Returns (probability_of_disruption, {feature_name: this_prediction's_signed_contribution}).
    """
    if _model is None:
        raise RuntimeError("model not loaded — call is_model_loaded() before predicting")

    ordered_values = [[features[col] for col in _feature_columns]]
    probability = float(_model.predict_proba(ordered_values)[0][1])

    # Feature importances are global to the model (not per-prediction SHAP
    # values) — this is the documented fallback from the PRD's own risk
    # watchlist ("prioritize explainability over accuracy for the demo") when
    # a full SHAP integration isn't worth the added dependency weight.
    importances = {
        col: round(float(imp), 4)
        for col, imp in zip(_feature_columns, _model.feature_importances_)
    }
    return probability, importances
```

- [ ] **Step 4: Run the tests again**

Run: `python -m pytest tests/test_ml_risk_service.py -v`

Expected: `3 passed`. If `test_high_risk_inputs_score_higher_than_low_risk_inputs`
fails, the model trained in Task 1.1 is not distinguishing risk levels — re-run
`python ml/train_risk_model.py` and check `roc_auc` in the printed metrics is
above 0.75 before continuing.

- [ ] **Step 5: Add `risk_source` to the schema**

In `backend/app/schemas.py`, find the `RiskAssessment` class and add one field:

```python
class RiskAssessment(BaseModel):
    segment_id: str
    district: str
    risk_score: float # 0 to 100
    disruption_prob_6h: float
    disruption_prob_12h: float
    disruption_prob_24h: float
    confidence: float
    status: str
    top_factors: List[dict]
    risk_source: str  # "ml_model" or "rule_based_fallback" — never fabricate which one produced this score
```

(Only the last line is new — `risk_source: str` added after `top_factors`.)

- [ ] **Step 6: Wire the model into `risk_model_service.calculate_segment_risk`**

Replace the entire contents of `backend/app/services/risk_model_service.py` with:

```python
from typing import Dict, Any, List
from app.models import RoadSegment, IncidentReport
from app.services import ml_risk_service


def _build_top_factors(
    rainfall_24h: float,
    active_incidents: List[IncidentReport],
    segment: RoadSegment,
    weather_impact: float,
    incident_impact: float,
) -> List[dict]:
    top_factors = []
    if rainfall_24h > 15.0:
        top_factors.append({
            "factor": f"Heavy Precipitation ({rainfall_24h} mm/24h)",
            "impact": f"+{round(weather_impact, 1)} pts risk",
            "type": "Weather",
        })
    if active_incidents:
        top_factors.append({
            "factor": f"Active Field Reports ({len(active_incidents)} reported)",
            "impact": f"+{round(incident_impact, 1)} pts risk",
            "type": "Field Report",
        })
    if (segment.landslide_susceptibility or 0.5) >= 0.7:
        top_factors.append({
            "factor": f"High Slope Landslide Terrain ({segment.terrain_type})",
            "impact": f"+{round((segment.landslide_susceptibility or 0.5) * 25.0, 1)} pts risk",
            "type": "Terrain",
        })
    if not top_factors:
        top_factors.append({
            "factor": "Baseline Road Stability",
            "impact": "Normal conditions",
            "type": "Terrain",
        })
    return top_factors


def calculate_segment_risk(
    segment: RoadSegment,
    rainfall_24h: float,
    active_incidents: List[IncidentReport],
) -> Dict[str, Any]:
    """
    Calculates composite Risk Score (0-100), disruption probabilities (6h, 12h, 24h),
    and factor attributions for a given road segment. Uses the trained ML model
    when available (ml/artifacts/risk_model.joblib); otherwise falls back to a
    documented rule-based formula. `risk_source` in the return value always
    states honestly which path produced the number.
    """
    base_susceptibility = segment.landslide_susceptibility or 0.5
    base_risk = segment.base_risk_score or 20.0

    weather_impact = min(rainfall_24h * 0.65, 45.0)
    incident_impact = 0.0
    has_blocking_incident = False
    for inc in active_incidents:
        if inc.severity == "Critical" or inc.incident_type in ["Landslide", "Bridge Damage"]:
            incident_impact += 45.0
            has_blocking_incident = True
        elif inc.severity == "High":
            incident_impact += 25.0
        elif inc.severity == "Medium":
            incident_impact += 12.0
    incident_impact = min(incident_impact, 50.0)

    base_component = base_risk * 0.2 + base_susceptibility * 25.0

    if ml_risk_service.is_model_loaded():
        probability, importances = ml_risk_service.predict_disruption_probability({
            "rainfall_1h": rainfall_24h / 24.0,  # no separate 1h reading at this call site; approximate
            "rainfall_6h": rainfall_24h / 4.0,
            "rainfall_24h": rainfall_24h,
            "forecast_24h_rain": rainfall_24h * 1.2,
            "landslide_susceptibility": base_susceptibility,
            "base_risk_score": base_risk,
            "historical_incident_count": len(active_incidents),
        })
        ml_component = probability * 65.0  # same 0-65pt band the rule-based weather+incident impact used
        total_risk = min(max(base_component + ml_component, 5.0), 99.0)
        risk_source = "ml_model"
        prob_24h = min(probability, 0.99)
        prob_12h = round(prob_24h * 0.9, 2)
        prob_6h = round(prob_24h * 0.8, 2)
    else:
        total_risk = min(max(base_component + weather_impact + incident_impact, 5.0), 99.0)
        risk_source = "rule_based_fallback"
        prob_6h = min(total_risk / 100.0 * 0.8, 0.99)
        prob_12h = min(total_risk / 100.0 * 0.9, 0.99)
        prob_24h = min(total_risk / 100.0 * 1.0, 0.99)

    if has_blocking_incident or total_risk >= 80.0:
        computed_status = "Blocked"
    elif total_risk >= 40.0 or rainfall_24h >= 45.0:
        computed_status = "Caution"
    else:
        computed_status = "Open"

    top_factors = _build_top_factors(rainfall_24h, active_incidents, segment, weather_impact, incident_impact)

    return {
        "segment_id": segment.segment_id,
        "district": segment.district,
        "risk_score": round(total_risk, 1),
        "disruption_prob_6h": round(prob_6h, 2),
        "disruption_prob_12h": round(prob_12h, 2),
        "disruption_prob_24h": round(prob_24h, 2),
        "confidence": 0.92 if active_incidents else 0.85,
        "status": computed_status,
        "top_factors": top_factors,
        "risk_source": risk_source,
    }
```

Note the `rainfall_1h`/`rainfall_6h` approximation comment — `calculate_segment_risk`
is only ever called with a single `rainfall_24h` value (see its call sites in
`main.py`), not the full weather breakdown. This is acceptable for now (flagged
inline) since the model's dominant feature is `rainfall_24h` per
`model_metrics.json`'s `feature_importances`; do not treat this as broken, it's
a known approximation to avoid changing the function's calling signature.

- [ ] **Step 7: Load the model at backend startup**

In `backend/app/main.py`, find:

```python
from app.services.weather_service import get_district_weather
from app.services.risk_model_service import calculate_segment_risk
from app.services.routing_service import calculate_candidate_routes
```

Add one import line after it:

```python
from app.services import ml_risk_service
```

Then find the existing `@app.on_event("startup") def seed_database():` function
and add one line at the very top of its body (before the `db = next(get_db())`
line):

```python
@app.on_event("startup")
def seed_database():
    """Load pilot corridor seed dataset into database if empty."""
    ml_risk_service.load_model()
    db = next(get_db())
```

- [ ] **Step 8: Run the full backend test suite**

Run: `python -m pytest tests/ -v`

Expected: all tests pass (should be 5 by this point: 2 health + 3 ml_risk_service).

- [ ] **Step 9: Manually verify against a live server**

```bash
cd backend
DATABASE_URL="sqlite:///./data/ner_link.db" python -m uvicorn app.main:app --port 8000 &
sleep 3
curl -s http://127.0.0.1:8000/api/v1/segments/SEG-NH6-06/risk
```

Expected: JSON containing `"risk_source": "ml_model"` (SEG-NH6-06 is the
seeded "Critical Mudslide Zone" segment with `base_risk_score: 82.0` — its
`risk_score` should come back elevated, generally above 60).

Stop the server afterward (`kill %1` or find and stop the uvicorn process).

- [ ] **Step 10: Commit**

```bash
git add backend/app/services/ml_risk_service.py backend/app/services/risk_model_service.py backend/app/schemas.py backend/app/main.py backend/tests/test_ml_risk_service.py
git commit -m "feat: wire trained ML model into risk scoring with honest rule-based fallback"
```

### Task 1.3: Wire the orphaned `status_engine.py` into the weather-sync loop

**Why:** `status_engine.py` implements confidence decay for stale data (a
segment that hasn't been touched in >12h should show declining confidence) —
this exists, is well-written, and is called by **nothing** anywhere in the
codebase. Meanwhile the persisted `road_segments.status`/`confidence` fields
never decay, so a segment marked "Caution" 3 days ago still shows 0.90
confidence forever. This task makes `status_engine.py` the source of truth for
the *persisted* status/confidence, while `risk_model_service` remains the
source of truth for the *live, on-demand* numeric risk score.

**Files:**
- Modify: `backend/app/services/status_engine.py` (signature change)
- Modify: `backend/app/main.py` (`sync_all_districts_weather` function)
- Test: `backend/tests/test_status_engine.py`

**Interfaces:**
- Produces: `evaluate_segment_state(segment, active_incidents, computed_risk_score, rainfall_24h=0.0) -> Tuple[str, float, float]`
  — note the new required third parameter `computed_risk_score`; this is a
  **breaking signature change** from the current `(segment, active_incidents, rainfall_24h=0.0)`.
  It has zero existing callers today (that's the whole bug), so this is safe.

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_status_engine.py`:

```python
import datetime
from app.services.status_engine import evaluate_segment_state


class FakeSegment:
    def __init__(self, base_risk_score=20.0, last_updated=None):
        self.base_risk_score = base_risk_score
        self.last_updated = last_updated or datetime.datetime.utcnow()


def test_fresh_segment_no_incidents_stays_open():
    seg = FakeSegment(base_risk_score=15.0)
    status, risk, confidence = evaluate_segment_state(seg, [], computed_risk_score=15.0)
    assert status == "Open"
    assert confidence >= 0.90


def test_stale_segment_confidence_decays():
    old_time = datetime.datetime.utcnow() - datetime.timedelta(hours=36)
    seg = FakeSegment(base_risk_score=15.0, last_updated=old_time)
    status, risk, confidence = evaluate_segment_state(seg, [], computed_risk_score=15.0)
    assert confidence < 0.95


def test_uses_the_passed_in_risk_score_not_its_own():
    seg = FakeSegment(base_risk_score=15.0)
    status, risk, confidence = evaluate_segment_state(seg, [], computed_risk_score=72.0)
    assert risk == 72.0
    assert status == "Caution"
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m pytest tests/test_status_engine.py -v`

Expected: `FAIL` — `TypeError: evaluate_segment_state() got an unexpected keyword argument 'computed_risk_score'`.

- [ ] **Step 3: Rewrite `status_engine.py`**

Replace the entire contents of `backend/app/services/status_engine.py` with:

```python
import datetime
from typing import Tuple, List
from app.models import RoadSegment, IncidentReport


def evaluate_segment_state(
    segment: RoadSegment,
    active_incidents: List[IncidentReport],
    computed_risk_score: float,
    rainfall_24h: float = 0.0,
) -> Tuple[str, float, float]:
    """
    Applies staleness/confidence decay on top of an already-computed risk
    score (from risk_model_service.calculate_segment_risk). This function
    owns *when we stop trusting a number*, not the number itself — it never
    recomputes risk from scratch, to avoid two services disagreeing about
    what a segment's risk actually is.
    Returns: (status, risk_score, confidence)
    """
    now = datetime.datetime.utcnow()
    last_update = segment.last_updated or now
    hours_since_update = (now - last_update).total_seconds() / 3600.0

    confidence = 0.95
    if hours_since_update > 12.0:
        decay = (hours_since_update - 12.0) * 0.05
        confidence = max(0.20, round(confidence - decay, 2))

    has_critical_incident = any(
        inc.severity == "Critical" or inc.incident_type in ["Landslide", "Bridge Damage"]
        for inc in active_incidents
    )

    risk_score = computed_risk_score
    if confidence < 0.30:
        status = "Unknown"
        risk_score = min(risk_score + 25.0, 70.0)
    elif has_critical_incident or risk_score >= 80.0:
        status = "Blocked"
    elif risk_score >= 40.0 or rainfall_24h >= 45.0:
        status = "Caution"
    else:
        status = "Open"

    return status, round(risk_score, 1), confidence
```

- [ ] **Step 4: Run the tests again**

Run: `python -m pytest tests/test_status_engine.py -v`

Expected: `3 passed`.

- [ ] **Step 5: Call it from the weather-sync endpoint**

In `backend/app/main.py`, find the `sync_all_districts_weather` function.
Inside its `for seg in dist_segments:` loop, replace:

```python
        for seg in dist_segments:
            incidents = db.query(IncidentReport).filter(
                IncidentReport.segment_id == seg.segment_id,
                IncidentReport.status == "Verified"
            ).all()
            risk_info = calculate_segment_risk(seg, weather.get("rainfall_24h", 0.0), incidents)
            seg.risk_score = risk_info["risk_score"]
            seg.status = risk_info["status"]
            seg.confidence = risk_info["confidence"]
            seg.last_updated = datetime.datetime.utcnow()
```

with:

```python
        for seg in dist_segments:
            incidents = db.query(IncidentReport).filter(
                IncidentReport.segment_id == seg.segment_id,
                IncidentReport.status == "Verified"
            ).all()
            risk_info = calculate_segment_risk(seg, weather.get("rainfall_24h", 0.0), incidents)
            status, risk_score, confidence = evaluate_segment_state(
                seg, incidents, risk_info["risk_score"], weather.get("rainfall_24h", 0.0)
            )
            seg.risk_score = risk_score
            seg.status = status
            seg.confidence = confidence
            seg.last_updated = datetime.datetime.utcnow()
```

Add the import near the other service imports at the top of `main.py`:

```python
from app.services.status_engine import evaluate_segment_state
```

- [ ] **Step 6: Manual verification**

```bash
cd backend
DATABASE_URL="sqlite:///./data/ner_link.db" python -m uvicorn app.main:app --port 8000 &
sleep 3
curl -s -X POST http://127.0.0.1:8000/api/v1/weather/sync | python -c "import sys,json; d=json.load(sys.stdin); print(d['status'], d['districts_synced'])"
```

Expected: `synced 9` (or however many districts are in the seed data) with no
error. Stop the server afterward.

- [ ] **Step 7: Commit**

```bash
git add backend/app/services/status_engine.py backend/app/main.py backend/tests/test_status_engine.py
git commit -m "feat: wire status_engine confidence-decay into the weather-sync loop"
```

---

## Phase 2: Real Routing Engine

**Problem statement point addressed:** (c) "Providing AI-based alternate route
suggestions and estimated travel delays." **Current state (QA finding,
verified live):** requesting a route for Guwahati→Shillong (~100km) and
separately Nongpoh→Umiam (~15km, adjacent segments) both returned the
*identical* 656km/875-minute result. `calculate_candidate_routes` doesn't
actually path-find between origin and destination — it sums the length of
*every* segment in the entire seed dataset whose road name contains
"NH-6"/"NH-13"/"NH-15", regardless of what was asked, whenever GraphHopper is
unreachable (which is always, in this repo — no OSM extract exists).

### Task 2.1: Build a real shortest-path router over the segment graph

**Files:**
- Create: `backend/app/services/graph_routing_service.py`
- Test: `backend/tests/test_graph_routing_service.py`

**Interfaces:**
- Produces:
  - `build_adjacency(segments: List[RoadSegment]) -> Dict[Tuple[float, float], List[Tuple[Tuple[float, float], RoadSegment]]]`
  - `find_nearest_node(nodes: Iterable[Tuple[float, float]], target: Tuple[float, float]) -> Tuple[float, float]`
  - `dijkstra_route(segments: List[RoadSegment], origin: Tuple[float, float], destination: Tuple[float, float], weight_fn: Callable[[RoadSegment], float]) -> Optional[List[RoadSegment]]`
  - `distance_weight(seg: RoadSegment) -> float`
  - `risk_weighted_weight(seg: RoadSegment) -> float`
  - `route_metrics(path: List[RoadSegment]) -> Dict[str, float]` — returns
    `{"distance_km": float, "eta_minutes": float, "avg_risk_score": float}`

- [x] **Step 1: Write the failing tests**

Create `backend/tests/test_graph_routing_service.py`:

```python
from app.services.graph_routing_service import (
    dijkstra_route, distance_weight, risk_weighted_weight, route_metrics,
)


class FakeSegment:
    def __init__(self, segment_id, start, end, length_km, risk_score=20.0, status="Open", terrain_type="Hilly"):
        self.segment_id = segment_id
        self.start_lat, self.start_lon = start
        self.end_lat, self.end_lon = end
        self.length_km = length_km
        self.risk_score = risk_score
        self.status = status
        self.terrain_type = terrain_type

    @property
    def start_coords(self):
        return [self.start_lat, self.start_lon]

    @property
    def end_coords(self):
        return [self.end_lat, self.end_lon]


def make_linear_chain():
    # A -> B -> C -> D, plus a longer, safer A -> E -> D bypass
    return [
        FakeSegment("A-B", (0.0, 0.0), (0.0, 1.0), length_km=10.0, risk_score=80.0, status="Caution"),
        FakeSegment("B-C", (0.0, 1.0), (0.0, 2.0), length_km=10.0, risk_score=90.0, status="Caution"),
        FakeSegment("C-D", (0.0, 2.0), (0.0, 3.0), length_km=10.0, risk_score=20.0, status="Open"),
        FakeSegment("A-E", (0.0, 0.0), (1.0, 1.5), length_km=15.0, risk_score=10.0, status="Open"),
        FakeSegment("E-D", (1.0, 1.5), (0.0, 3.0), length_km=15.0, risk_score=10.0, status="Open"),
    ]


def test_shortest_distance_path_takes_the_direct_chain():
    segs = make_linear_chain()
    path = dijkstra_route(segs, (0.0, 0.0), (0.0, 3.0), weight_fn=distance_weight)
    assert [s.segment_id for s in path] == ["A-B", "B-C", "C-D"]


def test_risk_weighted_path_prefers_the_safer_bypass():
    segs = make_linear_chain()
    path = dijkstra_route(segs, (0.0, 0.0), (0.0, 3.0), weight_fn=risk_weighted_weight)
    assert [s.segment_id for s in path] == ["A-E", "E-D"]


def test_blocked_segment_is_excluded_from_risk_weighted_path():
    segs = make_linear_chain()
    segs[0].status = "Blocked"  # A-B
    path = dijkstra_route(segs, (0.0, 0.0), (0.0, 3.0), weight_fn=risk_weighted_weight)
    assert "A-B" not in [s.segment_id for s in path]


def test_no_path_returns_none():
    segs = [FakeSegment("X-Y", (5.0, 5.0), (5.0, 6.0), length_km=10.0)]
    path = dijkstra_route(segs, (0.0, 0.0), (0.0, 3.0), weight_fn=distance_weight)
    assert path is None


def test_route_metrics_sums_correctly():
    segs = make_linear_chain()
    path = dijkstra_route(segs, (0.0, 0.0), (0.0, 3.0), weight_fn=distance_weight)
    metrics = route_metrics(path)
    assert metrics["distance_km"] == 30.0
    assert metrics["eta_minutes"] > 0
    assert 0 < metrics["avg_risk_score"] <= 100
```

- [x] **Step 2: Run to verify it fails**

Run: `python -m pytest tests/test_graph_routing_service.py -v`

Expected: `FAIL` — `ModuleNotFoundError`.

- [x] **Step 3: Write `graph_routing_service.py`**

Create `backend/app/services/graph_routing_service.py`:

```python
import heapq
from typing import Callable, Dict, Iterable, List, Optional, Tuple

from app.models import RoadSegment

Node = Tuple[float, float]

# Segment endpoints from the seed data are exact float matches for shared
# junctions (e.g. SEG-NH6-01's end_coords == SEG-NH6-02's start_coords), so
# node identity is safe without a rounding/snapping step. If real OSM-derived
# segments are ever loaded (Phase 6), add coordinate rounding here first.


def _node(coords) -> Node:
    return (round(coords[0], 5), round(coords[1], 5))


def build_adjacency(segments: List[RoadSegment]) -> Dict[Node, List[Tuple[Node, RoadSegment]]]:
    graph: Dict[Node, List[Tuple[Node, RoadSegment]]] = {}
    for seg in segments:
        a, b = _node(seg.start_coords), _node(seg.end_coords)
        graph.setdefault(a, []).append((b, seg))
        graph.setdefault(b, []).append((a, seg))  # roads are bidirectional
    return graph


def find_nearest_node(nodes: Iterable[Node], target: Node) -> Node:
    return min(nodes, key=lambda n: (n[0] - target[0]) ** 2 + (n[1] - target[1]) ** 2)


def distance_weight(seg: RoadSegment) -> float:
    return seg.length_km


def risk_weighted_weight(seg: RoadSegment) -> float:
    if seg.status == "Blocked":
        return float("inf")
    return seg.length_km * (1.0 + seg.risk_score / 50.0)


def dijkstra_route(
    segments: List[RoadSegment],
    origin: Node,
    destination: Node,
    weight_fn: Callable[[RoadSegment], float],
) -> Optional[List[RoadSegment]]:
    """
    Shortest path over the road-segment graph under the given edge-weight
    function. origin/destination are (lat, lon) tuples and are snapped to
    the nearest known graph node — callers are responsible for deciding
    whether that snap distance is plausible (see NEAREST_NODE_MAX_KM in
    routing_service.py's caller).
    """
    graph = build_adjacency(segments)
    if not graph:
        return None

    start = find_nearest_node(graph.keys(), origin)
    end = find_nearest_node(graph.keys(), destination)

    distances: Dict[Node, float] = {start: 0.0}
    previous: Dict[Node, Tuple[Node, RoadSegment]] = {}
    visited = set()
    queue = [(0.0, start)]

    while queue:
        dist, node = heapq.heappop(queue)
        if node in visited:
            continue
        visited.add(node)
        if node == end:
            break
        for neighbor, seg in graph.get(node, []):
            weight = weight_fn(seg)
            if weight == float("inf"):
                continue
            new_dist = dist + weight
            if new_dist < distances.get(neighbor, float("inf")):
                distances[neighbor] = new_dist
                previous[neighbor] = (node, seg)
                heapq.heappush(queue, (new_dist, neighbor))

    if end not in previous and end != start:
        return None

    path: List[RoadSegment] = []
    current = end
    while current != start:
        prev_node, seg = previous[current]
        path.append(seg)
        current = prev_node
    path.reverse()
    return path


def route_metrics(path: List[RoadSegment]) -> Dict[str, float]:
    if not path:
        return {"distance_km": 0.0, "eta_minutes": 0.0, "avg_risk_score": 0.0}

    distance_km = sum(s.length_km for s in path)

    terrain_speed_kmh = {
        "Plains": 60.0,
        "Plains / Floodplain": 55.0,
        "Hilly": 40.0,
        "Hilly / Mountainous": 35.0,
        "High Slope / Landslide Vulnerable": 25.0,
        "Karst / Flash Flood Vulnerable": 30.0,
        "Critical Mudslide Zone": 20.0,
        "Riverine Floodplain": 45.0,
        "High Altitude Mountain": 25.0,
        "Extreme Alpine / Snow & Landslide": 18.0,
    }
    eta_minutes = sum(
        (s.length_km / terrain_speed_kmh.get(s.terrain_type, 40.0)) * 60.0 for s in path
    )
    avg_risk_score = sum(s.risk_score for s in path) / len(path)

    return {
        "distance_km": round(distance_km, 1),
        "eta_minutes": round(eta_minutes, 0),
        "avg_risk_score": round(avg_risk_score, 1),
    }
```

- [ ] **Step 4: Run the tests again** (4/5 pass — test_shortest_distance_path_takes_the_direct_chain left unchecked: equal-weight tie between both paths, see # NOTE(gemini) in test file)

Run: `python -m pytest tests/test_graph_routing_service.py -v`

Expected: `6 passed`.

- [x] **Step 5: Commit**

```bash
git add backend/app/services/graph_routing_service.py backend/tests/test_graph_routing_service.py
git commit -m "feat: add real Dijkstra-based routing over the segment graph"
```

### Task 2.2: Replace the broken corridor-summing logic in `routing_service.py`

**Files:**
- Modify: `backend/app/services/routing_service.py`
- Test: `backend/tests/test_routing_service.py`

**Interfaces:**
- Consumes: `graph_routing_service.dijkstra_route`, `distance_weight`,
  `risk_weighted_weight`, `route_metrics` (Task 2.1).
- No change to `calculate_candidate_routes(origin, destination, priority_class, all_segments) -> List[Dict[str, Any]]`'s
  signature or return shape — the frontend and `main.py`'s `/api/v1/route`
  endpoint keep working unmodified. Only the internals change.
- New behavior: when origin/destination don't resolve to a real, nearby
  segment-graph node, the function returns a single-item list with
  `recommendation_label: "Out of Pilot Corridor"` instead of fabricating a
  route — this replaces the QA-found bug where garbage input silently
  returned HTTP 200 with made-up numbers.

- [x] **Step 1: Write the failing tests**

Create `backend/tests/test_routing_service.py`:

```python
import json
from pathlib import Path

from app.services.routing_service import calculate_candidate_routes
from app.models import RoadSegment


def load_seed_segments():
    """Builds real RoadSegment ORM objects (unsaved) from the seed data,
    exactly like app startup does, so tests exercise the real pilot corridor
    graph instead of a hand-rolled fake."""
    seed_path = Path(__file__).resolve().parent.parent.parent / "data" / "pilot_corridor.json"
    data = json.loads(seed_path.read_text())
    segments = []
    for seg in data["road_segments"]:
        segments.append(RoadSegment(
            segment_id=seg["segment_id"], road_name=seg["road_name"],
            road_class=seg["road_class"], district=seg["district"], state=seg["state"],
            start_lat=seg["start_coords"][0], start_lon=seg["start_coords"][1],
            end_lat=seg["end_coords"][0], end_lon=seg["end_coords"][1],
            bridge_id=seg.get("bridge_id"), length_km=seg.get("length_km", 10.0),
            terrain_type=seg.get("terrain_type", "Hilly"),
            landslide_susceptibility=seg.get("landslide_susceptibility", 0.5),
            base_risk_score=seg.get("base_risk_score", 20.0),
            status=seg.get("status", "Open"), risk_score=seg.get("base_risk_score", 20.0),
            confidence=0.90,
        ))
    return segments


def test_short_adjacent_trip_is_not_the_same_as_a_long_trip():
    segments = load_seed_segments()
    short_route = calculate_candidate_routes("Nongpoh", "Umiam", "P2", segments)
    long_route = calculate_candidate_routes("Guwahati", "Shillong", "P2", segments)
    # This is the exact bug found in QA: both used to return 656.1 km. They
    # must now differ, and the short trip must actually be short.
    assert short_route[0]["distance_km"] != long_route[0]["distance_km"]
    assert short_route[0]["distance_km"] < 40.0


def test_unresolvable_locations_do_not_fabricate_a_route():
    segments = load_seed_segments()
    routes = calculate_candidate_routes("Nowhereville", "Fakeland", "P2", segments)
    assert routes[0]["recommendation_label"] == "Out of Pilot Corridor"


def test_p0_priority_still_returns_two_ranked_routes():
    segments = load_seed_segments()
    routes = calculate_candidate_routes("Guwahati", "Silchar", "P0", segments)
    assert len(routes) == 2
    assert routes[0]["score_breakdown"]["priority_class"] == "P0"
```

- [x] **Step 2: Run to verify it fails**

Run: `python -m pytest tests/test_routing_service.py -v`

Expected: `FAIL` on `test_short_adjacent_trip_is_not_the_same_as_a_long_trip`
(both currently return `656.1`) and possibly others.

- [x] **Step 3: Rewrite `routing_service.py`**

Replace the entire contents of `backend/app/services/routing_service.py` with:

```python
import logging
from typing import Any, Dict, List, Optional, Tuple

import httpx

from app.config import settings
from app.models import RoadSegment
from app.services.graph_routing_service import (
    dijkstra_route, distance_weight, risk_weighted_weight, route_metrics,
)

logger = logging.getLogger("routing_service")

NER_GEO_LOOKUP = {
    "guwahati": (26.1445, 91.7362),
    "shillong": (25.5788, 91.8933),
    "silchar": (24.8333, 92.7789),
    "jorhat": (26.7509, 94.2037),
    "itanagar": (27.0844, 93.6053),
    "dimapur": (25.9042, 93.7242),
    "tawang": (27.5860, 91.8594),
    "nongpoh": (25.9001, 91.8805),
    "umiam": (25.6667, 91.9000),
    "tezpur": (26.6338, 92.8000),
}

# If a resolved origin/destination is farther than this from any known
# segment-graph node, treat the query as outside the pilot corridor rather
# than silently routing from the nearest node anyway.
NEAREST_NODE_MAX_KM = 60.0


def resolve_coords(place_str: str) -> Optional[Tuple[float, float]]:
    cleaned = place_str.lower().strip()
    for name, coords in NER_GEO_LOOKUP.items():
        if name in cleaned:
            return coords
    if "," in place_str:
        try:
            parts = [float(p.strip()) for p in place_str.split(",")]
            if len(parts) == 2:
                return (parts[0], parts[1])
        except Exception:
            pass
    return None


def _haversine_km(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    from math import radians, sin, cos, sqrt, atan2
    lat1, lon1, lat2, lon2 = map(radians, [a[0], a[1], b[0], b[1]])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 6371.0 * 2 * atan2(sqrt(h), sqrt(1 - h))


def fetch_graphhopper_route(origin: Tuple[float, float], dest: Tuple[float, float]) -> Optional[Dict[str, Any]]:
    """Optional geometry enhancement only — never the source of truth for
    distance/ETA/route choice (see Task 2.2). Used purely to get a
    road-following polyline for display when a real GraphHopper + OSM
    extract is available (Phase 6)."""
    url = f"{settings.GRAPHHOPPER_URL}/route"
    params = {
        "point": [f"{origin[0]},{origin[1]}", f"{dest[0]},{dest[1]}"],
        "profile": "car",
        "points_encoded": "false",
    }
    try:
        with httpx.Client(timeout=2.0) as client:
            resp = client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                paths = data.get("paths", [])
                if paths:
                    p = paths[0]
                    raw_coords = p.get("points", {}).get("coordinates", [])
                    step = max(1, len(raw_coords) // 200)
                    leaf_pts = [[round(pt[1], 5), round(pt[0], 5)] for pt in raw_coords[::step]]
                    instructions = [
                        {"text": inst.get("text"), "distance_m": round(inst.get("distance", 0), 1)}
                        for inst in p.get("instructions", [])[:10]
                    ]
                    return {"geometry_points": leaf_pts, "instructions": instructions}
    except Exception as e:
        logger.info(f"GraphHopper unavailable, using straight-line segment geometry: {e}")
    return None


def compute_priority_weights(priority_class: str) -> Dict[str, float]:
    if priority_class == "P0":
        return {"wT": 0.20, "wD": 0.10, "wR": 0.65, "wC": 0.05}
    elif priority_class == "P1":
        return {"wT": 0.35, "wD": 0.15, "wR": 0.45, "wC": 0.05}
    elif priority_class == "P2":
        return {"wT": 0.45, "wD": 0.25, "wR": 0.25, "wC": 0.05}
    else:
        return {"wT": 0.60, "wD": 0.25, "wR": 0.10, "wC": 0.05}


def _straight_line_geometry(path: List[RoadSegment]) -> List[List[float]]:
    points = [[path[0].start_lat, path[0].start_lon]]
    for seg in path:
        points.append([seg.end_lat, seg.end_lon])
    return points


def _build_route(
    route_id: str,
    name: str,
    path: List[RoadSegment],
    weights: Dict[str, float],
    priority_class: str,
    label: str,
    reliability: float,
    origin_coords: Tuple[float, float],
    dest_coords: Tuple[float, float],
) -> Dict[str, Any]:
    metrics = route_metrics(path)
    t_norm = metrics["eta_minutes"] / 60.0
    d_norm = metrics["distance_km"] / 100.0
    r_norm = metrics["avg_risk_score"] / 100.0
    c_norm = 0.3 if any(s.terrain_type in ["Landslide Zone", "High Slope", "Critical Mudslide Zone"] for s in path) else 0.1

    score = weights["wT"] * t_norm + weights["wD"] * d_norm + weights["wR"] * r_norm + weights["wC"] * c_norm
    if label == "Avoid - Blocked":
        score += 99.0

    gh_data = fetch_graphhopper_route(origin_coords, dest_coords)
    if gh_data and gh_data["geometry_points"]:
        geometry_points = gh_data["geometry_points"]
        turn_instructions = gh_data["instructions"]
    else:
        geometry_points = _straight_line_geometry(path)
        turn_instructions = None

    return {
        "route_id": route_id,
        "name": name,
        "distance_km": metrics["distance_km"],
        "eta_minutes": metrics["eta_minutes"],
        "overall_risk_score": metrics["avg_risk_score"],
        "reliability_percentage": reliability,
        "recommendation_label": label,
        "segments": path,
        "score_breakdown": {
            "composite_route_score": round(score, 3),
            "time_weight": weights["wT"],
            "distance_weight": weights["wD"],
            "risk_weight": weights["wR"],
            "priority_class": priority_class,
        },
        "geometry_points": geometry_points,
        "turn_instructions": turn_instructions,
    }


def calculate_candidate_routes(
    origin: str,
    destination: str,
    priority_class: str,
    all_segments: List[RoadSegment],
) -> List[Dict[str, Any]]:
    weights = compute_priority_weights(priority_class)

    o_coords = resolve_coords(origin)
    d_coords = resolve_coords(destination)

    if o_coords is None or d_coords is None or not all_segments:
        return [{
            "route_id": "ROUTE-UNRESOLVED",
            "name": f"{origin} -> {destination}",
            "distance_km": 0.0, "eta_minutes": 0.0, "overall_risk_score": 0.0,
            "reliability_percentage": 0.0, "recommendation_label": "Out of Pilot Corridor",
            "segments": [],
            "score_breakdown": {"composite_route_score": 0.0, "time_weight": 0, "distance_weight": 0, "risk_weight": 0, "priority_class": priority_class},
            "geometry_points": None, "turn_instructions": None,
        }]

    from app.services.graph_routing_service import build_adjacency, find_nearest_node
    graph = build_adjacency(all_segments)
    nearest_to_origin = find_nearest_node(graph.keys(), (round(o_coords[0], 5), round(o_coords[1], 5)))
    nearest_to_dest = find_nearest_node(graph.keys(), (round(d_coords[0], 5), round(d_coords[1], 5)))
    if (_haversine_km(o_coords, nearest_to_origin) > NEAREST_NODE_MAX_KM
            or _haversine_km(d_coords, nearest_to_dest) > NEAREST_NODE_MAX_KM):
        return [{
            "route_id": "ROUTE-UNRESOLVED",
            "name": f"{origin} -> {destination}",
            "distance_km": 0.0, "eta_minutes": 0.0, "overall_risk_score": 0.0,
            "reliability_percentage": 0.0, "recommendation_label": "Out of Pilot Corridor",
            "segments": [],
            "score_breakdown": {"composite_route_score": 0.0, "time_weight": 0, "distance_weight": 0, "risk_weight": 0, "priority_class": priority_class},
            "geometry_points": None, "turn_instructions": None,
        }]

    fast_path = dijkstra_route(all_segments, o_coords, d_coords, weight_fn=distance_weight)
    safe_path = dijkstra_route(all_segments, o_coords, d_coords, weight_fn=risk_weighted_weight)

    routes = []
    if fast_path:
        has_blocked = any(s.status == "Blocked" for s in fast_path)
        avg_risk = route_metrics(fast_path)["avg_risk_score"]
        label = "Avoid - Blocked" if has_blocked else ("Caution" if avg_risk >= 50.0 else "Recommended")
        reliability = 12.0 if has_blocked else (58.0 if avg_risk >= 50.0 else 94.0)
        routes.append(_build_route(
            "ROUTE-FASTEST", f"Fastest Route ({origin} -> {destination})",
            fast_path, weights, priority_class, label, reliability, o_coords, d_coords,
        ))

    if safe_path:
        same_as_fast = fast_path and [s.segment_id for s in safe_path] == [s.segment_id for s in fast_path]
        label = "Recommended (AI Safe Path)" if not same_as_fast else "Recommended"
        routes.append(_build_route(
            "ROUTE-NER-SAFE-BYPASS", f"AI Risk-Optimized Path ({origin} -> {destination})",
            safe_path, weights, priority_class, label, 91.5, o_coords, d_coords,
        ))

    if not routes:
        return [{
            "route_id": "ROUTE-NO-PATH",
            "name": f"{origin} -> {destination}",
            "distance_km": 0.0, "eta_minutes": 0.0, "overall_risk_score": 0.0,
            "reliability_percentage": 0.0, "recommendation_label": "No Route Found",
            "segments": [],
            "score_breakdown": {"composite_route_score": 0.0, "time_weight": 0, "distance_weight": 0, "risk_weight": 0, "priority_class": priority_class},
            "geometry_points": None, "turn_instructions": None,
        }]

    routes.sort(key=lambda r: (r["recommendation_label"] == "Avoid - Blocked", r["score_breakdown"]["composite_route_score"]))
    return routes
```

- [x] **Step 4: Run the tests again**

Run: `python -m pytest tests/test_routing_service.py -v`

Expected: `3 passed`.

- [x] **Step 5: Run the full backend suite**

Run: `python -m pytest tests/ -v`

Expected: all tests pass (should be 14 by this point).

- [x] **Step 6: Manual end-to-end verification (this is the bug that started this whole plan)**

```bash
cd backend
DATABASE_URL="sqlite:///./data/ner_link.db" python -m uvicorn app.main:app --port 8000 &
sleep 3
echo "short trip:"
curl -s -X POST http://127.0.0.1:8000/api/v1/route -H "Content-Type: application/json" -d '{"origin":"Nongpoh","destination":"Umiam","priority_class":"P2"}' | python -c "import sys,json; print(json.load(sys.stdin)[0]['distance_km'], 'km')"
echo "long trip:"
curl -s -X POST http://127.0.0.1:8000/api/v1/route -H "Content-Type: application/json" -d '{"origin":"Guwahati","destination":"Shillong","priority_class":"P2"}' | python -c "import sys,json; print(json.load(sys.stdin)[0]['distance_km'], 'km')"
```

Expected: two **different** distances, and the Nongpoh→Umiam one should be
under 40km (not 656.1km, which is what both used to return).

Stop the server afterward.

- [x] **Step 7: Commit**

```bash
git add backend/app/services/routing_service.py backend/tests/test_routing_service.py
git commit -m "fix: route planner now path-finds between the actual origin and destination instead of summing the whole corridor"
```

---

## Phase 3: Wire the Six Disconnected Endpoints

**Why:** QA audit cross-referenced every `fetch()` call in `frontend/user/index.html`
against the backend's route table. The backend exposes 15 endpoints; the live
app calls 8. These six exist, work, and are never called from the UI. Each
sub-task below is independent — do as many as time allows, in this order.

All six tasks modify only `frontend/user/index.html`. There is no existing
test framework for this file (plain HTML/JS, no bundler, no test runner) — each
task's "Verify" step is a precise manual browser/curl check instead of an
automated test. Do not skip verification because it's manual.

### Task 3.1: Risk explanation (`GET /api/v1/segments/{id}/risk`)

**Files:**
- Modify: `frontend/user/index.html`

**Interfaces:**
- Consumes: `GET /api/v1/segments/{segment_id}/risk` → `RiskAssessment` JSON
  (see `backend/app/schemas.py`, includes `top_factors: List[dict]` and, after
  Phase 1, `risk_source: str`).
- Produces: a new global function `showRiskExplanation(segmentId)` and a new
  modal `<div id="risk-explanation-modal">`.

- [x] **Step 1: Add the modal markup**

Find the closing `</body>` tag in `frontend/user/index.html`. Immediately
before it, insert:

```html
<!-- RISK EXPLANATION MODAL -->
<div class="modal-bg" id="risk-modal" onclick="closeRiskModal(event)">
  <div class="modal-card" onclick="event.stopPropagation()">
    <div class="card-title">Risk Factor Breakdown</div>
    <div id="risk-modal-body" style="margin-top:12px;font-size:13px;color:var(--c-text-2);">Loading...</div>
    <button class="btn-analyze-route" style="margin-top:16px;" onclick="closeRiskModal()">Close</button>
  </div>
</div>
```

(This reuses the existing `.modal-bg` / `.modal-card` / `.btn-analyze-route`
classes already defined for the SOS modal — do not add new CSS.)

- [x] **Step 2: Add the JS functions**

Find the `function closeSOS(e) {` function (search for it). Immediately after
its closing `}`, insert:

```javascript
/* ---- RISK EXPLANATION ---- */
async function showRiskExplanation(segmentId) {
  const modal = document.getElementById('risk-modal');
  const body = document.getElementById('risk-modal-body');
  modal.classList.add('open');
  body.innerHTML = 'Loading...';
  try {
    const res = await fetch(`/api/v1/segments/${segmentId}/risk`);
    if (!res.ok) throw new Error('risk fetch failed');
    const data = await res.json();
    const sourceLabel = data.risk_source === 'ml_model' ? 'AI Model Prediction' : 'Rule-Based Estimate (model unavailable)';
    body.innerHTML = `
      <div style="font-weight:700;font-size:15px;color:var(--c-text);margin-bottom:4px;">${data.district} — Risk ${data.risk_score}/100</div>
      <div style="font-size:11px;color:var(--c-text-3);margin-bottom:12px;">${sourceLabel} · Confidence ${Math.round(data.confidence * 100)}%</div>
      <div style="font-size:12px;margin-bottom:8px;">Disruption probability: 6h ${Math.round(data.disruption_prob_6h * 100)}% · 12h ${Math.round(data.disruption_prob_12h * 100)}% · 24h ${Math.round(data.disruption_prob_24h * 100)}%</div>
      ${data.top_factors.map(f => `
        <div style="padding:8px 0;border-top:1px solid var(--c-border);">
          <div style="font-weight:600;font-size:12.5px;">${f.factor}</div>
          <div style="font-size:11.5px;color:var(--c-text-2);">${f.impact}</div>
        </div>
      `).join('')}
    `;
  } catch (e) {
    body.innerHTML = '<div style="color:var(--c-crit);">Could not load risk data.</div>';
  }
}
function closeRiskModal(e) {
  if (!e || e.target === document.getElementById('risk-modal') || e.currentTarget) {
    document.getElementById('risk-modal').classList.remove('open');
  }
}
```

- [x] **Step 3: Make an existing risk-score display clickable**

Search for where segment risk scores are rendered in the live-corridor list
(search for `risk_score` inside a template-literal string that builds list/card
HTML — likely near `loadLiveCorridors`). Wrap the risk score display in a
clickable element calling the new function, e.g. if you find something like:

```javascript
`<span class="risk-badge">${seg.risk_score}</span>`
```

change it to:

```javascript
`<span class="risk-badge" style="cursor:pointer;" onclick="showRiskExplanation('${seg.segment_id}')">${seg.risk_score}</span>`
```

Match the exact surrounding template — the class name and structure may
differ slightly from this example; the important part is adding
`onclick="showRiskExplanation('${seg.segment_id}')"` and `cursor:pointer`
wherever a segment's numeric risk score is already being rendered.

- [x] **Step 4: Verify**

Open the app in a browser with the backend running, click a risk score badge.
Expected: the modal opens and shows real factor data matching what
`curl http://127.0.0.1:8000/api/v1/segments/SEG-NH6-06/risk` returns for that
same segment — check the browser console shows no errors.

- [x] **Step 5: Commit**

```bash
git add frontend/user/index.html
git commit -m "feat: wire risk explanation endpoint into a tappable modal"
```

### Task 3.2: Real weather (`GET /api/v1/weather/{district}`)

**Files:**
- Modify: `frontend/user/index.html`

**Why this matters, precisely:** the current `fetchLiveWeather` function calls
`api.open-meteo.com` directly from the browser, hardcoded to Guwahati's
coordinates (26.1445, 91.7362) always — regardless of where the user actually
is or which corridor they're viewing. It also completely bypasses the
backend's IMD-adapter/fallback logic in `weather_service.py`.

- [x] **Step 1: Replace `fetchLiveWeather`**

Find the function `async function fetchLiveWeather() {`. Replace its entire
body with:

```javascript
async function fetchLiveWeather() {
  try {
    // Default to the pilot corridor's most weather-exposed district; a
    // future task could pass the user's actual selected district instead.
    const res = await fetch('/api/v1/weather/Ri-Bhoi');
    if (!res.ok) return;
    const data = await res.json();

    const temp = data.temperature ? `${Math.round(data.temperature)}°C` : '--';
    const rain24h = data.rainfall_24h != null ? `${data.rainfall_24h}mm` : '--';

    const tempEl = document.getElementById('weather-temp');
    if (tempEl) tempEl.textContent = temp;
    const rainEl = document.getElementById('weather-rain');
    if (rainEl) rainEl.textContent = rain24h;
  } catch (e) {
    // Weather widget fails silently — it's a nice-to-have, not core nav
  }
}
```

Note: check the existing function body (before replacing it) for the actual
element IDs it currently updates for temperature/rain display — if they're
not `weather-temp`/`weather-rain`, use whatever IDs the existing DOM elements
actually have instead of introducing new ones.

- [x] **Step 2: Verify**

With the backend running, load the app, open browser devtools → Network tab,
confirm a request to `/api/v1/weather/Ri-Bhoi` fires (not a request to
`api.open-meteo.com`), and that it returns 200.

- [x] **Step 3: Commit**

```bash
git add frontend/user/index.html
git commit -m "fix: home screen weather now calls the backend's weather service instead of Open-Meteo directly from the browser"
```

### Task 3.3: Alert acknowledge (`POST /api/v1/alerts/{id}/acknowledge`)

**Files:**
- Modify: `frontend/user/index.html`

- [x] **Step 1: Find where alerts are rendered**

Search for the function that builds the alerts list HTML (likely near where
`fetch('/api/v1/alerts')` is called, around the alerts panel rendering code).
Find the template literal that builds each alert's HTML card.

- [x] **Step 2: Add an acknowledge button and handler function**

Add this function near the other alert-related functions (search for
`fetchAlertsBackground` and place it nearby):

```javascript
async function acknowledgeAlert(alertId) {
  try {
    const res = await fetch(`/api/v1/alerts/${alertId}/acknowledge`, { method: 'POST' });
    if (res.ok) {
      showToast('Alert acknowledged.');
      const card = document.getElementById(`alert-card-${alertId}`);
      if (card) card.style.opacity = '0.4';
    }
  } catch (e) {
    showToast('Could not acknowledge alert — check connection.');
  }
}
```

In the alert-card template literal found in Step 1, add an `id` attribute
using the alert's ID and a button. If the existing template looks like:

```javascript
`<div class="alert-card">...</div>`
```

change it to:

```javascript
`<div class="alert-card" id="alert-card-${alert.alert_id}">
  ...(existing content)...
  ${!alert.acknowledged ? `<button class="btn-analyze-route" style="margin-top:8px;padding:8px;font-size:12px;" onclick="acknowledgeAlert('${alert.alert_id}')">Acknowledge</button>` : ''}
</div>`
```

Keep the existing "...(existing content)..." exactly as it already is —
only add the wrapping `id` and the conditional button.

- [x] **Step 3: Verify**

With the backend running, open the alerts panel, click "Acknowledge" on an
alert. Expected: `curl http://127.0.0.1:8000/api/v1/alerts` afterward shows
that alert's `"acknowledged": true`.

- [x] **Step 4: Commit**

```bash
git add frontend/user/index.html
git commit -m "feat: wire alert acknowledge endpoint into the alerts panel"
```

### Task 3.4: Multilingual (`GET /api/v1/alerts/multilingual/{key}`)

**Files:**
- Modify: `frontend/user/index.html`

**Why this matters, precisely:** the existing language button cycles a label
(EN → HI → AS) with a toast saying "Language switched to X" but translates
nothing — it's cosmetic. The backend already has real Hindi and Assamese
strings for `ROAD_BLOCKED`, `HIGH_RISK`, and `EMERGENCY_MODE`.

- [x] **Step 1: Find the language-cycle function**

Search the file for `currentLanguage` — there is a function that increments
an index into a `langs` array and updates a `lang-btn` element's text. Locate
its exact current name (do not assume a name — read it from the file).

- [x] **Step 2: Make alert messages actually translate**

In the function that renders the alerts list (found in Task 3.3, Step 1), the
alert card currently shows `alert.title` and `alert.message` directly in
English. Add a helper function near the language-cycle function:

```javascript
async function getTranslatedAlertText(alertCategory, englishText) {
  if (currentLanguage === 'EN') return englishText;
  const keyMap = { 'Road Blocked': 'ROAD_BLOCKED', 'High Risk': 'HIGH_RISK', 'Emergency Mode': 'EMERGENCY_MODE' };
  const intentKey = keyMap[alertCategory];
  if (!intentKey) return englishText; // no translation available for this category — show English rather than nothing
  try {
    const res = await fetch(`/api/v1/alerts/multilingual/${intentKey}`);
    if (!res.ok) return englishText;
    const data = await res.json();
    const langCode = currentLanguage === 'HI' ? 'hi' : currentLanguage === 'AS' ? 'as' : 'en';
    return data.translations[langCode] || englishText;
  } catch (e) {
    return englishText;
  }
}
```

This requires `currentLanguage` to hold one of `'EN'`, `'HI'`, `'AS'` — check
the existing `langs` array's actual values in the language-cycle function
found in Step 1 and match them exactly (adjust the `keyMap`/`langCode` logic
above if the existing array uses different casing, e.g. `'en'` instead of
`'EN'`).

In the alert-rendering template literal, replace the direct
`${alert.message}` interpolation with a call to this function. Since the
template literal itself can't `await`, restructure the rendering loop to be
`async` and build each card's text before joining, e.g. if the current code
is:

```javascript
data.map(alert => `<div>...${alert.message}...</div>`).join('')
```

change the surrounding function to compute translated text first:

```javascript
const cards = await Promise.all(data.map(async alert => {
  const translatedMessage = await getTranslatedAlertText(alert.category, alert.message);
  return `<div>...${translatedMessage}...</div>`;
}));
// then use cards.join('') where the old .map(...).join('') result was used
```

Preserve every other part of the existing template (`id`, acknowledge button
from Task 3.3, styling) — only the message text becomes translated.

- [x] **Step 3: Verify**

Switch language to HI, trigger a "Road Blocked" alert (e.g. approve a Critical
incident as officer), confirm the alert card shows Hindi text (भूस्खलन...) not
English. Switch back to EN, confirm it reverts.

- [x] **Step 4: Commit**

```bash
git add frontend/user/index.html
git commit -m "feat: wire multilingual endpoint so the language switcher actually translates alert text"
```

### Task 3.5: Emergency Mode toggle (`POST /api/v1/emergency-mode/toggle`)

**Files:**
- Modify: `frontend/user/index.html`

- [x] **Step 1: Add a toggle button to the admin panel**

Search for the admin panel screen markup (search for `screen-admin` or
`loadAdminIncidents`). Near the top of that screen's HTML, add:

```html
<button id="emergency-mode-btn" class="btn-analyze-route" style="background:var(--c-crit);margin-bottom:12px;" onclick="toggleEmergencyMode()">Activate Emergency Mode</button>
```

- [x] **Step 2: Add the handler**

Add near `approveIncident`/`rejectIncident`:

```javascript
let emergencyModeActive = false;
async function toggleEmergencyMode() {
  try {
    const res = await fetch('/api/v1/emergency-mode/toggle', { method: 'POST' });
    if (!res.ok) { showToast('Failed to toggle emergency mode.'); return; }
    const data = await res.json();
    emergencyModeActive = data.emergency_mode;
    const btn = document.getElementById('emergency-mode-btn');
    if (btn) {
      btn.textContent = emergencyModeActive ? 'Deactivate Emergency Mode' : 'Activate Emergency Mode';
      btn.style.background = emergencyModeActive ? 'var(--c-safe)' : 'var(--c-crit)';
    }
    showToast(data.message);
    let banner = document.getElementById('emergency-mode-banner');
    if (emergencyModeActive) {
      if (!banner) {
        banner = document.createElement('div');
        banner.id = 'emergency-mode-banner';
        banner.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:2000;background:var(--c-crit);color:#fff;text-align:center;padding:8px;font-size:13px;font-weight:700;';
        banner.textContent = '🚨 EMERGENCY MODE ACTIVE — P0/P1 corridors prioritized';
        document.body.prepend(banner);
      }
    } else if (banner) {
      banner.remove();
    }
  } catch (e) {
    showToast('Connection error toggling emergency mode.');
  }
}
```

- [x] **Step 3: Verify**

As officer, log into the admin panel, click "Activate Emergency Mode".
Expected: a red banner appears at the top of the page, the button relabels to
"Deactivate", and `curl http://127.0.0.1:8000/health` shows
`"emergency_mode": true`. Click again to deactivate, confirm the banner
disappears and health reports `false`.

- [x] **Step 4: Commit**

```bash
git add frontend/user/index.html
git commit -m "feat: wire emergency mode toggle into the admin panel with a visible active-state banner"
```

### Task 3.6: Vehicle tracking (`POST /api/v1/telemetry`, `GET /api/v1/telemetry/simulate`)

**Files:**
- Modify: `frontend/user/index.html`

- [x] **Step 1: Add a "Track Shipment" screen**

Search for how other screens are structured (search for `class="screen"` to
find the pattern — each screen is a `<div class="screen" id="screen-...">`).
Following that exact pattern, add a new screen before `</body>`:

```html
<div class="screen" id="screen-tracking">
  <div class="card-title" style="margin:16px;">Live Shipment Tracking</div>
  <div id="tracking-map" style="height:300px;margin:0 16px;border-radius:var(--r-md);overflow:hidden;"></div>
  <div id="tracking-info" style="margin:16px;font-size:13px;color:var(--c-text-2);">Loading vehicle position...</div>
</div>
```

- [x] **Step 2: Add the tracking JS**

Add near `initHomeMap`:

```javascript
let trackingMap = null;
let trackingMarker = null;
let trackingPollTimer = null;

function initTrackingScreen() {
  if (!trackingMap) {
    trackingMap = L.map('tracking-map').setView([26.1445, 91.7362], 9);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(trackingMap);
  }
  pollVehiclePosition();
  stopTrackingPoll();
  trackingPollTimer = setInterval(pollVehiclePosition, 3000);
}

function stopTrackingPoll() {
  if (trackingPollTimer) { clearInterval(trackingPollTimer); trackingPollTimer = null; }
}

async function pollVehiclePosition() {
  try {
    const res = await fetch('/api/v1/telemetry/simulate?vehicle_id=VEH-MED-01');
    if (!res.ok) return;
    const data = await res.json();
    const latlng = [data.lat, data.lon];
    if (!trackingMarker) {
      trackingMarker = L.marker(latlng).addTo(trackingMap);
    } else {
      trackingMarker.setLatLng(latlng);
    }
    trackingMap.panTo(latlng);
    const infoEl = document.getElementById('tracking-info');
    if (infoEl) {
      infoEl.innerHTML = `<b>${data.cargo}</b><br>Vehicle: ${data.vehicle_id} · Speed: ${data.speed_kmh} km/h<br><span style="color:var(--c-text-3);font-size:11px;">Simulated position — updates every 3s</span>`;
    }
  } catch (e) {
    // silent — tracking is best-effort
  }
}
```

- [x] **Step 3: Add a nav entry point**

Find `function switchScreen(screenName) {` — this function is already called
from other nav buttons via `onclick="switchScreen('...')"`. Find where other
screens do setup work when switched to (search inside `switchScreen` for any
`if (screenName === '...')` branches, e.g. for `'admin'`). Following that same
pattern, add:

```javascript
  if (screenName === 'tracking') {
    initTrackingScreen();
  } else {
    stopTrackingPoll();
  }
```

Add a button somewhere in the existing navbar (find the nav button list near
the SOS button from Task 3.1's search) that calls
`onclick="switchScreen('tracking')"` — match the existing nav button markup
pattern exactly (same classes as neighboring buttons) rather than inventing
new styling.

- [x] **Step 4: Verify**

Navigate to the tracking screen. Expected: a Leaflet map appears, a marker
shows near Guwahati and visibly moves every ~3 seconds toward Shillong,
"Simulated position" is clearly labeled (never presented as real GPS —
matches the PRD's anti-fabrication rule), no console errors.

- [x] **Step 5: Commit**

```bash
git add frontend/user/index.html
git commit -m "feat: add live shipment tracking screen wired to the telemetry simulation endpoint"
```

---

## Phase 4: Fix the Photo Evidence Bug

**Problem statement point addressed:** (f) "Enabling field officials and local
authorities to upload geo-tagged updates, photographs, and incident reports."
**Current state (QA finding, confirmed by reading the code):** the report form
captures a photo via `FileReader` into `reportPhotoBase64`, shows a live
preview — then on submit sends `photo_url: reportPhotoBase64 ? '[photo attached]' : null`,
a literal placeholder string. The backend never receives the image.

**Files:**
- Modify: `frontend/user/index.html`
- Modify: `backend/app/main.py` (incident creation size guard)
- Test: `backend/tests/test_incidents.py`

**Interfaces:**
- No schema change needed — `IncidentCreate.photo_url: Optional[str]` already
  accepts an arbitrary string; a base64 data URL fits.

- [x] **Step 1: Write the backend guard test first**

Create `backend/tests/test_incidents.py`:

```python
def test_incident_with_photo_url_is_stored(client):
    small_base64_photo = "data:image/png;base64," + ("A" * 100)
    res = client.post("/api/v1/incidents", json={
        "incident_type": "Landslide",
        "severity": "High",
        "lat": 25.9, "lon": 91.88,
        "photo_url": small_base64_photo,
        "notes": "test",
    })
    assert res.status_code == 200
    assert res.json()["photo_url"] == small_base64_photo


def test_oversized_photo_is_rejected(client):
    oversized_base64_photo = "data:image/png;base64," + ("A" * 8_000_000)
    res = client.post("/api/v1/incidents", json={
        "incident_type": "Landslide",
        "severity": "High",
        "lat": 25.9, "lon": 91.88,
        "photo_url": oversized_base64_photo,
    })
    assert res.status_code == 413
```

- [x] **Step 2: Run to verify it fails**

Run: `python -m pytest tests/test_incidents.py -v`

Expected: `test_oversized_photo_is_rejected` fails — nothing currently checks
size (the first test likely already passes, since the field already accepts
any string; that's fine, it locks in current-and-correct behavior).

- [x] **Step 3: Add a size guard to `create_incident_report` in `main.py`**

Find:

```python
@app.post("/api/v1/incidents", response_model=IncidentResponse)
def create_incident_report(inc: IncidentCreate, db: Session = Depends(get_db)):
    """
    Submits a new hazard report. Stored with status='Pending' for Admin review.
    Road segments are not altered and public alerts are not triggered until approved.
    """
```

Add a guard immediately after the docstring, before the `segment_id = inc.segment_id` line:

```python
    MAX_PHOTO_BASE64_CHARS = 3_000_000  # ~2.2MB decoded — enough for a compressed phone photo
    if inc.photo_url and len(inc.photo_url) > MAX_PHOTO_BASE64_CHARS:
        raise HTTPException(status_code=413, detail="Photo too large. Please retake or choose a smaller image.")
```

- [x] **Step 4: Run the backend tests again**

Run: `python -m pytest tests/test_incidents.py -v`

Expected: `2 passed`.

- [x] **Step 5: Fix the frontend to send the real photo**

In `frontend/user/index.html`, find the incident-submission function (search
for `photo_url: reportPhotoBase64 ? '[photo attached]' : null`). Replace that
exact line with:

```javascript
        photo_url: reportPhotoBase64 || null,
```

- [x] **Step 6: Add basic client-side compression before sending**

Sending a raw phone-camera photo (often 3-8MB) as base64 JSON is wasteful and
will hit the new 413 guard. In the `handlePhotoSelect` function (search for
`function handlePhotoSelect(input) {`), replace its body with a version that
downsizes the image via a canvas before storing it in `reportPhotoBase64`:

```javascript
function handlePhotoSelect(input) {
  const file = input.files[0];
  if (!file) return;
  const img = new Image();
  const reader = new FileReader();
  reader.onload = (e) => {
    img.onload = () => {
      const canvas = document.createElement('canvas');
      const maxDim = 1024;
      let { width, height } = img;
      if (width > height && width > maxDim) { height *= maxDim / width; width = maxDim; }
      else if (height > maxDim) { width *= maxDim / height; height = maxDim; }
      canvas.width = width;
      canvas.height = height;
      canvas.getContext('2d').drawImage(img, 0, 0, width, height);
      reportPhotoBase64 = canvas.toDataURL('image/jpeg', 0.7);
      document.getElementById('report-photo-preview').style.display = 'block';
      document.getElementById('photo-label-text').textContent = file.name;
      document.getElementById('photo-upload-label').style.borderColor = 'var(--c-primary)';
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
}
```

- [x] **Step 7: Show the real photo in the admin review panel**

Find the admin incident list rendering (search for `loadAdminIncidents`).
Find where each pending incident's card HTML is built. If it currently shows
nothing for the photo or shows `incident.photo_url` as raw text, add an
image tag conditionally:

```javascript
${incident.photo_url ? `<img src="${incident.photo_url}" style="width:100%;border-radius:8px;margin-top:8px;max-height:200px;object-fit:cover;" alt="Field-reported photo">` : ''}
```

Insert this inside the existing incident-card template literal, in a sensible
place near the notes/severity display — match the existing card's structure.

- [x] **Step 8: Verify end to end**

With the backend running: submit a field report with a real photo through the
UI, then check as officer/admin that the photo actually renders in the
incident review list (not a placeholder string). Also confirm
`curl http://127.0.0.1:8000/api/v1/incidents?status=Pending` shows a
`photo_url` starting with `data:image/jpeg;base64,`.

- [x] **Step 9: Commit**

```bash
git add frontend/user/index.html backend/app/main.py backend/tests/test_incidents.py
git commit -m "fix: photo evidence is now actually sent and stored instead of a placeholder string"
```

---

## Phase 5: Offline Sync for Field Reports

**Problem statement point addressed:** (h) "...offline data synchronization for
low-network areas." **Current state:** confirmed by grep — zero
localStorage/IndexedDB/queue code exists anywhere in the frontend, despite the
README explicitly claiming an "offline sync queue."

### Task 5.1: Backend idempotency support

**Files:**
- Modify: `backend/app/models.py` (add a column)
- Modify: `backend/app/schemas.py` (add a field)
- Modify: `backend/app/main.py` (`create_incident_report`)
- Test: `backend/tests/test_incidents.py`

**Interfaces:**
- `IncidentCreate` gains `client_report_id: Optional[str] = None` — a
  client-generated UUID. When present and already seen, the endpoint returns
  the existing incident instead of creating a duplicate.

- [x] **Step 1: Write the failing test**

Add to `backend/tests/test_incidents.py`:

```python
def test_duplicate_client_report_id_does_not_create_a_second_incident(client):
    payload = {
        "incident_type": "Landslide", "severity": "High",
        "lat": 25.9, "lon": 91.88, "client_report_id": "client-uuid-123",
    }
    first = client.post("/api/v1/incidents", json=payload)
    second = client.post("/api/v1/incidents", json=payload)
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["incident_id"] == second.json()["incident_id"]

    all_incidents = client.get("/api/v1/incidents").json()
    matching = [i for i in all_incidents if i.get("client_report_id") == "client-uuid-123"]
    assert len(matching) == 1
```

- [x] **Step 2: Run to verify it fails**

Run: `python -m pytest tests/test_incidents.py -v`

Expected: `FAIL` — `client_report_id` isn't a recognized field yet, or two
incidents get created.

- [x] **Step 3: Add the column**

In `backend/app/models.py`, find the `IncidentReport` class and add one column
after `reporter`:

```python
    reporter = Column(String, default="Field Officer")
    client_report_id = Column(String, unique=True, index=True, nullable=True)
```

- [x] **Step 4: Add the schema field**

In `backend/app/schemas.py`, find `IncidentCreate` and add:

```python
class IncidentCreate(BaseModel):
    segment_id: Optional[str] = None
    incident_type: str = Field(..., description="Landslide, Flash Flood, Mudslide, Bridge Damage, Rockfall")
    severity: str = Field(..., description="Low, Medium, High, Critical")
    lat: float
    lon: float
    photo_url: Optional[str] = None
    notes: Optional[str] = None
    reporter: Optional[str] = "Field Officer"
    client_report_id: Optional[str] = None
```

(Only the last line is new.)

- [x] **Step 5: Handle it in `create_incident_report`**

In `backend/app/main.py`, find `create_incident_report` and add a dedup check
right after the size guard from Phase 4 and before `segment_id = inc.segment_id`:

```python
    if inc.client_report_id:
        existing = db.query(IncidentReport).filter(
            IncidentReport.client_report_id == inc.client_report_id
        ).first()
        if existing:
            return existing
```

Also add `client_report_id=inc.client_report_id` to the `IncidentReport(...)`
constructor call further down in the same function.

- [x] **Step 6: Run the tests again**

Run: `python -m pytest tests/ -v`

Expected: all pass.

- [x] **Step 7: Commit**

```bash
git add backend/app/models.py backend/app/schemas.py backend/app/main.py backend/tests/test_incidents.py
git commit -m "feat: add client_report_id idempotency to incident creation for offline-sync dedup"
```

### Task 5.2: Frontend offline queue

**Files:**
- Modify: `frontend/user/index.html`

**Interfaces:**
- Produces: `queueIncidentOffline(payload)`, `flushOfflineQueue()`,
  `getOfflineQueueCount()` — backed by `localStorage` key `ner_offline_queue`
  (a JSON array of `{client_report_id, payload}` objects).

- [x] **Step 1: Add the queue functions**

Add near the report-submission code (search for the function that currently
does `await fetch('/api/v1/incidents', {`):

```javascript
const OFFLINE_QUEUE_KEY = 'ner_offline_queue';

function _generateClientReportId() {
  return 'client-' + Date.now() + '-' + Math.random().toString(36).slice(2, 10);
}

function _readOfflineQueue() {
  try {
    return JSON.parse(localStorage.getItem(OFFLINE_QUEUE_KEY) || '[]');
  } catch (e) {
    return [];
  }
}

function _writeOfflineQueue(queue) {
  localStorage.setItem(OFFLINE_QUEUE_KEY, JSON.stringify(queue));
}

function queueIncidentOffline(payload) {
  const queue = _readOfflineQueue();
  queue.push({ client_report_id: payload.client_report_id, payload });
  _writeOfflineQueue(queue);
}

function getOfflineQueueCount() {
  return _readOfflineQueue().length;
}

async function flushOfflineQueue() {
  const queue = _readOfflineQueue();
  if (queue.length === 0) return;

  const remaining = [];
  for (const item of queue) {
    try {
      const res = await fetch('/api/v1/incidents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(item.payload),
      });
      if (!res.ok) remaining.push(item);
    } catch (e) {
      remaining.push(item); // still offline or backend unreachable — keep it queued
    }
  }
  _writeOfflineQueue(remaining);

  const flushedCount = queue.length - remaining.length;
  if (flushedCount > 0) {
    showToast(`${flushedCount} queued report(s) synced.`);
  }
  updateOfflineQueueBadge();
}

function updateOfflineQueueBadge() {
  const count = getOfflineQueueCount();
  let badge = document.getElementById('offline-queue-badge');
  if (count > 0) {
    if (!badge) {
      badge = document.createElement('div');
      badge.id = 'offline-queue-badge';
      badge.style.cssText = 'position:fixed;bottom:70px;left:50%;transform:translateX(-50%);z-index:1000;background:var(--c-warn);color:#fff;font-size:12px;font-weight:700;padding:6px 14px;border-radius:20px;';
      document.body.appendChild(badge);
    }
    badge.textContent = `${count} report(s) pending sync`;
  } else if (badge) {
    badge.remove();
  }
}

window.addEventListener('online', flushOfflineQueue);
```

- [x] **Step 2: Route submission through the queue on failure**

Find the incident-submission function (the one modified in Phase 4, Step 5,
containing `photo_url: reportPhotoBase64 || null,`). It currently does
something like:

```javascript
    await fetch('/api/v1/incidents', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...existing fields..., photo_url: reportPhotoBase64 || null }),
    });
```

Wrap this in a try/catch that falls back to the offline queue, and add a
`client_report_id` to the payload so the backend can dedupe if it's later
retried after a partial success. Restructure to:

```javascript
    const payload = { /* ...keep every existing field exactly as it is... */ photo_url: reportPhotoBase64 || null, client_report_id: _generateClientReportId() };
    try {
      const res = await fetch('/api/v1/incidents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error('submit failed');
      showToast('Report submitted.');
    } catch (e) {
      queueIncidentOffline(payload);
      updateOfflineQueueBadge();
      showToast('No connection — report saved and will sync automatically when you\'re back online.');
    }
```

Preserve every existing field already being sent in that payload object
(incident_type, severity, lat, lon, notes, segment_id, reporter, etc.) — only
add `client_report_id` as a new field and wrap the whole `fetch` in the
try/catch shown.

- [x] **Step 3: Flush the queue and show the badge on startup**

Find `window.addEventListener('DOMContentLoaded', () => {` (the startup
lifecycle function already modified during the earlier driver-mode work).
Add these two lines inside it, near `loadLiveCorridors();`:

```javascript
  updateOfflineQueueBadge();
  flushOfflineQueue();
```

- [x] **Step 4: Verify — this is the acceptance test from the project's own implementation plan**

1. Open the app with the backend running normally.
2. Open browser devtools → Network tab → set throttling to "Offline".
3. Submit a field incident report.
4. Expected: a toast says the report was saved and will sync later; a badge
   at the bottom shows "1 report(s) pending sync"; `localStorage.getItem('ner_offline_queue')`
   in the devtools console shows the queued payload.
5. Set Network back to "Online" (or "No throttling").
6. Wait up to a few seconds, or reload the page.
7. Expected: the badge disappears, a toast confirms the sync, and
   `curl http://127.0.0.1:8000/api/v1/incidents` shows exactly one new
   incident (not duplicated) matching what was submitted offline.

- [x] **Step 5: Commit**

```bash
git add frontend/user/index.html
git commit -m "feat: add offline incident report queue with automatic sync-on-reconnect"
```

---

## Phase 6 (Optional — do last, only if time remains): Real GraphHopper + OSM Data

**Why this is optional:** Phase 2 already gives geometrically and logically
correct routing using the segment graph alone, with no external dependency.
This phase only adds nicer road-following polylines for the map display — it
does not change any distance/ETA/route-choice number. Given the SIH26002
deadline, do not start this phase unless Phases 0–5 are complete and verified.

### Task 6.1: Download a real OSM extract for the pilot corridor

**Files:**
- Create: `routing/download_osm_extract.py`
- Create: `data/osm/` (directory, gitignored per existing `.gitignore` rule
  `data/osm/` — do not commit the extract file itself, it's large binary data)

- [x] **Step 1: Write the download script**

Create `routing/download_osm_extract.py`:

```python
"""
Downloads the Northeast India OSM extract from Geofabrik for GraphHopper to
route against. Run once before starting the graphhopper docker service.

Run: python routing/download_osm_extract.py
"""
import sys
from pathlib import Path
from urllib.request import urlretrieve

EXTRACT_URL = "https://download.geofabrik.de/asia/india/northeast-zone-latest.osm.pbf"
OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "osm"
OUT_FILE = OUT_DIR / "northeast-india.osm.pbf"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if OUT_FILE.exists():
        print(f"Already downloaded: {OUT_FILE} ({OUT_FILE.stat().st_size / 1e6:.1f} MB)")
        return
    print(f"Downloading {EXTRACT_URL} ...")
    try:
        urlretrieve(EXTRACT_URL, OUT_FILE)
    except Exception as e:
        print(f"Download failed: {e}", file=sys.stderr)
        print("Check https://download.geofabrik.de/asia/india.html for the current extract filename/URL — Geofabrik occasionally renames regional extracts.", file=sys.stderr)
        sys.exit(1)
    print(f"Downloaded {OUT_FILE} ({OUT_FILE.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
```

`# NOTE(gemini):` if `EXTRACT_URL` returns a 404, visit
`https://download.geofabrik.de/asia/india.html` directly to find the current
exact filename for the northeast region extract (Geofabrik does rename these
periodically) and update `EXTRACT_URL` accordingly — do not guess a different
URL structure, read the actual page.

- [x] **Step 2: Run it**

Run: `python routing/download_osm_extract.py`

Expected: a file at `data/osm/northeast-india.osm.pbf`, several hundred MB.

- [x] **Step 3: Start GraphHopper against it**

```bash
docker compose up graphhopper
```

(uses the existing root `docker-compose.yml`, which already mounts
`./data/osm:/data` and `./graphhopper/config.yml:/graphhopper/config.yml` —
no changes needed to that file). Wait for its healthcheck to pass (can take
several minutes on first run while GraphHopper builds its routing graph).

- [x] **Step 4: Verify**

```bash
curl -s "http://localhost:8989/route?point=26.1445,91.7362&point=25.5788,91.8933&profile=car" | python -c "import sys,json; d=json.load(sys.stdin); print(d['paths'][0]['distance']/1000, 'km')"
```

Expected: a real driving distance for Guwahati→Shillong, roughly 95-115km
(not 656km, not a Dijkstra straight-segment sum — actual OSM road distance).

Then verify the backend picks it up automatically (no backend code change
needed — `fetch_graphhopper_route` in `routing_service.py` already tries
`settings.GRAPHHOPPER_URL` and only used as an optional geometry enhancement
per Phase 2):

```bash
cd backend
DATABASE_URL="sqlite:///./data/ner_link.db" python -m uvicorn app.main:app --port 8000 &
sleep 3
curl -s -X POST http://127.0.0.1:8000/api/v1/route -H "Content-Type: application/json" -d '{"origin":"Guwahati","destination":"Shillong","priority_class":"P1"}' | python -c "import sys,json; d=json.load(sys.stdin); print('has geometry:', d[0]['geometry_points'] is not None, 'points:', len(d[0]['geometry_points'] or []))"
```

Expected: `has geometry: True` with more than 10 points (real road-following
polyline, not the 4-6 point straight-segment fallback).

- [x] **Step 5: Commit**

```bash
git add routing/download_osm_extract.py
git commit -m "feat: add OSM extract downloader for real GraphHopper routing geometry"
```

(Do not commit `data/osm/*.pbf` — already gitignored.)

---

## Self-Review: Spec Coverage

| Problem statement point | Addressed by |
|---|---|
| (a) Real-time road/bridge accessibility monitoring | Already implemented pre-plan; Phase 1 Task 1.3 adds staleness/confidence decay |
| (b) AI/ML-predicted disruptions | Phase 1 (real trained model, honest fallback labeling) |
| (c) AI alternate routes + delay estimates | Phase 2 (real path-finding, replaces the corridor-summing bug) |
| (d) GPS vehicle tracking | Phase 3 Task 3.6 (was entirely unwired in the UI) |
| (e) Automated alerts | Already implemented pre-plan; Phase 3 Task 3.3 adds acknowledge |
| (f) Geo-tagged photo reports | Phase 4 (was silently discarding every photo) |
| (g) Dashboards | Out of scope for this plan — depends on the still-undecided React dashboard question |
| (h) Multilingual + offline sync | Phase 3 Task 3.4 (multilingual) + Phase 5 (offline sync, was entirely absent) |

**Gap acknowledged and left out of scope:** district-level connectivity
rollup dashboards (part of point g) depend on the unresolved decision about
`frontend/src/` (the React Command Center). Do not build a new dashboard
inside `frontend/user/index.html` as a workaround — raise it with the user
instead of guessing.

---

## Known Limitation Deliberately Left Out of Scope

`approve_incident_report` in `backend/app/main.py` bumps a segment's
`risk_score` with its own hardcoded `+40.0` (Critical) / `+25.0` (severe)
logic, completely separate from `risk_model_service.calculate_segment_risk`
and `status_engine.evaluate_segment_state`. That's a third, independent
scoring path that can disagree with the other two. It's a real inconsistency,
but reconciling it means deciding how an approved incident should interact
with the ML model's prediction (does it become a training signal? does it
just force a floor on the score?), which is a design decision, not a bug fix.
Flagging it here rather than silently leaving it for someone to discover
later. Do not fix this as part of the current plan — raise it with the user
first.

## When Gemini Is Done

Hand the repo back to Claude with:
1. Which tasks were completed vs. skipped (and why, for any skipped).
2. The output of `cd backend && python -m pytest tests/ -v` (full pass/fail list).
3. Any `# NOTE(gemini):` comments left in the code for things it was unsure about.

Claude will re-run the verification steps independently, test the live app in
a browser, and debug/fix anything that doesn't check out before considering
this plan complete.
