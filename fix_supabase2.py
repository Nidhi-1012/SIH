import pathlib

targets = [
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\app.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\mobile\index.html',
    r'C:\Users\hp\OneDrive\Desktop\SIH\frontend\public\index_mobile.html',
]

OLD_SNIPPET = '''// Check session on startup and update UI
async function checkAdminSession() {
  if (!supabaseClient) return null;
  try {'''

NEW_SNIPPET = '''// Check session on startup and update UI
async function checkAdminSession() {
  if (!supabaseClient && window.supabase) {
    supabaseClient = window.supabase.createClient(SUPABASE_PROJECT_URL, SUPABASE_ANON_KEY);
  }
  if (!supabaseClient) return null;
  try {'''

for target in targets:
    p = pathlib.Path(target)
    if not p.exists(): continue
    text = p.read_text(encoding='utf-8')
    if OLD_SNIPPET in text and NEW_SNIPPET not in text:
        text = text.replace(OLD_SNIPPET, NEW_SNIPPET)
        p.write_text(text, encoding='utf-8')
        print(f"Updated checkAdminSession in: {p.name}")
