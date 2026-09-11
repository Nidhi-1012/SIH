import pathlib

target = r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\user\index.html'
p = pathlib.Path(target)
text = p.read_text(encoding='utf-8')

OLD = "  // Always start at home map — clear any stale overlays\n  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));"

NEW = """  // Always start at home map — clear any stale overlays
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));

  // Show Driver Mode badge if navigated from /driver/
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('mode') === 'driver') {
    const badge = document.createElement('div');
    badge.id = 'driver-mode-badge';
    badge.style.cssText = 'position:fixed;top:16px;left:50%;transform:translateX(-50%);z-index:1000;background:#34c759;color:#fff;font-size:12px;font-weight:700;padding:5px 14px;border-radius:20px;box-shadow:0 2px 8px rgba(52,199,89,0.4);pointer-events:none;letter-spacing:0.3px;';
    badge.textContent = '🚚 DRIVER MODE';
    document.body.appendChild(badge);
  }"""

if OLD in text:
    text = text.replace(OLD, NEW)
    p.write_text(text, encoding='utf-8')
    print("Added Driver Mode badge to user app")
else:
    print("Pattern not found")
