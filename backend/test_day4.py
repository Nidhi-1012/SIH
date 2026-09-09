import urllib.request
import json

print("=== Testing PRD §6.3 Multi-Objective RouteScore Ranking ===")

for priority in ['P0', 'P1', 'P2', 'P3']:
    data = json.dumps({
        'origin': 'Guwahati (Assam)',
        'destination': 'Silchar (Assam via NH-6)',
        'priority_class': priority
    }).encode('utf-8')
    
    req = urllib.request.Request(
        'http://127.0.0.1:8000/api/v1/route',
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    routes = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    top = routes[0]
    score = top['score_breakdown']['composite_route_score']
    w_r = top['score_breakdown']['risk_weight']
    w_t = top['score_breakdown']['time_weight']
    print(f"Priority Class {priority}: Top Choice='{top['recommendation_label']}' | Composite RouteScore={score:.3f} (Risk Wt={w_r}, Time Wt={w_t})")
