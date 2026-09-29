"""Render the completed source-conditioned comparisons and check served bytes."""
from pathlib import Path
import argparse,datetime as dt,json,os,subprocess,urllib.request
B=Path(__file__).resolve().parent;R=Path('/jackbox/home/MH370')
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--state',type=Path,default=B/'spatial-comparison-status.json');p.add_argument('--suffix',default='');a=p.parse_args()
s=json.loads(a.state.read_text());assert s['status']=='completed'
for category in ['drift','pleiades']:
 preview=R/('mh370-'+category+'-comparison.html')
 subprocess.run(['/tmp/mh370-acoustic-venv/bin/python',str(R/'crates/reporting/scripts/spatial_evidence_report.py'),'--state',str(a.state),'--category',category,'--output',str(B/(category+a.suffix+'-comparison')),'--inline-output',str(preview)],check=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1'))
 web=Path('/jackbox/home/.iso/thread-storage/thr_rzreetwcyu/overnight-analysis/web')/preview.name;web.write_bytes(preview.read_bytes());assert urllib.request.urlopen('http://127.0.0.1:8771/overnight/'+preview.name).read()==preview.read_bytes()
 with (B/'progress.md').open('a') as f:f.write('\n'+dt.datetime.now(dt.timezone.utc).isoformat()+': '+category+' comparison report generated and localHTTP200byte-match checked. Scientific weights and support limitations remain in the native output.\n')
 if category=='drift':
  companion=preview.with_name('mh370-stokes-comparison.html');served=web.with_name(companion.name);served.write_bytes(companion.read_bytes());assert urllib.request.urlopen('http://127.0.0.1:8771/overnight/'+served.name).read()==companion.read_bytes()
