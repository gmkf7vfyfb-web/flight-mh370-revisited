import json,time
done=json.load(open('handoff_kadri_results.json'))
fid="1f938cf5-20bc-4aee-ba61-9768284cbcb2"; deadline=time.time()+1750
while time.time()<deadline and fid not in done:
    for r in host.collect([fid], timeout=60):
        if r.get('status')!='running': done[fid]=r
json.dump(done, open('handoff_kadri_results.json','w'), default=str)
print(fid in done, done.get(fid,{}).get('status'))