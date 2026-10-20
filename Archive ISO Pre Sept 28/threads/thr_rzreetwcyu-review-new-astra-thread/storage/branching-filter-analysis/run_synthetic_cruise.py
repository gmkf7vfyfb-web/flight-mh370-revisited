"""Run the pre-generated recovery design without giving truth to inference."""
from pathlib import Path
import argparse
import datetime as dt
import hashlib
import json
import os
import resource
import subprocess
import time

B = Path(__file__).resolve().parent
R = Path('/jackbox/home/MH370')
D = B / 'synthetic-cruise-recovery'
P = B / 'synthetic-cruise-status.json'
EXE = B / 'synthetic-cruise-executable'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
now = lambda: dt.datetime.now(dt.timezone.utc).isoformat()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--design',type=Path,default=D/'design.json')
    parser.add_argument('--state',type=Path,default=P)
    parser.add_argument('--after-state',type=Path)
    parser.add_argument('--report-directory',type=Path,default=B/'synthetic-cruise-comparison')
    parser.add_argument('--inline-output',type=Path,default=R/'mh370-synthetic-recovery.html')
    parser.add_argument('--executable',type=Path,default=EXE)
    parser.add_argument('--resume-unstarted',action='store_true')
    args=parser.parse_args();status_path=args.state
    previous=None
    if args.resume_unstarted:
        previous=json.loads(status_path.read_text())
        assert previous['status'] in ['needs_inspection','waiting_for_numerical_workers'] and not previous['runs'] and not previous.get('current')
        old_process=Path('/proc')/str(previous.get('driver_pid',0))/'cmdline'
        assert not old_process.exists() or not old_process.read_bytes(), 'Previous unstarted driver is still live'
    else:
        assert not status_path.exists(), 'Inspect previous state; do not relaunch a run'
    design = json.loads(args.design.read_text())
    assert design['status'] == 'prepared_before_inference'
    executable=args.executable
    assert sha(executable) == design['executable_sha256']
    state = dict(status='running', design=str(args.design), design_sha256=sha(args.design),
                 executable=str(executable), executable_sha256=sha(executable), threads=4,
                 started_utc=now(), driver_pid=os.getpid(), completed_pairs=0, runs=[])
    if previous is not None:state['previous_unstarted_orchestration_attempt']=previous
    def save():
        state['updated_utc'] = now()
        tmp = status_path.with_suffix('.tmp')
        tmp.write_text(json.dumps(state, indent=2) + '\n')
        tmp.replace(status_path)
    def event(message):
        with (B / 'progress.md').open('a') as f:
            f.write('\n' + now() + ': ' + message + '\n')
    save()
    try:
        if args.after_state:
            state.update(status='waiting_for_numerical_workers',after_state=str(args.after_state));save()
            while True:
                previous=json.loads(args.after_state.read_text())
                if previous['status']=='completed':break
                if previous['status'] in ['needs_inspection','dependency_needs_inspection']:
                    raise RuntimeError('Preceding task needs inspection')
                time.sleep(10)
            state['status']='running';save()
        for fixture in design['fixtures']:
            for run in fixture['runs']:
                cfg = Path(run['configuration'])
                output = Path(run['output'])
                assert sha(cfg) == run['configuration_sha256']
                config = json.loads(cfg.read_text())
                assert sha(config['inputs']['observations']) == fixture['observations_sha256']
                assert (config['model']['fuel'] is not None) == bool(design.get('fuel_condition_enabled'))
                bank_path=config['initial_operating_proposal']
                if bank_path is not None:
                    assert design['initial_proposal_strategy']=='observation_only_completed_pilots'
                    assert sha(bank_path)==fixture['initial_proposal_sha256']
                    bank=json.loads(Path(bank_path).read_text())
                    assert bank['source_identity']['inputs']['observations']==fixture['observations_sha256']
                else:
                    assert not fixture.get('initial_proposal_sha256')
                assert not output.exists(), 'Refusing existing output'
                command = [str(executable), 'estimate-cruise', '--config', str(cfg),
                           '--output', str(output), '--threads', '4']
                current = dict(run, truth_seed=fixture['truth_seed'], status='running',
                               started_utc=now(), command=command)
                state['current'] = current
                started = time.monotonic()
                with output.with_suffix('.log').open('x') as log:
                    child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, cwd=R)
                    current['pid'] = child.pid
                    save()
                    code = child.wait()
                current.update(returncode=code, elapsed_seconds=time.monotonic() - started,
                               finished_utc=now(), peak_child_rss_kb=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)
                summary_path = output / 'summary.json'
                summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}
                if code and summary.get('status') != 'completed_zero_support':
                    current['status'] = 'needs_inspection'
                    raise RuntimeError('Inference error; no automatic rerun: ' + str(output))
                current.update(status='completed' if not code else 'completed_zero_support', summary=summary)
                if not code:
                    assert summary['initial_particles'] == design['initial_candidates_per_run']
                    assert summary['posterior_available'] and sha(output / 'posterior.csv') == summary['posterior_csv_sha256']
                state['runs'].append(current)
                state.pop('current')
                save()
            state['completed_pairs'] += 1
            if state['completed_pairs'] == len(design['fixtures']):
                state.update(status='completed',finished_utc=now())
            save()
            event(f"Synthetic recovery pair {state['completed_pairs']}/{len(design['fixtures'])} complete at {design['initial_candidates_per_run']} candidates per run; truth seed {fixture['truth_seed']}. These are controls, not additional MH370 candidates.")
            reporter = R / 'crates/reporting/scripts/synthetic_cruise_report.py'
            if reporter.exists():
                result = subprocess.run(['/tmp/mh370-acoustic-venv/bin/python', str(reporter),
                    '--state', str(status_path), '--output', str(args.report_directory),
                    '--inline-output', str(args.inline_output)],
                    capture_output=True, text=True, env=dict(os.environ, OPENBLAS_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1'))
                state['latest_report_returncode'] = result.returncode
                if result.returncode: state['latest_report_error'] = result.stderr[-3000:]
                save()
        state.update(status='completed', finished_utc=now())
        save()
        event(f"All {len(design['fixtures'])} synthetic data sets and {2*len(design['fixtures'])} inference runs completed at {design['initial_candidates_per_run']} candidates per run; assess coverage and numerical variation before any broader claim.")
    except BaseException as error:
        state.update(status='needs_inspection', error=str(error))
        save()
        raise


if __name__ == '__main__':
    main()
