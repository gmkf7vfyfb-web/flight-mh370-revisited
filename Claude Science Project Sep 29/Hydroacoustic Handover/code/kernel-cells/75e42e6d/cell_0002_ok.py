r = host.query("SELECT id, body FROM memories WHERE id IN ('mem_d2421dfbab8d','mem_15b33243c74f','mem_dc0395e2fe69','mem_11121243c1de')")
for x in r['rows']: print(x, '\n')
r = host.query("SELECT id, body FROM memories WHERE superseded_by IS NULL AND (body LIKE '%Safety Investigation Report%' OR body LIKE '%SIR%') AND (body LIKE '%fileId%' OR body LIKE '%mot.gov.my%' OR body LIKE '%Drive%') LIMIT 12")
for x in r['rows']: print(x[0], x[1][:500], '\n')