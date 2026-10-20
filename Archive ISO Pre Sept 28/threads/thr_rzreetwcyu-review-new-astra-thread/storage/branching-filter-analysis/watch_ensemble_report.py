"""Refresh the canonical report after each completed extension replicate."""
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import time

B = Path(__file__).resolve().parent
OUTPUT = B / 'pooled-arc-density'
PYTHON = '/tmp/mh370-acoustic-venv/bin/python'
REPORT = '/jackbox/home/MH370/crates/reporting/scripts/arc_density_report.py'
INLINE = Path('/jackbox/home/MH370/mh370-report-preview.html')
WEB = B.parent / 'overnight-analysis/web/branching-filter.html'
STATUS = B / 'ensemble-report-status.json'


def save(state):
    state['updated_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
    temporary = STATUS.with_suffix('.tmp')
    temporary.write_text(json.dumps(state, indent=2) + '\n')
    temporary.replace(STATUS)


def main():
    rendered = None
    status = dict(status='starting', reporter_pid=os.getpid())
    save(status)
    try:
        while True:
            sampling = json.loads((B / 'million-extension.json').read_text())
            seeds = sampling['original_seeds'] + [r['seed'] for r in sampling['additional_runs'] if r['status'] == 'completed']
            identity = (tuple(seeds), sampling['status'])
            if identity != rendered:
                command = [PYTHON, REPORT, '--runs'] + [str(B / f'runs/fuel-initial-proposal-85000-seed-{s}') for s in seeds]
                command += ['--output', str(OUTPUT), '--inline-output', str(INLINE), '--baseline-runs', '3',
                            '--extension-state', str(B / 'million-extension.json')]
                status.update(status='rendering', seeds=seeds, command=command)
                save(status)
                with (B / 'ensemble-report-render.log').open('w') as log:
                    subprocess.run(command, check=True, stdout=log, stderr=subprocess.STDOUT,
                                   env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1'),
                                   cwd='/jackbox/home/MH370')
                temporary = WEB.with_suffix('.html.tmp')
                temporary.write_bytes(INLINE.read_bytes())
                temporary.replace(WEB)
                summary = json.loads((OUTPUT / 'summary.json').read_text())
                status.update(status='waiting_for_sampling', rendered_candidates=summary['total_initial_candidates'],
                              regions=summary['regions'], rendered_utc=summary['generated_utc'])
                save(status)
                text = (status['updated_utc'] + ': Pooled browser report updated to '
                        f'{summary["total_initial_candidates"]:,} initial candidates; '
                        f'35–38S probability {100*summary["regions"]["between_35S_and_38S"]:.4f}%. '
                        'Reference altitude is labelled explicitly; terminal altitude/Mach distributions and nonoverlapping replicate groups included.')
                with (B / 'progress.md').open('a') as log:
                    log.write('\n' + text + '\n')
                print(text, flush=True)
                rendered = identity
            if sampling['status'] in ['sampling_completed', 'needs_inspection']:
                status['status'] = 'completed' if sampling['status'] == 'sampling_completed' else 'sampling_needs_inspection'
                save(status)
                break
            time.sleep(10)
    except BaseException as error:
        status.update(status='needs_inspection', error=str(error))
        save(status)
        raise


if __name__ == '__main__':
    main()
