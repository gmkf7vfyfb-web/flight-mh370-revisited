"""Refresh model-specific browser reports as the explicit comparison runs finish."""
import json
import os
from pathlib import Path
import subprocess
import time
import datetime as dt
B=Path(__file__).resolve().parent
state_path=B/'model-report-status.json'
assert not state_path.exists(),'Do not launch duplicate report watchers'
last=-1
while True:
 queue=json.loads((B/'relaxation-status.json').read_text())
 count=sum(r['status']=='completed' for r in queue['runs'])
 if count and count!=last:
  command=['/tmp/mh370-acoustic-venv/bin/python','/jackbox/home/MH370/crates/reporting/scripts/flight_sensitivity_report.py','--status',str(B/'relaxation-status.json'),'--baseline',str(B/'runs/recovered-history-seed-37091631'),str(B/'runs/recovered-history-seed-37091640'),'--output',str(B/'model-comparison'),'--inline-output','/jackbox/home/MH370/mh370-model-comparison.html']
  environment=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1')
  with (B/'model-report-driver.log').open('a') as log:
   result=subprocess.run(command,env=environment,stdout=log,stderr=subprocess.STDOUT)
  state=dict(status='running' if result.returncode==0 else 'needs_inspection',rendered_runs=count,updated_utc=dt.datetime.now(dt.timezone.utc).isoformat(),driver_pid=os.getpid())
  if result.returncode==0:
   Path('/jackbox/home/.iso/thread-storage/thr_rzreetwcyu/overnight-analysis/web/mh370-model-comparison.html').write_bytes(Path('/jackbox/home/MH370/mh370-model-comparison.html').read_bytes())
   last=count
  state_path.write_text(json.dumps(state,indent=2)+'\n')
  if result.returncode:raise RuntimeError('Model report failed; inspect driver log')
 if queue['status'] in ['sampling_completed','needs_inspection']:
  state['status']='completed' if queue['status']=='sampling_completed' else 'upstream_needs_inspection'
  state_path.write_text(json.dumps(state,indent=2)+'\n')
  break
 time.sleep(20)
