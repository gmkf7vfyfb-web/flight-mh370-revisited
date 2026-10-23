t = host.query("SELECT name, sql FROM sqlite_master WHERE type='table' AND name LIKE '%message%'")
for r in t['rows']: print(r[0], '\n', r[1][:600], '\n')