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
