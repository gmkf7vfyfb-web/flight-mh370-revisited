"""Apply frozen antenna cases to explicitly selected saved flight populations."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

B=Path(__file__).resolve().parent
state_path=Path(sys.argv[1])
state=json.loads(state_path.read_text())
assert state['status']=='prepared','Do not rerun a completed or running queue'
def save():
 state['updated_utc']=dt.datetime.now(dt.timezone.utc).isoformat()
 temporary=state_path.with_suffix('.tmp');temporary.write_text(json.dumps(state,indent=2)+'\n');temporary.replace(state_path)
state.update(status='running',driver_pid=os.getpid());save()
try:
 for run in state['runs']:
  while run.get('source_output') and not (Path(run['source_output'])/'summary.json').exists():
   upstream=json.loads(Path(state['upstream_status']).read_text())
   if upstream['status']=='needs_inspection':raise RuntimeError('Upstream flight queue needs inspection')
   state['waiting_for_source']=run['source_output'];save();time.sleep(10)
  state.pop('waiting_for_source',None)
  assert not Path(run['output']).exists()
  Path(run['output']).parent.mkdir(parents=True,exist_ok=True)
  assert hashlib.sha256(Path(state['executable']).read_bytes()).hexdigest()==state['executable_sha256']
  run.update(status='running',configuration_sha256=hashlib.sha256(Path(run['config']).read_bytes()).hexdigest())
  command=[state['executable'],'condition-flight-antenna','--config',run['config'],'--output',run['output']]
  with Path(run['output']+'.log').open('x') as log:
   child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,cwd='/tmp/mh370-branching-filter')
   run['pid']=child.pid;save();code=child.wait()
  if code:raise RuntimeError(f'Antenna conditioning failed with code {code}: {run["output"]}')
  result=json.loads((Path(run['output'])/'summary.json').read_text())
  run.update(status='completed',elapsed_seconds=result['elapsed_seconds'],case_count=len(result['cases']));save()
  line=state['updated_utc']+f': Antenna conditioning complete for seed {run["seed"]}: {len(result["cases"])} explicit cases in {result["elapsed_seconds"]:.2f}s, using existing trajectories only.\n'
  print(line,flush=True)
  with (B/'progress.md').open('a') as f:f.write('\n'+line)
 state['status']='completed';save()
except BaseException as error:
 state.update(status='needs_inspection',error=str(error));save();raise
