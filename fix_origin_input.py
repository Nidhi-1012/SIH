import pathlib

targets = [
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\app.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\index_mobile.html',
]

for target in targets:
    p = pathlib.Path(target)
    if not p.exists(): continue
    
    text = p.read_text(encoding='utf-8')
    original = text
    
    # Remove default value from desk-origin
    text = text.replace(
        '<input id="desk-origin" type="text" placeholder="Your Location" value="Guwahati, Assam"/>',
        '<input id="desk-origin" type="text" placeholder="Your Location"/>'
    )
    
    # Also check if it's there without self-closing tag just in case
    text = text.replace(
        '<input id="desk-origin" type="text" placeholder="Your Location" value="Guwahati, Assam">',
        '<input id="desk-origin" type="text" placeholder="Your Location">'
    )

    if text != original:
        p.write_text(text, encoding='utf-8')
        print(f"Updated {p.name}")
    else:
        print(f"No changes for {p.name}")
