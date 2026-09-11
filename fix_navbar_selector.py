import pathlib

targets = [
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\user\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\app.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\index_mobile.html',
]

# Replace the wrong 'topnav' id references with the correct querySelector
OLD_HIDE_ADMIN = "const tnav = document.getElementById('topnav'); if(tnav) tnav.style.display='none';\n    loadAdminIncidents();"
NEW_HIDE_ADMIN = "const tnav = document.querySelector('.apple-nav') || document.querySelector('header'); if(tnav) tnav.style.display='none';\n    loadAdminIncidents();"

# Also fix the restore on switchScreen home path
OLD_RESTORE = "const tnav = document.getElementById('topnav'); if(tnav) tnav.style.display='';"
NEW_RESTORE = "const tnav = document.querySelector('.apple-nav') || document.querySelector('header'); if(tnav) tnav.style.display='';"

# Also fix the nav screen hide (used for full-screen navigation)
OLD_HIDE_NAV = "const tnav = document.getElementById('topnav'); if(tnav) tnav.style.display='none';\n    const tnav = document.getElementById('topnav'); if("
# That's unlikely to match - let's just grep for all topnav occurrences
for target in targets:
    p = pathlib.Path(target)
    if not p.exists(): continue
    text = p.read_text(encoding='utf-8')
    original = text

    text = text.replace(OLD_HIDE_ADMIN, NEW_HIDE_ADMIN)
    text = text.replace(OLD_RESTORE, NEW_RESTORE)
    # Also fix nav screen hide
    text = text.replace(
        "const tnav = document.getElementById('topnav'); if(tnav) tnav.style.display='none';",
        "const tnav = document.querySelector('.apple-nav') || document.querySelector('header'); if(tnav) tnav.style.display='none';"
    )

    if text != original:
        p.write_text(text, encoding='utf-8')
        print(f"Fixed {p.name}")
    else:
        print(f"No change in {p.name}")
