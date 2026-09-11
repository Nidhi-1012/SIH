import pathlib

targets = [
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\app.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\index_mobile.html',
]

OLD_ORIGIN_HTML = '''        <div class="input-group">
          <div class="pin-origin"></div>
          <input id="desk-origin" type="text" placeholder="Your Location"/>
        </div>'''

NEW_ORIGIN_HTML = '''        <div class="input-group" style="position:relative;">
          <div class="pin-origin"></div>
          <input id="desk-origin" type="text" placeholder="Your Location" autocomplete="off"
            onfocus="showOriginDropdown()" onblur="hideOriginDropdown()" oninput="hideOriginDropdown()"/>
          <!-- Current Location dropdown -->
          <div id="origin-dropdown" style="
            display:none;
            position:absolute;
            top:calc(100% + 4px);
            left:0; right:0;
            background:#ffffff;
            border:1px solid var(--c-border);
            border-radius:var(--r-md);
            box-shadow:0 8px 24px rgba(0,0,0,0.10);
            z-index:200;
            overflow:hidden;
          ">
            <button
              onmousedown="useCurrentLocationAsOrigin(event)"
              style="display:flex;align-items:center;gap:10px;width:100%;padding:12px 14px;background:none;border:none;cursor:pointer;text-align:left;font-family:inherit;font-size:13px;color:var(--c-primary);font-weight:600;"
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 1v4M12 19v4M1 12h4M19 12h4"/></svg>
              Use Current Location
            </button>
          </div>
        </div>'''

ORIGIN_JS = '''
/* ---- ORIGIN CURRENT LOCATION HELPER ---- */
function showOriginDropdown() {
  const el = document.getElementById('origin-dropdown');
  if (el) el.style.display = 'block';
}
function hideOriginDropdown() {
  setTimeout(() => {
    const el = document.getElementById('origin-dropdown');
    if (el) el.style.display = 'none';
  }, 150);
}
function useCurrentLocationAsOrigin(e) {
  if (e) e.preventDefault();
  const input = document.getElementById('desk-origin');
  if (input) {
    input.value = 'Detecting...';
    input.disabled = true;
  }
  const el = document.getElementById('origin-dropdown');
  if (el) el.style.display = 'none';
  
  if (!navigator.geolocation) {
    if (input) { input.value = ''; input.disabled = false; input.placeholder = 'GPS not supported'; }
    return;
  }
  navigator.geolocation.getCurrentPosition(
    (gpos) => {
      const lat = gpos.coords.latitude.toFixed(5);
      const lon = gpos.coords.longitude.toFixed(5);
      if (input) {
        input.value = `${lat}, ${lon}`;
        input.disabled = false;
      }
      // Also update the global pos used by route finder
      if (typeof pos !== 'undefined') {
        pos.lat = gpos.coords.latitude;
        pos.lon = gpos.coords.longitude;
      }
      showToast('Current location detected!');
    },
    () => {
      if (input) { input.value = ''; input.disabled = false; input.placeholder = 'Could not detect location'; }
      showToast('GPS access denied — please type your location.');
    },
    { enableHighAccuracy: true, timeout: 8000 }
  );
}
'''

for target in targets:
    p = pathlib.Path(target)
    if not p.exists(): continue

    text = p.read_text(encoding='utf-8')
    original = text

    # Replace old origin input
    if OLD_ORIGIN_HTML in text:
        text = text.replace(OLD_ORIGIN_HTML, NEW_ORIGIN_HTML)

    # Inject JS before closing </script>
    if 'useCurrentLocationAsOrigin' not in text:
        idx = text.rfind('</script>')
        if idx > -1:
            text = text[:idx] + ORIGIN_JS + '\n' + text[idx:]

    if text != original:
        p.write_text(text, encoding='utf-8')
        print(f"Updated {p.name}")
    else:
        print(f"No changes in {p.name}")
