import json,time
fids=[r['frame_id'] for r in json.load(open('handoff_kadri_dispatch.json'))]
done=json.load(open('handoff_kadri_results.json'))
deadline=time.time()+1750; new=False
while time.time()<deadline and not new:
    for r in host.collect([f for f in fids if f not in done], timeout=60):
        if r.get('status')!='running': done[r['frame_id']]=r; new=True
json.dump(done, open('handoff_kadri_results.json','w'), default=str)
print(len(done), [(r.get('name'), r.get('status')) for r in done.values()])