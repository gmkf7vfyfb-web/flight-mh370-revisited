"""Audit saved recovery support at cells used by the joint estimate; no sampling."""
from pathlib import Path
import csv
import datetime as dt
import hashlib
import json
import math
import resource
import time
import tomllib

import numpy as np

B = Path(__file__).resolve().parent
R = Path('/jackbox/home/MH370')
OUT = B / 'drift-recovery-support.json'
if OUT.exists():
    raise RuntimeError('Inspect completed recovery-support diagnostic before repeating')
started = time.monotonic()
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
inputs = []


def read(path, expected=None):
    path = Path(path)
    digest = sha(path)
    if expected is not None:
        assert digest == expected, path
    inputs.append(dict(path=str(path), sha256=digest))
    return json.loads(path.read_text())


def quantiles(values, weights):
    values, weights = np.asarray(values), np.asarray(weights)
    order = np.argsort(values, kind='stable')
    cumulative = np.cumsum(weights[order])
    assert cumulative[-1] > 0
    indices = np.searchsorted(cumulative, cumulative[-1] * np.array([.05, .5, .95]))
    return values[order[indices]].tolist()


attribution = read(B / 'drift-evidence-attribution-status.json')
extra = read(B / 'drift-source-sampling-status.json')
assert attribution['status'] == extra['status'] == 'completed'
identities = [dict(label='reference', path=attribution['source_path'], sha256=attribution['source_sha256'])] + extra['sources']
sources = {}
reconstruction_errors = []
for identity in identities:
    path = Path(identity['path'])
    data = read(path, identity['sha256'])
    manifest = read(path.with_name('run-manifest.json'))
    cfg_path = Path(manifest['config_path'])
    if not cfg_path.is_absolute():
        cfg_path = R / cfg_path
    assert sha(cfg_path) == manifest['config_sha256']
    cfg = tomllib.loads(cfg_path.read_text())
    inputs.append(dict(path=str(cfg_path), sha256=sha(cfg_path)))
    families = {f['id']: f for f in cfg['motion_families']}
    cells = []
    for cell in data['cells']:
        recoveries = {}
        for event in cell['recoveries']:
            # Resolve the actual profile winner; the supplied nine-event atlas
            # currently has exactly one response law for each recovered event.
            matches = [(family, r) for family in cell['motion_families']
                       for r in family['recoveries'] if r['event_id'] == event['event_id']]
            best_value = max(r['log_compatibility'] for _, r in matches)
            winners = [f for f, r in matches if r['log_compatibility'] == best_value]
            assert event['log_compatibility'] == best_value
            assert len(winners) == 1, 'Retain ties explicitly before extending this diagnostic'
            family = winners[0]
            declaration = families[family['id']]['debris']
            observation = next(e for e in declaration['events'] if e['id'] == event['event_id'])
            ensemble = next(e for e in family['recovery_ensembles'] if e['event_id'] == event['event_id'])
            floor = declaration['probability_floor']
            encounter = event['mean_encounter_weight']
            probability = floor + (1 - floor) * encounter
            error = abs(observation['evidence_weight'] * math.log(probability) - event['log_compatibility'])
            assert error < 1e-12
            reconstruction_errors.append(error)
            recoveries[event['event_id']] = dict(
                log_compatibility=event['log_compatibility'], mean_encounter_weight=encounter,
                leaf_weight_ess=event['effective_sample_size'],
                represented_initial_ancestors=ensemble['sampling']['represented_initial_ancestors'],
                floor_fraction_of_event_compatibility=floor / probability,
                response_family=family['id'], compatible_response_family_count=len(matches),
                probability_floor=floor, spatial_bandwidth_km=declaration['spatial_bandwidth_km'],
                discovery_delay=observation['discovery_delay'])
        cells.append(dict(id=cell['id'], position=cell['position'], recoveries=recoveries))
    sources[identity['label']] = dict(identity=dict(identity, seed=data['seed'], particles_per_cell=data['particles_per_cell'],
        executable_sha256=manifest['executable_sha256']), cells=cells)
assert sources['alternate']['identity']['executable_sha256'] == sources['doubled']['identity']['executable_sha256']
ids = [c['id'] for c in sources['reference']['cells']]
for source in sources.values():
    assert [c['id'] for c in source['cells']] == ids
    assert [c['position'] for c in source['cells']] == [c['position'] for c in sources['reference']['cells']]
