import pathlib

targets = [
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\app.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\index_mobile.html',
]

OLD_SCREEN = '''    <!-- REPORT HAZARD SCREEN (OVERLAY) -->
    <div class="screen" id="screen-report">
      <div class="inner-hdr">
        <button class="back-btn" onclick="switchScreen('home')">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
        </button>
        <div>
          <div class="inner-hdr-title">Report Road Hazard</div>
          <div class="inner-hdr-sub">Instant GPS Snapping to Highway Segment</div>
        </div>
      </div>
      <div class="scrollable-body">
        <div class="card-title">Select Hazard Type</div>
        <div class="hazard-grid">
          <button class="hz-btn sel" onclick="pickHazard(this,'Landslide')">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m8 3 4 8 5-5 5 15H2L8 3z"/></svg>
            <span>Landslide / Rockfall</span>
          </button>
          <button class="hz-btn" onclick="pickHazard(this,'Flash Flood')">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12h20M2 16h20M2 20h20"/></svg>
            <span>Waterlogging / Flood</span>
          </button>
          <button class="hz-btn" onclick="pickHazard(this,'Road Blocked')">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="m9 9 6 6m0-6-6 6"/></svg>
            <span>Road Blocked</span>
          </button>
          <button class="hz-btn" onclick="pickHazard(this,'Bridge Collapse')">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19V5M20 19V5M4 12h16M4 8l16 8M4 16l16-8"/></svg>
            <span>Bridge / Culvert Issue</span>
          </button>
        </div>

        <div class="card-title" style="margin-top:12px;">Notes / Observations</div>
        <textarea id="report-note" style="background:var(--c-surface);border:1px solid var(--c-border);border-radius:var(--r-md);padding:12px;font-size:13.5px;min-height:90px;resize:none;width:100%;color:var(--c-text);" placeholder="Describe current road passability, estimated delay, or landmarks..."></textarea>

        <button class="btn-analyze-route" style="background:var(--c-crit);margin-top:10px;" onclick="submitReport()">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>
          <span>Submit Verified Field Report</span>
        </button>
      </div>
    </div>'''

NEW_SCREEN = '''    <!-- REPORT HAZARD SCREEN (OVERLAY) -->
    <div class="screen" id="screen-report">
      <div class="inner-hdr">
        <button class="back-btn" onclick="switchScreen('home')">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
        </button>
        <div>
          <div class="inner-hdr-title">Report Road Hazard</div>
          <div class="inner-hdr-sub">Instant GPS Snapping to Highway Segment</div>
        </div>
      </div>
      <div class="scrollable-body">

        <!-- HAZARD TYPE -->
        <div class="card-title">Select Hazard Type</div>
        <div class="hazard-grid">
          <button class="hz-btn sel" onclick="pickHazard(this,'Landslide')">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m8 3 4 8 5-5 5 15H2L8 3z"/></svg>
            <span>Landslide / Rockfall</span>
          </button>
          <button class="hz-btn" onclick="pickHazard(this,'Flash Flood')">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12h20M2 16h20M2 20h20"/></svg>
            <span>Waterlogging / Flood</span>
          </button>
          <button class="hz-btn" onclick="pickHazard(this,'Road Blocked')">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="m9 9 6 6m0-6-6 6"/></svg>
            <span>Road Blocked</span>
          </button>
          <button class="hz-btn" onclick="pickHazard(this,'Bridge Collapse')">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19V5M20 19V5M4 12h16M4 8l16 8M4 16l16-8"/></svg>
            <span>Bridge / Culvert Issue</span>
          </button>
        </div>

        <!-- LOCATION -->
        <div class="card-title" style="margin-top:14px;">Location</div>
        <div id="report-location-box" style="display:flex;align-items:center;gap:10px;background:var(--c-surface);border:1px solid var(--c-border);border-radius:var(--r-md);padding:11px 14px;">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--c-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
          <span id="report-loc-text" style="font-size:13px;color:var(--c-text-2);flex:1;">Detecting your GPS location...</span>
          <button onclick="detectReportLocation()" style="font-size:11px;font-weight:600;color:var(--c-primary);background:none;border:none;cursor:pointer;white-space:nowrap;">
            Refresh
          </button>
        </div>

        <!-- PHOTO UPLOAD -->
        <div class="card-title" style="margin-top:14px;">Add Photo Evidence</div>
        <label id="photo-upload-label" style="display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;background:var(--c-surface);border:1.5px dashed var(--c-border);border-radius:var(--r-md);padding:18px;cursor:pointer;min-height:90px;transition:border-color .2s;" onclick="document.getElementById('report-photo-input').click()">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--c-text-3)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3Z"/><circle cx="12" cy="13" r="3"/></svg>
          <span id="photo-label-text" style="font-size:12px;color:var(--c-text-3);">Tap to take photo or choose from gallery</span>
        </label>
        <input type="file" id="report-photo-input" accept="image/*" capture="environment" style="display:none;" onchange="handlePhotoSelect(this)"/>
        <div id="report-photo-preview" style="display:none;margin-top:8px;border-radius:var(--r-md);overflow:hidden;border:1px solid var(--c-border);">
          <img id="preview-img" style="width:100%;max-height:180px;object-fit:cover;display:block;"/>
          <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:var(--c-surface);">
            <span style="font-size:11px;color:var(--c-text-2);">Photo attached</span>
            <button onclick="clearPhoto()" style="font-size:11px;color:var(--c-crit);background:none;border:none;cursor:pointer;font-weight:600;">Remove</button>
          </div>
        </div>

        <!-- NOTES -->
        <div class="card-title" style="margin-top:14px;">Notes / Observations</div>
        <textarea id="report-note" style="background:var(--c-surface);border:1px solid var(--c-border);border-radius:var(--r-md);padding:12px;font-size:13px;min-height:80px;resize:none;width:100%;color:var(--c-text);" placeholder="Describe current road passability, estimated delay, or landmarks..."></textarea>

        <button class="btn-analyze-route" style="background:var(--c-crit);margin-top:12px;" onclick="submitReport()">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>
          <span>Submit Verified Field Report</span>
        </button>
      </div>
    </div>'''

