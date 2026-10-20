"""Finish one authorized terminal ensemble, likelihood cases, and browser report."""
from pathlib import Path
import datetime as dt,hashlib,json,os,subprocess,urllib.request,sys
B=Path(__file__).resolve().parent;state_path=Path(sys.argv[1]) if len(sys.argv)>1 else B/'terminal-ensemble-status.json';s=json.loads(state_path.read_text());assert s['status']=='prepared'
def save():
 s['updated_utc']=dt.datetime.now(dt.timezone.utc).isoformat();temp=state_path.with_suffix('.tmp');temp.write_text(json.dumps(s,indent=2)+'\n');temp.replace(state_path)
s.update(status='running',driver_pid=os.getpid());save()
try:
 exe=Path(s.get('executable',str(B/'cruise-impact-executable')))
 assert hashlib.sha256(exe.read_bytes()).hexdigest()==s['executable_sha256']
 subprocess.run(['python3',str(B/'run_cruise_impact.py'),s['configuration'],s['output'],str(exe)],check=True)
 done=json.loads(Path(s['output']+'-status.json').read_text())
 if done['status']!='completed':raise RuntimeError('Terminal sampling needs inspection: '+s['output'])
 s.update(status='conditioning',sampling_elapsed_seconds=done['elapsed_seconds'],peak_child_rss_kb=done['peak_child_rss_kb']);save()
 subprocess.run([str(exe),'condition-cruise-impacts','--config',s['conditional_configuration'],'--output',s['conditional_output']],check=True)
 s['status']='reporting';save()
 root=Path('/jackbox/home/MH370');preview=Path(s.get('inline_output',str(root/'mh370-impact-comparison.html')))
 subprocess.run(['/tmp/mh370-acoustic-venv/bin/python',str(root/'crates/reporting/scripts/cruise_impact_report.py'),'--source',s['conditional_output'],'--output',s.get('report_directory',str(B/'impact-comparison')),'--inline-output',str(preview)],env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1'),check=True)
 web=Path('/jackbox/home/.iso/thread-storage/thr_rzreetwcyu/overnight-analysis/web')/preview.name;web.write_bytes(preview.read_bytes())
 assert urllib.request.urlopen('http://127.0.0.1:8771/overnight/'+preview.name).read()==preview.read_bytes()
 s.update(status='completed',report=str(preview));save()
 with (B/'progress.md').open('a') as f:f.write('\n'+s['updated_utc']+': Terminal ensemble, all120conditional cases and browser report completed. Continue owner task; this milestone does not finish the broader goal.\n')
except Exception as e:
 s.update(status='needs_inspection',error=str(e));save();raise
