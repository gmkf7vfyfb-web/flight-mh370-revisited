r = host.collect(["1a5e1fbe-325f-4e94-a8a4-21ad56efb838"], timeout=30)[0]
print(r['status'], r.get('deviations'), [ (a.get('filename'),a.get('version_id')) for a in (r.get('artifacts_created') or [])])
print(r.get('response','')[:6000])