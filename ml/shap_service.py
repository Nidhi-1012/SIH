from typing import Dict, Any, List

def compute_shap_explanations(
    feature_row: Dict[str, float],
    risk_score: float
) -> List[Dict[str, Any]]:
    """
    Computes surrogate SHAP feature attributions for risk score breakdown.
    Returns array of top factor impacts for front-end explanation panel.
    """
    factors = []
    
    r24 = feature_row.get('rainfall_24h', 0.0)
    if r24 > 15.0:
        impact_pts = min(round(r24 * 0.45, 1), 40.0)
        factors.append({
            "factor": f"Precipitation Intensity ({r24} mm/24h)",
            "impact": f"+{impact_pts} pts risk",
            "type": "Weather"
        })

    slope = feature_row.get('slope_deg', 20.0)
    susceptibility = feature_row.get('landslide_susceptibility', 0.5)
    if susceptibility > 0.6 or slope > 25.0:
        impact_pts = round(slope * 0.4 + susceptibility * 15.0, 1)
        factors.append({
            "factor": f"High Slope Landslide Terrain ({slope}° slope)",
            "impact": f"+{impact_pts} pts risk",
            "type": "Terrain"
        })

    incidents = feature_row.get('incident_count', 0)
    if incidents > 0:
        impact_pts = min(incidents * 40.0, 50.0)
        factors.append({
            "factor": f"Active Field Reports ({incidents} verified)",
            "impact": f"+{impact_pts} pts risk",
            "type": "Field Report"
        })

    if not factors:
        factors.append({
            "factor": "Baseline Road Stability",
            "impact": "Normal conditions",
            "type": "Terrain"
        })

    return factors
