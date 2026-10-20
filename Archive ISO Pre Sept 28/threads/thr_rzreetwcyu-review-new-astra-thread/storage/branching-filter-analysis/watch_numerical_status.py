"""Publish actual process status for the fixed active comparison; no job launches."""
from pathlib import Path
import datetime as dt
import json, time, os
B=Path(__file__).parent
DEST=B.parent/'overnight-analysis/web/mh370-running-status.json'
TASKS=[('Original sampler, larger fuel controls','synthetic-cruise-larger-fuel-status.json'),
       ('Revised sampler, larger fuel controls','synthetic-cruise-command-path-larger-status.json'),
       ('Manoeuvre-rate sampling control','synthetic-cruise-rate-partition-status.json'),
       ('500,000-candidate fuel recovery controls','synthetic-cruise-high-effort-fuel-status.json'),
       ('Independent command-rate prior controls','synthetic-cruise-independent-rates-status.json')]
def alive(pid, executable=None):
    if not pid:return False
    try:
        args=(Path('/proc')/str(pid)/'cmdline').read_bytes().split(b'\0')
        return bool(args[0]) and (executable is None or args[0].decode()==executable)
    except (FileNotFoundError,PermissionError,ProcessLookupError):return False
while True:
    jobs=[]
    for title, name in TASKS:
        state=json.loads((B/name).read_text())
        current=state.get('current',{})
        worker_alive=alive(current.get('pid'),state['executable'])
        driver_alive=alive(state.get('driver_pid'))
        design=json.loads(Path(state['design']).read_text())
        job={'title':title,'recorded_status':state['status'],'completed_runs':len(state['runs']),
             'planned_runs':sum(len(f['runs']) for f in design['fixtures']),
             'candidates_per_run':design['initial_candidates_per_run'],
             'worker_alive':worker_alive,'driver_alive':driver_alive,
             'running_seed':current.get('inference_seed') if worker_alive else None,
             'run_started_utc':current.get('started_utc') if worker_alive else None}
        jobs.append(job)
    terminal=all(j['recorded_status'] in ['completed','deferred_by_owner','needs_inspection','dependency_needs_inspection'] for j in jobs)
    snapshot={'checked_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'jobs':jobs,
              'comparison_finished':terminal,'scope':'This fixed numerical comparison only; not completion of the estimator/paper objective.'}
    tmp=DEST.with_suffix('.tmp');tmp.write_text(json.dumps(snapshot,indent=2)+'\n');tmp.replace(DEST)
    if terminal:break
    time.sleep(15)
