import pathlib
text = pathlib.Path(r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\index.html').read_text(encoding='utf-8')
idx = text.find('async function fetchAlertsBackground')
print(text[max(0, idx-100):idx+800])
