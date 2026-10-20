"""Report retained forward/backward flight trials; never run inference."""
import datetime as dt
import hashlib
import json
from html import escape

import matplotlib.pyplot as plt
import numpy as np


def _cdf_difference(a, b):
    grid = np.sort(np.r_[a, b])
    return float(np.max(np.abs(np.searchsorted(np.sort(a), grid, side='right') / len(a)
                               - np.searchsorted(np.sort(b), grid, side='right') / len(b))))


def write_sampling_report(directory, web):
    """Render explicit run comparisons and numerical-resolution checks."""
    from flight_analysis_results import _page
    stamp = dt.datetime.now(dt.timezone.utc).isoformat()
    rows, families, inputs = [], {}, {}
    correction_path = directory / 'integration-correction.json'
    correction_record = json.loads(correction_path.read_text()) if correction_path.exists() else {}
    manifests = list(directory.glob('*/seed-*/run-manifest.json')) + list(directory.glob('*pilot/run-manifest.json'))
    for manifest_path in sorted(manifests):
        run = manifest_path.parent
        manifest = json.loads(manifest_path.read_text())
        command = manifest['command']; at = command.index('--counts')
        counts = [int(x) for x in command[at + 1:at + 4]]
        progress = run / 'progress.jsonl'
        history = [json.loads(line) for line in progress.read_text().splitlines()] if progress.exists() else []
        last = history[-1] if history else {}
        summary_path = run / 'summary.json'
        complete = summary_path.exists() and (run / 'particles.npz').exists()
        pilot = run.name.endswith('pilot')
        failure_path = run / 'failure.json'
        failure = json.loads(failure_path.read_text()) if failure_path.exists() else None
        row = {'family': run.name if pilot else run.parent.name, 'seed': manifest['seed'], 'particles': manifest['particles'],
               'counts': counts, 'complete': complete, 'temperature': last.get('temperature', 0),
               'pilot': pilot, 'failure': failure,
               'acceptance': last.get('mutation_acceptance'),
               'elapsed_s': failure.get('elapsed_s', failure.get('allocated_seconds', last.get('elapsed_s', 0))) if failure else last.get('elapsed_s', 0),
               'elapsed_is_conservative_allocation': bool(failure and 'elapsed_s' not in failure and 'allocated_seconds' in failure),
               'method': ('Blocks + accurate likelihood' if '--surrogate-config' in command
                          else 'Blocks + exact mode update' if '--mode-updates' in command else 'Original blocks'),
               'input_sha256': manifest['input_sha256'], 'log_normalizer': last.get('log_normalizer'),
               'categorical_mode_change_fraction': last.get('categorical_mode_change_fraction'),
               'root_count': last.get('root_count'),
               'global_independence_acceptances': last.get('global_independence_acceptances')}
        row['before_integration_correction'] = any(
            key.endswith('/target/release/mh370') and value == correction_record.get('before_binary_sha256')
            for key, value in manifest['input_sha256'].items())
        if complete:
            summary = json.loads(summary_path.read_text()); population = np.load(run / 'particles.npz')
            row['elapsed_s'] = summary['elapsed_s']
            if not pilot:families.setdefault(run.parent.name, []).append((row, population['data'][:, :2], population['modes']))
            inputs[str(summary_path)] = hashlib.sha256(summary_path.read_bytes()).hexdigest()
            inputs[str(run / 'particles.npz')] = hashlib.sha256((run / 'particles.npz').read_bytes()).hexdigest()
        for artifact in [progress, failure_path]:
            if artifact.exists():
                inputs[str(artifact)] = hashlib.sha256(artifact.read_bytes()).hexdigest()
        inputs[str(manifest_path)] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        rows.append(row)
    comparisons, panels = {}, []
    for family, runs in sorted(families.items(), key=lambda item: any(
            run[0]['before_integration_correction'] for run in item[1])):
        if len(runs) < 2:
            continue
        first, second = runs[-2:]
        a, b = first[1], second[1]
        quantiles = np.max(np.abs(np.quantile(a, [.05, .5, .95], axis=0)
                                 - np.quantile(b, [.05, .5, .95], axis=0)))
        cdf = [_cdf_difference(a[:, i], b[:, i]) for i in range(2)]
        mode_difference = max(float(np.max(np.abs(
            np.bincount(first[2][:, i], minlength=5) / len(a)
            - np.bincount(second[2][:, i], minlength=5) / len(b)))) for i in [0, -1])
        mode_differences = [float(np.max(np.abs(np.bincount(first[2][:, i], minlength=5) / len(a)
                            - np.bincount(second[2][:, i], minlength=5) / len(b))))
                            for i in range(first[2].shape[1])]
        # Same-input consistency is necessary for a replicate comparison.
        common = set(first[0]['input_sha256']) & set(second[0]['input_sha256'])
        mismatches = [p for p in common if first[0]['input_sha256'][p] != second[0]['input_sha256'][p]]
        edges = [-90, -35, -32, -30, -25, -20, 90]
        result = {'seeds': [first[0]['seed'], second[0]['seed']], 'counts': first[0]['counts'],
                  'coordinate_cdf_max_differences': cdf, 'coordinate_quantile_max_difference_deg': float(quantiles),
                  'initial_and_final_mode_frequency_max_difference': mode_difference,
                  'per_slot_mode_frequency_max_differences': mode_differences,
                  'mode_names': ['constant_true_track', 'constant_true_heading', 'constant_magnetic_track',
                                 'constant_magnetic_heading', 'great_circle_track_continuation'],
                  'per_run_per_slot_mode_fractions': [
                      [(np.bincount(run[2][:, slot], minlength=5) / len(run[2])).tolist()
                       for slot in range(run[2].shape[1])] for run in [first, second]],
                  'common_input_hash_mismatches': mismatches,
                  'log_normalizer_difference': abs(first[0]['log_normalizer'] - second[0]['log_normalizer']),
                  'latitude_bin_edges_deg': edges,
                  'latitude_bin_fractions': [(np.histogram(x[:, 0], edges)[0] / len(x)).tolist() for x in [a, b]],
                  'coordinate_quantiles_05_50_95': [np.quantile(x, [.05, .5, .95], axis=0).tolist() for x in [a, b]],
                  'provisional_resolution_agreement': not mismatches and max(cdf) < .05 and quantiles < .5 and mode_difference < .05,
                  'scope': 'Finite-run numerical agreement under the declared model; not complete-support or physical calibration proof.'}
        comparisons[family] = result
        (directory / family / 'numerical-assessment.json').write_text(json.dumps(result, indent=2))
        fig, axes = plt.subplots(2, 1, figsize=(5.6, 6.0))
        for axis, column, label in zip(axes, [0, 1], ['Latitude (degrees)', 'Longitude (degrees east)']):
            for info, points, _ in runs:
                ordered = np.sort(points[:, column])
                axis.step(ordered, np.arange(1, len(ordered) + 1) / len(ordered), where='post',
                          label=f"N={info['particles']:,}, seed {info['seed']}")
            axis.set(xlabel='00:11 ' + label.lower(), ylabel='Empirical cumulative fraction', ylim=(0, 1))
            axis.grid(alpha=.2); axis.legend(fontsize=8)
        fig.tight_layout(); name = 'sampling-' + family + '.svg'
        fig.savefig(web / name); plt.close(fig)
        conclusion = 'The provisional numerical resolution checks agree.' if result['provisional_resolution_agreement'] else 'The independent populations disagree beyond the provisional numerical resolution.'
        historical = ('<p><strong>Historical comparison before the integration repair.</strong> '
                      'It demonstrates the earlier instability; it is not an accurate-model probability estimate.</p>'
                      if any(run[0]['before_integration_correction'] for run in runs) else '')
        ancestry_note = ''
        ancestry_path = directory / family / 'ancestry-diagnostic.json'
        if ancestry_path.exists():
            ancestry = json.loads(ancestry_path.read_text())
            fractions = [100 * run['largest_ancestral_fraction'] for run in ancestry['runs']]
            ancestry_note = ('<p>The largest inherited ancestral group contains '
                             + ' and '.join(f'{fraction:.1f}%' for fraction in fractions)
                             + ' of the two final populations. Descendants can move after resampling, '
                             'so ancestry is not an effective-sample-size calculation; strong concentration '
                             'is nevertheless a warning that particle count alone can overstate exploration.</p>')
            inputs[str(ancestry_path)] = hashlib.sha256(ancestry_path.read_bytes()).hexdigest()
        panels.append(f'<section><h2>{escape(family.replace("-", " ").capitalize())}</h2>'
                      f'<p>Conditional counts: {result["counts"][0]} direction, {result["counts"][1]} Mach and '
                      f'{result["counts"][2]} altitude command changes. All five navigation modes remain in the physical prior.</p><p>{conclusion} '
                      f'Largest coordinate-CDF difference: {100*max(cdf):.1f} percentage points. '
                      f'Largest 5th/50th/95th coordinate-quantile shift: {quantiles:.2f}°. '
                      f'Largest initial/final mode-frequency difference: {100*mode_difference:.1f} percentage points.</p>'
                      + historical +
                      f'<img src="{name}" alt="Independent 00:11 endpoint distributions for {escape(family)}">'
                      '<p>These plots compare numerical populations. Agreement between two runs alone cannot establish that all important route families were explored. Correlated particles are not treated as independent observations in a significance test.</p>'
                      + ancestry_note + '</section>')
    table = ''
    for row in rows:
        acceptance = '—' if row['acceptance'] is None else f"{100*row['acceptance']:.1f}%"
        status = ('Timing pilot complete' if row['pilot'] else 'Complete numerical run') if row['complete'] else f"Incomplete; tempering {row['temperature']:.3f}"
        if row['failure']:status = 'Stopped: ' + row['failure']['message']
        if row['before_integration_correction']:status += '; before integration repair'
        elapsed = f"{row['elapsed_s']/60:.1f}" + (' (allocated)' if row['elapsed_is_conservative_allocation'] else '')
        table += f'<tr><td>{"/".join(map(str,row["counts"]))}</td><td>{escape(row["method"])}</td><td>{row["particles"]:,}</td><td>{row["seed"]}</td><td>{escape(status)}</td><td>{acceptance}</td><td>{elapsed}</td></tr>'
    control_path = directory / 'nonuniform-mode-control/summary.json'
    if not control_path.exists():
        control_path = directory / 'mathematical-control/summary.json'
    controls = json.loads(control_path.read_text())
    ledger = json.loads((directory / 'compute-ledger.json').read_text())
    for artifact in [directory / 'compute-ledger.json', correction_path,
                     control_path]:
        if artifact.exists():
            inputs[str(artifact)] = hashlib.sha256(artifact.read_bytes()).hexdigest()
    correction = ''
    categorical_control = directory / 'nonuniform-mode-control/summary.json'
    if not categorical_control.exists():
        categorical_control = directory / 'categorical-mathematical-control/summary.json'
    if categorical_control.exists():
        checked = json.loads(categorical_control.read_text())
        correction = ('<p>The first independent 1,024/2,048 comparison failed. A focused diagnostic found poor movement between navigation modes, including modes with similar likelihood at the same controls. Later trials evaluate all five choices for one randomly chosen mode slot per particle at each tempering update and adjust each continuous block scale from its local acceptance. Computational guidance was also adjusted to propose mode-compatible controls; the physical prior remains equal across the five modes. '
                      f'The exact categorical and deterministic-motion checks {"passed" if checked["passed"] else "failed"}; the flight comparison still has to establish stability.</p>')
    integration_note = ''
    refinement = directory / 'categorical-flight-refinement/summary.json'
    if refinement.exists():
        check = json.loads(refinement.read_text())
        integration_note = ('<section class="note"><h2>Integration accuracy</h2>'
                            f'<p>The saved-flight refinement check passed {check["passed"]} of {check["cases"]} representative trajectories. '
                            'It compares the declared integration step with half and quarter steps, including changes in observation residuals and likelihood. '
                            'A failed check prevents release of probability weights even if independent sampling runs agree. '
                            'The initial check found material turn-integration error; a correction is being tested separately before further ensembles.</p></section>')
    refined = directory / 'canonical-flight-refinement/summary.json'
    if not refined.exists():
        refined = directory / 'refined-flight-check/summary.json'
    if refined.exists():
        verified = json.loads(refined.read_text())
        for artifact in [refined, refined.parent / 'refinement.json',
                         directory / 'categorical-flight-refinement/refinement.json']:
            inputs[str(artifact)] = hashlib.sha256(artifact.read_bytes()).hexdigest()
        old = json.loads((directory / 'categorical-flight-refinement/refinement.json').read_text())
        new = json.loads((refined.parent / 'refinement.json').read_text())
        metrics = ['coarse_and_half_vs_quarter_position_nm',
                   'coarse_and_half_vs_quarter_max_standardized_observation_change',
                   'coarse_and_half_vs_quarter_log_likelihood_change']
        maxima = [[max(max(r[k]) for r in records if k in r) for k in metrics] for records in [old, new]]
        integration_note = ('<section class="note"><h2>Flight integration corrected</h2>'
                            '<p>The controller now evaluates heading feedback at the midpoint, and the position update accounts for the change in the local north/east frame. Independent exponential-turn and constant-heading parallel checks support these changes. '
                            'The accurate numerical setting is 10-second steady steps, 2.5-second transition steps and a 0.001° heading-capture tolerance.</p>'
                            f'<p>On the same {verified["cases"]} representative saved trajectories, all {verified["passed"]} accurate-step checks pass. '
                            f'The largest endpoint change on refinement fell from {maxima[0][0]:.3f} to {maxima[1][0]:.3f} nautical miles; '
                            f'the largest standardized residual change fell from {maxima[0][1]:.3f} to {maxima[1][1]:.3f}; '
                            f'the largest log-likelihood change fell from {maxima[0][2]:.3f} to {maxima[1][2]:.3f}. '
                            'These are integration checks, not independent aircraft-performance validation.</p>'
                            '<p>The temporary sampler now supports a cheap screening calculation followed by an accurate acceptance correction. Every probability weight uses the accurate model. A coarse replay rejection cannot itself exclude a trajectory. Joint moves of all continuous controls are also available to address their strong correlations. These algorithm changes still require independent flight-run comparisons.</p></section>')
    conclusion_path = directory / 'conclusion.json'
    conclusion = json.loads(conclusion_path.read_text()) if conclusion_path.exists() else None
    lead = ''
    if conclusion:
        lead = '<section class="note"><h2>Result of this bounded attempt</h2>'
        lead += '<p>' + escape(conclusion['paragraphs'][0]) + '</p>'
        lead += '<details><summary>Results, repairs and limitations</summary>'
        lead += ''.join('<p>' + escape(paragraph) + '</p>' for paragraph in conclusion['paragraphs'][1:])
        lead += '</details>'
        lead += '</section>'
        inputs[str(conclusion_path)] = hashlib.sha256(conclusion_path.read_bytes()).hexdigest()
    body = ('<h1>Flight sampling through 00:11</h1>'
            f'<p>Updated {escape(stamp)}. Forward/backward control-block investigation.</p>'
            + lead + ''.join(panels) + '<details><summary>Model conditions, integration checks and all trials</summary>' +
            '<p>The first family has four direction changes, two Mach changes and two altitude changes. Counts are fixed conditional families, not an inferred prior over all counts below a maximum. Initial Mach spans 0.30–0.87 and altitude 500–43,000 ft, subject to the declared performance approximation. Navigation-mode probabilities, radar prior, initial zero vertical speed, fuel anchor and observation uncertainties remain explicit model choices.</p>'
            '<p>This trial uses BTO/BFO through 00:11 and aircraft/fuel propagation to that time. It does not apply the later exhaustion-time screen or final BFOs. Terminal flight and other evidence comparisons are outside this trial.</p>'
            '<p>Each update revises a block of controls and replays a continuous flight. Blocks are traversed in forward and reverse order, with corrected conditional proposals and occasional whole-route moves. This is control-space blocked smoothing inside SMC, not backward stitching of stored aircraft states.</p>'
            f'<p>The independent mathematical checks {"passed" if controls["passed"] else "failed"}: ordered command-time density and a deterministic-motion problem with an exactly calculated posterior. These checks do not establish MH370 sampling stability.</p>'
            + correction + integration_note + '<div style="overflow-x:auto"><table><thead><tr><th>Direction/Mach/altitude</th><th>Method</th><th>Particles</th><th>Seed</th><th>Status</th><th>Last acceptance</th><th>Minutes</th></tr></thead><tbody>'
            + table + '</tbody></table></div></details>'
            + '<p>Provisional resolution targets are a coordinate-CDF difference below five percentage points, coordinate-quantile shifts below 0.5°, and initial/final mode-frequency differences below five percentage points. These are numerical criteria; higher-work, guide-coverage and flight controls remain necessary before treating a result as reliable.</p>'
            + f'<p>Recorded numerical work, including stopped trials and controls: {ledger["allocated_seconds"]/60:.1f} minutes of a 90-minute initial allowance. This counts numerical-batch elapsed time, not the longer engineering and reporting time. Running batches are added on completion or failure. This ledger is separate from the closed overnight allowance.</p>')
    page = _page('MH370 forward/backward flight sampling', body)
    page = page.replace('</style>', 'table{border-collapse:collapse;font-size:.85rem}td,th{padding:8px;border-bottom:1px solid #ddd;text-align:left}</style>')
    (web / 'flight-sampling.html').write_text(page)
    state = {'updated_utc': stamp, 'runs': rows, 'comparisons': comparisons, 'conclusion': conclusion, 'input_sha256': inputs,
             'new_evidence': 'BTO/BFO through 00:11 only, plus declared powered-flight/fuel model',
             'report_source_sha256': hashlib.sha256(__import__('pathlib').Path(__file__).read_bytes()).hexdigest()}
    (web / 'flight-sampling.json').write_text(json.dumps(state, indent=2))
    index = web / 'index.html'
    html = index.read_text()
    marker = '<!-- active-flight-sampling -->'
    end = '<!-- end-active-flight-sampling -->'
    if marker in html:
        before, rest = html.split(marker, 1); html = before + rest.split(end, 1)[1]
    note = marker + '<section class="note"><h2>The trajectory distribution through 00:11</h2><p>The forward/backward investigation begins at 4/2/2 and tests independent ensembles in the thousands. <a href="flight-sampling.html">Open the sampling results and comparisons</a>. Earlier terminal illustrations below are outside this trial.</p></section>' + end
    index.write_text(html.replace('<main>', '<main>' + note, 1))
