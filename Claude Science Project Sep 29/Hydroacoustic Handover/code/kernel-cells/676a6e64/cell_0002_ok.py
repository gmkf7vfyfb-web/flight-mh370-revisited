fr = host.frames()
import re
rows = fr['frames']
print([k for k in rows[0].keys()])
for r in rows:
    if re.search(r'hydro', (r.get('name') or '') + (r.get('task_summary') or ''), re.I):
        print(r['id'][:8], r['created_at'][:16], r['status'], r['agent_name'], '|', r['name'], '|', (r.get('task_summary') or '')[:150])
print('--- try search')
try:
    s = host.frames(search='Review Hydroacoustic Module Brief')
    print(str(s)[:1500])
except Exception as e:
    print('search err', e)
