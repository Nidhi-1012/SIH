import pathlib
text = pathlib.Path(r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\index.html').read_text(encoding='utf-8')
marker = 'id="desk-origin"'
idx = text.find(marker)
if idx > -1:
    print(text[max(0, idx-300):idx+300])
else:
    print("NOT FOUND")
