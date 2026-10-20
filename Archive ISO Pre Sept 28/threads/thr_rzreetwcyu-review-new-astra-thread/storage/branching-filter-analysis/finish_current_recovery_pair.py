"""Finish recording one already-running child after the owner deferred its queue."""
from pathlib import Path
import datetime as dt, hashlib, json, os, signal, subprocess, time
B=Path(__file__).resolve().parent;R=Path('/jackbox/home/MH370')
P=B/'synthetic-cruise-high-effort-fuel-status.json'
now=lambda:dt.datetime.now(dt.timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
s=json.loads(P.read_text());current=s['current'];driver=s['driver_pid'];child=current['pid']
assert current['inference_seed']==37111901 and len(s['runs'])==1 and s['driver_control_state']=='stopped_while_current_child_finishes'
assert str(P).encode() in (Path('/proc')/str(driver)/'cmdline').read_bytes()
def save():
    s['updated_utc']=now();tmp=P.with_suffix('.tmp');tmp.write_text(json.dumps(s,indent=2)+'\n');tmp.replace(P)
s['completion_recorder_pid']=os.getpid();save();peak=0
while True:
    process=Path('/proc')/str(child)
    try:
        lines=(process/'status').read_text().splitlines()
        state=next(v for v in lines if v.startswith('State:')).split()[1]
        if state=='Z':break
        assert (process/'cmdline').read_bytes().split(b'\0')[0].decode()==s['executable']
        hwm=next((v.split()[1] for v in lines if v.startswith('VmHWM:')),None)
        if hwm is not None:peak=max(peak,int(hwm))
    except FileNotFoundError:break
    time.sleep(10)
output=Path(current['output']);summary_path=output/'summary.json'
try:
    summary=json.loads(summary_path.read_text())
    assert summary['posterior_available'] and summary['initial_particles']==500000
    assert sha(output/'posterior.csv')==summary['posterior_csv_sha256']
    current.update(status='completed',summary=summary,finished_utc=now(),
        elapsed_seconds=summary['elapsed_seconds'],observed_peak_child_rss_kb=peak,
        completion_basis='Completed summary and independently checked posterior checksum; child exit code not reaped by this recorder.')
    s['runs'].append(current);s.pop('current');s['completed_pairs']=1
    s.update(status='deferred_by_owner',driver_control_state='terminated_after_current_pair',
        remaining_unstarted_runs=6,finished_current_pair_utc=now())
except Exception as error:
    s.update(status='needs_inspection',error='Current-pair completion verification: '+str(error))
# The original driver remains stopped, so it cannot start an additional child.
assert str(P).encode() in (Path('/proc')/str(driver)/'cmdline').read_bytes()
os.kill(driver,signal.SIGTERM);os.kill(driver,signal.SIGCONT);save()
if s['status']=='deferred_by_owner':
    command=['/tmp/mh370-acoustic-venv/bin/python',str(R/'crates/reporting/scripts/synthetic_cruise_report.py'),
        '--state',str(P),'--output',str(B/'synthetic-cruise-high-effort-fuel-comparison'),
        '--inline-output',str(R/'mh370-synthetic-high-effort-fuel-recovery.html')]
    done=subprocess.run(command,capture_output=True,text=True,env=dict(os.environ,OPENBLAS_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1'))
    s['latest_report_returncode']=done.returncode
    if done.returncode:s['latest_report_error']=done.stderr[-3000:]
    save()
    if not done.returncode:
        subprocess.run(['/tmp/mh370-acoustic-venv/bin/python',str(R/'crates/reporting/scripts/report_index.py'),
            '--analysis',str(B),'--inline-output',str(R/'mh370-results.html')],check=True,
            env=dict(os.environ,OPENBLAS_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1'))
with (B/'progress.md').open('a') as f:
    f.write('\n'+now()+': Current500k recovery pair recorded; remaining six runs deferred under Pete\'s antenna/drift priority. Status '+s['status']+'. The original driver is terminated; no additional recovery inference launched.\n')
