"""Finish the fixed proposal comparison, verify weights and publish its finding."""
import csv,datetime as dt,hashlib,json,os,subprocess,sys,time
from pathlib import Path
import numpy as np
B=Path(__file__).parent;D=B/'terminal-proposal-refresh';R=Path('/jackbox/home/MH370');PY='/tmp/mh370-acoustic-venv/bin/python'
sys.path.insert(0,str(R/'crates/reporting/scripts'))
from cruise_impact_report import validate_numerical_comparison
from final_contact_report import LABELS,maximum_cdf_gap
from flight_drift_report import FAMILIES,metrics
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=lambda:dt.datetime.now(dt.timezone.utc).isoformat()
def write(p,v):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n');t.replace(p)
def status(text,finished=False):
 write(B.parent/'overnight-analysis/web/mh370-running-status.json',dict(checked_utc=now(),comparison_finished=finished,jobs=[dict(title=text,recorded_status='completed' if finished else 'verifying/reporting',driver_alive=not finished,driver_pid=os.getpid(),worker_alive=not finished,completed_runs=2,planned_runs=2)]))
def command(args,name):
 with (D/(name+'.log')).open('w') as stream:subprocess.run(args,cwd=R,stdout=stream,stderr=subprocess.STDOUT,check=True,env={**os.environ,'MH370_REPORT_PYTHON':PY,'OPENBLAS_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'})
if (D/'comparison.json').exists():raise RuntimeError('Comparison already exists; no unchanged repeat')
while True:
 state=read(D/'progress.json')
 if state['status']=='conditioned':break
 if state['status']=='failed':raise RuntimeError('Sampling failed; no automatic retry')
 try:os.kill(state['driver_pid'],0)
 except ProcessLookupError:raise RuntimeError('Sampler owner vanished before completion; inspect saved work')
 time.sleep(3)
started=time.perf_counter()
try:
 status('Checking the two completed terminal-proposal pilots independently')
 command([PY,str(B/'verify_final_contacts.py'),str(D)],'independent-likelihoods')
 verify=read(D/'independent-verification.json');assert verify['status']=='passed'
 old=read(B/'joint-terminal-replication-status.json')['runs'];inputs=[('Original guide A',Path(old[0]['conditional_output'])),('Original guide B',Path(old[1]['conditional_output']))]+[(r['label'],Path(r['conditioned'])) for r in state['runs']]
 baseline=read(inputs[0][1]/'summary.json');results=[];hashes={}
 for label,parent in inputs:
  summary=read(parent/'summary.json');hashes[str(parent/'summary.json')]=sha(parent/'summary.json')
  if label!='Original guide A':validate_numerical_comparison(baseline,summary)
  assert summary['source_configuration']['draws_per_source']==2048
  for family in summary['families']:
   for case in family['cases']:
    if case['name'] not in LABELS:continue
    path=parent/case['weights_file'];assert sha(path)==case['weights_sha256']
    with path.open() as f:rows=[r for r in csv.DictReader(f) if r['impact_latitude_deg'] and float(r['conditional_weight'])>0]
    points=np.array([(float(r['impact_latitude_deg']),float(r['impact_longitude_deg'])) for r in rows]);w=np.array([float(r['conditional_weight']) for r in rows]);w/=w.sum();roots=np.array([(int(r['source_index']),int(r['root_id'])) for r in rows])
    results.append(dict(run=label,family=family['name'],case=case['name'],metrics=metrics(points,w,roots),latitude=points[:,0],impact_minutes=np.array([float(r['impact_time_s'])/60 for r in rows]),weight=w,source_csv_sha256=case['weights_sha256']))
 comparisons=[]
 for family in FAMILIES:
  for case in LABELS:
   group=[next(r for r in results if r['family']==family and r['case']==case and r['run']==label) for label,_ in inputs]
   comparisons.append(dict(family=family,case=case,label=LABELS[case],original_latitude_cdf_gap=maximum_cdf_gap(group[0],group[1],'latitude'),refreshed_latitude_cdf_gap=maximum_cdf_gap(group[2],group[3],'latitude'),original_impact_time_cdf_gap=maximum_cdf_gap(group[0],group[1],'impact_minutes'),refreshed_impact_time_cdf_gap=maximum_cdf_gap(group[2],group[3],'impact_minutes'),original_effective_impact_rows=[g['metrics']['row_weight_effective_count'] for g in group[:2]],refreshed_effective_impact_rows=[g['metrics']['row_weight_effective_count'] for g in group[2:]],refreshed_largest_ancestor_share=[g['metrics']['largest_ancestor_share'] for g in group[2:]]))
 result=dict(status='checked numerical comparison',generated_utc=now(),families=FAMILIES,comparisons=comparisons,draws_per_cruise_source=2048,cruise_sources=6,physical_and_observation_configuration_checks='passed',source_summaries=hashes,independent_weight_verification_sha256=sha(D/'independent-verification.json'),proposal_verification=state['proposal_verification'],sampling_elapsed_seconds=sum(r['elapsed_seconds'] for r in state['runs']),postprocessing_elapsed_seconds=time.perf_counter()-started,promoted_to_default=False,note='This comparison measures numerical efficiency only. The new guide is not made the default by completion of these runs; no fixed CDF-gap threshold or physical-model odds are used. Read each conditional case and both aerodynamic models separately.')
 write(D/'comparison.json',result)
 status('Proposal comparison checked; updating the final-contact report')
 command([str(R/'target/iteration/mh370'),'report-final-contacts','--analysis',str(B),'--output',str(B/'final-contact-report'),'--inline-output',str(R/'mh370-final-contacts.html')],'report')
 command(['node',str(B/'verify_final_contact_browser.cjs')],'browser-check')
 command([PY,str(R/'crates/reporting/scripts/report_index.py'),'--analysis',str(B),'--inline-output',str(R/'mh370-results.html')],'index')
 write(D/'completion.json',dict(status='completed',completed_utc=now(),comparison_sha256=sha(D/'comparison.json'),postprocessing_elapsed_seconds=time.perf_counter()-started))
 status('Final-contact and combined evidence maps complete; proposal comparison checked and reported',finished=True)
 for p in [B/'progress.md',B.parent/'overnight-analysis/progress.md']:
  with p.open('a') as f:f.write('\n'+now()+': Two refreshed-guide terminal pilots, independent likelihood verification, comparison against equal-size original-guide runs, and browser refresh completed. See terminal-proposal-refresh/comparison.json. No default proposal change or validated posterior claim; the full estimator/paper objective remains unfinished. No numerical job remains in this fixed queue.\n')
except Exception as e:
 write(D/'completion.json',dict(status='failed',error=repr(e),checked_utc=now()));status('Proposal postprocessing stopped; inspect the recorded error before any retry',finished=True);raise
