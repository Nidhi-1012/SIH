import pathlib

targets = [
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\app.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\index_mobile.html',
]

OLD_NAV_HTML = '''    <!-- SCREEN: LIVE CORRIDOR NAV WITH TURN-BY-TURN -->
    <div class="screen" id="screen-nav">
      <div class="nav-map-wrap">
        <div id="nav-map"></div>

        <div class="nav-top-overlay">
          <div class="nav-card">
            <div class="nav-arrow-box">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="19" x2="12" y2="5"/>
                <polyline points="5 12 12 5 19 12"/>
              </svg>
            </div>
            <div>
              <div style="font-size:17px;font-weight:700;" id="nav-dist-txt">3.2 km</div>
              <div style="font-size:12.5px;opacity:0.85;" id="nav-road-txt">Continue on NH-6 Safe Corridor</div>
            </div>
          </div>
        </div>

        <div class="nav-bottom-overlay">
          <div class="nav-stats">
            <div><div class="ns-val" id="ns-eta">2h 15m</div><div class="ns-lbl">Estimated Arrival</div></div>
            <div><div class="ns-val" id="ns-dist">96 km</div><div class="ns-lbl">Remaining</div></div>
            <div><div class="ns-val" id="ns-risk" style="color:var(--c-safe)">18%</div><div class="ns-lbl">Safety Risk</div></div>
          </div>
          <div style="display:flex;gap:10px;">
            <button class="btn-analyze-route" style="background:rgba(0,0,0,0.08);color:var(--c-text);" onclick="endNav()">Exit Navigation</button>
            <button class="btn-analyze-route" style="background:var(--c-crit);" onclick="openSOS()">Emergency SOS</button>
          </div>
        </div>
      </div>
    </div>'''

NEW_NAV_HTML = '''    <!-- SCREEN: LIVE CORRIDOR NAV WITH TURN-BY-TURN -->
    <div class="screen" id="screen-nav">
      <div class="nav-map-wrap">
        <div id="nav-map"></div>

        <!-- HAZARD WARNING OVERLAY (Hidden by default) -->
        <div id="nav-hazard-warning" style="display:none;position:absolute;top:100px;left:16px;right:16px;background:var(--c-crit);color:#fff;border-radius:var(--r-md);padding:14px;box-shadow:var(--shadow-lg);z-index:900;">
          <div style="display:flex;align-items:center;gap:10px;font-weight:700;font-size:16px;margin-bottom:6px;">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            <span id="nav-hw-title">CAUTION: Landslide-risk zone ahead</span>
          </div>
          <div style="font-size:13.5px;opacity:0.95;margin-bottom:10px;" id="nav-hw-desc">Heavy rainfall and steep terrain are increasing the risk. (1.8 km ahead)</div>
          <button onclick="document.getElementById('nav-hazard-warning').style.display='none'" style="width:100%;padding:8px;background:rgba(0,0,0,0.2);border:none;color:#fff;border-radius:var(--r-sm);font-weight:600;">Dismiss</button>
        </div>

        <div class="nav-top-overlay">
          <div class="nav-card" style="background:var(--c-safe);color:#fff;border:none;">
            <div class="nav-arrow-box" style="background:rgba(0,0,0,0.15);" id="nav-turn-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="19" x2="12" y2="5"/>
                <polyline points="5 12 12 5 19 12"/>
              </svg>
            </div>
            <div style="flex:1;">
              <div style="font-size:19px;font-weight:700;" id="nav-dist-txt">Detecting...</div>
              <div style="font-size:14px;opacity:0.95;" id="nav-road-txt">Calculating safest route</div>
            </div>
            <button onclick="toggleNavVoice()" id="nav-voice-btn" style="background:none;border:none;color:#fff;padding:8px;cursor:pointer;">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>
            </button>
          </div>
        </div>

        <!-- RECENTER BUTTON -->
        <button onclick="recenterNavMap()" style="position:absolute;bottom:260px;right:16px;z-index:800;width:44px;height:44px;background:#fff;border-radius:22px;border:none;box-shadow:var(--shadow-md);display:flex;align-items:center;justify-content:center;cursor:pointer;">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--c-primary)" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="3"/></svg>
        </button>

        <div class="nav-bottom-overlay" style="padding-bottom:calc(env(safe-area-inset-bottom, 0px) + 16px);">
          
          <!-- NER SAFEROUTE INTELLIGENCE CARD -->
          <div style="background:var(--c-surface);border:1px solid var(--c-border);border-radius:var(--r-md);padding:14px;margin-bottom:12px;box-shadow:var(--shadow-sm);">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
              <div style="font-weight:700;font-size:13px;color:var(--c-text);display:flex;align-items:center;gap:6px;">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--c-primary)" stroke-width="2.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                NER SAFEROUTE
              </div>
              <div id="ns-risk-badge" style="background:var(--c-safe-soft);color:var(--c-safe);padding:3px 8px;border-radius:var(--r-pill);font-weight:700;font-size:11px;">
                Overall Risk: 18%
              </div>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:11.5px;color:var(--c-text-2);margin-bottom:6px;">
              <span>🌧 Weather: Low</span>
              <span>🪨 Landslide: 12%</span>
              <span>🌊 Flood: 8%</span>
            </div>
            <div id="ns-ai-insight" style="font-size:12px;color:var(--c-safe);font-weight:600;display:flex;align-items:center;gap:4px;">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
              No major hazards ahead on this segment.
            </div>
          </div>

          <div class="nav-stats">
            <div><div class="ns-val" id="ns-eta" style="color:var(--c-safe);">--:--</div><div class="ns-lbl">Arrival</div></div>
            <div><div class="ns-val" id="ns-dist">-- km</div><div class="ns-lbl">Distance</div></div>
            <div><div class="ns-val" id="ns-time">-- min</div><div class="ns-lbl">Time</div></div>
          </div>
          
          <div style="display:flex;gap:10px;">
            <button class="btn-analyze-route" style="background:rgba(0,0,0,0.06);color:var(--c-text);" onclick="endNav()">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              Exit
            </button>
            <button class="btn-analyze-route" style="background:var(--c-crit);" onclick="openSOS()">
              🆘 SOS / Report
            </button>
          </div>
        </div>
      </div>
    </div>'''