events = sorted(sources['reference']['cells'][0]['recoveries'])
cell_index = {name: i for i, name in enumerate(ids)}
cases, baseline_by_terminal = [], {}
selected_variants = {'recoveries-only': 'reference', 'recoveries-only--drift-alternate': 'alternate', 'recoveries-only--drift-doubled': 'doubled'}
for job in attribution['completed'] + extra['completed']:
    if job['evidence_variant'] not in selected_variants:
        continue
    label = selected_variants[job['evidence_variant']]
    data = read(Path(job['output']) / 'conditional-spatial-sensitivity.json', job['output_sha256'])
    before, after = np.zeros(len(ids)), np.zeros(len(ids))
    rows = data['particle_values']
    assert abs(math.fsum(r['conditional_weight'] for r in rows) - 1) < 1e-12
    for row in rows:
        if row['support_status'] == 'supported':
            i = cell_index[row['surface_cell_id']]
            before[i] += row['baseline_weight']
            after[i] += row['conditional_weight']
        else:
            assert row['conditional_weight'] == 0
    assert abs(before.sum() - data['supported_baseline_mass']) < 1e-12
    assert abs(after.sum() - 1) < 1e-12
    key = (job['terminal_family'], job['seed'])
    baseline = before / before.sum()
    if key in baseline_by_terminal:
        assert np.allclose(baseline_by_terminal[key], baseline, rtol=0, atol=1e-14)
    else:
        baseline_by_terminal[key] = baseline
    cells = sources[label]['cells']
    ell = np.array([math.fsum(c['recoveries'][e]['log_compatibility'] for e in events) for c in cells])
    expected = before * np.exp(ell - ell.max())
    expected /= expected.sum()
    assert np.allclose(after, expected, rtol=1e-11, atol=1e-13)
    statistics = {}
    for event in events:
        values = [c['recoveries'][event] for c in cells]
        ess = np.array([v['leaf_weight_ess'] for v in values])
        ancestors = np.array([v['represented_initial_ancestors'] for v in values])
        floor = np.array([v['floor_fraction_of_event_compatibility'] for v in values])
        zero = np.array([v['mean_encounter_weight'] == 0 for v in values])
        statistics[event] = dict(
            leaf_weight_ess_quantiles_05_50_95=quantiles(ess, after),
            represented_ancestor_quantiles_05_50_95=quantiles(ancestors, after),
            mean_floor_fraction_under_joint_weights=float(after @ floor),
            joint_mass_on_zero_encounter_cells=float(after[zero].sum()))
    cases.append(dict(terminal_family=key[0], seed=key[1], numerical_run=job['numerical_run'], drift_source=label,
        supported_baseline_mass=float(before.sum()), cell_weights=after.tolist(),
        north_of_35S=math.fsum(r['conditional_weight'] for r in rows if r['latitude_deg'] > -35),
        events=statistics))
assert len(cases) == 18
# Compare the two same-executable calculations, on identical flight-supported
# cells. Subtract the weighted constant log offset because it cancels on
# normalization; the remaining shape change alters relative source odds.
shape_comparisons = []
for key, baseline in baseline_by_terminal.items():
    comparisons = {}
    for event in events + ['all-nine-recoveries']:
        def terms(label):
            return np.array([math.fsum(c['recoveries'][e]['log_compatibility'] for e in events)
                if event == 'all-nine-recoveries' else c['recoveries'][event]['log_compatibility']
                for c in sources[label]['cells']])
        delta = terms('doubled') - terms('alternate')
        offset = float(baseline @ delta)
        centered = delta - offset
        comparisons[event] = dict(constant_log_offset=offset,
            centered_log_difference_quantiles_05_50_95=quantiles(centered, baseline),
            centered_log_difference_rms=float(np.sqrt(baseline @ centered**2)))
    shape_comparisons.append(dict(terminal_family=key[0], seed=key[1], baseline_cell_weights=baseline.tolist(), events=comparisons))

result = dict(status='completed', created_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
    scope='Saved-data support diagnostic for 18 R600 recovery-only compositions; no new flight or ocean simulation.',
    script_sha256=sha(__file__), inputs=inputs, sources=sources, cell_ids=ids, events=events,
    cases=cases, same_executable_shape_comparisons=shape_comparisons,
    maximum_event_term_reconstruction_error=max(reconstruction_errors),
    limitations=[
        'ESS is calculated from final arrival-weighted leaves. Resampling creates related paths, so it is not a count of independent successful arrivals or a calibrated error bar.',
        'Represented initial ancestors count all retained paths in that event ensemble, including paths with no recovery contribution. Event-weighted ancestor ESS was not saved.',
        'Support quantiles describe where each provisional joint distribution puts its mass, not sampling confidence or a pass/fail threshold.',
        'The floor fraction describes the additive floor within an event score; it is not the fraction of posterior probability caused by the floor.',
        'The alternate and doubled sources share an executable but change both seed and sample size. The reference executable differs; none of these surfaces is averaged.',
        'Discovery-delay probabilities, spatial bandwidth and response laws are declared model choices. Changing them requires separate conditional calculations; they are not inferred from discovery dates alone.',
        'All nine recovered events have one configured response family in these archived inputs. The generic source profiler does not select among multiple competing response laws for them here.'
    ], elapsed_seconds=time.monotonic()-started, peak_rss_kb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
OUT.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
with (B / 'drift-recovery-support.csv').open('w') as stream:
    writer = csv.writer(stream)
    writer.writerow(['terminal_family','seed','drift_source','event','leaf_ess_q05','leaf_ess_q50','leaf_ess_q95','ancestors_q05','ancestors_q50','ancestors_q95','joint_mean_floor_fraction','joint_mass_zero_encounter'])
    for case in cases:
        for event, row in case['events'].items():
            writer.writerow([case['terminal_family'],case['seed'],case['drift_source'],event,
                *row['leaf_weight_ess_quantiles_05_50_95'],*row['represented_ancestor_quantiles_05_50_95'],
                row['mean_floor_fraction_under_joint_weights'],row['joint_mass_on_zero_encounter_cells']])
print(json.dumps(dict(status=result['status'], cases=len(cases), source_cells=sum(len(s['cells']) for s in sources.values()),
    event_term_checks=len(reconstruction_errors), elapsed_seconds=result['elapsed_seconds'], peak_rss_kb=result['peak_rss_kb'])))
for event in ['reunion-flaperon-recovery','mossel-bay-engine-cowling-recovery','paindane-flap-fairing-recovery']:
    medians = [c['events'][event]['leaf_weight_ess_quantiles_05_50_95'][1] for c in cases]
    rms = [c['events'][event]['centered_log_difference_rms'] for c in shape_comparisons]
    print(event, 'leaf_ESS_median_range', min(medians), max(medians), 'shape_RMS_log_range', min(rms), max(rms),
          'maximum_joint_mean_floor_fraction', max(c['events'][event]['mean_floor_fraction_under_joint_weights'] for c in cases))
