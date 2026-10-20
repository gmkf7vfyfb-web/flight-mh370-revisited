"""Durably execute the frozen additional MH370 replicates, without agent liveness."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import argparse

B = Path(__file__).resolve().parent
STATE = B / 'million-extension.json'
BINARY = Path('/tmp/mh370-branching-filter/target/release/mh370')


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(state):
    state['updated_utc'] = now()
    temp = STATE.with_suffix('.tmp')
    temp.write_text(json.dumps(state, indent=2) + '\n')
    temp.replace(STATE)


def event(message):
    line = now() + ': ' + message
    print(line, flush=True)
    with (B / 'progress.md').open('a') as f:
        f.write('\n' + line + '\n')


def main():
    global STATE, BINARY
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state',type=Path,default=STATE)
    STATE=parser.parse_args().state
    state = json.loads(STATE.read_text())
    BINARY=Path(state.get('executable',str(BINARY)))
    if state['status'] != 'prepared':
        raise RuntimeError('Not a fresh prepared extension; inspect saved state before resuming.')
    state.update(status='running', started_utc=now(), driver_pid=os.getpid())
    save(state)
    try:
        if state.get('after_state'):
            state['status']='waiting_for_numerical_workers';save(state)
            while True:
                previous=json.loads(Path(state['after_state']).read_text())
                if previous['status']=='completed':break
                if previous['status'] in ['needs_inspection','dependency_needs_inspection']:
                    raise RuntimeError('Preceding numerical task needs inspection')
                time.sleep(10)
            state['status']='running';save(state)
        for item in state['additional_runs']:
            cfg = Path(item['config'])
            output = Path(item['output'])
            if output.exists():
                raise RuntimeError(f'Refusing to overwrite or rerun existing output: {output}')
            if sha(BINARY) != state['executable_sha256'] or sha(cfg) != item['configuration_sha256']:
                raise RuntimeError('Frozen binary or configuration changed')
            config = json.loads(cfg.read_text())
            actual_proposal=sha(config['initial_operating_proposal']) if config['initial_operating_proposal'] else None
            if actual_proposal != item['proposal_sha256']:
                raise RuntimeError('Frozen proposal bank changed')
            command = [str(BINARY), state.get('command','estimate-branching-flight'), '--config', str(cfg),
                       '--output', str(output), '--threads', '4']
            item.update(status='running', started_utc=now(), command=command)
            started = time.monotonic()
            with Path(item['log']).open('x') as log:
                child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                                         cwd=state.get('working_directory','/tmp/mh370-branching-filter'))
                item['pid'] = child.pid
                state['active_seed'] = item['seed']
                save(state)
                event(f'{state.get("label","Million-candidate extension")}: seed {item["seed"]} started, PID {child.pid}; '
                      f'{state["completed_initial_candidates"]:,} initial candidates completed so far.')
                code = child.wait()
            item.update(returncode=code, finished_utc=now(), process_elapsed_seconds=time.monotonic()-started)
            if code != 0:
                item['status'] = 'failed'
                raise RuntimeError(f'Seed {item["seed"]} returned {code}; no automatic rerun.')
            summary = json.loads((output / 'summary.json').read_text())
            provenance = json.loads((output / 'provenance.json').read_text())
            if not summary.get('posterior_available') or summary['initial_particles'] != item.get('initial_candidates',85000):
                raise RuntimeError('Run did not produce the specified completed estimate')
            if sha(output / 'posterior.csv') != summary['posterior_csv_sha256']:
                raise RuntimeError('Posterior checksum mismatch')
            if provenance['scientific_source_sha256'] != state['scientific_source_sha256']:
                raise RuntimeError('Scientific source mismatch')
            item.update(status='completed', summary=summary)
            state['completed_initial_candidates'] += summary['initial_particles']
            state['active_seed'] = None
            save(state)
            event(f'{state.get("label","Million-candidate extension")}: seed {item["seed"]} completed in '
                  f'{summary["elapsed_seconds"]:.2f} s; '
                  f'{state["completed_initial_candidates"]:,} total initial candidates. '
                  'This is a finite conditional estimate; no numerical precision threshold used to stop sampling.')
        state.update(status=state.get('completion_status','sampling_completed'), finished_utc=now(), active_seed=None)
        save(state)
        event(state.get('completion_note','All nine extension replicates completed. Total 1,020,000 initial candidates; pooled reporting follows.'))
        if state.get('report_command'):
            report=subprocess.run(state['report_command'],capture_output=True,text=True)
            state['report_returncode']=report.returncode
            if report.returncode:state['report_error']=report.stderr[-3000:]
            save(state)
    except BaseException as error:
        state.update(status='needs_inspection', error=str(error))
        save(state)
        event('Extension needs inspection: ' + str(error))
        raise


if __name__ == '__main__':
    main()
