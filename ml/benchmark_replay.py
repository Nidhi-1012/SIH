"""
Benchmark replay: compares three routing strategies against the REAL pilot-
corridor segment graph (data/pilot_corridor.json) under two simulated
weather scenarios, using the actual backend routing/risk code -- not
hand-typed numbers. Every figure in ml/artifacts/benchmark_results.json is
either computed here or an average of numbers computed here.

Both scenarios recompute every segment's risk score via the real
risk_model_service (same function the live API calls) under a shared
rainfall value, applied corridor-wide:

  - Scenario 1, "Severe Monsoon Closure" (95mm/24h): pushes the corridor's
    highest-risk segments to Blocked. Demonstrates stranding avoidance --
    does the router refuse to drive through a confirmed closure?
  - Scenario 2, "Elevated Risk Advisory" (40mm/24h): pushes the corridor's
    highest-risk segment (SEG-NH6-06, "Critical Mudslide Zone") to Caution
    -- elevated, but not closed -- while a real alternate route
    (SEG-NH6-06-ALT, a longer, safer bypass added specifically so this
    comparison is possible) stays Open at much lower risk. Demonstrates
    genuine proactive rerouting: does the router choose the safer path
    *before* a segment fails, or only react once it's fully closed?

Three strategies, compared over the same set of real town-to-town pairs on
the pilot corridor:
  - Baseline A "Naive Shortest Distance": ignores risk AND blocked status
    entirely (an old-fashioned GPS with no live road-condition feed).
  - Baseline B "Reactive Closure-Only": avoids segments already Blocked,
    otherwise pure shortest distance -- no awareness of elevated-but-open risk.
  - NER-LINK AI: risk-weighted routing (graph_routing_service.risk_weighted_weight),
    the same function backend/app/services/routing_service.py uses live.

Run: python ml/benchmark_replay.py
Produces: ml/artifacts/benchmark_results.json
"""
import copy
import datetime
import json
import sys
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "backend"))

from app.services import ml_risk_service  # noqa: E402
from app.services.risk_model_service import calculate_segment_risk  # noqa: E402
from app.services.graph_routing_service import (  # noqa: E402
    dijkstra_route, risk_weighted_weight, route_metrics,
)

SCENARIOS = [
    {
        "key": "severe_monsoon_closure",
        "label": "Severe Monsoon Closure",
        "rainfall_24h_mm": 95.0,
        "demonstrates": "Stranding avoidance -- does the router refuse a confirmed closure?",
    },
    {
        "key": "elevated_risk_advisory",
        "label": "Elevated Risk Advisory",
        "rainfall_24h_mm": 40.0,
        "demonstrates": (
            "Proactive rerouting -- with SEG-NH6-06 elevated to Caution but "
            "still technically open, does the router choose the safer "
            "SEG-NH6-06-ALT bypass before the road fails, or only react "
            "once it's fully closed?"
        ),
    },
]

# Real town-to-town pairs on the pilot corridor (see data/pilot_corridor.json
# for the underlying segment graph). Chosen to isolate each chokepoint:
BENCHMARK_PAIRS = [
    ("Guwahati", (26.1445, 91.7362), "Silchar", (24.8333, 92.7789)),      # crosses both chokepoints (Nongpoh-Umiam + Jowai-Sonapur)
    ("Guwahati", (26.1445, 91.7362), "Shillong", (25.5788, 91.8933)),     # crosses Nongpoh-Umiam only
    ("Shillong", (25.5788, 91.8933), "Silchar", (24.8333, 92.7789)),      # crosses Jowai-Sonapur only -- clean bypass demo
    ("Jowai", (25.4485, 92.2030), "Silchar", (24.8333, 92.7789)),         # crosses Jowai-Sonapur only -- clean bypass demo
    ("Nongpoh", (25.9001, 91.8805), "Silchar", (24.8333, 92.7789)),       # crosses both chokepoints
    ("Guwahati", (26.1445, 91.7362), "Tezpur", (26.6338, 92.8000)),       # control: NH-15, unaffected by either chokepoint
]


