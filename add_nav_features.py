import pathlib

targets = [
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\app.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\index_mobile.html',
]

OLD_HTML_CARD = '''          <!-- NER SAFEROUTE INTELLIGENCE CARD -->
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
          </div>'''

NEW_HTML_CARD = '''          <!-- NER SAFEROUTE INTELLIGENCE CARD -->
          <div style="background:var(--c-surface);border:1px solid var(--c-border);border-radius:var(--r-md);padding:14px;margin-bottom:12px;box-shadow:var(--shadow-sm);transition:all 0.3s;" id="ns-expandable-card">
            <div style="display:flex;justify-content:space-between;align-items:center;cursor:pointer;" onclick="toggleNavCard()">
              <div style="font-weight:700;font-size:13px;color:var(--c-text);display:flex;align-items:center;gap:6px;">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--c-primary)" stroke-width="2.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                NER SAFEROUTE
              </div>
              <div style="display:flex;align-items:center;gap:8px;">
                <div id="ns-risk-badge" style="background:var(--c-safe-soft);color:var(--c-safe);padding:3px 8px;border-radius:var(--r-pill);font-weight:700;font-size:11px;">
                  Overall Risk: 18% 🟢
                </div>
                <svg id="ns-card-chev" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6"/></svg>
              </div>
            </div>
            
            <div id="ns-card-details" style="display:none;margin-top:12px;padding-top:12px;border-top:1px solid var(--c-border-subtle);">
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:12px;color:var(--c-text-2);margin-bottom:10px;">
                <span id="ns-card-w">🌧 Weather: Clear</span>
                <span id="ns-card-l">🪨 Landslide: 12%</span>
                <span id="ns-card-f">🌊 Flood: 8%</span>
                <span id="ns-card-r">🚧 Road: Clear</span>
              </div>
              <div id="ns-ai-insight" style="font-size:12px;color:var(--c-safe);font-weight:600;display:flex;align-items:center;gap:4px;background:var(--c-bg);padding:8px;border-radius:var(--r-sm);">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
                Safest practical route calculated.
              </div>
            </div>
          </div>
          
          <!-- SAFER ROUTE AVAILABLE POPUP (Hidden by default) -->
          <div id="nav-safer-popup" style="display:none;position:absolute;bottom:240px;left:16px;right:16px;background:#ffffff;border:2px solid var(--c-safe);border-radius:var(--r-md);padding:14px;box-shadow:var(--shadow-lg);z-index:900;">
            <div style="display:flex;align-items:center;gap:8px;font-weight:800;color:var(--c-safe);margin-bottom:6px;">
              ⭐ SAFER ROUTE AVAILABLE
            </div>
            <div style="font-size:13px;color:var(--c-text-2);margin-bottom:12px;">This alternative route has significantly lower disaster risk.</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;font-size:12px;margin-bottom:14px;">
              <div style="background:var(--c-bg);padding:8px;border-radius:var(--r-sm);border:1px solid var(--c-crit);">
                <div style="color:var(--c-text-3);font-size:10px;font-weight:600;margin-bottom:2px;">CURRENT</div>
                <div style="font-weight:700;color:var(--c-crit);">🔴 Risk: 78%</div>
                <div style="color:var(--c-text);">ETA: 2h 10m</div>
              </div>
              <div style="background:var(--c-safe-soft);padding:8px;border-radius:var(--r-sm);border:1px solid var(--c-safe);">
                <div style="color:var(--c-safe);font-size:10px;font-weight:700;margin-bottom:2px;">ALTERNATIVE</div>
                <div style="font-weight:700;color:var(--c-safe);">🟢 Risk: 21%</div>
                <div style="color:var(--c-text);">ETA: 2h 27m</div>
              </div>
            </div>
            <div style="display:flex;gap:10px;">
              <button onclick="document.getElementById('nav-safer-popup').style.display='none'" style="flex:1;padding:10px;background:var(--c-bg);border:none;border-radius:var(--r-sm);font-weight:600;color:var(--c-text-2);">Keep Current</button>
              <button onclick="acceptSaferRoute()" style="flex:1.5;padding:10px;background:var(--c-safe);border:none;border-radius:var(--r-sm);font-weight:700;color:#fff;box-shadow:var(--shadow-sm);">Take Safer Route</button>
            </div>
          </div>'''

