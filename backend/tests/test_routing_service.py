import json
from pathlib import Path

from app.services.routing_service import calculate_candidate_routes
from app.models import RoadSegment


def load_seed_segments():
    """Builds real RoadSegment ORM objects (unsaved) from the seed data,
    exactly like app startup does, so tests exercise the real pilot corridor
    graph instead of a hand-rolled fake."""
    seed_path = Path(__file__).resolve().parent.parent.parent / "data" / "pilot_corridor.json"
    data = json.loads(seed_path.read_text())
    segments = []
    for seg in data["road_segments"]:
        segments.append(RoadSegment(
            segment_id=seg["segment_id"], road_name=seg["road_name"],
            road_class=seg["road_class"], district=seg["district"], state=seg["state"],
            start_lat=seg["start_coords"][0], start_lon=seg["start_coords"][1],
            end_lat=seg["end_coords"][0], end_lon=seg["end_coords"][1],
            bridge_id=seg.get("bridge_id"), length_km=seg.get("length_km", 10.0),
            terrain_type=seg.get("terrain_type", "Hilly"),
            landslide_susceptibility=seg.get("landslide_susceptibility", 0.5),
            base_risk_score=seg.get("base_risk_score", 20.0),
            status=seg.get("status", "Open"), risk_score=seg.get("base_risk_score", 20.0),
            confidence=0.90,
        ))
    return segments


def test_short_adjacent_trip_is_not_the_same_as_a_long_trip():
    segments = load_seed_segments()
    short_route = calculate_candidate_routes("Nongpoh", "Umiam", "P2", segments)
    long_route = calculate_candidate_routes("Guwahati", "Shillong", "P2", segments)
    # This is the exact bug found in QA: both used to return 656.1 km. They
    # must now differ, and the short trip must actually be short.
    assert short_route[0]["distance_km"] != long_route[0]["distance_km"]
    assert short_route[0]["distance_km"] < 40.0


def test_unresolvable_locations_do_not_fabricate_a_route():
    segments = load_seed_segments()
    routes = calculate_candidate_routes("Nowhereville", "Fakeland", "P2", segments)
    assert routes[0]["recommendation_label"] == "Out of Pilot Corridor"


def test_p0_priority_still_returns_two_ranked_routes():
    segments = load_seed_segments()
    routes = calculate_candidate_routes("Guwahati", "Silchar", "P0", segments)
    assert len(routes) == 2
    assert routes[0]["score_breakdown"]["priority_class"] == "P0"
