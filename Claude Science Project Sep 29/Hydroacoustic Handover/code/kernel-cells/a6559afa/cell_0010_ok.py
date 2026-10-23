t = host.query("SELECT name FROM sqlite_master WHERE type='table'")
print([r[0] for r in t['rows']])