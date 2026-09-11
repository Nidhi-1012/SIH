import pathlib, re
text = pathlib.Path(r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\index.html').read_text(encoding='utf-8')
for m in re.finditer(r'href="([^"]+)"', text):
    print(m.group(1))
