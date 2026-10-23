
import re
hits = []
for term in ["Hydroacoustic", "hydroacoustic", "Kadri", "Airplane", "Detection", ".pdf"]:
    try:
        r = host.artifacts(search=term)
    except Exception as e:
        print(term, "ERR", e); continue
    for a in r:
        hits.append(a)
seen=set()
for a in hits:
    k = a.get('artifact_id') or a.get('id')
    if k in seen: continue
    seen.add(k)
    fn = a.get('filename') or a.get('name')
    if fn and (fn.lower().endswith('.pdf') or 'hydro' in fn.lower() or 'kadri' in fn.lower()):
        print(fn, '|', k, '|', a.get('created_at') or a.get('created'))
print(len(seen), "unique matches total")
