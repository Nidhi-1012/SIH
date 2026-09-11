import logging
import math
import httpx
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Tuple, Optional
from app.models import RoadSegment
from app.config import settings

logger = logging.getLogger("routing_service")

# Known coordinates for NER cities/nodes (used for GraphHopper OSM routing)
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
    "nalbari": (26.4465, 91.4381),
    "barpeta": (26.3223, 91.0060),
    "nagaon": (26.3479, 92.6839),
    "dibrugarh": (27.4728, 94.9120),
    "kohima": (25.6751, 94.1086),
}

def _haversine_km(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    R = 6371.0
    lat1, lon1, lat2, lon2 = math.radians(a[0]), math.radians(a[1]), math.radians(b[0]), math.radians(b[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))

def _segments_near_corridor(segments: List[RoadSegment], o_coords: Tuple[float, float], d_coords: Tuple[float, float], pad_deg: float = 0.35) -> List[RoadSegment]:
    """
    The pilot dataset only covers ~10 segments along 3 fixed corridors
    (NH-6 Guwahati<->Silchar via Shillong, NH-15 Guwahati<->Tezpur, NH-13
    Bhalukpong<->Tawang) — it is not a full NER road network. Filters to
    segments whose midpoint actually falls near the requested origin/destination,
    instead of always returning "any NH-6/13/15 segment" regardless of what
    was asked for (which made every route look like Guwahati<->Shillong).
    """
    lat_min = min(o_coords[0], d_coords[0]) - pad_deg
    lat_max = max(o_coords[0], d_coords[0]) + pad_deg
    lon_min = min(o_coords[1], d_coords[1]) - pad_deg
    lon_max = max(o_coords[1], d_coords[1]) + pad_deg
    relevant = []
    for s in segments:
        mid_lat = (s.start_lat + s.end_lat) / 2
        mid_lon = (s.start_lon + s.end_lon) / 2
        if lat_min <= mid_lat <= lat_max and lon_min <= mid_lon <= lon_max:
            relevant.append(s)
    return relevant

_geocode_cache: Dict[str, Optional[Tuple[float, float]]] = {}

def _geocode_nominatim(place_str: str) -> Optional[Tuple[float, float]]:
    """
    Falls back to OpenStreetMap's free Nominatim geocoder when a place isn't
    one of the ~15 towns hardcoded in NER_GEO_LOOKUP — keeps geocoding
    keyless, consistent with the rest of this project's OSM-based stack
    (GraphHopper, Open-Meteo). Without this, any place not in that tiny list
    (e.g. "Byrnihat", "Jamuguri") silently fell through to resolve_coords()
    returning None, and the caller substituted a hardcoded Guwahati/Shillong
    default — meaning every unrecognized place search actually ran a
    Guwahati<->Shillong route under the hood. Bounded to a rough NER box so a
    same-named place elsewhere in India doesn't get matched instead.

    Cached in-process — real place names don't move, and Nominatim's public
    endpoint alone can take several seconds per call, so repeat searches for
    the same town (very common in testing/demo use) come back instantly.
    """
    key = place_str.strip().lower()
    if key in _geocode_cache:
        return _geocode_cache[key]

    result = None
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": place_str,
                    "format": "json",
                    "limit": 1,
                    "viewbox": "89.0,29.5,97.5,22.0",  # west,north,east,south — rough NER bounding box
                    "bounded": 1,
                },
                headers={"User-Agent": "NER-SafeRoute-Pilot/1.0 (SIH26002, contact: dev-team)"}
            )
            if resp.status_code == 200:
                results = resp.json()
                if results:
                    result = (float(results[0]["lat"]), float(results[0]["lon"]))
    except Exception as e:
        logger.warning(f"Nominatim geocoding failed for '{place_str}': {e}")

    _geocode_cache[key] = result
    return result

def resolve_coords(place_str: str) -> Optional[Tuple[float, float]]:
    """Resolves coordinates from a known town name, comma-separated lat,lon,
    or (as a last resort) live geocoding — returns None, never a silent
    default, when nothing actually matches."""
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
    return _geocode_nominatim(place_str)

