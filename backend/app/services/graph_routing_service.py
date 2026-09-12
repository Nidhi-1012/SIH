import heapq
from typing import Callable, Dict, Iterable, List, Optional, Tuple

from app.models import RoadSegment

Node = Tuple[float, float]

# Segment endpoints from the seed data are exact float matches for shared
# junctions (e.g. SEG-NH6-01's end_coords == SEG-NH6-02's start_coords), so
# node identity is safe without a rounding/snapping step. If real OSM-derived
# segments are ever loaded (Phase 6), add coordinate rounding here first.


def _node(coords) -> Node:
    return (round(coords[0], 5), round(coords[1], 5))


def build_adjacency(segments: List[RoadSegment]) -> Dict[Node, List[Tuple[Node, RoadSegment]]]:
    graph: Dict[Node, List[Tuple[Node, RoadSegment]]] = {}
    for seg in segments:
        a, b = _node(seg.start_coords), _node(seg.end_coords)
        graph.setdefault(a, []).append((b, seg))
        graph.setdefault(b, []).append((a, seg))  # roads are bidirectional
    return graph


def find_nearest_node(nodes: Iterable[Node], target: Node) -> Node:
    return min(nodes, key=lambda n: (n[0] - target[0]) ** 2 + (n[1] - target[1]) ** 2)


def distance_weight(seg: RoadSegment) -> float:
    return seg.length_km


def risk_weighted_weight(seg: RoadSegment) -> float:
    if seg.status == "Blocked":
        return float("inf")
    return seg.length_km * (1.0 + seg.risk_score / 50.0)


_COUNTER = 0  # heap tie-breaker — ensures FIFO ordering for equal-weight paths


def dijkstra_route(
    segments: List[RoadSegment],
    origin: Node,
    destination: Node,
    weight_fn: Callable[[RoadSegment], float],
) -> Optional[List[RoadSegment]]:
    """
    Shortest path over the road-segment graph under the given edge-weight
    function. origin/destination are (lat, lon) tuples and are snapped to
    the nearest known graph node — callers are responsible for deciding
    whether that snap distance is plausible (see NEAREST_NODE_MAX_KM in
    routing_service.py's caller).
    """
    global _COUNTER
    graph = build_adjacency(segments)
    if not graph:
        return None

    start = find_nearest_node(graph.keys(), origin)
    end = find_nearest_node(graph.keys(), destination)

    # If origin and dest snap to the same node but are actually different
    # physical locations, the graph is disconnected from the real request —
    # treat as no path rather than returning an empty list (which would look
    # like a found 0-hop route).
    if start == end and (round(origin[0], 5), round(origin[1], 5)) != (round(destination[0], 5), round(destination[1], 5)):
        return None

    distances: Dict[Node, float] = {start: 0.0}
    previous: Dict[Node, Tuple[Node, RoadSegment]] = {}
    visited = set()
    _COUNTER += 1
    queue = [(0.0, _COUNTER, start)]

    while queue:
        dist, _, node = heapq.heappop(queue)
        if node in visited:
            continue
        visited.add(node)
        if node == end:
            break
        for neighbor, seg in graph.get(node, []):
            weight = weight_fn(seg)
            if weight == float("inf"):
                continue
            new_dist = dist + weight
            if new_dist < distances.get(neighbor, float("inf")):
                distances[neighbor] = new_dist
                previous[neighbor] = (node, seg)
                _COUNTER += 1
                heapq.heappush(queue, (new_dist, _COUNTER, neighbor))

    if end not in previous and end != start:
        return None

    path: List[RoadSegment] = []
    current = end
    while current != start:
        prev_node, seg = previous[current]
        path.append(seg)
        current = prev_node
    path.reverse()
    return path


def route_metrics(path: List[RoadSegment]) -> Dict[str, float]:
    if not path:
        return {"distance_km": 0.0, "eta_minutes": 0.0, "avg_risk_score": 0.0}

    distance_km = sum(s.length_km for s in path)

    terrain_speed_kmh = {
        "Plains": 60.0,
        "Plains / Floodplain": 55.0,
        "Hilly": 40.0,
        "Hilly / Mountainous": 35.0,
        "High Slope / Landslide Vulnerable": 25.0,
        "Karst / Flash Flood Vulnerable": 30.0,
        "Critical Mudslide Zone": 20.0,
        "Riverine Floodplain": 45.0,
        "High Altitude Mountain": 25.0,
        "Extreme Alpine / Snow & Landslide": 18.0,
    }
    eta_minutes = sum(
        (s.length_km / terrain_speed_kmh.get(s.terrain_type, 40.0)) * 60.0 for s in path
    )
    avg_risk_score = sum(s.risk_score for s in path) / len(path)

    return {
        "distance_km": round(distance_km, 1),
        "eta_minutes": round(eta_minutes, 0),
        "avg_risk_score": round(avg_risk_score, 1),
    }
