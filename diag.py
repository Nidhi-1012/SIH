import pathlib
text = pathlib.Path(r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\index.html').read_text(encoding='utf-8')
idx = text.find('function startNav')
if idx > -1:
    print(text[max(0, idx-50):idx+2500])
