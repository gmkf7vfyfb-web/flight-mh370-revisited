"""Render the 16/8/8 estimate as larger interacting populations finish."""
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import time
B=Path(__file__).resolve().parent
state_path=B/'enlarged-report-status.json'
assert not state_path.exists(),'Do not duplicate the report watcher'
last=-1
while True:
 queue=json.loads((B/'enlarged-relaxation-status.json').read_text())
 completed=[Path(r['output']) for r in queue['runs'] if r['status']=='completed']
 if completed and len(completed)!=last:
  original=[B/f'runs/turns16-mach8-altitude8-vertical-bfo-seed-{seed}' for seed in [37091631,37091640]]
  command=['/tmp/mh370-acoustic-venv/bin/python','/jackbox/home/MH370/crates/reporting/scripts/arc_density_report.py','--runs',*[str(p) for p in original+completed],'--baseline-runs','2','--output',str(B/'broader-arc-density'),'--inline-output','/jackbox/home/MH370/mh370-broader-arc-density.html']
  with (B/'enlarged-report-driver.log').open('a') as log:
   result=subprocess.run(command,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1'),stdout=log,stderr=subprocess.STDOUT)
  state=dict(status='running' if result.returncode==0 else 'needs_inspection',rendered_enlarged_runs=len(completed),updated_utc=dt.datetime.now(dt.timezone.utc).isoformat(),driver_pid=os.getpid())
  state_path.write_text(json.dumps(state,indent=2)+'\n')
  if result.returncode:raise RuntimeError('Enlarged report failed; inspect log')
  Path('/jackbox/home/.iso/thread-storage/thr_rzreetwcyu/overnight-analysis/web/mh370-broader-arc-density.html').write_bytes(Path('/jackbox/home/MH370/mh370-broader-arc-density.html').read_bytes())
  last=len(completed)
 if queue['status'] in ['sampling_completed','needs_inspection']:
  state['status']='completed' if queue['status']=='sampling_completed' else 'upstream_needs_inspection';state_path.write_text(json.dumps(state,indent=2)+'\n');break
 time.sleep(20)
