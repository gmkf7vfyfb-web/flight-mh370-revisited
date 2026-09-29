"""Execute distinct surface conditions without rerunning any trajectory."""
from pathlib import Path
import datetime as dt,hashlib,json,os,subprocess,time,sys
B=Path(__file__).resolve().parent;P=Path(sys.argv[1]) if len(sys.argv)>1 else B/'spatial-comparison-status.json';s=json.loads(P.read_text());assert s['status']=='prepared'
def save():
 s['updated_utc']=dt.datetime.now(dt.timezone.utc).isoformat();t=P.with_suffix('.tmp');t.write_text(json.dumps(s,indent=2)+'\n');t.replace(P)
assert hashlib.sha256(Path(s['executable']).read_bytes()).hexdigest()==s['executable_sha256']
if s.get('after_state'):
 s.update(status='waiting_for_numerical_workers',driver_pid=os.getpid());save()
 while True:
  predecessor=json.loads(Path(s['after_state']).read_text())
  if predecessor['status']=='completed':break
  if predecessor['status']=='needs_inspection':
   s.update(status='dependency_needs_inspection');save();raise RuntimeError('Preceding numerical task needs inspection')
  time.sleep(10)
s.update(status='running',driver_pid=os.getpid());save();started=time.monotonic()
try:
 for entry in s['queue']:
  output=Path(entry['output']);assert not output.exists(),str(output)
  t=time.monotonic();s['current']=entry['name'];save()
  run=subprocess.run([s['executable'],'apply-conditional-surface','--config',entry['config'],'--output',str(output)],capture_output=True,text=True)
  if run.returncode:raise RuntimeError(run.stderr)
  j=json.loads((output/'conditional-spatial-sensitivity.json').read_text());entry=dict(entry,elapsed_seconds=time.monotonic()-t,supported_baseline_mass=j['supported_baseline_mass'],conditional_effective_rows=j['conditional_effective_sample_size'],conditional_mean=j['conditional_mean']);s['completed'].append(entry);save()
 s.update(status='completed',elapsed_seconds=time.monotonic()-started);s.pop('current',None);save()
 with (B/'progress.md').open('a') as f:f.write('\n'+s['updated_utc']+': Completed '+str(len(s['completed']))+' separately labelled spatial comparisons from retained impacts; no trajectory resampling. Generate and inspect conditional reports next.\n')
 if 'report_suffix' in s:
  report=subprocess.run([sys.executable,str(B/'render_spatial_comparisons.py'),'--state',str(P),'--suffix='+s['report_suffix']],capture_output=True,text=True)
  s['reports_completed']=report.returncode==0
  if report.returncode:s['report_error']=report.stderr[-3000:]
  save()
except Exception as e:s.update(status='needs_inspection',error=str(e));save();raise
