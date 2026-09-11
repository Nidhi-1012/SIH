import pathlib

targets = [
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\app.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\index_mobile.html',
]

ALERT_POLLER_SCRIPT = '''
/* ---- LIVE ALERTS BACKGROUND POLLER ---- */
async function fetchAlertsBackground() {
  try {
    const res = await fetch('/api/v1/alerts');
    const data = await res.json();
    const badge = document.getElementById('nav-alert-badge');
    if (badge) {
      if (Array.isArray(data) && data.length > 0) {
        badge.textContent = data.length;
        badge.style.display = 'inline-flex';
      } else {
        badge.style.display = 'none';
      }
    }
  } catch (e) {
    // silently fail in background
  }
}
'''

for target in targets:
    p = pathlib.Path(target)
    if not p.exists(): continue
    
    text = p.read_text(encoding='utf-8')
    original = text
    
    # 1. Remove hardcoded 11
    text = text.replace('id="nav-alert-badge">11</span>', 'id="nav-alert-badge" style="display:none;">0</span>')
    
    # 2. Add background poller script before the closing script tag
    if 'fetchAlertsBackground' not in text:
        idx = text.rfind('</script>')
        text = text[:idx] + ALERT_POLLER_SCRIPT + '\n' + text[idx:]
        
    # 3. Add to DOMContentLoaded
    if 'fetchAlertsBackground();' not in text:
        init_hook = text.find('setInterval(fetchLiveWeather, 60000);')
        if init_hook > -1:
            text = text[:init_hook] + 'fetchAlertsBackground();\n  setInterval(fetchAlertsBackground, 15000);\n  ' + text[init_hook:]
            
    if text != original:
        p.write_text(text, encoding='utf-8')
        print(f"Updated {p.name}")
    else:
        print(f"No changes for {p.name}")
