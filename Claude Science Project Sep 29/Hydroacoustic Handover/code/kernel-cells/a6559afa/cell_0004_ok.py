cut=int(now-1.5*86400*1000)
m = host.query(f"""SELECT id, created_at, body FROM memories WHERE subject_project_id='proj_9cc1a5a85f63' AND created_at > {cut} AND superseded_by IS NULL ORDER BY created_at""")
out=[]
for r in m['rows']:
    out.append(f"--- {datetime.datetime.fromtimestamp(r[1]/1000).strftime('%m-%d %H:%M')} {r[0]}\n{r[2]}")
open('handoff_mem.txt','w').write('\n'.join(out))
print(len(m['rows']))
fr = host.query("SELECT output_data FROM frames WHERE id='a35831fe-107a-4961-bc9f-e6fd6d255601'")
od = fr['rows'][0][0] or ''
open('handoff_review.txt','w').write(od)
print(len(od))
fr2 = host.query("SELECT output_data FROM frames WHERE id='676a6e64-2eac-490f-b67d-6c3f5c82f047'")
open('handoff_main.txt','w').write(fr2['rows'][0][0] or '')
print(len(fr2['rows'][0][0] or ''))