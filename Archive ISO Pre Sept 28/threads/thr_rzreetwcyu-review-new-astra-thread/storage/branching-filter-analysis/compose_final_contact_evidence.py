"""Compose a completed terminal comparison with fixed drift/search inputs.

Uses the canonical runner and independently checks both searched-area updates
and the four-case mixture. Never samples aircraft/ocean paths or retries outputs.
"""
import argparse,copy,datetime as dt,hashlib,json,os,subprocess,time,tomllib
from pathlib import Path
B=Path(__file__).parent;R=Path('/jackbox/home/MH370');PY='/tmp/mh370-acoustic-venv/bin/python';EXE=R/'target/iteration/mh370'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def write(p,v):
 q=p.with_suffix('.tmp');q.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n');q.replace(p)
parser=argparse.ArgumentParser();parser.add_argument('--contacts',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();D=args.output
contacts=read(args.contacts/'progress.json');assert contacts['status']=='completed' and len(contacts['runs'])==2
assert read(args.contacts/'independent-verification.json')['status']=='passed'
if (args.contacts/'parent-weight-verification.json').exists():assert read(args.contacts/'parent-weight-verification.json')['status']=='passed'
if D.exists():raise RuntimeError('Existing composition must be inspected; no automatic rerun')
D.mkdir();state=dict(status='composing',driver_pid=os.getpid(),started_utc=now(),completed=[],new_flight_or_ocean_samples=0,executable_sha256=sha(EXE),source_code_sha256=sha(__file__),contact_progress_sha256=sha(args.contacts/'progress.json'))
suite=read(B/'mixed-terminal-sampling/search-seed-37094011.json')
mixture_template=read(B/'impact-model-mixture.json');case_names=[c['name'] for c in mixture_template['groups'][0]['components']]
assert len(case_names)==4 and len(set(case_names))==4
parents=[p for p in suite['populations'] if p['metadata']['evidence_variant']=='nine-recoveries'];assert len(parents)==4

def status(title,worker=None):
 state['checked_utc']=now();write(D/'progress.json',state);done=state['status'] in ['completed','failed']
 write(B.parent/'overnight-analysis/web/mh370-running-status.json',dict(checked_utc=state['checked_utc'],comparison_finished=done,jobs=[dict(title=title,recorded_status=state['status'],driver_alive=not done,driver_pid=os.getpid(),worker_alive=worker is not None,worker_pid=worker,completed_runs=len(state['completed']),planned_runs=32)]))

def command(arguments,label):
 start=time.monotonic()
 with (D/(label+'.log')).open('x') as stream:
  child=subprocess.Popen(arguments,cwd=R,env={**os.environ,'OPENBLAS_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'},stdout=stream,stderr=subprocess.STDOUT)
  while True:
   pid,wait,usage=os.wait4(child.pid,os.WNOHANG)
   if pid:child.returncode=os.waitstatus_to_exitcode(wait);break
   status(label,child.pid);time.sleep(.5)
 resource=dict(command=arguments,elapsed_seconds=time.monotonic()-start,peak_rss_kib=usage.ru_maxrss,user_cpu_seconds=usage.ru_utime,system_cpu_seconds=usage.ru_stime,exit_code=child.returncode)
 write(D/(label+'-resources.json'),resource)
 if child.returncode:raise RuntimeError('Inspect '+str(D/(label+'.log')))

started=time.monotonic();status('Composing completed terminal runs with the same nine recovered objects')
try:
 populations=[];groups=[]
 for run in contacts['runs']:
  assert sha(Path(run['conditioned'])/'summary.json')==run['summary_sha256']
  for parent in parents:
   oldmeta=parent['metadata'];meta=dict(oldmeta,numerical_run=run['label'],terminal_seed=run['seed'])
   cfgpath=Path(parent['path']).parent.with_suffix('.toml');cfg=tomllib.loads(cfgpath.read_text())
   group=dict(id=str(run['seed'])+'--'+meta['terminal_family']+'--cowling-'+str(meta['cowling_seed']),metadata={k:v for k,v in meta.items() if k!='evidence_variant'},components=[])
   for case in case_names:
    name=str(run['seed'])+'--'+meta['terminal_family']+'--'+case+'--cowling-'+str(meta['cowling_seed'])
    text=cfgpath.read_text().replace(cfg['name'],name).replace(cfg['terminal_conditioned_source']['directory'],run['conditioned']).replace('r600-no-startup-offset',case)
    modified=tomllib.loads(text);assert modified['model']==cfg['model'];assert modified['relative_likelihood_floor']==cfg['relative_likelihood_floor']==0
    p=D/(name+'.toml');p.write_text(text);dest=D/name
    command([str(EXE),'apply-conditional-surface','--config',str(p),'--output',str(dest)],name)
    result=dest/'conditional-spatial-sensitivity.json';item=dict(id=name,path=str(result),sha256=sha(result),weight_field='conditional_weight',metadata=dict(meta,contact_case=case))
    populations.append(item);state['completed'].append(item)
    group['components'].append(dict(name=case,probability=.25,search_population=str(D/'search-conditioned'/(name+'.json')),terminal_summary=str(Path(run['conditioned'])/'summary.json')))
   groups.append(group)
 search=copy.deepcopy(suite);search['populations']=populations;search['conditions'][0]='Explicit final-contact alternatives with identical relaxed cruise, fuel, positive-lift terminal controls and nine recovered-object drift likelihoods. Numerical proposal corrections retain the original conditional target. Conditional on computed impacts and native drift support.'
 cp=D/'search-configuration.json';write(cp,search);state['status']='search-update'
 dest=D/'search-conditioned';command([str(EXE),'apply-searched-area-evidence','--config',str(cp),'--output',str(dest)],'search')
 state['search_manifest']=str(dest/'manifest.json');state['search_manifest_sha256']=sha(dest/'manifest.json');state['status']='verifying'
 command([PY,str(B/'verify_debris_search.py'),str(dest/'manifest.json')],'verify-search');assert read(dest/'independent-verification.json')['status']=='passed'
 for group in groups:
  for component in group['components']:component['sha256']=sha(component['search_population'])
 mixture=copy.deepcopy(mixture_template);mixture['groups']=groups
 cp=D/'mixture-configuration.json';write(cp,mixture);state['status']='model-mixture'
 dest=D/'model-mixture';command([str(EXE),'average-impact-models','--config',str(cp),'--output',str(dest)],'mixture')
 command([PY,str(R/'crates/reporting/scripts/tests/verify_impact_mixture.py'),'--manifest',str(dest/'manifest.json')],'verify-mixture')
 assert read(dest/'independent-verification.json')['status']=='passed'
 state.update(status='completed',completed_utc=now(),elapsed_seconds=time.monotonic()-started,mixture_manifest=str(dest/'manifest.json'),mixture_manifest_sha256=sha(dest/'manifest.json'))
 status('Parent-guided drift/search/case mixtures independently checked; owner assessment continues')
except Exception as error:
 state.update(status='failed',error=repr(error));status('Evidence composition stopped; inspect before a corrected continuation');raise
