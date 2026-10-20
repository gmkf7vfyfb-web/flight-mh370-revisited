"""Execute a frozen, explicit model-comparison queue independently of chat liveness."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import sys

B = Path(__file__).resolve().parent
STATE = Path(sys.argv[1]) if len(sys.argv)>1 else B / 'relaxation-status.json'

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save(state):
    state['updated_utc'] = now()
    temporary = STATE.with_suffix('.tmp')
    temporary.write_text(json.dumps(state, indent=2) + '\n')
    temporary.replace(STATE)

def event(message):
    line = now() + ': ' + message
    print(line, flush=True)
    with (B / 'progress.md').open('a') as file:
        file.write('\n' + line + '\n')

def main():
    state = json.loads(STATE.read_text())
    assert state['status'] == 'prepared', 'Inspect state before restarting; never duplicate runs'
    state.update(status='running', driver_pid=os.getpid(), started_utc=now())
    save(state)
    try:
        for run in state['runs']:
            output = Path(run['output'])
            assert not output.exists(), 'Existing output must not be overwritten'
            assert sha(state['executable']) == state['executable_sha256']
            assert sha(run['config']) == run['configuration_sha256']
            configuration=json.loads(Path(run['config']).read_text())
            initial_candidates=configuration['roots_per_mode']*len(configuration['modes'])
            command = [state['executable'], 'estimate-branching-flight', '--config', run['config'],
                       '--output', str(output), '--threads', str(state['threads'])]
            started = time.monotonic()
            run.update(status='running', command=command, started_utc=now())
            with (B / (output.name + '.log')).open('x') as log:
                child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                                         cwd='/tmp/mh370-branching-filter')
                run['pid'] = child.pid
                save(state)
                event(f"Sensitivity {run['family']}, seed {run['seed']}: {initial_candidates:,} candidates running, PID {child.pid}.")
                code = child.wait()
            run.update(returncode=code, process_elapsed_seconds=time.monotonic()-started)
            if code:
                run['status'] = 'failed'
                raise RuntimeError(f"{output.name} failed, return code {code}; no automatic rerun")
            summary = json.loads((output / 'summary.json').read_text())
            assert summary['posterior_available'] and summary['initial_particles'] == initial_candidates
            assert sha(output / 'posterior.csv') == summary['posterior_csv_sha256']
            trace = json.loads((output / 'trajectory-examples.json').read_text())
            assert trace['full_contact_state_and_likelihood_match']
            run.update(status='completed', finished_utc=now(), summary=summary,
                       exact_replay_checks=trace['exact_replay_checks'])
            save(state)
            event(f"Sensitivity {run['family']}, seed {run['seed']} completed in {summary['elapsed_seconds']:.2f}s, with exact trace checks. Model-specific comparison follows.")
        state.update(status='sampling_completed', finished_utc=now())
        save(state)
        event('Initial manoeuvre-relaxation comparison queue completed. All model families remain separate; further work is not stopped by this milestone.')
    except BaseException as error:
        state.update(status='needs_inspection', error=str(error))
        save(state)
        event('Sensitivity queue needs inspection: ' + str(error))
        raise

if __name__ == '__main__':
    main()
