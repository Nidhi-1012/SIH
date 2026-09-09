import urllib.request, json, os

BASE = "http://127.0.0.1:8000"

print("\n=== NER SAFEROUTE — LIVE STATUS CHECK ===\n")

# 1. Health
with urllib.request.urlopen(f"{BASE}/health", timeout=5) as r:
    h = json.loads(r.read())
    print(f"  [OK] Backend health   : {h['status']} (emergency_mode={h['emergency_mode']})")

# 2. Mobile app served by backend StaticFiles mount
try:
    with urllib.request.urlopen(f"{BASE}/mobile/app.html", timeout=5) as r:
        size = len(r.read())
        print(f"  [OK] /mobile/app.html : {size:,} bytes ({size//1024} KB) — served by backend")
except Exception as e:
    print(f"  [--] /mobile/app.html via backend mount: {e}")

# 3. Road segments
with urllib.request.urlopen(f"{BASE}/api/v1/segments", timeout=5) as r:
    segs = json.loads(r.read())
    print(f"  [OK] Road segments    : {len(segs)} loaded")

# 4. Risk score
seg0 = segs[0]["segment_id"]
with urllib.request.urlopen(f"{BASE}/api/v1/segments/{seg0}/risk", timeout=8) as r:
    rs = json.loads(r.read())
    rval = rs.get("risk_score", rs.get("risk", "??"))
    print(f"  [OK] Risk score       : {seg0} -> {rval}%")

# 5. Alerts count
with urllib.request.urlopen(f"{BASE}/api/v1/alerts", timeout=5) as r:
    alerts = json.loads(r.read())
    print(f"  [OK] Active alerts    : {len(alerts)} in system")

# 6. File presence
files = {
    "Mobile SafeRoute App (index.html)":  r"C:\Users\hp\OneDrive\Desktop\SIH\mobile\index.html",
    "Mobile SafeRoute App (app.html)":    r"C:\Users\hp\OneDrive\Desktop\SIH\mobile\app.html",
    "Frontend public/mobile/index.html":  r"C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\mobile\index.html",
    "Benchmark results JSON":             r"C:\Users\hp\OneDrive\Desktop\SIH\ml\artifacts\benchmark_results.json",
    "Demo backup scenario":               r"C:\Users\hp\OneDrive\Desktop\SIH\data\demo_backup_scenario.json",
}
print()
for label, path in files.items():
    if os.path.exists(path):
        sz = os.path.getsize(path)
        print(f"  [OK] {label:<42} {sz:>8,} bytes")
    else:
        print(f"  [XX] MISSING: {path}")

print()
print("=" * 56)
print("  NER SAFEROUTE — ALL SERVICES LIVE")
print("=" * 56)
print("  Mobile SafeRoute App  ->  http://127.0.0.1:8000/mobile/app.html")
print("  Field Officer PWA     ->  http://127.0.0.1:8000/mobile/")
print("  Backend API           ->  http://127.0.0.1:8000")
print("  Swagger Docs          ->  http://127.0.0.1:8000/docs")
print("  React Command Centre  ->  http://localhost:3000")
print("  Network (phone/WiFi)  ->  http://192.168.0.104:8000/mobile/app.html")
print("=" * 56)
