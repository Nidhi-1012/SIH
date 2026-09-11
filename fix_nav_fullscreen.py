import pathlib

targets = [
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\app.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\index_mobile.html',
]

# Fix 1: The top navbar (id="topnav") stays visible over the nav screen.
# We need to hide it when screen-nav is active.
OLD_NAV_CSS = '''/* NAVIGATION SCREEN */
#screen-nav { position: fixed !important; inset: 0 !important; z-index: 200 !important; }'''

NEW_NAV_CSS = '''/* NAVIGATION SCREEN */
#screen-nav { position: fixed !important; inset: 0 !important; z-index: 500 !important; background: #fff; }
#screen-nav .leaflet-routing-container { display: none !important; }'''

# Fix 2: When nav screen opens, hide the top navbar
OLD_SWITCH_NAV = "  } else if (screenName === 'nav') {\n    document.getElementById('screen-nav').classList.add('active');"

NEW_SWITCH_NAV = "  } else if (screenName === 'nav') {\n    document.getElementById('screen-nav').classList.add('active');\n    const tnav = document.getElementById('topnav'); if(tnav) tnav.style.display='none';"

# Fix 3: Restore topnav on endNav
OLD_ENDNAV_EXIT = "  switchScreen('home');"

NEW_ENDNAV_EXIT = "  const tnav = document.getElementById('topnav'); if(tnav) tnav.style.display='';\n  switchScreen('home');"

for target in targets:
    p = pathlib.Path(target)
    if not p.exists(): continue
    text = p.read_text(encoding='utf-8')
    original = text
    
    text = text.replace(OLD_NAV_CSS, NEW_NAV_CSS)
    text = text.replace(OLD_SWITCH_NAV, NEW_SWITCH_NAV)
    text = text.replace(OLD_ENDNAV_EXIT, NEW_ENDNAV_EXIT)
    
    if text != original:
        p.write_text(text, encoding='utf-8')
        print(f"Fixed nav screen: {p.name}")
    else:
        print(f"No change: {p.name}")
