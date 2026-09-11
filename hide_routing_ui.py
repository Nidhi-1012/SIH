import pathlib

targets = [
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\app.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\index_mobile.html',
]

OLD_STYLE = '''/* =============================================================
   APPLE HUMAN INTERFACE SYSTEM TOKENS
============================================================= */'''

NEW_STYLE = '''/* =============================================================
   APPLE HUMAN INTERFACE SYSTEM TOKENS
============================================================= */
/* Overrides for cleaner Nav UI */
.leaflet-routing-container { display: none !important; }
'''

for target in targets:
    p = pathlib.Path(target)
    if not p.exists(): continue
    text = p.read_text(encoding='utf-8')
    if '.leaflet-routing-container' not in text:
        text = text.replace(OLD_STYLE, NEW_STYLE)
        p.write_text(text, encoding='utf-8')
        print(f"Updated CSS {p.name}")
