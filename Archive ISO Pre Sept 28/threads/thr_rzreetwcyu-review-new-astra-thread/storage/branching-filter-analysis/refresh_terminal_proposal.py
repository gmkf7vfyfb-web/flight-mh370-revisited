"""Two independent terminal pilots after refitting numerical guidance only."""
import csv,datetime as dt,hashlib,json,math,os,shutil,subprocess,time
from pathlib import Path
B=Path(__file__).parent;R=Path('/jackbox/home/MH370');D=B/'terminal-proposal-refresh';PY='/tmp/mh370-acoustic-venv/bin/python'
def read(p):return json.loads(Path(p).read_text())
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def write(p,v):
 q=p.with_suffix('.tmp');q.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n');q.replace(p)
if D.exists():raise RuntimeError('Inspect existing proposal-refresh work; no automatic repeat')
D.mkdir();executable=D/'mh370';shutil.copy2(R/'target/iteration/mh370',executable)
state=dict(status='preparing',driver_pid=os.getpid(),started_utc=now(),executable=str(executable),executable_sha256=sha(executable),reason='Both-BFO impact updates remain concentrated after larger draws, especially after debris/search. Refit the same numerical guide from actual stored guided controls in the larger completed pilot. Keep physical priors, mixture widths/fractions and exact importance correction unchanged.',draws_per_source=2048,planned_runs=2,runs=[],source_code_sha256={str(R/'crates/runner/src/cruise_impact_commands.rs'):sha(R/'crates/runner/src/cruise_impact_commands.rs')})
def status(title,worker=None):
 state['checked_utc']=now();write(D/'progress.json',state);done=state['status'] in ['conditioned','failed']
 write(B.parent/'overnight-analysis/web/mh370-running-status.json',dict(checked_utc=state['checked_utc'],comparison_finished=done,jobs=[dict(title=title,recorded_status=state['status'],driver_alive=not done,driver_pid=os.getpid(),worker_alive=worker is not None,worker_pid=worker,completed_runs=len(state['runs']),planned_runs=2,candidates_per_run=12288,run_started_utc=state.get('run_started_utc'))]))
def command(args,name):
 started=time.perf_counter()
 with (D/(name+'.log')).open('w') as f:
  proc=subprocess.Popen(args,cwd=R,stdout=f,stderr=subprocess.STDOUT,env={**os.environ,'OPENBLAS_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'})
  while proc.poll() is None:status(name,proc.pid);time.sleep(2)
  if proc.returncode:raise RuntimeError('Inspect '+str(D/(name+'.log')))
 return time.perf_counter()-started
start=time.perf_counter();status('Refitting terminal numerical guidance from retained actual control coordinates')
try:
 source=B/'final-contact-comparison/contacts-37094012';bank=D/'control-proposal.json';command([str(executable),'prepare-terminal-control-proposal','--source',str(source),'--output',str(bank),'--centres-per-case','32'],'prepare-controls')
 fitted=read(bank);selected={(family,c['source_index'],c['draw']):c for family,centres in fitted['families'].items() for c in centres};found=set();largest=0.
 src=Path(read(source/'summary.json')['source']);assert sha(src/'continuations.jsonl')==fitted['source_continuations_sha256'];assert sha(source/'summary.json')==fitted['source_condition_summary_sha256']
 for line in (src/'continuations.jsonl').open():
  row=json.loads(line);key=row.get('family'),row['source_index'],row['draw']
  if key not in selected:continue
  c=selected[key];actual=row['control_unit_coordinates'];assert len(actual)==len(c['coordinates'])
  for a,b in zip(actual,c['coordinates']):
   assert abs(a-b)<=2*max(math.ulp(a),math.ulp(b));largest=max(largest,abs(a-b))
  assert 0<=min(actual) and max(actual)<1
  assert len(c['active_coordinates'])==len(actual)
  ctx=[row['fuel_sample']['fuel_at_exhaustion']['time'],row['boundary']['aircraft']['altitude'],row['boundary']['true_airspeed'],row['boundary']['aircraft']['position']['latitude']]
  for a,b in zip(ctx,c['context']):assert abs(a-b)<=2*max(math.ulp(a),math.ulp(b))
  found.add(key)
 assert found==set(selected)
 verification=dict(status='passed',centres=len(found),maximum_coordinate_roundtrip_error=largest,method='Independent comparison of every selected centre with the actual saved guided draw and exhaustion context; two-ULP JSON representation tolerance. No prior-RNG reconstruction of guided controls.',bank_sha256=sha(bank),source_continuations_sha256=fitted['source_continuations_sha256']);write(D/'proposal-verification.json',verification)
 state.update(proposal_bank=str(bank),proposal_bank_sha256=sha(bank),proposal_verification=verification)
 template=read(src/'resolved-config.json');cases=read(source/'resolved-config.json')['cases']
 for seed,label in [(37095011,'Refreshed guide A'),(37095012,'Refreshed guide B')]:
  name='terminal-seed-'+str(seed);cfg=json.loads(json.dumps(template));cfg.update(name=name,seed=seed,draws_per_source=2048);cfg['control_proposal']['bank']=str(bank)
  restored=json.loads(json.dumps(cfg));restored.update(name=template['name'],seed=template['seed'],draws_per_source=template['draws_per_source']);restored['control_proposal']['bank']=template['control_proposal']['bank'];assert restored==template
  cp=D/(name+'.json');write(cp,cfg);output=D/name;state.update(status='sampling',active_seed=seed,run_started_utc=now());status(label+': unchanged terminal physics, refreshed corrected numerical guide')
  elapsed=command([str(executable),'continue-cruise-to-impact','--config',str(cp),'--output',str(output)],'sample-'+str(seed))
  conditioned=D/(name+'-conditioned');cc=D/(name+'-conditioned.json');write(cc,dict(schema_version=1,source=str(output),cases=cases));state['status']='conditioning';command([str(executable),'condition-cruise-impacts','--config',str(cc),'--output',str(conditioned)],'condition-'+str(seed))
  state['runs'].append(dict(seed=seed,label=label,source=str(output),source_summary_sha256=sha(output/'summary.json'),conditioned=str(conditioned),summary_sha256=sha(conditioned/'summary.json'),configuration=str(cc),configuration_sha256=sha(cc),terminal_configuration=str(cp),terminal_configuration_sha256=sha(cp),elapsed_seconds=elapsed));status('Completed '+label)
 state.update(status='conditioned',completed_utc=now(),elapsed_seconds=time.perf_counter()-start);status('Two proposal-refresh pilots finished; independent verification and comparison are next')
except Exception as error:
 state.update(status='failed',error=repr(error),failed_utc=now());status('Proposal-refresh work stopped; inspect the error before any retry');raise