def load_segments() -> list:
    seed_path = REPO_ROOT / "data" / "pilot_corridor.json"
    data = json.loads(seed_path.read_text())
    segments = []
    for seg in data["road_segments"]:
        segments.append(SimpleNamespace(
            segment_id=seg["segment_id"],
            road_name=seg["road_name"],
            district=seg["district"],
            start_lat=seg["start_coords"][0], start_lon=seg["start_coords"][1],
            end_lat=seg["end_coords"][0], end_lon=seg["end_coords"][1],
            start_coords=seg["start_coords"], end_coords=seg["end_coords"],
            length_km=seg.get("length_km", 10.0),
            terrain_type=seg.get("terrain_type", "Hilly"),
            landslide_susceptibility=seg.get("landslide_susceptibility", 0.5),
            base_risk_score=seg.get("base_risk_score", 20.0),
            status=seg.get("status", "Open"),
            risk_score=seg.get("base_risk_score", 20.0),
        ))
    return segments


def apply_scenario(segments: list, rainfall_24h: float) -> str:
    """Recomputes every segment's risk_score/status via the real
    risk_model_service under the given shared rainfall. Returns which
    source produced the numbers ("ml_model" or "rule_based_fallback") so
    the report never claims a model result it didn't actually get."""
    risk_source = "rule_based_fallback"
    for seg in segments:
        result = calculate_segment_risk(seg, rainfall_24h, active_incidents=[])
        seg.risk_score = result["risk_score"]
        seg.status = result["status"]
        risk_source = result["risk_source"]
    return risk_source


def naive_distance_weight(seg) -> float:
    """Baseline A: distance only, blind to status or risk entirely."""
    return seg.length_km


def blocked_only_weight(seg) -> float:
    """Baseline B: avoids a confirmed closure, otherwise pure distance --
    no signal at all for a segment that's merely high-risk but still open."""
    if seg.status == "Blocked":
        return float("inf")
    return seg.length_km


def run_strategy(segments: list, weight_fn, blocked_segment_ids: set, caution_segment_ids: set) -> dict:
    per_pair = []
    for origin_name, origin, dest_name, dest in BENCHMARK_PAIRS:
        path = dijkstra_route(segments, origin, dest, weight_fn=weight_fn)
        if path is None:
            per_pair.append({
                "pair": f"{origin_name} -> {dest_name}",
                "routed": False,
                "reason": "No path avoiding the blocked segment(s) exists in the pilot corridor graph",
            })
            continue
        metrics = route_metrics(path)
        path_ids = {s.segment_id for s in path}
        per_pair.append({
            "pair": f"{origin_name} -> {dest_name}",
            "routed": True,
            "segments": sorted(path_ids),
            "distance_km": metrics["distance_km"],
            "eta_minutes": metrics["eta_minutes"],
            "avg_risk_score": metrics["avg_risk_score"],
            "drives_through_confirmed_closure": bool(path_ids & blocked_segment_ids),
            "drives_through_elevated_caution_segment": bool(path_ids & caution_segment_ids),
        })

    routed = [p for p in per_pair if p["routed"]]
    unrouted_count = len(per_pair) - len(routed)
    stranded_count = sum(1 for p in routed if p["drives_through_confirmed_closure"])
    caution_count = sum(1 for p in routed if p["drives_through_elevated_caution_segment"])

    return {
        "pairs_evaluated": len(per_pair),
        "pairs_with_no_available_route": unrouted_count,
        "pairs_routed_through_confirmed_closure": stranded_count,
        "stranding_rate_pct": round(100.0 * stranded_count / len(per_pair), 1),
        "pairs_routed_through_elevated_caution_segment": caution_count,
        "avg_risk_exposure": round(sum(p["avg_risk_score"] for p in routed) / len(routed), 1) if routed else None,
        "avg_eta_minutes": round(sum(p["eta_minutes"] for p in routed) / len(routed), 1) if routed else None,
        "per_pair_detail": per_pair,
    }


