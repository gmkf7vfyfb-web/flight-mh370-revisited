print(host.query("SELECT sql FROM sqlite_master WHERE name='frames'")[0])
rows = host.query("""SELECT id, text, created_at FROM memories WHERE created_at > datetime('now','-2 days') AND (text LIKE '%ydro%' OR text LIKE '%candidate%') ORDER BY created_at""")
for r in rows: print('\n---', r['created_at'], r['id'], '\n', r['text'])