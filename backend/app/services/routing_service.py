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
    "bhalukpong": (27.0125, 92.6410),
    "nalbari": (26.4465, 91.4364),
    "barpeta": (26.3229, 91.0064),
    "nagaon": (26.3480, 92.6840),
    "dibrugarh": (27.4728, 94.9120),
    "kohima": (25.6751, 94.1086),
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
