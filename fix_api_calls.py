import pathlib
import re

targets = [
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\app.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\index_mobile.html',
]

for target in targets:
    p = pathlib.Path(target)
    if not p.exists():
        print(f"SKIP (not found): {p.name}")
        continue
    
    text = p.read_text(encoding='utf-8')
    original = text

    # Fix 1: Replace hardcoded http://127.0.0.1:8000 with empty string (relative URLs)
    text = text.replace("'http://127.0.0.1:8000/api/", "'/api/")
    text = text.replace('"http://127.0.0.1:8000/api/', '"/api/')

    # Fix 2: Fix submitReport - latitude/longitude -> lat/lon
    old_body = '''body: JSON.stringify({
        incident_type: selHazard,
        severity: 'High',
        description: note || `${selHazard} reported on active corridor`,
        latitude: pos.lat,
        longitude: pos.lon
      })'''
    new_body = '''body: JSON.stringify({
        incident_type: selHazard,
        severity: 'High',
        notes: note || `${selHazard} reported on active corridor`,
        lat: pos.lat,
        lon: pos.lon
      })'''
    text = text.replace(old_body, new_body)

    if text != original:
        p.write_text(text, encoding='utf-8')
        print(f"Fixed: {p.name}")
    else:
        print(f"No changes needed: {p.name}")
