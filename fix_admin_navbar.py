import pathlib

targets = [
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\user\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\app.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\index_mobile.html',
]

# In switchScreen, when admin is opened, hide the topnav.
# When home is restored, show the topnav again.
OLD_SWITCH = "  } else if (screenName === 'admin') {\n    document.getElementById('screen-admin').classList.add('active');"
NEW_SWITCH = "  } else if (screenName === 'admin') {\n    document.getElementById('screen-admin').classList.add('active');\n    const tnav = document.getElementById('topnav'); if(tnav) tnav.style.display='none';"

# Also restore navbar when switching back to home from admin
OLD_HOME = "function switchScreen(screenName) {\n  ['screen-alerts','screen-report','screen-admin','screen-nav'].forEach(id => {\n    const el = document.getElementById(id);\n    if (el) el.classList.remove('active');\n  });"
NEW_HOME = "function switchScreen(screenName) {\n  ['screen-alerts','screen-report','screen-admin','screen-nav'].forEach(id => {\n    const el = document.getElementById(id);\n    if (el) el.classList.remove('active');\n  });\n  const tnav = document.getElementById('topnav'); if(tnav) tnav.style.display='';"

for target in targets:
    p = pathlib.Path(target)
    if not p.exists(): continue
    text = p.read_text(encoding='utf-8')
    original = text
    
    text = text.replace(OLD_SWITCH, NEW_SWITCH)
    text = text.replace(OLD_HOME, NEW_HOME)
    
    if text != original:
        p.write_text(text, encoding='utf-8')
        print(f"Fixed {p.name}")
    else:
        print(f"No change in {p.name} - checking for alternate pattern...")
        # Try finding switchScreen function and patching after the remove-all block
        idx = text.find("function switchScreen(screenName)")
        if idx > -1:
            print(text[idx:idx+400])