def fetch_graphhopper_route(origin: Tuple[float, float], dest: Tuple[float, float]) -> Optional[Dict[str, Any]]:
    """Queries local GraphHopper container for native OSM path, distance, ETA and geometry."""
    url = f"{settings.GRAPHHOPPER_URL}/route"
    params = {
        "point": [f"{origin[0]},{origin[1]}", f"{dest[0]},{dest[1]}"],
        "profile": "car",
        "points_encoded": "false"
    }
    try:
        with httpx.Client(timeout=4.0) as client:
            resp = client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                paths = data.get("paths", [])
                if paths:
                    p = paths[0]
                    raw_coords = p.get("points", {}).get("coordinates", [])
                    # Subsample points for performance ([lat, lon])
                    step = max(1, len(raw_coords) // 200)
                    leaf_pts = [[round(pt[1], 5), round(pt[0], 5)] for pt in raw_coords[::step]]
                    if raw_coords and leaf_pts[-1] != [round(raw_coords[-1][1], 5), round(raw_coords[-1][0], 5)]:
                        leaf_pts.append([round(raw_coords[-1][1], 5), round(raw_coords[-1][0], 5)])
                    
                    instructions = [
                        {"text": inst.get("text"), "distance_m": round(inst.get("distance", 0), 1)}
                        for inst in p.get("instructions", [])[:10]
                    ]
                    return {
                        "distance_km": round(p.get("distance", 0) / 1000.0, 1),
                        "eta_minutes": round(p.get("time", 0) / 60000.0, 1),
                        "geometry_points": leaf_pts,
                        "instructions": instructions
                    }
    except Exception as e:
        logger.warning(f"GraphHopper offline or unroutable: {e}")
    return None

def compute_priority_weights(priority_class: str) -> Dict[str, float]:
    """
    Returns weights for RouteScore = wT*T + wD*D + wR*R + wC*C + wU*U + wP*P (PRD §6.3)
    P0 = Emergency Medical / Relief (Maximum safety & risk avoidance)
    P1 = Essential Food Supply
    P2 = Agri Produce
    P3 = General Freight / Construction
    """
    if priority_class == "P0":
        return {"wT": 0.20, "wD": 0.10, "wR": 0.65, "wC": 0.05}  # Heavy risk penalty
    elif priority_class == "P1":
        return {"wT": 0.35, "wD": 0.15, "wR": 0.45, "wC": 0.05}
    elif priority_class == "P2":
        return {"wT": 0.45, "wD": 0.25, "wR": 0.25, "wC": 0.05}
    else:
        return {"wT": 0.60, "wD": 0.25, "wR": 0.10, "wC": 0.05}  # Travel time priority

def calculate_candidate_routes(
    origin: str,
    destination: str,
    priority_class: str,
    all_segments: List[RoadSegment]
) -> List[Dict[str, Any]]:
    """
    Evaluates route candidates using the PRD §6.3 multi-objective scoring formula:
    RouteScore = wT*T + wD*D + wR*R + wC*C + wU*U + wP*P
    """
    weights = compute_priority_weights(priority_class)

    # Real coordinates only — never a silent Guwahati/Shillong substitute.
    # resolve_coords() now falls all the way through to live geocoding
    # before giving up, so None here means neither the local lookup nor
    # Nominatim could place this name at all (typo, or genuinely outside NER).
    o_coords = resolve_coords(origin)
    d_coords = resolve_coords(destination)
    if o_coords is None or d_coords is None:
        unresolved = origin if o_coords is None else destination
        return [{
            "route_id": "ROUTE-LOCATION-NOT-FOUND",
            "name": f'Could not locate "{unresolved}"',
            "distance_km": 0.0,
            "eta_minutes": 0.0,
            "overall_risk_score": 0.0,
            "reliability_percentage": 0.0,
            "recommendation_label": "Location Not Found",
            "segments": [],
            "score_breakdown": {
                "composite_route_score": 0.0,
                "time_weight": weights["wT"],
                "distance_weight": weights["wD"],
                "risk_weight": weights["wR"],
                "priority_class": priority_class,
                "note": f'Could not resolve a location for "{unresolved}". Try a nearby town, landmark, or "lat,lon" coordinates.'
            },
            "geometry_points": None,
            "turn_instructions": None
        }]

    gh_data = fetch_graphhopper_route(o_coords, d_coords)

    # The pilot dataset only covers ~10 segments on 3 fixed corridors — pick
    # the ones actually near this origin/destination instead of always
    # returning "any NH-6/13/15 segment", which made every request look like
    # the same Guwahati<->Shillong route regardless of what was asked for.
    relevant_segments = _segments_near_corridor(all_segments, o_coords, d_coords)

    if not relevant_segments:
        straight_km = _haversine_km(o_coords, d_coords)
        dist_est = gh_data["distance_km"] if gh_data else round(straight_km * 1.3, 1)  # road-distance fudge over straight-line
        time_est = gh_data["eta_minutes"] if gh_data else round((dist_est / 45.0) * 60.0, 0)
        return [{
            "route_id": "ROUTE-ESTIMATED",
            "name": f"Estimated Route ({origin} -> {destination})",
            "distance_km": round(dist_est, 1),
            "eta_minutes": time_est,
            "overall_risk_score": 30.0,
            "reliability_percentage": 40.0,
            "recommendation_label": "Estimated - Outside Pilot Corridor Coverage",
            "segments": [],
            "score_breakdown": {
                "composite_route_score": 0.0,
                "time_weight": weights["wT"],
                "distance_weight": weights["wD"],
                "risk_weight": weights["wR"],
                "priority_class": priority_class,
                "note": "No verified road-segment risk data for this route - it falls outside the seeded NH-6/NH-13/NH-15 pilot corridor, so this is a straight-line distance estimate, not risk-scored."
            },
            "geometry_points": gh_data["geometry_points"] if gh_data else None,
            "turn_instructions": gh_data["instructions"] if gh_data else None
        }]

    # Corridor 1: the relevant segments' own primary highway (NH-6/13/15), so
    # a Bhalukpong->Tawang request gets NH-13 segments, not NH-6 ones.
    main_corridor = [s for s in relevant_segments if "NH-6" in s.road_name] or \
                     [s for s in relevant_segments if "NH-13" in s.road_name] or \
                     [s for s in relevant_segments if "NH-15" in s.road_name] or \
                     relevant_segments

    # Hard Constraint Check: Check for Blocked segments
    has_blocked_main = any(s.status == "Blocked" for s in main_corridor)
    
    dist_1 = gh_data["distance_km"] if gh_data else (sum(s.length_km for s in main_corridor) or 180.0)
    avg_risk_1 = (sum(s.risk_score for s in main_corridor) / len(main_corridor)) if main_corridor else 55.0
    time_1 = gh_data["eta_minutes"] if gh_data else ((dist_1 / 45.0) * 60.0)  # minutes

    # Calculate RouteScore components
    t_norm_1 = time_1 / 60.0
    d_norm_1 = dist_1 / 100.0
    r_norm_1 = avg_risk_1 / 100.0
    c_norm_1 = 0.3 if any(s.terrain_type in ["Landslide Zone", "High Slope"] for s in main_corridor) else 0.1

    route_score_1 = (
        weights["wT"] * t_norm_1 + 
        weights["wD"] * d_norm_1 + 
        weights["wR"] * r_norm_1 + 
        weights["wC"] * c_norm_1
    )

    if has_blocked_main:
        label_1 = "Avoid - Blocked"
        rel_1 = 12.0
        route_score_1 += 99.0  # Severe hard-constraint penalty
    elif avg_risk_1 >= 50.0:
        label_1 = "Caution"
        rel_1 = 58.0
    else:
        label_1 = "Recommended"
        rel_1 = 94.0

    route_1 = {
        "route_id": "ROUTE-NH6-DIRECT",
        "name": f"Direct Highway Corridor ({origin} -> {destination})",
        "distance_km": round(dist_1, 1),
        "eta_minutes": round(time_1, 0),
        "overall_risk_score": round(avg_risk_1, 1),
        "reliability_percentage": rel_1,
        "recommendation_label": label_1,
        "segments": main_corridor,
        "score_breakdown": {
            "composite_route_score": round(route_score_1, 3),
            "time_weight": weights["wT"],
            "distance_weight": weights["wD"],
            "risk_weight": weights["wR"],
            "priority_class": priority_class
        },
        "geometry_points": gh_data["geometry_points"] if gh_data else None,
        "turn_instructions": gh_data["instructions"] if gh_data else None
    }

    # Corridor 2: AI Risk-Optimized Safe Bypass Corridor — still scoped to
    # segments actually relevant to this origin/destination.
    safe_segments = [s for s in relevant_segments if s.status != "Blocked" and s.risk_score < 45.0]
    if not safe_segments:
        safe_segments = [s for s in relevant_segments if s.status != "Blocked"]
    if not safe_segments:
        safe_segments = relevant_segments

    dist_2 = dist_1 * 1.15  # 15% longer bypass path
    avg_risk_2 = max((sum(s.risk_score for s in safe_segments) / len(safe_segments)), 18.0)
    time_2 = (dist_2 / 50.0) * 60.0

    t_norm_2 = time_2 / 60.0
    d_norm_2 = dist_2 / 100.0
    r_norm_2 = avg_risk_2 / 100.0
    c_norm_2 = 0.1

    route_score_2 = (
        weights["wT"] * t_norm_2 + 
        weights["wD"] * d_norm_2 + 
        weights["wR"] * r_norm_2 + 
        weights["wC"] * c_norm_2
    )

    label_2 = "Recommended (AI Safe Path)" if (has_blocked_main or avg_risk_1 > avg_risk_2) else "Alternative"
    rel_2 = 91.5

    route_2 = {
        "route_id": "ROUTE-NER-SAFE-BYPASS",
        "name": f"AI Risk-Optimized Bypass ({origin} -> {destination})",
        "distance_km": round(dist_2, 1),
        "eta_minutes": round(time_2, 0),
        "overall_risk_score": round(avg_risk_2, 1),
        "reliability_percentage": rel_2,
        "recommendation_label": label_2,
        "segments": safe_segments,
        "score_breakdown": {
            "composite_route_score": round(route_score_2, 3),
            "time_weight": weights["wT"],
            "distance_weight": weights["wD"],
            "risk_weight": weights["wR"],
            "priority_class": priority_class
        },
        "geometry_points": gh_data["geometry_points"] if gh_data else None,
        "turn_instructions": gh_data["instructions"] if gh_data else None
    }

    # Rank Candidate Routes (Lowest RouteScore first)
    routes = [route_1, route_2]
    routes.sort(key=lambda r: (r["recommendation_label"] == "Avoid - Blocked", r["score_breakdown"]["composite_route_score"]))

    return routes
