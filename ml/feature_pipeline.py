import pandas as pd
import numpy as np
from typing import Dict, Any

FEATURE_COLUMNS = [
    'rainfall_1h',
    'rainfall_6h',
    'rainfall_24h',
    'forecast_24h_rain',
    'slope_deg',
    'landslide_susceptibility',
    'soil_saturation',
    'incident_count'
]

def extract_segment_features(
    segment: Any,
    weather: Dict[str, Any],
    incident_count: int = 0
) -> pd.DataFrame:
    """
    Extracts normalized feature vector for a road segment and district weather.
    """
    r_1h = float(weather.get('rainfall_1h', 0.0))
    r_6h = float(weather.get('rainfall_6h', 0.0))
    r_24h = float(weather.get('rainfall_24h', 0.0))
    f_24h = float(weather.get('forecast_24h_rain', r_24h * 1.2))

    susceptibility = float(getattr(segment, 'landslide_susceptibility', 0.5))
    
    # Estimate slope angle based on terrain type
    terrain = str(getattr(segment, 'terrain_type', 'Hilly'))
    if 'Alpine' in terrain or 'Landslide' in terrain:
        slope = 38.5
    elif 'Mountain' in terrain or 'Hilly' in terrain:
        slope = 28.0
    else:
        slope = 10.0

    # Soil saturation proxy
    saturation = min(100.0, r_24h * 0.75 + r_6h * 1.2 + 15.0)

    feature_dict = {
        'rainfall_1h': r_1h,
        'rainfall_6h': r_6h,
        'rainfall_24h': r_24h,
        'forecast_24h_rain': f_24h,
        'slope_deg': slope,
        'landslide_susceptibility': susceptibility,
        'soil_saturation': saturation,
        'incident_count': incident_count
    }

    return pd.DataFrame([feature_dict])[FEATURE_COLUMNS]
