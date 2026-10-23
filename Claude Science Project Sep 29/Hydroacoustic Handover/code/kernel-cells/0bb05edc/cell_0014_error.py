
rows = host.query("SELECT * FROM memories WHERE id LIKE 'mem_eab4efd3005c%' OR text LIKE '%Metz%' ORDER BY created_at DESC LIMIT 50")
print(len(rows))
for r in rows:
    print({k: (str(v)[:160] if k=='text' else v) for k,v in r.items()})
    print('---')
