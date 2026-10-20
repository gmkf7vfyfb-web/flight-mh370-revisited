"""Recover specific old leaf histories with byte-identical endpoint checks."""
from pathlib import Path
import datetime as dt, hashlib, json, os, resource, subprocess, time
B=Path(__file__).resolve().parent;STATE=B/'requested-history-status.json'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def save(s):
 s['updated_utc']=now();tmp=STATE.with_suffix('.tmp');tmp.write_text(json.dumps(s,indent=2)+'\n');tmp.replace(STATE)
def log(message):
 with (B/'progress.md').open('a') as f:f.write('\n'+now()+': '+message+'\n')
 print(message,flush=True)
def main():
 state=json.loads(STATE.read_text());assert state['status']=='prepared';exe=B/'requested-history-executable';assert exe.exists()
 state.update(status='running',driver_pid=os.getpid(),executable=str(exe),executable_sha256=digest(exe));save(state)
 for job in state['runs']:
  config=Path(job['config']);source=Path(job['source']);output=Path(job['output']);assert not output.exists();output.parent.mkdir(exist_ok=True)
  assert digest(config)==job['configuration_sha256'] and digest(exe)==state['executable_sha256']
  command=[str(exe),'estimate-branching-flight','--config',str(config),'--output',str(output),'--threads',str(state['threads'])]
  job.update(status='running',started_utc=now(),command=command);start=time.monotonic()
  with (B/('requested-history-'+str(job['source_index'])+'.log')).open('x') as f:
   child=subprocess.Popen(command,stdout=f,stderr=subprocess.STDOUT,cwd='/tmp/mh370-branching-filter');job['pid']=child.pid;save(state)
   log(f"Recovering {len(job['requested_slots'])} selected historical paths from {source.name}; no new candidates. PID {child.pid}.")
   code=child.wait()
  job.update(exit_code=code,elapsed_seconds=time.monotonic()-start,peak_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)
  if code:raise RuntimeError(f'History recovery failed: {source.name}; no automatic rerun')
  original=json.loads((source/'summary.json').read_text());current=json.loads((output/'summary.json').read_text())
  assert digest(output/'posterior.csv')==digest(source/'posterior.csv'), 'Recovery changed endpoint inference'
  assert original['log_evidence']==current['log_evidence'], 'Recovery changed evidence'
  trace=json.loads((output/'trajectory-examples.json').read_text());assert trace['full_contact_state_and_likelihood_match']
  assert set(job['requested_slots']).issubset({v['terminal_slot'] for v in trace['examples']})
  job.update(status='completed',finished_utc=now(),posterior_byte_identical=True,exact_contact_checks=trace['exact_replay_checks'],trajectory_sha256=digest(output/'trajectory-examples.json'));save(state)
  log(f"Recovered requested histories from {source.name} in {job['elapsed_seconds']:.1f}s; posterior CSV and evidence exactly match the saved original.")
 state.update(status='completed',finished_utc=now());save(state);log('Requested conditional-hypothesis histories recovered. Continue terminal examples and canonical integration.')
if __name__=='__main__':
 try:main()
 except BaseException as error:
  s=json.loads(STATE.read_text());s.update(status='needs_inspection',error=repr(error));save(s);log('History recovery needs inspection: '+repr(error));raise
