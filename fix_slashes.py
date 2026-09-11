import pathlib

target = r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\index.html'
p = pathlib.Path(target)
text = p.read_text(encoding='utf-8')
text = text.replace('<a href="/login/user"', '<a href="/login/user/"')
text = text.replace('<a href="/login/driver"', '<a href="/login/driver/"')
text = text.replace('<a href="/login/officer"', '<a href="/login/officer/"')
p.write_text(text, encoding='utf-8')
