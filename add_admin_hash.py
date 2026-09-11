import pathlib

target = r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\user\index.html'
p = pathlib.Path(target)
text = p.read_text(encoding='utf-8')

# We need to make the app automatically open #screen-admin if the hash is #admin
OLD = '''window.addEventListener('DOMContentLoaded', () => {
  initHomeMap();
  fetchLiveWeather();
  loadLiveCorridors();'''

NEW = '''window.addEventListener('DOMContentLoaded', () => {
  initHomeMap();
  fetchLiveWeather();
  loadLiveCorridors();
  
  if (window.location.hash === '#admin') {
    switchScreen('admin');
  }
'''

if OLD in text:
    text = text.replace(OLD, NEW)
    p.write_text(text, encoding='utf-8')
    print("Updated app to support #admin deep link")
else:
    print("Could not find DOMContentLoaded")
