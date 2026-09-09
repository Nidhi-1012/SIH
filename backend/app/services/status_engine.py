import datetime
from typing import Tuple
from app.models import RoadSegment, IncidentReport

def evaluate_segment_state(
    segment: RoadSegment, 
    active_incidents: list[IncidentReport],
    rainfall_24h: float = 0.0
) -> Tuple[str, float, float]:
    """
    Evaluates segment state: Open, Caution, Blocked, Unknown
    Applies staleness decay if last update > 12 hours old.
    Returns: (new_status, new_risk_score, new_confidence)
    """
    now = datetime.datetime.utcnow()
    last_update = segment.last_updated or now
    hours_since_update = (now - last_update).total_seconds() / 3600.0

    # Base confidence decay (0.05 loss per hour after 12h staleness window)
    confidence = 0.95
    if hours_since_update > 12.0:
        decay = (hours_since_update - 12.0) * 0.05
        confidence = max(0.20, round(confidence - decay, 2))

    # Evaluate Incidents
    has_critical_incident = False
    has_high_incident = False
    for inc in active_incidents:
        if inc.severity == "Critical" or inc.incident_type in ["Landslide", "Bridge Damage"]:
            has_critical_incident = True
        elif inc.severity in ["High", "Medium"]:
            has_high_incident = True

    # State Machine Logic
    if confidence < 0.30:
        new_status = "Unknown"
        risk_score = min(segment.base_risk_score + 25.0, 70.0)
    elif has_critical_incident:
        new_status = "Blocked"
        risk_score = 92.0
    elif has_high_incident or rainfall_24h >= 45.0 or segment.base_risk_score >= 50.0:
        new_status = "Caution"
        risk_score = max(55.0, segment.base_risk_score + 15.0)
    else:
        new_status = "Open"
        risk_score = max(10.0, segment.base_risk_score)

    return new_status, round(risk_score, 1), confidence
