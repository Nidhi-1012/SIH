from typing import Dict, Any, List
from app.models import RoadSegment, IncidentReport

def calculate_segment_risk(
    segment: RoadSegment, 
    rainfall_24h: float, 
    active_incidents: List[IncidentReport]
) -> Dict[str, Any]:
    """
    Calculates composite Risk Score (0-100), disruption probabilities (6h, 12h, 24h),
    and SHAP-style factor attributions for a given road segment.
    """
    base_susceptibility = segment.landslide_susceptibility or 0.5
    base_risk = segment.base_risk_score or 20.0
    
    # 1. Weather Impact Factor (Rainfall intensity)
    weather_impact = min(rainfall_24h * 0.65, 45.0)
    
    # 2. Incident Impact Factor (Field reports)
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

    # 3. Calculate Composite Score
    total_risk = base_risk * 0.2 + (base_susceptibility * 25.0) + weather_impact + incident_impact
    total_risk = min(max(total_risk, 5.0), 99.0)

    # 4. Disruption Probabilities at 6h, 12h, 24h
    prob_6h = min(total_risk / 100.0 * 0.8, 0.99)
    prob_12h = min(total_risk / 100.0 * 0.9, 0.99)
    prob_24h = min(total_risk / 100.0 * 1.0, 0.99)

    # 5. Status State Machine
    if has_blocking_incident or total_risk >= 80.0:
        computed_status = "Blocked"
    elif total_risk >= 40.0 or rainfall_24h >= 45.0:
        computed_status = "Caution"
    else:
        computed_status = "Open"

    # 6. Factor Explanations (SHAP Feature Attributions)
    top_factors = []
    if rainfall_24h > 15.0:
        top_factors.append({
            "factor": f"Heavy Precipitation ({rainfall_24h} mm/24h)",
            "impact": f"+{round(weather_impact, 1)} pts risk",
            "type": "Weather"
        })
    if active_incidents:
        top_factors.append({
            "factor": f"Active Field Reports ({len(active_incidents)} reported)",
            "impact": f"+{round(incident_impact, 1)} pts risk",
            "type": "Field Report"
        })
    if base_susceptibility >= 0.7:
        top_factors.append({
            "factor": f"High Slope Landslide Terrain ({segment.terrain_type})",
            "impact": f"+{round(base_susceptibility * 25.0, 1)} pts risk",
            "type": "Terrain"
        })

    if not top_factors:
        top_factors.append({
            "factor": "Baseline Road Stability",
            "impact": "Normal conditions",
            "type": "Terrain"
        })

    return {
        "segment_id": segment.segment_id,
        "district": segment.district,
        "risk_score": round(total_risk, 1),
        "disruption_prob_6h": round(prob_6h, 2),
        "disruption_prob_12h": round(prob_12h, 2),
        "disruption_prob_24h": round(prob_24h, 2),
        "confidence": 0.92 if active_incidents else 0.85,
        "status": computed_status,
        "top_factors": top_factors
    }
