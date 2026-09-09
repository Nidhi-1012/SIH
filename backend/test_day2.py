import urllib.request
import json

# 1. Post field incident report
inc_data = json.dumps({
    'segment_id': 'SEG-NH6-03',
    'incident_type': 'Landslide',
    'severity': 'Critical',
    'lat': 25.9001,
    'lon': 91.8805,
    'notes': 'Massive rockslide blocked both lanes near milepost 42.',
    'reporter': 'Field Officer Nongpoh'
}).encode('utf-8')

req = urllib.request.Request('http://127.0.0.1:8000/api/v1/incidents', data=inc_data, headers={'Content-Type': 'application/json'})
res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
print(f"Incident Submitted: {res['incident_id']} - {res['incident_type']} ({res['severity']})")

# 2. Verify road segment status update
seg_data = json.loads(urllib.request.urlopen('http://127.0.0.1:8000/api/v1/segments').read().decode('utf-8'))
blocked = [s for s in seg_data if s['segment_id'] == 'SEG-NH6-03'][0]
print(f"Updated Segment Status: {blocked['road_name']} -> STATUS: {blocked['status']} | RISK SCORE: {blocked['risk_score']}")

# 3. Test dynamic route re-ranking
route_req = json.dumps({'origin': 'Guwahati (Assam)', 'destination': 'Silchar (Assam via NH-6)', 'priority_class': 'P0'}).encode('utf-8')
req_r = urllib.request.Request('http://127.0.0.1:8000/api/v1/route', data=route_req, headers={'Content-Type': 'application/json'})
routes = json.loads(urllib.request.urlopen(req_r).read().decode('utf-8'))
print("\nRoute Recommendations post-incident:")
for r in routes:
    name_clean = r['name'].encode('ascii', 'ignore').decode('ascii')
    print(f" - {name_clean}: Label='{r['recommendation_label']}', Risk={r['overall_risk_score']}, ETA={r['eta_minutes']}m")
