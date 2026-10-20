"""Extend the saved antenna comparison to the completed broader million."""
from pathlib import Path
import datetime as dt,json,os,subprocess,urllib.request
B=Path(__file__).resolve().parent;R=Path('/jackbox/home/MH370');p=B/'antenna-broader-million-status.json';assert not p.exists()
base=json.loads((B/'antenna-enlarged-status.json').read_text());new=json.loads((B/'broader-million-status.json').read_text());assert new['status']=='completed'
s={k:base[k] for k in ['executable','executable_sha256']};s.update(status='prepared',runs=[],created_utc=dt.datetime.now(dt.timezone.utc).isoformat())
for old,run in zip(base['runs'],new['runs']):
 cfg=json.loads(Path(old['config']).read_text());cfg['source_run']=run['output'];name='antenna-broader-170000-seed-'+str(run['seed']);cp=B/(name+'.json');cp.write_text(json.dumps(cfg,indent=2)+'\n')
 s['runs'].append(dict(family=old['family'],seed=run['seed'],config=str(cp),output=str(B/'antenna-runs'/name),source_output=run['output'],status='prepared'))
p.write_text(json.dumps(s,indent=2)+'\n');subprocess.run(['python3',str(B/'run_antenna_conditions.py'),str(p)],check=True)
preview=R/'mh370-antenna-comparison.html';statuses=[str(B/x) for x in ['antenna-baseline-status.json','antenna-relaxation-status.json','antenna-enlarged-status.json','antenna-broader-million-status.json']]
subprocess.run(['/tmp/mh370-acoustic-venv/bin/python',str(R/'crates/reporting/scripts/antenna_sensitivity_report.py'),'--statuses',*statuses,'--output',str(B/'antenna-comparison'),'--inline-output',str(preview)],env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1'),check=True)
web=Path('/jackbox/home/.iso/thread-storage/thr_rzreetwcyu/overnight-analysis/web')/preview.name;web.write_bytes(preview.read_bytes());assert urllib.request.urlopen('http://127.0.0.1:8771/overnight/'+preview.name).read()==preview.read_bytes()
