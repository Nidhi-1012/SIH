import pathlib

targets = [
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\app.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\index_mobile.html',
]

# Add auto-refresh for admin portal: poll every 10s when admin screen is active
auto_refresh_snippet = '''
/* ---- ADMIN PANEL AUTO-REFRESH ---- */
let adminPollTimer = null;
function startAdminPoll() {
  stopAdminPoll();
  adminPollTimer = setInterval(() => {
    if (document.getElementById('screen-admin') &&
        document.getElementById('screen-admin').classList.contains('active')) {
      loadAdminIncidents();
    }
  }, 10000); // refresh every 10 seconds
}
function stopAdminPoll() {
  if (adminPollTimer) { clearInterval(adminPollTimer); adminPollTimer = null; }
}
'''

# Modify switchScreen to start/stop poll
old_switch_part = "  } else if (screenName === 'admin') {\n    document.getElementById('screen-admin').classList.add('active');\n    loadAdminIncidents();"
new_switch_part = "  } else if (screenName === 'admin') {\n    document.getElementById('screen-admin').classList.add('active');\n    loadAdminIncidents();\n    startAdminPoll();"

# Also stop poll when leaving admin
old_remove = "  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));"
new_remove = "  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));\n  stopAdminPoll();"

for target in targets:
    p = pathlib.Path(target)
    if not p.exists():
        print(f"SKIP: {p.name}")
        continue
    
    text = p.read_text(encoding='utf-8')
    original = text
    
    # Add auto-refresh snippet if not already present
    if 'adminPollTimer' not in text:
        # Insert before the closing </script> tag
        idx = text.rfind('</script>')
        if idx > -1:
            text = text[:idx] + auto_refresh_snippet + '\n' + text[idx:]
    
    # Patch switchScreen to start poll
    if old_switch_part in text:
        text = text.replace(old_switch_part, new_switch_part)
    
    # Patch switchScreen to stop poll when leaving
    if old_remove in text and 'stopAdminPoll()' not in text:
        text = text.replace(old_remove, new_remove)
    
    if text != original:
        p.write_text(text, encoding='utf-8')
        print(f"Updated: {p.name}")
    else:
        print(f"Already up-to-date: {p.name}")
