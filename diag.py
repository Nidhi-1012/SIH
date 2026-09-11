import pathlib
text = pathlib.Path(r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\index.html').read_text(encoding='utf-8')
# Verify all three features are present
print("Location box:", 'report-location-box' in text)
print("Photo input:", 'report-photo-input' in text)
print("handlePhotoSelect:", 'handlePhotoSelect' in text)
print("detectReportLocation:", 'detectReportLocation' in text)
print("submitReport updated:", 'reportPhotoBase64' in text)
print("Auto-detect on open:", 'setTimeout(detectReportLocation, 200)' in text)
