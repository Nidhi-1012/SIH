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
