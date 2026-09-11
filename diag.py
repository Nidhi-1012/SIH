import pathlib
text = pathlib.Path(r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\index.html').read_text(encoding='utf-8')
idx = text.find('supabaseClient')
print(text[max(0,idx-200):idx+600])
