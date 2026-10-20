import json,os,subprocess,time,datetime as dt,shutil
from pathlib import Path
D=Path(__file__).resolve().parent;B=D.parent;R=Path('/jackbox/home/MH370');W=B.parent/'overnight-analysis/web';P=D/'mixed/model-mixture/report';start=time.monotonic()
args=[str(D/'mh370'),'report-impact-mixture','--manifest',str(D/'mixed/model-mixture/manifest.json'),'--analysis',str(B),'--output',str(P),'--inline-output',str(R/'mh370-impact-model-mixture.html'),'--diagnostics',str(D/'estimator-stability-inputs.json')]
with (D/'report-layout.log').open('x') as stream:
 child=subprocess.Popen(args,cwd=R,stdout=stream,stderr=subprocess.STDOUT,env={**os.environ,'OPENBLAS_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1','MH370_REPORT_PYTHON':'/tmp/mh370-acoustic-venv/bin/python'})
 while True:
  pid,wait,u=os.wait4(child.pid,os.WNOHANG)
  if pid:child.returncode=os.waitstatus_to_exitcode(wait);break
  (W/'mh370-running-status.json').write_text(json.dumps(dict(checked_utc=dt.datetime.now(dt.timezone.utc).isoformat(),comparison_finished=False,jobs=[dict(title='Correcting figure title spacing and regenerating the report',recorded_status='rendering',driver_alive=True,driver_pid=os.getpid(),worker_alive=True,worker_pid=child.pid,completed_runs=2,planned_runs=2,candidates_per_run=12288)]),indent=2)+'\n');time.sleep(2)
result=dict(elapsed_seconds=time.monotonic()-start,peak_rss_kib=u.ru_maxrss,exit_code=child.returncode,reason='Visual inspection found overlapping heading in case-probability plot; increased title clearance. No new numerical experiment.')
(D/'report-layout-resources.json').write_text(json.dumps(result,indent=2)+'\n')
assert child.returncode==0
shutil.copy2(R/'mh370-impact-model-mixture.html',W/'mh370-impact-model-mixture.html')
subprocess.run(['/tmp/mh370-acoustic-venv/bin/python',str(D/'verify_report.py')],check=True,env={**os.environ,'OPENBLAS_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'})
