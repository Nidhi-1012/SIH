import pathlib

targets = [
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\user\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\app.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\index_mobile.html',
]

for target in targets:
    p = pathlib.Path(target)
    if not p.exists(): continue
    text = p.read_text(encoding='utf-8')
    # Ensure the #admin deep-link auto-open is present
    if "window.location.hash === '#admin'" not in text:
        OLD = "  initHomeMap();\n  fetchLiveWeather();\n  loadLiveCorridors();"
        NEW = "  if (window.location.hash === '#admin') {\n    switchScreen('admin');\n  }\n\n  initHomeMap();\n  fetchLiveWeather();\n  loadLiveCorridors();"
        if OLD in text:
            text = text.replace(OLD, NEW)
            p.write_text(text, encoding='utf-8')
            print(f"Added #admin deep link to {p.name}")
        else:
            print(f"Could not add deep link to {p.name}")
    else:
        print(f"{p.name} already has #admin deep link")
