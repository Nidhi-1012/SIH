import pathlib

targets = [
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\app.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\index_mobile.html',
]

# Fix 1: fitBounds needs a maxZoom to prevent zooming too far out
OLD_FITBOUNDS = "homeMap.fitBounds(routeLine.getBounds(), { padding: [70, 70] });"
NEW_FITBOUNDS = "homeMap.fitBounds(routeLine.getBounds(), { padding: [60, 60], maxZoom: 11 });"

# Fix 2: origin in the API call is hardcoded - use the input field value
OLD_ORIGIN = "body: JSON.stringify({ origin: 'Guwahati', destination: destInput, priority_class: 'P2' })"
NEW_ORIGIN = "body: JSON.stringify({ origin: originInput || 'Guwahati', destination: destInput, priority_class: 'P2' })"

# Fix 3: Read origin input at start of findRoutes - it reads destInput but not originInput
OLD_FIND_ROUTES_START = "  const destInput = document.getElementById('desk-dest').value.trim() || document.getElementById('mob-dest').value.trim();"
NEW_FIND_ROUTES_START = "  const originInput = document.getElementById('desk-origin').value.trim() || '';\n  const destInput = document.getElementById('desk-dest').value.trim() || document.getElementById('mob-dest').value.trim();"

for target in targets:
    p = pathlib.Path(target)
    if not p.exists(): continue
    
    text = p.read_text(encoding='utf-8')
    original = text
    
    text = text.replace(OLD_FITBOUNDS, NEW_FITBOUNDS)
    text = text.replace(OLD_ORIGIN, NEW_ORIGIN)
    text = text.replace(OLD_FIND_ROUTES_START, NEW_FIND_ROUTES_START)
    
    if text != original:
        p.write_text(text, encoding='utf-8')
        print(f"Updated {p.name}")
    else:
        print(f"No change in {p.name}")
