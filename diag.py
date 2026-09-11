import pathlib
text = pathlib.Path(r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\index.html').read_text(encoding='utf-8')
idx = text.find('navRoutingControl = L.Routing.control({')
if idx > -1:
    print(text[max(0, idx-100):idx+800])