OLD_STARTNAV_ROUTING = '''  navRoutingControl = L.Routing.control({
    waypoints: [L.latLng(startPt[0], startPt[1]), L.latLng(endPt[0], endPt[1])],
    routeWhileDragging: false,
    addWaypoints: false,
    showAlternatives: false,
    fitSelectedRoutes: true,
    lineOptions: { styles: [{ color: '#0071e3', opacity: 0.9, weight: 7 }] },'''

NEW_STARTNAV_ROUTING = '''  navRoutingControl = L.Routing.control({
    waypoints: [L.latLng(startPt[0], startPt[1]), L.latLng(endPt[0], endPt[1])],
    routeWhileDragging: false,
    addWaypoints: false,
    showAlternatives: false,
    fitSelectedRoutes: true,
    // Hide default line, we will draw segmented risk lines
    routeLine: function(route) { return L.polyline([], {weight:0}); },'''

OLD_JS_HOOKS = '''    // Initial direction
    if (routes[0].instructions && routes[0].instructions.length > 0) {
      const inst = routes[0].instructions[0];
      document.getElementById('nav-road-txt').textContent = inst.road || 'Proceed to route';
      document.getElementById('nav-dist-txt').textContent = inst.text;
      speakVoice(inst.text);
    }
  });'''

NEW_JS_HOOKS = '''    // Initial direction
    if (routes[0].instructions && routes[0].instructions.length > 0) {
      const inst = routes[0].instructions[0];
      document.getElementById('nav-road-txt').textContent = inst.road || 'Proceed to route';
      document.getElementById('nav-dist-txt').textContent = inst.text;
      if (isFirstRouteLoad) { speakVoice(inst.text); isFirstRouteLoad = false; }
    }
    
    // DRAW RISK-COLORED SEGMENTS
    if (window.navRiskLayers) {
      window.navRiskLayers.forEach(l => navMap.removeLayer(l));
    }
    window.navRiskLayers = [];
    
    const coords = routes[0].coordinates;
    const segments = 4;
    const chunkSize = Math.floor(coords.length / segments);
    
    for (let i = 0; i < segments; i++) {
      const chunk = coords.slice(i * chunkSize, (i===segments-1) ? coords.length : (i+1)*chunkSize + 1);
      
      // Determine segment risk dynamically
      let color = '#34c759'; // Green 0-30%
      let riskVal = Math.floor(Math.random() * 25) + 5;
      let reason = 'Safe segment';
      
      if (navCurrentRoute.overall > 60 && i === 2) {
        color = '#ff3b30'; // Red 81-100%
        riskVal = Math.floor(Math.random() * 15) + 81;
        reason = 'Heavy rainfall, steep terrain, previous landslides';
      } else if (navCurrentRoute.overall > 40 && i === 1) {
        color = '#ff9f0a'; // Orange 61-80%
        riskVal = Math.floor(Math.random() * 20) + 61;
        reason = 'Moderate flood risk due to river overflow';
      } else if (navCurrentRoute.overall > 20 && i === 3) {
        color = '#f1c40f'; // Yellow 31-60%
        riskVal = Math.floor(Math.random() * 30) + 31;
        reason = 'Wet road conditions';
      }

      const pl = L.polyline(chunk, { color: color, weight: 8, opacity: 0.85, lineCap: 'round', lineJoin: 'round' }).addTo(navMap);
      
      // Hazard Information on Tap
      if (riskVal > 30) {
        pl.bindPopup(`
          <div style="font-family:-apple-system,sans-serif;padding:4px;">
            <div style="font-size:10px;font-weight:700;color:var(--c-text-3);margin-bottom:2px;">WHY IS THIS AREA RISKY?</div>
            <div style="font-weight:600;font-size:13px;color:var(--c-text);line-height:1.4;">${reason}</div>
            <div style="margin-top:6px;font-size:12px;font-weight:700;color:${color};">Risk: ${riskVal}%</div>
          </div>
        `);
      }
      window.navRiskLayers.push(pl);
    }
  });'''

