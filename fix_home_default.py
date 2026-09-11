import pathlib

targets = [
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\user\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\app.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\index_mobile.html',
]

# On DOMContentLoaded, explicitly close all screens so home map is always default
OLD = "window.addEventListener('DOMContentLoaded', () => {\n  initHomeMap();\n  fetchLiveWeather();\n  loadLiveCorridors();\n  \n  if (window.location.hash === '#admin') {\n    switchScreen('admin');\n  }"

NEW = "window.addEventListener('DOMContentLoaded', () => {\n  // Always start at home map — clear any stale overlays\n  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));\n  \n  initHomeMap();\n  fetchLiveWeather();\n  loadLiveCorridors();\n  \n  if (window.location.hash === '#admin') {\n    switchScreen('admin');\n  }"

for target in targets:
    p = pathlib.Path(target)
    if not p.exists(): continue
    text = p.read_text(encoding='utf-8')
    if OLD in text:
        text = text.replace(OLD, NEW)
        p.write_text(text, encoding='utf-8')
        print(f"Fixed {p.name}")
    else:
        print(f"Pattern not found in {p.name}")
