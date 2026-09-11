import pathlib
text = pathlib.Path(r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\index.html').read_text(encoding='utf-8')
idx = text.find('function renderAdminList')
print(text[idx:idx+2000])
