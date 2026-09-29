"""Recover and verify exact histories from selected completed replicates."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess

B = Path(__file__).resolve().parent
PATH = B / 'history-replay-status.json'


def save(state):
    state['updated_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
    temporary=PATH.with_suffix('.tmp');temporary.write_text(json.dumps(state,indent=2)+'\n');temporary.replace(PATH)


def main():
    state=json.loads(PATH.read_text())
    assert state['status']=='prepared', 'Inspect previous execution before restarting'
    state.update(status='running',driver_pid=os.getpid());save(state)
    try:
        for run in state['runs']:
            output=Path(run['output'])
            assert not output.exists(), 'Never overwrite an existing replay'
            assert hashlib.sha256(Path(state['executable']).read_bytes()).hexdigest()==state['executable_sha256']
            command=[state['executable'],'estimate-branching-flight','--config',run['config'],'--output',str(output),'--threads','4']
            run.update(status='running',command=command)
            with (B/f'history-replay-seed-{run["seed"]}.log').open('x') as log:
                child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,cwd='/tmp/mh370-branching-filter')
                run['pid']=child.pid;save(state)
                code=child.wait()
            if code: raise RuntimeError(f'Replay seed {run["seed"]} failed with return code {code}')
            source=json.loads((Path(run['source'])/'summary.json').read_text())
            result=json.loads((output/'summary.json').read_text())
            examples=json.loads((output/'trajectory-examples.json').read_text())
            if source['posterior_csv_sha256']!=result['posterior_csv_sha256'] or source['log_evidence']!=result['log_evidence']:
                raise RuntimeError('Replay changed original endpoint probability output')
            run.update(status='completed',posterior_csv_byte_identical=True,log_evidence_identical=True,
                       elapsed_seconds=result['elapsed_seconds'],exact_contact_state_checks=examples['exact_replay_checks'],
                       examples=len(examples['examples']),positive_latitude_bins=len(examples['bins']))
            save(state)
            text=(state['updated_utc']+f': Exact history recovery seed {run["seed"]} complete in {result["elapsed_seconds"]:.2f}s; '
                  f'posterior CSV and log evidence identical to original, {examples["exact_replay_checks"]} full contact-state/likelihood matches. '
                  'Illustrative paths and all positive-particle ancestral contact mappings retained; no additional independent candidates counted.')
            print(text,flush=True)
            with (B/'progress.md').open('a') as f:f.write('\n'+text+'\n')
        state['status']='completed';save(state)
    except BaseException as error:
        state.update(status='needs_inspection',error=str(error));save(state);raise


if __name__=='__main__':main()
