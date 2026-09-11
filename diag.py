import pathlib
text = pathlib.Path(r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\user\index.html').read_text(encoding='utf-8')

# Find the actual navbar element - check different possible IDs
for keyword in ['id="topnav"', 'id="nav-bar"', 'id="navbar"', 'id="top-bar"', 'class="topnav"', 'class="navbar"', '<nav ', '<header ']:
    idx = text.find(keyword)
    if idx > -1:
        print(f"Found '{keyword}' at {idx}")
        print(text[max(0,idx-50):idx+200])
        print("---")
