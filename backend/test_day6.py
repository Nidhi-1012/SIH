import urllib.request
import json

print("=== Testing Day 6 Multilingual Safety Layer & Emergency Mode ===")

# 1. Multilingual Safety Alerts (EN, HI, AS)
res_m = json.loads(urllib.request.urlopen('http://127.0.0.1:8000/api/v1/alerts/multilingual/ROAD_BLOCKED').read().decode('utf-8'))
print("Multilingual Road Blocked Warning:")
for lang, text in res_m['translations'].items():
    clean_text = text.encode('ascii', 'ignore').decode('ascii') if lang != 'en' else text
    print(f" [{lang.upper()}] {clean_text if clean_text else '[Unicode Hindi/Assamese Text Available]'}")

# 2. Emergency Mode Toggle
req_e = urllib.request.Request('http://127.0.0.1:8000/api/v1/emergency-mode/toggle', data=b'{}', headers={'Content-Type': 'application/json'})
res_e = json.loads(urllib.request.urlopen(req_e).read().decode('utf-8'))
print(f"\nEmergency Mode Active: {res_e['emergency_mode']}")
print(f"Multilingual Broadcast: {res_e['multilingual_broadcast']['en']}")
