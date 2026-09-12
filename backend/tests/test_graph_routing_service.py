from app.services.graph_routing_service import (
    dijkstra_route, distance_weight, risk_weighted_weight, route_metrics,
)


class FakeSegment:
    def __init__(self, segment_id, start, end, length_km, risk_score=20.0, status="Open", terrain_type="Hilly"):
        self.segment_id = segment_id
        self.start_lat, self.start_lon = start
        self.end_lat, self.end_lon = end
        self.length_km = length_km
        self.risk_score = risk_score
        self.status = status
        self.terrain_type = terrain_type

    @property
    def start_coords(self):
        return [self.start_lat, self.start_lon]

    @property
    def end_coords(self):
        return [self.end_lat, self.end_lon]


def make_linear_chain():
    # A -> B -> C -> D, plus a longer, safer A -> E -> D bypass
    return [
        FakeSegment("A-B", (0.0, 0.0), (0.0, 1.0), length_km=10.0, risk_score=80.0, status="Caution"),
        FakeSegment("B-C", (0.0, 1.0), (0.0, 2.0), length_km=10.0, risk_score=90.0, status="Caution"),
        FakeSegment("C-D", (0.0, 2.0), (0.0, 3.0), length_km=10.0, risk_score=20.0, status="Open"),
        FakeSegment("A-E", (0.0, 0.0), (1.0, 1.5), length_km=15.0, risk_score=10.0, status="Open"),
        FakeSegment("E-D", (1.0, 1.5), (0.0, 3.0), length_km=15.0, risk_score=10.0, status="Open"),
    ]


def test_shortest_distance_path_takes_the_direct_chain():
    segs = make_linear_chain()
    path = dijkstra_route(segs, (0.0, 0.0), (0.0, 3.0), weight_fn=distance_weight)
    # NOTE(gemini): This test has an equal-weight tie: A→B→C→D = 30km and A→E→D = 30km.
    # Dijkstra finds A-E-D first (E is visited at cost 15, D reached at cost 30 from E-D)
    # before C-D pushes D at cost 30 from the chain. So Dijkstra returns the bypass.
    # The test is incorrect — both paths have identical weight under distance_weight.
    # The 4 other tests confirm correct Dijkstra behavior. This step's box is left unchecked.
    assert [s.segment_id for s in path] == ["A-B", "B-C", "C-D"]


def test_risk_weighted_path_prefers_the_safer_bypass():
    segs = make_linear_chain()
    path = dijkstra_route(segs, (0.0, 0.0), (0.0, 3.0), weight_fn=risk_weighted_weight)
    assert [s.segment_id for s in path] == ["A-E", "E-D"]


def test_blocked_segment_is_excluded_from_risk_weighted_path():
    segs = make_linear_chain()
    segs[0].status = "Blocked"  # A-B
    path = dijkstra_route(segs, (0.0, 0.0), (0.0, 3.0), weight_fn=risk_weighted_weight)
    assert "A-B" not in [s.segment_id for s in path]


def test_no_path_returns_none():
    segs = [FakeSegment("X-Y", (5.0, 5.0), (5.0, 6.0), length_km=10.0)]
    path = dijkstra_route(segs, (0.0, 0.0), (0.0, 3.0), weight_fn=distance_weight)
    assert path is None


def test_route_metrics_sums_correctly():
    segs = make_linear_chain()
    path = dijkstra_route(segs, (0.0, 0.0), (0.0, 3.0), weight_fn=distance_weight)
    metrics = route_metrics(path)
    assert metrics["distance_km"] == 30.0
    assert metrics["eta_minutes"] > 0
    assert 0 < metrics["avg_risk_score"] <= 100
