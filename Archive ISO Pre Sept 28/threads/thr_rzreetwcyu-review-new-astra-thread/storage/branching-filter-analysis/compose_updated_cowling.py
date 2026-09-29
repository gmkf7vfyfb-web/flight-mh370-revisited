"""Replace only the cowling likelihood using two completed source-grid estimates."""
from pathlib import Path
import copy, datetime as dt, hashlib, json, math, os, subprocess, sys, time, tomllib

B = Path(__file__).resolve().parent
R = Path('/jackbox/home/MH370')
OUT = B / 'cowling-drift-composition'
STATUS = B / 'cowling-drift-composition-status.json'
EXE = B / 'spatial-composition-executable'
EVENT = 'mossel-bay-engine-cowling-recovery'
sys.path.insert(0, str(R / 'crates/reporting/scripts'))
from flight_drift_report import cowling_sampling_data

sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
now = lambda: dt.datetime.now(dt.timezone.utc).isoformat()

def write(path, value):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    temp.replace(path)

def main():
    if STATUS.exists() or OUT.exists():
        raise RuntimeError('Inspect existing cowling composition; no automatic repeat')
    started = time.monotonic()
    control = cowling_sampling_data(B)
    grid = control['full_grid']
    assert grid is not None and grid['source_cells'] == 77
    attribution_path = B / 'drift-evidence-attribution-status.json'
    attribution = json.loads(attribution_path.read_text())
    assert attribution['status'] == 'completed'
    source_path = Path(attribution['source_path'])
    assert sha(source_path) == attribution['source_sha256']
    source = json.loads(source_path.read_text())
    source_cells = {c['id']: c for c in source['cells']}
    manifest = json.loads(source_path.with_name('run-manifest.json').read_text())
    original_config = Path(manifest['config_path'])
    assert sha(original_config) == manifest['config_sha256']
    old = tomllib.loads(original_config.read_text())
    new_path = B / 'cowling-arrival-sampling/configs/remaining-sources-guidance-540-seed-37093011.toml'
    new = tomllib.loads(new_path.read_text())
    for key in ['release_unix_seconds', 'currents', 'stokes', 'wind', 'coast']:
        assert old[key] == new[key]
    family = lambda cfg: next(f for f in cfg['motion_families'] if f['id'] == 'low-exposure-exterior')
    first, second = family(old), family(new)
    assert first['motion'] == second['motion']
    for key in ['pre_discovery_window_days', 'spatial_bandwidth_km', 'probability_floor']:
        assert first['debris'][key] == second['debris'][key]
    assert next(e for e in first['debris']['events'] if e['id'] == EVENT) == second['debris']['events'][0]
    notes = [
        'Only the Mossel Bay cowling numerical likelihood is replaced; all other debris terms and optional conditions retain their original calculations.',
        'The two cowling estimates use independent seeds at 4096 original paths per cell with 540-day computational guidance. They share the same physical law, discovery-delay distribution and spatial kernel.',
        'These are not two independent recalculations of the complete nine-debris model. Other evidence terms, cruise samples and each selected terminal population are shared.',
        'All 77 original source cells are covered. Four previously completed cells per seed are retained without resimulation. No source prior is included in the reused likelihood.',
        'The reference support mask, nearest-cell geometry, time tolerance and flight/fuel/final-contact choices are retained. The new cowling contribution is applied exactly once.',
        'Remaining cowling variability and ancestral concentration are reported; no calibration or overall convergence is established. No new flight or ocean paths are sampled here.',
    ]
    OUT.mkdir()
    variants = []
    for seed in grid['seeds']:
        replacement = {r['cell_id']: r for r in grid['rows'] if r['seed'] == seed}
        assert set(replacement) == set(source_cells)
        for kind in ['recoveries-only', 'full-declared']:
            template = next(v for v in attribution['variants'] if v['id'] == kind)
            handoff_path = Path(template['handoff'])
            assert sha(handoff_path) == template['handoff_sha256']
            handoff = json.loads(handoff_path.read_text())
            f = handoff['families'][0]
            name = kind + '--cowling-seed-' + str(seed)
            suffix = 'A' if seed == grid['seeds'][0] else 'B'
            label = ('9 recoveries only' if kind == 'recoveries-only' else '9 recoveries + extra conditions') + ' · updated cowling ' + suffix
            f.update(id=f['id'] + '--cowling-seed-' + str(seed), label=label)
            for key in ['source_diagnostics', 'source_result']:
                if key in f:
                    f[key + '_retained_terms_reference'] = f.pop(key)
            f['conditions'] += notes
            f['limitations'] += notes
            for cell in f['cells']:
                saved = source_cells[cell['id']]
                old_term = next(r['log_compatibility'] for r in saved['recoveries'] if r['event_id'] == EVENT)
                new_term = replacement[cell['id']]['log_compatibility']
                original_terms = [r['log_compatibility'] for r in saved['recoveries'] if r['event_id'] != EVENT]
                recovered = math.fsum(original_terms + [new_term])
                selected = cell['selected_log_terms']
                assert abs(selected['recovered'] - math.fsum(original_terms + [old_term])) < 1e-12
                selected['recovered'] = recovered
                if cell['evidence_log_likelihood'] is not None:
                    cell['evidence_log_likelihood'] = math.fsum(selected.values())
                cell['event_effective_sample_size'][EVENT] = replacement[cell['id']]['leaf_ess']
                cell['cowling_ancestry'] = replacement[cell['id']]['ancestry']
                cell['cowling_log_change'] = new_term - old_term
            maximum = max(c['evidence_log_likelihood'] for c in f['cells'] if c['evidence_log_likelihood'] is not None)
            z = math.fsum(math.exp(c['evidence_log_likelihood'] - maximum) for c in f['cells'] if c['evidence_log_likelihood'] is not None)
            for cell in f['cells']:
                ell = cell['evidence_log_likelihood']
                cell.update(relative_log_likelihood=ell - maximum if ell is not None else None,
                    relative_likelihood=math.exp(ell - maximum) if ell is not None else None,
                    diagnostic_uniform_cell_mass=math.exp(ell - maximum) / z if ell is not None else None)
            handoff.update(title=label, derivation=dict(script_sha256=sha(__file__), template_sha256=sha(handoff_path),
                retained_source_sha256=sha(source_path), replacement_input_sha256=grid['input_sha256'],
                seed=seed, event_id=EVENT, source_prior_removed=True, limitations=notes))
            output = OUT / (name + '.json')
            write(output, handoff)
            variants.append(dict(id=name, label=label, base_variant=kind, cowling_seed=seed,
                events=template['events'], isotope=template['isotope'], non_recovery=template['non_recovery'],
                handoff=str(output), handoff_sha256=sha(output), family_id=f['id']))
    queue = []
    for job in attribution['completed']:
        for variant in variants:
            if job['evidence_variant'] != variant['base_variant']:
                continue
            template = next(v for v in attribution['variants'] if v['id'] == variant['base_variant'])
            name = job['name'] + '--cowling-seed-' + str(variant['cowling_seed'])
            config = OUT / (name + '.toml')
            assert sha(job['config']) == job['config_sha256']
            value = Path(job['config']).read_text().replace(job['name'], name).replace(template['handoff'], variant['handoff']).replace(template['family_id'], variant['family_id'])
            config.write_text(value)
            queue.append(dict(job, name=name, evidence_variant=variant['id'], config=str(config),
                config_sha256=sha(config), output=str(OUT / name), cowling_seed=variant['cowling_seed']))
    assert len(queue) == 24
    state = dict(status='running', started_utc=now(), driver_pid=os.getpid(), script_sha256=sha(__file__),
        executable=str(EXE), executable_sha256=sha(EXE), source_status=str(attribution_path),
        source_status_sha256=sha(attribution_path), variants=variants, queue=queue, completed=[],
        input_sha256=control['input_sha256'], full_grid_input_sha256=grid['input_sha256'], limitations=notes)
    web_status = B.parent / 'overnight-analysis/web/mh370-running-status.json'
    def save(worker=None, finished=False):
        state['checked_utc'] = now()
        write(STATUS, state)
        write(web_status, dict(checked_utc=state['checked_utc'], comparison_finished=finished,
            jobs=[dict(title='Apply updated cowling likelihood to saved flight and impact populations',
                candidates_per_run=0, sample_unit='new trajectories; saved weights only',
                completed_runs=len(state['completed']), planned_runs=len(queue), driver_alive=not finished,
                driver_pid=os.getpid(), worker_alive=worker is not None, worker_pid=worker,
                run_started_utc=state.get('run_started_utc'), recorded_status=state['status'])]))
    save()
    try:
        for job in queue:
            assert sha(job['config']) == job['config_sha256']
            assert sha(job['parent_summary']) == job['parent_summary_sha256']
            state['run_started_utc'] = now()
            before = time.monotonic()
            command = [str(EXE), 'apply-conditional-surface', '--config', job['config'], '--output', job['output']]
            with Path(job['output']).with_suffix('.log').open('x') as log:
                child = subprocess.Popen(command, cwd=R, stdout=log, stderr=subprocess.STDOUT)
                save(child.pid)
                if child.wait():
                    raise RuntimeError('Composition failed; no repeat: ' + job['name'])
            path = Path(job['output']) / 'conditional-spatial-sensitivity.json'
            state['completed'].append(dict(job, command=command, elapsed_seconds=time.monotonic() - before, output_sha256=sha(path)))
            save()
        state.update(status='completed', completed_utc=now(), elapsed_seconds=time.monotonic() - started)
        save(finished=True)
        print(json.dumps(dict(status='completed', comparisons=len(queue), elapsed_seconds=state['elapsed_seconds'])))
    except Exception as error:
        state.update(status='needs_inspection', error=str(error))
        save(finished=True)
        raise

if __name__ == '__main__':
    main()
