import time
now=time.time()*1000
cut=int(now-3*86400*1000)
f = host.query(f"""SELECT id, parent_frame_id, agent_name, status, created_at, updated_at, name, delegate_name, substr(coalesce(task_summary,''),1,100) ts, total_cost, input_tokens, output_tokens
FROM frames WHERE project_id='proj_9cc1a5a85f63' AND updated_at > {cut} ORDER BY created_at""")
import datetime
for r in f['rows']:
    r=list(r); r[4]=datetime.datetime.fromtimestamp(r[4]/1000 if r[4]>1e11 else r[4]).strftime('%m-%d %H:%M'); r[5]=datetime.datetime.fromtimestamp(r[5]/1000 if r[5]>1e11 else r[5]).strftime('%m-%d %H:%M')
    print(r)