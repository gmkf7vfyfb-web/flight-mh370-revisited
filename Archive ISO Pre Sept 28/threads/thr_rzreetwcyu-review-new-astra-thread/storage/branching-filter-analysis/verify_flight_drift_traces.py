from pathlib import Path
import json,hashlib,datetime as dt,time,math
B=Path(__file__).resolve().parent;out=B/'flight-drift-selected-terminal-traces';start=time.monotonic()
rows=[json.loads(line) for line in (out/'continuations.jsonl').open()];key=lambda r:(r['source_index'],r['draw'],r.get('family'));wanted={key(r):r for r in rows};assert len(wanted)==8
found={}
for line in (B/'terminal-million-extended-weather/continuations.jsonl').open():
 r=json.loads(line);k=key(r)
 if k in wanted:found[k]=r
assert set(found)==set(wanted)
counts=[]
for k,r in wanted.items():
 original=found[k]
 ignore={'terminal_trace','powered_trace','atmosphere_sampling_counts'}
 assert {k:v for k,v in original.items() if k not in ignore}=={k:v for k,v in r.items() if k not in ignore},k
 delta=[a-b for a,b in zip(r['atmosphere_sampling_counts'],original['atmosphere_sampling_counts'])]
 assert all(v>=0 for v in delta)
 counts.append(dict(identity=k,additional_atmosphere_lookups=delta,trace_states=len(r['terminal_trace'])))
selection=json.loads((B/'flight-drift-route-selection.json').read_text());cache={};prefix=[]
for chosen in selection['selections']:
 ident=chosen['spatial_particle']['identity'];p=chosen['exact_history_source']['path']
 if p not in cache:cache[p]=json.loads(Path(p).read_text())
 e=next(e for e in cache[p]['examples'] if e['terminal_slot']==ident['parent_slot']);r=wanted[(ident['source_index'],ident['draw'],ident['terminal_family'])]
 a=e['terminal']['flight']['aircraft'];b=r['source_state_0011']['aircraft'];assert e['root']==r['root_id'] and a['time']==b['time']
 delta=[a['position']['latitude']-b['position']['latitude'],a['position']['longitude']-b['position']['longitude'],a['altitude']-b['altitude']]
 assert all(abs(v)<1e-9 for v in delta);prefix.append(delta)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
v=dict(checked_utc=dt.datetime.now(dt.timezone.utc).isoformat(),status='passed',exact_original_physical_records_matched=len(rows),
 source_continuations_sha256=sha(B/'terminal-million-extended-weather/continuations.jsonl'),selected_continuations_sha256=sha(out/'continuations.jsonl'),
 additional_trace_metadata=counts,cruise_endpoint_differences_lat_deg_lon_deg_alt_ft=prefix,elapsed_seconds=time.monotonic()-start,
 scope='All original physical, contact, fuel and weight fields match exactly. Trace logging adds atmosphere lookups and path samples. Cruise-prefix differences are checked serialization roundoff; no posterior weights changed.')
(out/'replay-verification.json').write_text(json.dumps(v,indent=2)+'\n')
p=B/'flight-drift-traces-status.json';s=json.loads(p.read_text());s.update(status='completed',finished_utc=v['checked_utc'],verification=v,elapsed_seconds=json.loads((out/'summary.json').read_text())['elapsed_seconds']);p.write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(v))
