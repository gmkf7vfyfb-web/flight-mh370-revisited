res = host.collect(fids, timeout=1500)
for r in res: print(r.get('name'), r['status'], len(str(r.get('response',''))), [a.get('filename') for a in (r.get('artifacts_created') or [])])