OLD_STARTNAV = '''/* ---- TURN-BY-TURN NAVIGATION (FREE OSRM INTEGRATION) ---- */
function startNav(r) {
  switchScreen('nav');

  if (!navMap) {
    navMap = L.map('nav-map', { zoomControl: false }).setView([pos.lat, pos.lon], 12);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(navMap);
  } else {
    setTimeout(() => navMap.invalidateSize(), 150);
  }

  if (r.pts && r.pts.length > 0) {
    if (navRoutingControl) {
      navMap.removeControl(navRoutingControl);
      navRoutingControl = null;
    }

    const startPt = r.pts[0];
    const endPt = r.pts[r.pts.length - 1];

    navRoutingControl = L.Routing.control({
      waypoints: [L.latLng(startPt[0], startPt[1]), L.latLng(endPt[0], endPt[1])],
      routeWhileDragging: false,
      addWaypoints: false,
      fitSelectedRoutes: true,
      showAlternatives: false,
      lineOptions: { styles: [{ color: '#0071e3', opacity: 0.85, weight: 6 }] },
      createMarker: function() { return null; }
    }).addTo(navMap);
  }

  document.getElementById('ns-eta').textContent = r.time;
  document.getElementById('ns-dist').textContent = r.dist;
  document.getElementById('ns-risk').textContent = `${r.overall}%`;
  document.getElementById('ns-risk').style.color = r.overall <= 30 ? 'var(--c-safe)' : (r.overall <= 60 ? 'var(--c-warn)' : 'var(--c-crit)');
}

function endNav() {
  if (navRoutingControl && navMap) {
    navMap.removeControl(navRoutingControl);
    navRoutingControl = null;
  }
  switchScreen('home');
}'''

