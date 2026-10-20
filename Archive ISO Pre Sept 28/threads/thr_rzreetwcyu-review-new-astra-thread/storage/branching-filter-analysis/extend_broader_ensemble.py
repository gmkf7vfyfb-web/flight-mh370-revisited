"""Complete a million initial candidates under the broader existing physical prior."""
from pathlib import Path
import datetime as dt,hashlib,json,os,subprocess,urllib.request
B=Path(__file__).resolve().parent;P=B/'broader-million-status.json';old=json.loads((B/'enlarged-relaxation-status.json').read_text());assert old['status']=='sampling_completed';assert not P.exists()
s={k:old[k] for k in ['executable','executable_sha256','threads']};s.update(status='prepared',runs=[],created_utc=dt.datetime.now(dt.timezone.utc).isoformat(),purpose='Two independent170k runs finish1,020,000initial candidates under the unchanged16/8/8vertical-BFO model. This remains separate from the original4/2/2million.',total_compute_cap=None)
for base,seed in zip(old['runs'],[37091713,37091714]):
 c=json.loads(Path(base['config']).read_text());c['roots_per_mode']=34000;c['branching']['seed']=seed;c['name']='Broader16/8/8 cruise repeat:170,000initial candidates, seed'+str(seed)
 name='turns16-mach8-altitude8-vertical-bfo-170000-seed-'+str(seed);cfg=B/(name+'.json');assert not cfg.exists();cfg.write_text(json.dumps(c,indent=2)+'\n')
 s['runs'].append(dict(family=base['family'],counts=base['counts'],seed=seed,config=str(cfg),configuration_sha256=hashlib.sha256(cfg.read_bytes()).hexdigest(),output=str(B/'runs'/name),status='prepared'))
P.write_text(json.dumps(s,indent=2)+'\n')
subprocess.run(['python3',str(B/'run_sensitivity.py'),str(P)],check=True)
s=json.loads(P.read_text());assert s['status']=='sampling_completed'
terminal=json.loads((B/'terminal-ensemble-seed-37091811.json').read_text());sources=terminal['source_runs']+[r['output'] for r in s['runs']]
root=Path('/jackbox/home/MH370');preview=root/'mh370-broader-arc-density.html'
subprocess.run(['/tmp/mh370-acoustic-venv/bin/python',str(root/'crates/reporting/scripts/arc_density_report.py'),'--runs',*sources,'--output',str(B/'broader-arc-density'),'--inline-output',str(preview),'--baseline-runs','4'],env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1'),check=True)
web=Path('/jackbox/home/.iso/thread-storage/thr_rzreetwcyu/overnight-analysis/web')/preview.name;web.write_bytes(preview.read_bytes());assert urllib.request.urlopen('http://127.0.0.1:8771/overnight/'+preview.name).read()==preview.read_bytes()
s.update(status='completed',report=str(preview),updated_utc=dt.datetime.now(dt.timezone.utc).isoformat());P.write_text(json.dumps(s,indent=2)+'\n')
with (B/'progress.md').open('a') as f:f.write('\n'+s['updated_utc']+': Broader16/8/8one-millionpool and updated browser report complete. Continue remaining estimator work.\n')
