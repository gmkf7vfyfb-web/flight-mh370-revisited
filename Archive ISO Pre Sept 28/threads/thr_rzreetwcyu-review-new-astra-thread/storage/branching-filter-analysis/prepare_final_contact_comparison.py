"""Condition existing matched terminal predictions; never resimulate flights."""
import datetime as dt,hashlib,json,os,subprocess,time
from pathlib import Path
B=Path(__file__).parent
OUT=B/'final-contact-comparison'
BIN=B/'joint-terminal-proposal-executable'
WEB=B.parent/'overnight-analysis/web'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
def write(p,v):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n');t.replace(p)
def now():return dt.datetime.now(dt.timezone.utc).isoformat()
if OUT.exists():raise RuntimeError('Existing final-contact work must be inspected; no automatic repeat')
OUT.mkdir()
original=B/'terminal-million-extended-weather-conditioned/resolved-config.json'
cases=[c for c in json.loads(original.read_text())['cases'] if c['startup']['kind']=='no_offset' or c['name']=='both-sequential-shared-startup']
assert len(cases)==7
state=dict(status='conditioning',started_utc=now(),driver_pid=os.getpid(),executable=str(BIN),executable_sha256=sha(BIN),case_source=str(original),case_source_sha256=sha(original),cases=cases,runs=[],note='Two already-complete fourfold terminal sources; only final-contact likelihoods change. Fuel support is 00:15–00:19 UTC. No new flight or ocean simulation.')
def status():
 state['checked_utc']=now();write(OUT/'progress.json',state)
 write(WEB/'mh370-running-status.json',dict(status=state['status'],checked_utc=state['checked_utc'],message=state['note'],driver_pid=os.getpid(),completed=len(state['runs']),planned=2,comparison_finished=state['status'] in ['conditioned','failed'],jobs=[dict(title=state['note'],recorded_status=state['status'],driver_alive=state['status']=='conditioning',driver_pid=os.getpid(),worker_alive=state['status']=='conditioning',completed_runs=len(state['runs']),planned_runs=2)]))
status();started=time.perf_counter()
try:
 for seed in (37094011,37094012):
  src=B/f'mixed-terminal-sampling/terminal-seed-{seed}'
  conf=OUT/f'contacts-{seed}.json';target=OUT/f'contacts-{seed}'
  write(conf,dict(schema_version=1,source=str(src),cases=cases))
  state['active_seed']=seed;status();t=time.perf_counter()
  with (OUT/f'contacts-{seed}.log').open('w') as log:
   subprocess.run([str(BIN),'condition-cruise-impacts','--config',str(conf),'--output',str(target)],stdout=log,stderr=subprocess.STDOUT,check=True)
  state['runs'].append(dict(seed=seed,label='Fourfold A' if seed==37094011 else 'Fourfold B',source=str(src),source_summary_sha256=sha(src/'summary.json'),conditioned=str(target),summary_sha256=sha(target/'summary.json'),configuration=str(conf),configuration_sha256=sha(conf),elapsed_seconds=time.perf_counter()-t))
  status()
 state['status']='conditioned';state['completed_utc']=now();state['elapsed_seconds']=time.perf_counter()-started;state['note']='All seven final-contact conditions are computed for both saved terminal ensembles; independent verification and graphics are next. No flight/ocean sampler is running.';status()
except Exception as e:
 state['status']='failed';state['error']=repr(e);state['note']='Final-contact conditioning stopped; inspect the recorded error. No automatic retry.';status();raise