def run_scenario(scenario: dict) -> dict:
    segments = load_segments()
    risk_source = apply_scenario(segments, scenario["rainfall_24h_mm"])

    blocked_segment_ids = {s.segment_id for s in segments if s.status == "Blocked"}
    caution_segment_ids = {s.segment_id for s in segments if s.status == "Caution"}

    baseline_a = run_strategy(segments, naive_distance_weight, blocked_segment_ids, caution_segment_ids)
    baseline_b = run_strategy(copy.deepcopy(segments), blocked_only_weight, blocked_segment_ids, caution_segment_ids)
    ner_link_ai = run_strategy(copy.deepcopy(segments), risk_weighted_weight, blocked_segment_ids, caution_segment_ids)

    result = {
        "label": scenario["label"],
        "demonstrates": scenario["demonstrates"],
        "rainfall_24h_mm": scenario["rainfall_24h_mm"],
        "risk_score_source": risk_source,
        "segments_blocked_by_scenario": sorted(blocked_segment_ids),
        "segments_at_elevated_caution": sorted(caution_segment_ids),
        "baselines": {
            "naive_shortest_distance": baseline_a,
            "reactive_closure_only": baseline_b,
        },
        "ner_link_ai_risk_weighted": ner_link_ai,
    }

    if baseline_a["avg_risk_exposure"] and ner_link_ai["avg_risk_exposure"]:
        result["risk_exposure_reduction_vs_naive_baseline_pct"] = round(
            100.0 * (baseline_a["avg_risk_exposure"] - ner_link_ai["avg_risk_exposure"]) / baseline_a["avg_risk_exposure"],
            1,
        )
    return result


def run_benchmark_replay() -> dict:
    print("=== Benchmark Replay: real routing/risk code against the real pilot corridor ===")

    ml_risk_service.load_model()

    scenario_results = {}
    for scenario in SCENARIOS:
        print(f"\n--- Scenario: {scenario['label']} ({scenario['rainfall_24h_mm']}mm/24h) ---")
        result = run_scenario(scenario)
        scenario_results[scenario["key"]] = result

        a, b, ai = result["baselines"]["naive_shortest_distance"], result["baselines"]["reactive_closure_only"], result["ner_link_ai_risk_weighted"]
        print(f"  Naive baseline  -- stranding: {a['stranding_rate_pct']}% | through-Caution: {a['pairs_routed_through_elevated_caution_segment']}/{a['pairs_evaluated']} | avg risk: {a['avg_risk_exposure']}")
        print(f"  Reactive-only   -- stranding: {b['stranding_rate_pct']}% | through-Caution: {b['pairs_routed_through_elevated_caution_segment']}/{b['pairs_evaluated']} | avg risk: {b['avg_risk_exposure']} | unroutable: {b['pairs_with_no_available_route']}")
        print(f"  NER-LINK AI     -- stranding: {ai['stranding_rate_pct']}% | through-Caution: {ai['pairs_routed_through_elevated_caution_segment']}/{ai['pairs_evaluated']} | avg risk: {ai['avg_risk_exposure']} | unroutable: {ai['pairs_with_no_available_route']}")
        if "risk_exposure_reduction_vs_naive_baseline_pct" in result:
            print(f"  Risk exposure reduction vs. naive baseline: {result['risk_exposure_reduction_vs_naive_baseline_pct']}%")

    results = {
        "computed_at": datetime.datetime.utcnow().isoformat() + "Z",
        "methodology": (
            "Every number below comes from calling the same "
            "backend/app/services/{risk_model_service,graph_routing_service}.py "
            "code the live API uses, against the real segments in "
            "data/pilot_corridor.json (including SEG-NH6-06-ALT, a "
            "representative bypass route added specifically to make a "
            "genuine alternate-path comparison possible -- see its `notes` "
            "field in that file). No numbers in this file are hand-typed."
        ),
        "scenarios": scenario_results,
    }

    out_dir = REPO_ROOT / "ml" / "artifacts"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "benchmark_results.json").write_text(json.dumps(results, indent=2))

    return results


if __name__ == "__main__":
    run_benchmark_replay()
