
import datetime
r = host.query("""SELECT a.filename, av.id, av.size_bytes, av.created_at FROM artifact_versions av JOIN artifacts a ON a.id=av.artifact_id
WHERE lower(a.filename) LIKE '%.pdf' AND (a.filename LIKE '10.%' OR a.filename LIKE 'art%3A%' OR lower(a.filename) LIKE '%royer%' OR lower(a.filename) LIKE '%blackman%' OR lower(a.filename) LIKE '%nielsen%' OR lower(a.filename) LIKE '%vergoz%' OR lower(a.filename) LIKE '%brown%' OR lower(a.filename) LIKE '%atsb%' OR lower(a.filename) LIKE '%s4%' OR lower(a.filename) LIKE '%arxiv%' OR lower(a.filename) LIKE '%paper%' OR lower(a.filename) LIKE '%2019%' OR lower(a.filename) LIKE '%2023%' OR lower(a.filename) LIKE '%ucrl%')
ORDER BY a.filename""", limit=200)
print(r['row_count'])
seen=set()
for fn,vid,sz,ts in r['rows']:
    if fn in seen: continue
    seen.add(fn)
    print(fn[:80],'|',vid[:8],'|',sz,'|',datetime.datetime.utcfromtimestamp(ts/1000).strftime('%m-%d'))
