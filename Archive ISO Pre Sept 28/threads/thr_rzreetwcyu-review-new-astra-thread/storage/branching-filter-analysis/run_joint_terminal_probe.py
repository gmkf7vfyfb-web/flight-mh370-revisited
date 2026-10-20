"""Check the isolated joint proposal after earlier numerical jobs finish."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import os
import subprocess
import time
import argparse

B = Path(__file__).resolve().parent
P = B / 'joint-terminal-status.json'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state',type=Path,default=P)
    path=parser.parse_args().state
    state = json.loads(path.read_text())
    assert state['status'] == 'prepared'
    def save():
        state['updated_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
        tmp = path.with_suffix('.tmp')
        tmp.write_text(json.dumps(state, indent=2) + '\n')
        tmp.replace(path)
    state.update(status='waiting_for_numerical_workers', driver_pid=os.getpid())
    save()
    try:
        while True:
            predecessor = json.loads(Path(state['after_state']).read_text())
            if predecessor['status'] == 'completed': break
            if predecessor['status'] in ['needs_inspection', 'dependency_needs_inspection']:
                raise RuntimeError('Preceding task needs inspection')
            time.sleep(10)
        assert sha(state['executable']) == state['executable_sha256']
        state['status'] = 'running'
        save()
        for run in state['runs']:
            assert sha(run['config']) == run['configuration_sha256']
            assert not Path(run['output']).exists()
            run.update(status='running')
            save()
            subprocess.run(['python3', str(B / 'run_cruise_impact.py'), run['config'], run['output'], state['executable']], check=True)
            result = json.loads((B / (run['name'] + '-status.json')).read_text())
            assert result['status'] == 'completed', result
            run.update(status='completed', elapsed_seconds=result['elapsed_seconds'])
            if 'prior_reference' in run:
                reference = Path(run['prior_reference'])
                actual = Path(run['output']) / 'continuations.jsonl'
                run['prior_physical_records_byte_identical'] = actual.read_bytes() == reference.read_bytes()
                assert run['prior_physical_records_byte_identical'], 'Refactor changed the prior records; inspect before sampling'
            if 'conditioning' in run:
                subprocess.run([state['executable'], 'condition-cruise-impacts', '--config', run['conditioning'], '--output', run['conditional_output']], check=True)
                report = json.loads((Path(run['conditional_output']) / 'summary.json').read_text())
                run['cases'] = [dict(family=f['name'], case=c['name'], effective_rows=c['row_weight_effective_count'],
                    largest_row=c['largest_row_weight'], largest_ancestor=c['largest_initial_ancestor_weight'],
                    log_known_evidence=c['log_known_evidence_contribution'],
                    uncomputed_likelihood_incoming_mass=c['fraction_of_fuel_conditioned_prior_with_uncomputed_likelihood'])
                    for f in report['families'] for c in f['cases']]
            save()
        state['status'] = 'completed'
        save()
        with (B / 'progress.md').open('a') as f:
            f.write('\n' + state['updated_utc'] + ': '+state.get('completion_note','Joint conditional fuel/initial-lift proposal controls and two distinct-width pilots complete. Inspect weight/evidence support and independent replication before integration or escalation.')+'\n')
    except BaseException as error:
        state.update(status='needs_inspection', error=str(error))
        save()
        raise


if __name__ == '__main__': main()
