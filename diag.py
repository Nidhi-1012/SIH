import pathlib
text = pathlib.Path(r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\index.html').read_text(encoding='utf-8')
print("Has root div:", '<div id="root"' in text)
print("Has main.tsx:", 'src/main.tsx' in text)
print("Length:", len(text))