# JS additions for photo and location
OLD_SUBMIT = '''async function submitReport() {
  const note = document.getElementById('report-note').value.trim();
  showToast('Submitting verified report with GPS coordinates...');
  try {
    await fetch('/api/v1/incidents', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        incident_type: selHazard,
        severity: 'High',
        notes: note || `${selHazard} reported on active corridor`,
        lat: pos.lat,
        lon: pos.lon
      })
    });
  } catch (e) {}
  setTimeout(() => {
    showToast('Report submitted! Snapped to nearest highway segment.');
    switchScreen('home');
    document.getElementById('report-note').value = '';
  }, 600);
}'''

NEW_SUBMIT = '''/* ---- REPORT: Location & Photo helpers ---- */
let reportLat = null;
let reportLon = null;
let reportPhotoBase64 = null;

function detectReportLocation() {
  const el = document.getElementById('report-loc-text');
  if (!el) return;
  el.textContent = 'Detecting...';
  el.style.color = 'var(--c-text-2)';
  if (!navigator.geolocation) {
    el.textContent = 'GPS not supported on this device.';
    return;
  }
  navigator.geolocation.getCurrentPosition(
    (gpos) => {
      reportLat = gpos.coords.latitude;
      reportLon = gpos.coords.longitude;
      el.textContent = `${reportLat.toFixed(5)}, ${reportLon.toFixed(5)}  (Accuracy: ${Math.round(gpos.coords.accuracy)}m)`;
      el.style.color = 'var(--c-safe)';
    },
    () => {
      // Fallback to map center
      reportLat = pos.lat;
      reportLon = pos.lon;
      el.textContent = `${reportLat.toFixed(5)}, ${reportLon.toFixed(5)}  (map center)`;
      el.style.color = 'var(--c-warn)';
    },
    { enableHighAccuracy: true, timeout: 8000 }
  );
}

function handlePhotoSelect(input) {
  if (!input.files || !input.files[0]) return;
  const file = input.files[0];
  const reader = new FileReader();
  reader.onload = (e) => {
    reportPhotoBase64 = e.target.result;
    document.getElementById('preview-img').src = e.target.result;
    document.getElementById('report-photo-preview').style.display = 'block';
    document.getElementById('photo-label-text').textContent = file.name;
    document.getElementById('photo-upload-label').style.borderColor = 'var(--c-primary)';
  };
  reader.readAsDataURL(file);
}

function clearPhoto() {
  reportPhotoBase64 = null;
  document.getElementById('report-photo-input').value = '';
  document.getElementById('report-photo-preview').style.display = 'none';
  document.getElementById('photo-label-text').textContent = 'Tap to take photo or choose from gallery';
  document.getElementById('photo-upload-label').style.borderColor = 'var(--c-border)';
}

// Auto-detect location when report screen opens
const _origSwitchScreen = typeof switchScreen !== 'undefined' ? switchScreen : null;

async function submitReport() {
  const note = document.getElementById('report-note').value.trim();
  const lat = reportLat || pos.lat;
  const lon = reportLon || pos.lon;
  showToast('Submitting verified report with GPS coordinates...');
  try {
    await fetch('/api/v1/incidents', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        incident_type: selHazard,
        severity: 'High',
        notes: note || `${selHazard} reported on active corridor`,
        lat: lat,
        lon: lon,
        photo_url: reportPhotoBase64 ? '[photo attached]' : null,
        reporter: 'Citizen Field Reporter'
      })
    });
  } catch (e) {}
  setTimeout(() => {
    showToast('Report submitted! Pending admin verification.');
    switchScreen('home');
    document.getElementById('report-note').value = '';
    clearPhoto();
  }, 600);
}'''

# Also patch switchScreen to auto-detect location when opening report screen
OLD_SWITCH_REPORT = "  } else if (screenName === 'report') {\n    document.getElementById('screen-report').classList.add('active');"
NEW_SWITCH_REPORT = "  } else if (screenName === 'report') {\n    document.getElementById('screen-report').classList.add('active');\n    setTimeout(detectReportLocation, 200);"

for target in targets:
    p = pathlib.Path(target)
    if not p.exists():
        print(f"SKIP: {p.name}")
        continue

    text = p.read_text(encoding='utf-8')
    original = text

    # Replace old screen with new screen
    if OLD_SCREEN in text:
        text = text.replace(OLD_SCREEN, NEW_SCREEN)
    
    # Replace old submitReport with new version
    if OLD_SUBMIT in text:
        text = text.replace(OLD_SUBMIT, NEW_SUBMIT)
    
    # Patch switchScreen to detect location on open
    if OLD_SWITCH_REPORT in text:
        text = text.replace(OLD_SWITCH_REPORT, NEW_SWITCH_REPORT)

    if text != original:
        p.write_text(text, encoding='utf-8')
        print(f"Updated: {p.name}")
    else:
        print(f"No change: {p.name}")
