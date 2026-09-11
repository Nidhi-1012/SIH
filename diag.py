import pathlib

targets = [
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\user\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\app.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\index_mobile.html',
]

# The admin screen currently is a full-overlay screen (.screen.active = display:flex)
# but we also need to give it a proper admin-styled header instead of the topnav.
# Check current admin screen header
target = targets[0]
p = pathlib.Path(target)
text = p.read_text(encoding='utf-8')
idx = text.find('id="screen-admin"')
print(text[idx:idx+1500])