NEW_STARTNAV = '''/* ---- GOOGLE MAPS STYLE LIVE TURN-BY-TURN NAVIGATION ---- */
let navWatchId = null;
let navCurrentRoute = null;
let navVoiceEnabled = true;

function toggleNavVoice() {
  navVoiceEnabled = !navVoiceEnabled;
  const btn = document.getElementById('nav-voice-btn');
  if (navVoiceEnabled) {
    btn.innerHTML = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>';
    speakVoice("Voice navigation enabled");
  } else {
    btn.innerHTML = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><line x1="23" y1="9" x2="17" y2="15"/><line x1="17" y1="9" x2="23" y2="15"/></svg>';
  }
}

function speakVoice(text) {
  if (!navVoiceEnabled || !('speechSynthesis' in window)) return;
  const u = new SpeechSynthesisUtterance(text);
  u.rate = 1.0;
  window.speechSynthesis.speak(u);
}

function startNav(r) {
  switchScreen('nav');
  navCurrentRoute = r;

  // Init Map
  if (!navMap) {
    navMap = L.map('nav-map', { zoomControl: false }).setView([pos.lat, pos.lon], 16);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(navMap);
  } else {
    setTimeout(() => navMap.invalidateSize(), 150);
  }

  // Clear previous route
  if (navRoutingControl) {
    navMap.removeControl(navRoutingControl);
    navRoutingControl = null;
  }

  // Populate NER SafeRoute intelligence from the chosen route
  document.getElementById('ns-risk-badge').textContent = `Overall Risk: ${r.overall}%`;
  const badgeColor = r.overall <= 30 ? 'var(--c-safe)' : (r.overall <= 60 ? 'var(--c-warn)' : 'var(--c-crit)');
  const badgeBg = r.overall <= 30 ? 'var(--c-safe-soft)' : (r.overall <= 60 ? 'var(--c-warn-soft)' : 'var(--c-crit-soft)');
  document.getElementById('ns-risk-badge').style.color = badgeColor;
  document.getElementById('ns-risk-badge').style.background = badgeBg;
  
  if (r.overall > 60) {
    document.getElementById('ns-ai-insight').innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg> High hazard probability on this route. Drive carefully.`;
    document.getElementById('ns-ai-insight').style.color = 'var(--c-crit)';
  } else {
    document.getElementById('ns-ai-insight').innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg> Safest calculated segment ahead.`;
    document.getElementById('ns-ai-insight').style.color = 'var(--c-safe)';
  }

  // Setup Routing Control (OSRM)
  const startPt = r.pts[0];
  const endPt = r.pts[r.pts.length - 1];
  
  navRoutingControl = L.Routing.control({
    waypoints: [L.latLng(startPt[0], startPt[1]), L.latLng(endPt[0], endPt[1])],
    routeWhileDragging: false,
    addWaypoints: false,
    showAlternatives: false,
    fitSelectedRoutes: true,
    lineOptions: { styles: [{ color: '#0071e3', opacity: 0.9, weight: 7 }] },
    createMarker: function(i, wp, n) {
      if (i===0) { // user marker
        return L.circleMarker(wp.latLng, { radius:8, fillColor:'#0071e3', color:'#fff', weight:3, fillOpacity:1 });
      } else if (i===n-1) { // destination
        return L.marker(wp.latLng);
      }
      return null;
    }
  }).addTo(navMap);

  // Hook into routing events to update directions
  navRoutingControl.on('routesfound', function(e) {
    const routes = e.routes;
    const summary = routes[0].summary;
    
    // Update bottom stats
    document.getElementById('ns-dist').textContent = (summary.totalDistance / 1000).toFixed(1) + ' km';
    const totalMin = Math.round(summary.totalTime / 60);
    document.getElementById('ns-time').textContent = totalMin + ' min';
    
    const arrival = new Date(Date.now() + summary.totalTime * 1000);
    document.getElementById('ns-eta').textContent = arrival.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});

    // Initial direction
    if (routes[0].instructions && routes[0].instructions.length > 0) {
      const inst = routes[0].instructions[0];
      document.getElementById('nav-road-txt').textContent = inst.road || 'Proceed to route';
      document.getElementById('nav-dist-txt').textContent = inst.text;
      speakVoice(inst.text);
    }
  });

  // Start live GPS tracking
  if (navigator.geolocation) {
    navWatchId = navigator.geolocation.watchPosition(
      (posUpdate) => {
        const lat = posUpdate.coords.latitude;
        const lon = posUpdate.coords.longitude;
        // Update user marker (waypoint 0)
        const currentWps = navRoutingControl.getWaypoints();
        currentWps[0] = L.latLng(lat, lon);
        navRoutingControl.setWaypoints(currentWps); // Triggers recalculation dynamically if moved
        navMap.setView([lat, lon], 17, { animate: true });
        
        // Randomly simulate hazard warning in demo mode (10% chance per tick)
        if (Math.random() > 0.9 && r.overall > 30) {
          showNavHazardWarning();
        }
      },
      (err) => console.warn('GPS watch error', err),
      { enableHighAccuracy: true, maximumAge: 0, timeout: 5000 }
    );
  }
}

function showNavHazardWarning() {
  const el = document.getElementById('nav-hazard-warning');
  if (el.style.display === 'none') {
    el.style.display = 'block';
    speakVoice("Warning. Potential hazard detected ahead.");
    setTimeout(() => el.style.display = 'none', 8000);
  }
}

function recenterNavMap() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(p => {
      navMap.setView([p.coords.latitude, p.coords.longitude], 17, { animate: true });
    });
  }
}

function endNav() {
  if (navWatchId !== null) {
    navigator.geolocation.clearWatch(navWatchId);
    navWatchId = null;
  }
  if (navRoutingControl && navMap) {
    navMap.removeControl(navRoutingControl);
    navRoutingControl = null;
  }
  switchScreen('home');
}'''

for target in targets:
    p = pathlib.Path(target)
    if not p.exists(): continue
    text = p.read_text(encoding='utf-8')
    original = text
    
    text = text.replace(OLD_NAV_HTML, NEW_NAV_HTML)
    text = text.replace(OLD_STARTNAV, NEW_STARTNAV)
    
    if text != original:
        p.write_text(text, encoding='utf-8')
        print(f"Updated {p.name}")
    else:
        print(f"No changes in {p.name}")
