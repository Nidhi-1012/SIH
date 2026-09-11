import pathlib

targets = [
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\app.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\index_mobile.html',
]

OLD_POLLER = '''/* ---- LIVE ALERTS BACKGROUND POLLER ---- */
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
}'''

NEW_POLLER = '''/* ---- LIVE ALERTS BACKGROUND POLLER & BROWSER NOTIFICATIONS ---- */
let knownAlertIds = new Set();
let isFirstAlertFetch = true;

function triggerBrowserNotification(alertObj) {
  if (!("Notification" in window)) return;
  if (Notification.permission === "granted") {
    const title = alertObj.title || "NER SafeRoute: Live Alert";
    const options = {
      body: alertObj.message || "A new hazard has been verified on your route.",
      icon: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
      vibrate: [200, 100, 200, 100, 200]
    };
    const notif = new Notification(title, options);
    notif.onclick = () => {
      window.focus();
      if (typeof switchScreen === 'function') switchScreen('alerts');
    };
  }
}

async function fetchAlertsBackground() {
  try {
    const res = await fetch('/api/v1/alerts');
    const data = await res.json();
    const badge = document.getElementById('nav-alert-badge');
    
    if (Array.isArray(data)) {
      if (badge) {
        if (data.length > 0) {
          badge.textContent = data.length;
          badge.style.display = 'inline-flex';
        } else {
          badge.style.display = 'none';
        }
      }
      
      // Push notifications for NEW alerts
      if (!isFirstAlertFetch) {
        // Reverse array so oldest new alerts trigger first (though it's usually just 1)
        const reversedData = [...data].reverse();
        for (const a of reversedData) {
          if (!knownAlertIds.has(a.alert_id)) {
            triggerBrowserNotification(a);
            knownAlertIds.add(a.alert_id);
          }
        }
      } else {
        // First load: store existing alerts so we don't spam notifications
        for (const a of data) {
          knownAlertIds.add(a.alert_id);
        }
        isFirstAlertFetch = false;
        
        // Request notification permission if not yet decided
        if ("Notification" in window && Notification.permission === "default") {
          Notification.requestPermission();
        }
      }
    }
  } catch (e) {
    // silently fail in background
  }
}'''

for target in targets:
    p = pathlib.Path(target)
    if not p.exists(): continue
    
    text = p.read_text(encoding='utf-8')
    original = text
    
    if OLD_POLLER in text:
        text = text.replace(OLD_POLLER, NEW_POLLER)
        p.write_text(text, encoding='utf-8')
        print(f"Updated {p.name}")
    else:
        print(f"Old poller not found in {p.name}")
