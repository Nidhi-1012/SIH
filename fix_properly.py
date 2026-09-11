import pathlib
import re

targets = [
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\app.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\index_mobile.html',
]

def fix_file(path):
    p = pathlib.Path(path)
    if not p.exists(): return
    text = p.read_text(encoding='utf-8')

    # Look for the orphaned scrollable-body
    orphan_pattern = r'      <div class="scrollable-body">\s*<div class="card-title">Select Hazard Type</div>'
    match = re.search(orphan_pattern, text)
    
    if match:
        wrapper = '''    <!-- REPORT HAZARD SCREEN (OVERLAY) -->
    <div class="screen" id="screen-report">
      <div class="inner-hdr">
        <button class="back-btn" onclick="switchScreen('home')">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
        </button>
        <div>
          <div class="inner-hdr-title">Report Road Hazard</div>
          <div class="inner-hdr-sub">Instant GPS Snapping to Highway Segment</div>
        </div>
      </div>
'''
        
        # We need to insert this wrapper just before the matched <div class="scrollable-body">
        text = text[:match.start()] + wrapper + text[match.start():]
        
        # And we need to add the closing </div> for the screen at the end of the report block
        submit_btn = r'<span>Submit Verified Field Report</span>\s*</button>\s*</div>'
        submit_match = re.search(submit_btn, text)
        if submit_match:
            end_pos = submit_match.end()
            text = text[:end_pos] + '\n    </div>' + text[end_pos:]
            
        p.write_text(text, encoding='utf-8')
        print(f"Fixed {p.name}")
    else:
        print(f"Orphan pattern not found in {p.name}")

for t in targets:
    fix_file(t)
