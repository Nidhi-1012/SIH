import pathlib
text = pathlib.Path(r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\index.html').read_text(encoding='utf-8')
# Check screen-nav CSS and navbar
idx = text.find('screen-nav')
print(text[max(0, idx-300):idx+200])
print('\n\n---\n')
# Check if screen-nav has z-index that puts navbar on top
idx2 = text.find('.screen {')
print(text[idx2:idx2+300])
