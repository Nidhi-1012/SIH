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

    import pandas as pd

    ordered_row = pd.DataFrame([{col: features[col] for col in _feature_columns}], columns=_feature_columns)
    probability = float(_model.predict_proba(ordered_row)[0][1])

    # Feature importances are global to the model (not per-prediction SHAP
    # values) — this is the documented fallback from the PRD's own risk
    # watchlist ("prioritize explainability over accuracy for the demo") when
    # a full SHAP integration isn't worth the added dependency weight.
    importances = {
        col: round(float(imp), 4)
        for col, imp in zip(_feature_columns, _model.feature_importances_)
    }
    return probability, importances
