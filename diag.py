import pathlib, sys
sys.stdout.reconfigure(encoding='utf-8')
text = pathlib.Path(r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\index.html').read_text(encoding='utf-8')

idx = text.find('function findRoutes')
snippet = text[idx:idx+3000]
pathlib.Path(r'C:\Users\hp\OneDrive\Desktop\SIH\diag_out.txt').write_text(snippet, encoding='utf-8')
print("Done")
