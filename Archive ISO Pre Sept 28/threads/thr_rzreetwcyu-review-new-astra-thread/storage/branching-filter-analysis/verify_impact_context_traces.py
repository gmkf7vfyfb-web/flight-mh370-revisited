"""Check exact requested replays and their saved cruise joins before plotting."""
from pathlib import Path
import datetime as dt,hashlib,json,time
B=Path(__file__).resolve().parent;start=time.monotonic();inputs=json.loads((B/'impact-context-inputs.json').read_text());out=Path(inputs['trace_directory'])
key=lambda r:(r['source_index'],r['draw'],r.get('family'))
rows=list(map(json.loads,(out/'continuations.jsonl').open()));wanted={key(r):r for r in rows};assert len(wanted)==len(rows)
found={}
for line in (B/'terminal-million-extended-weather/continuations.jsonl').open():
    r=json.loads(line);k=key(r)
    if k in wanted:found[k]=r
assert set(found)==set(wanted)
ignore={'terminal_trace','powered_trace','atmosphere_sampling_counts'}
for k,r in wanted.items():
    assert {n:v for n,v in r.items() if n not in ignore}=={n:v for n,v in found[k].items() if n not in ignore},k
    assert all(a>=b for a,b in zip(r['atmosphere_sampling_counts'],found[k]['atmosphere_sampling_counts']))
cache={};joins=[]
for selection in inputs['selections']:
    p=selection['history_source']['path']
    if p not in cache:cache[p]=json.loads(Path(p).read_text())
    e=next(e for e in cache[p]['examples'] if e['terminal_slot']==selection['history_terminal_slot']);i=selection['spatial_particle']['identity'];r=wanted[(i['source_index'],i['draw'],i['terminal_family'])]
    a=e['terminal']['flight']['aircraft'];b=r['source_state_0011']['aircraft'];assert e['root']==r['root_id'] and a['time']==b['time']
    delta=[a['position']['latitude']-b['position']['latitude'],a['position']['longitude']-b['position']['longitude'],a['altitude']-b['altitude']]
    assert all(abs(x)<1e-9 for x in delta)
    end=r['terminal_trace'][-1]['kinematics']['point_mass']['position'];assert abs(end['latitude']-selection['spatial_particle']['latitude_deg'])<1e-9 and abs(end['longitude']-selection['spatial_particle']['longitude_deg'])<1e-9
    joins.append(delta)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
result=dict(status='passed',checked_utc=dt.datetime.now(dt.timezone.utc).isoformat(),exact_original_records=len(rows),selected_cruise_joins=len(joins),
    original_continuations_sha256=sha(B/'terminal-million-extended-weather/continuations.jsonl'),selected_continuations_sha256=sha(out/'continuations.jsonl'),
    maximum_absolute_join_difference=max(abs(x) for row in joins for x in row),script_sha256=sha(__file__),elapsed_seconds=time.monotonic()-start,
    scope='Original physical/contact/fuel/weight records identical; only passive path logs and associated atmosphere counters differ. All cruise-to-terminal joins and plotted impact coordinates match.')
(out/'replay-verification.json').write_text(json.dumps(result,indent=2)+'\n');p=B/'impact-context-traces-status.json';s=json.loads(p.read_text());s.update(status='completed',verification=result);p.write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(result))
