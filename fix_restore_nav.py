import pathlib

targets = [
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\user\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\app.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\index_mobile.html',
]

# The exact start of switchScreen function — first line clears all screens
OLD = "function switchScreen(screenName) {\n  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));"
NEW = "function switchScreen(screenName) {\n  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));\n  // Always restore navbar first; only admin/nav screens will hide it below\n  const _tnav = document.querySelector('.apple-nav') || document.querySelector('header'); if(_tnav) _tnav.style.display='';"

for target in targets:
    p = pathlib.Path(target)
    if not p.exists(): continue
    text = p.read_text(encoding='utf-8')
    if OLD in text and '// Always restore navbar first' not in text:
        text = text.replace(OLD, NEW)
        p.write_text(text, encoding='utf-8')
        print(f"Fixed {p.name}")
    else:
        print(f"Skipped {p.name} - already patched or pattern mismatch")
