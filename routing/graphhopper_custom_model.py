import json
from typing import List, Dict, Any

def generate_graphhopper_custom_model(blocked_segments: List[str], high_risk_segments: List[str]) -> Dict[str, Any]:
    """
    Generates GraphHopper custom_model JSON payload dynamically.
    Heavily penalizes Blocked road segments (0.001 multiplier) and high risk segments (0.2 multiplier).
    Matches GraphHopper v8+ CustomModel specification (PRD §6.3 / §14.3).
    """
    custom_model = {
        "speed": [
            {
                "if": "road_class == TERTIARY || road_class == UNCLASSIFIED",
                "multiply_by": "0.7"
            }
        ],
        "priority": [
            {
                "if": "surface == UNPAVED",
                "multiply_by": "0.6"
            }
        ]
    }

    # Add blocked segment exclusions
    if blocked_segments:
        for seg_id in blocked_segments:
            custom_model["priority"].append({
                "if": f"road_environment == '{seg_id}' || segment_id == '{seg_id}'",
                "multiply_by": "0.001"  # Near zero priority -> route around blocked road
            })

    # Add high-risk segment penalties
    if high_risk_segments:
        for seg_id in high_risk_segments:
            custom_model["speed"].append({
                "if": f"segment_id == '{seg_id}'",
                "multiply_by": "0.4"    # Reduce speed assumption by 60% on high risk zones
            })

    return custom_model

if __name__ == "__main__":
    cm = generate_graphhopper_custom_model(
        blocked_segments=["SEG-NH6-03"],
        high_risk_segments=["SEG-NH6-02", "SEG-NH6-06"]
    )
    print("Generated GraphHopper Custom Model:")
    print(json.dumps(cm, indent=2))
