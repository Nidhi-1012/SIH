import pathlib
text = pathlib.Path(r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\index.html').read_text(encoding='utf-8')
print('screen-nav present:', 'id="screen-nav"' in text)
print('the-map present:', 'id="the-map"' in text)
