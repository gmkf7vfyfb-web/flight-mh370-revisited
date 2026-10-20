"""Build the current browser report directory from recorded estimator results."""
import argparse
import datetime as dt
import hashlib
import html
import json
import statistics
from pathlib import Path
import urllib.request


def generate(analysis, preview):
    identities = {}
    def read(relative):
        path = analysis / relative
        data = path.read_bytes()
        identities[relative] = hashlib.sha256(data).hexdigest()
        return json.loads(data)
    broad = read('broader-arc-density/summary.json')
    terminal = read('terminal-million-extended-weather/progress.json')
    conditions = read('terminal-million-extended-weather-conditioned/summary.json')
    recovery = read('synthetic-cruise-status.json')
    recovery_scores = read('synthetic-cruise-comparison/summary.json')
    recovery_differences = [e['independent_maximum_coordinate_cdf_difference']
                           for e in recovery_scores['data_sets']
                           if 'independent_maximum_coordinate_cdf_difference' in e]
    recovery_medians = [statistics.median(d[k] for d in recovery_differences) for k in range(2)]
    spatial = read('spatial-million-status.json')
    report_state = read('report-state.json')
    browser_base = report_state.get('browser_report_base_url', '')
    impacts = sum(n for key, n in terminal['outcomes'].items() if key.endswith(':Impact'))
    ess = {name: [c['row_weight_effective_count'] for f in conditions['families']
                 for c in f['cases'] if c['name'] == name]
           for name in ['r600-no-startup-offset', 'both-sequential-no-startup-offset']}
    links = [
        ('mh370-broader-arc-density.html', 'Broader 00:11 distribution', '16 turns, 8 Mach and 8 altitude changes allowed; complexity by latitude and operating-state distributions.'),
        ('mh370-broader-route-examples.html', 'Actual broader-model trajectories', 'Recorded route examples in every populated 2.5° latitude bin.'),
        ('mh370-report-preview.html', 'Original 00:11 comparison', 'Separate million-candidate 4/2/2 model; its narrower assumptions remain explicit.'),
        ('mh370-model-comparison.html', 'Sensitivity to flight assumptions', 'Matched ensembles compare successive turn, speed and altitude allowances and vertical Doppler.'),
        ('mh370-antenna-comparison.html', 'Conditional antenna comparison', 'Separate gain, pitch and compensation assumptions; calibration is provisional.'),
        ('mh370-impact-comparison.html', '00:11 through impact', 'Twelve terminal flight models and ten final-contact cases each; includes R600 first and both-contact sensitivities.'),
        ('mh370-drift-comparison.html', 'Conditional ocean drift', 'Nine recovery episodes under the attributed CMEMS model; spatial support is explicit.'),
        ('mh370-stokes-comparison.html', 'Conditional Stokes sensitivity', 'Matched flaperon-only evidence under three surface Stokes factors.'),
        ('mh370-pleiades-comparison.html', 'Conditional Pléiades objects', 'Three separate transport models, conditional on object identity.'),
        ('mh370-acoustic-comparison.html', 'Acoustic predictions and Kadri examples', 'Arrival geometry, energy scenarios and recorded selected trajectories; no hydroacoustic detection likelihood.'),
        ('mh370-proposed-route-comparison.html', 'Godfrey/WSPR proposed route', 'Published route, speed/timing checks and predicted acoustic windows; no validated WSPR aircraft likelihood.'),
        ('mh370-search-comparison.html', 'Search context and 7,500 km² planning', 'Conditional cell capture and resolution sensitivity; existing coverage does not yet supply a calibrated non-detection likelihood.'),
        ('mh370-synthetic-recovery.html', 'Filter recovery controls', 'Repeated generated flights, separate truth scoring and independent numerical runs.'),
    ]
    larger_note = ''
    if (analysis / 'synthetic-cruise-larger-status.json').exists():
        larger = read('synthetic-cruise-larger-status.json')
        larger_note = f" Larger runs on the same eight fixed-index data sets: {larger['completed_pairs']} of 8 pairs complete at 100,000 candidates per run; {html.escape(larger['status'].replace('_',' '))}."
        if (preview.parent / 'mh370-synthetic-larger-recovery.html').exists():
            links.append(('mh370-synthetic-larger-recovery.html', 'Larger filter recovery runs', 'Two independent 100,000-candidate estimates for every third original synthetic data set.'))
    if (analysis / 'synthetic-cruise-guided-status.json').exists():
        guided = read('synthetic-cruise-guided-status.json')
        larger_note += f" The observation-fitted initial-proposal check has completed {guided['completed_pairs']} of 8 pairs; {html.escape(guided['status'].replace('_',' '))}."
        if (preview.parent / 'mh370-synthetic-guided-recovery.html').exists():
            links.append(('mh370-synthetic-guided-recovery.html', 'Observation-fitted proposal control', 'Same eight generated data sets; proposals fitted from separate observation-only pilots and corrected in the weights.'))
    items = ''
    files = {}
    for filename, title, description in links:
        path = preview.parent / filename
        if not path.exists():
            raise ValueError('Missing report: ' + str(path))
        files[filename] = hashlib.sha256(path.read_bytes()).hexdigest()
        items += f'<li><a href="{html.escape(browser_base + filename, quote=True)}" target="_blank" rel="noopener">{html.escape(title)}</a><p>{html.escape(description)}</p></li>'
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    document = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MH370 current results</title>
<style>body{{max-width:880px;margin:auto;padding:20px;font:17px/1.55 system-ui;color:#152d38;background:#fcfcfa}}a{{color:#086680}}h1{{font-size:1.8em}}h2{{font-size:1.2em}}ul{{padding-left:24px}}li{{padding:12px 0;border-bottom:1px solid #d9e1e4}}li p{{margin:3px 0;font-size:.93em}}small{{color:#53656e}}.note{{padding:14px;background:#eef4f5}}</style></head><body>
<h1>MH370: current calculations and limitations</h1><small>Generated {now}. This page links to browser reports; no PDF download is needed.</small>
<p>The broader cruise calculation now uses {broad['total_initial_candidates']:,} initial candidates. About {100*broad['regions']['between_35S_and_38S']:.0f}% of its computed 00:11 probability lies between 35°S and 38°S, with a northern tail. This is conditional on the stated flight, SATCOM and fuel assumptions. The final added ensemble and the earlier pool differ by up to {100*max(broad['additional_vs_baseline_cdf_difference']):.1f} percentage points in a coordinate CDF. The sample count does not remove that numerical uncertainty.</p>
<p>The full cruise pool has been continued to impact: {terminal['rows']:,} physical records, {impacts:,} computed impacts and 120 separate final-contact/model cases. The extended weather grid has removed the earlier altitude-domain failures. For R600-only cases, effective row counts range from {min(ess['r600-no-startup-offset']):.0f} to {max(ess['r600-no-startup-offset']):.0f}; using both BFOs without a startup offset leaves only {min(ess['both-sequential-no-startup-offset']):.1f}–{max(ess['both-sequential-no-startup-offset']):.1f}. Those narrow two-contact maps remain numerically unresolved.</p>
<p class="note">Core validation: {recovery['completed_pairs']} of 24 generated data sets have completed both independent 20,000-candidate estimates. Median latitude/longitude CDF disagreement between these pairs is {100*recovery_medians[0]:.1f}/{100*recovery_medians[1]:.1f} percentage points. Completion has not established statistical stability.{larger_note} The drift/Pléiades refresh from the full-million terminal source is {html.escape(spatial['status'].replace('_',' '))}; {len(spatial['completed'])} of {len(spatial['queue'])} comparisons have finished.</p>
<h2>Open a report</h2><ul>{items}</ul>
<h2>What remains unresolved</h2><p>A reliable, fully combined impact estimate still needs stronger numerical support for the two-BFO sequence and defensible calibration of the optional evidence. Public fuel and terminal aerodynamic proxies are explicit model choices. Impact velocity direction does not establish aircraft body attitude. Acoustic coupling, event identification, WSPR aircraft detection and seabed detection probabilities are not measured likelihoods in these results. Models with different assumptions remain separate; the reported spread is not automatically a confidence interval or an operational search recommendation.</p>
<p>Each linked report records its own inputs, configurations, numerical limits and reproduction command. Complete weights and vector figures remain in the recorded run artifacts. The original estimator and publishable-paper objective remains active.</p></body></html>'''
    out = analysis / 'current-report'
    out.mkdir(exist_ok=True)
    (out / 'index.html').write_text(document)
    preview.write_text(document)
    manifest = dict(generated_utc=now, input_sha256=identities, report_sha256=files)
    web = analysis.parent / 'overnight-analysis/web'
    (web / preview.name).write_text(document)
    for filename in files:
        (web / filename).write_bytes((preview.parent / filename).read_bytes())
        assert urllib.request.urlopen('http://127.0.0.1:8771/overnight/' + filename).read() == (preview.parent / filename).read_bytes(), filename
    assert urllib.request.urlopen('http://127.0.0.1:8771/overnight/' + preview.name).read() == preview.read_bytes()
    manifest['all_linked_reports_local_http_byte_verified'] = True
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--analysis', required=True, type=Path)
    p.add_argument('--inline-output', required=True, type=Path)
    a = p.parse_args()
    generate(a.analysis, a.inline_output)