JS_ADDITIONS = '''
let isFirstRouteLoad = true;
function toggleNavCard() {
  const el = document.getElementById('ns-card-details');
  const chev = document.getElementById('ns-card-chev');
  if (el.style.display === 'none') {
    el.style.display = 'block';
    chev.style.transform = 'rotate(180deg)';
  } else {
    el.style.display = 'none';
    chev.style.transform = 'rotate(0deg)';
  }
}

function acceptSaferRoute() {
  document.getElementById('nav-safer-popup').style.display='none';
  speakVoice("Rerouting to safer alternative route.");
  // Simulate picking the safer route
  navCurrentRoute.overall = 21;
  document.getElementById('ns-risk-badge').textContent = 'Overall Risk: 21% 🟢';
  document.getElementById('ns-risk-badge').style.background = 'var(--c-safe-soft)';
  document.getElementById('ns-risk-badge').style.color = 'var(--c-safe)';
  document.getElementById('ns-ai-insight').innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg> Safest practical route calculated.`;
  document.getElementById('ns-ai-insight').style.color = 'var(--c-safe)';
  // Force map update
  if (navRoutingControl) {
    const wps = navRoutingControl.getWaypoints();
    navRoutingControl.setWaypoints([wps[0], wps[wps.length-1]]);
  }
}

// Inside the GPS watch interval, simulate Safer Route popup if risk is high
// This replaces the old random hazard logic for better demonstration
'''

for target in targets:
    p = pathlib.Path(target)
    if not p.exists(): continue
    text = p.read_text(encoding='utf-8')
    original = text
    
    text = text.replace(OLD_HTML_CARD, NEW_HTML_CARD)
    text = text.replace(OLD_STARTNAV_ROUTING, NEW_STARTNAV_ROUTING)
    text = text.replace(OLD_JS_HOOKS, NEW_JS_HOOKS)
    
    if 'toggleNavCard()' not in text:
        idx = text.find('function showNavHazardWarning()')
        if idx > -1:
            text = text[:idx] + JS_ADDITIONS + '\n' + text[idx:]
            
        # Hook Safer Route popup trigger into the GPS watcher
        old_gps_hazard = '''        // Randomly simulate hazard warning in demo mode (10% chance per tick)
        if (Math.random() > 0.9 && r.overall > 30) {
          showNavHazardWarning();
        }'''
        new_gps_hazard = '''        // Dynamic Safer Route trigger in demo mode
        if (r.overall > 60 && Math.random() > 0.85 && document.getElementById('nav-safer-popup').style.display === 'none') {
          document.getElementById('nav-safer-popup').style.display = 'block';
          speakVoice("A safer route is available. Tap to accept.");
        } else if (r.overall > 30 && r.overall <= 60 && Math.random() > 0.9) {
          showNavHazardWarning();
        }'''
        text = text.replace(old_gps_hazard, new_gps_hazard)
        
        # Add emoji to risk badge on init
        text = text.replace(
            "document.getElementById('ns-risk-badge').textContent = `Overall Risk: ${r.overall}%`;",
            "const rEmoji = r.overall <= 30 ? '🟢' : (r.overall <= 60 ? '🟡' : '🔴');\n  document.getElementById('ns-risk-badge').textContent = `Overall Risk: ${r.overall}% ${rEmoji}`;"
        )

    if text != original:
        p.write_text(text, encoding='utf-8')
        print(f"Updated {p.name}")
