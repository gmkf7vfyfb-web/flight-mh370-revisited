rows = host.query("SELECT id, text FROM memories WHERE id IN ('mem_d2421dfbab8d','mem_15b33243c74f','mem_aa436b9ac0ea','mem_dc0395e2fe69','mem_11121243c1de','mem_bc3a7380aa85')")
for r in rows: print(r, '\n')
rows = host.query("SELECT id, text FROM memories WHERE text LIKE '%SIR%' AND (text LIKE '%fileId%' OR text LIKE '%Drive%') LIMIT 15")
for r in rows: print(r, '\n')