"""Score completed independent synthetic pairs; never inspect unfinished truth."""
import argparse
import datetime as dt
import html
import json
import math
from pathlib import Path
import shlex
import shutil
import urllib.request

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from arc_density_report import cdf_difference, digest, quantiles, read_run


def score_run(run, truth):
    xy, w = run['points'], run['weight']
    ranks = [float(w[xy[:, k] <= truth[k]].sum()) for k in range(2)]
    roots = {}
    for row, weight in zip(run['rows'], w):
        roots[row['root']] = roots.get(row['root'], 0.) + float(weight)
    return dict(cdf_at_truth=ranks, coordinate_quantiles_05_50_95=quantiles(xy, w),
                largest_ancestor_mass=max(roots.values()), weighted_row_effective_count=float(1 / (w @ w)),
                elapsed_seconds=run['summary']['elapsed_seconds'],
                log_evidence=run['summary']['log_evidence'],
                posterior_sha256=run['summary']['posterior_csv_sha256'])


def wilson(k, n):
    if not n:
        return None
    z = 1.959963984540054
    center = (k / n + z*z / (2*n)) / (1 + z*z/n)
    half = z * math.sqrt(k/n * (1-k/n)/n + z*z/(4*n*n)) / (1+z*z/n)
    return [max(0., center-half), min(1., center+half)]


def summarize(entries):
    result = []
    for replicate in range(2):
        for coordinate in range(2):
            values = [e['replicates'][replicate]['cdf_at_truth'][coordinate]
                      for e in entries if e['replicates'][replicate] is not None]
            result.append(dict(replicate=replicate, coordinate=['latitude', 'longitude'][coordinate],
                total_data_sets=len(entries), computed_posteriors=len(values),
                uncomputed_posteriors=len(entries)-len(values),
                intervals=[dict(nominal_mass=mass,
                    inside=sum((1-mass)/2 <= v <= (1+mass)/2 for v in values),
                    wilson95_fraction_among_computed=wilson(sum((1-mass)/2 <= v <= (1+mass)/2 for v in values), len(values)))
                    for mass in [.5, .9]]))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--state', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--inline-output', required=True, type=Path)
    p.add_argument('--reference-summary', type=Path)
    a = p.parse_args()
    state = json.loads(a.state.read_text())
    design_path = Path(state['design'])
    assert digest(design_path) == state['design_sha256']
    design = json.loads(design_path.read_text())
    fuel_enabled = bool(design.get('fuel_condition_enabled'))
    fuel_note = ('Generating routes were accepted by an independent uniform draw against the same remaining-fuel-envelope probability used in inference. Acceptance uses no SATCOM measurement or noise value. This checks computation conditional on that envelope, not the physical validity of the fuel model or an exact exhaustion trajectory.'
                 if fuel_enabled else 'Fuel is disabled, isolating the flight/SATCOM process.')
    observation_fitted = design.get('initial_proposal_strategy') == 'observation_only_completed_pilots'
    proposal_note = ('The initial Mach/altitude proposal was learned from completed pilots using each generated data set\'s own observations, with the existing importance correction and full-prior fallback. It has no access to the generating route.'
                    if observation_fitted else 'The accident-specific initial proposal is disabled for this control.')
    completed = {r['inference_seed']: r for r in state['runs']}
    entries = []
    for fixture in design['fixtures']:
        # Both inference attempts must finish before this scorer opens truth.
        if not all(r['inference_seed'] in completed for r in fixture['runs']):
            continue
        truth_path = Path(fixture['truth_file'])
        assert digest(truth_path) == fixture['truth_sha256']
        truth = json.loads(truth_path.read_text())
        terminal = truth['contact_states'][-1]
        position = terminal['aircraft']['position']
        target = [position['latitude'], position['longitude']]
        runs = [read_run(Path(r['output'])) if completed[r['inference_seed']]['status'] == 'completed' else None
                for r in fixture['runs']]
        e = dict(truth_seed=fixture['truth_seed'], truth_coordinates_deg=target,
                 generating_mode=truth['generating_mode'],
                 generating_limited_manoeuvre_counts=terminal['limited_manoeuvre_counts'],
                 truth_sha256=fixture['truth_sha256'],
                 replicates=[score_run(r, target) if r is not None else None for r in runs])
        if all(r is not None for r in runs):
            e['independent_maximum_coordinate_cdf_difference'] = cdf_difference(
                (runs[0]['points'], runs[0]['weight']), (runs[1]['points'], runs[1]['weight']))
            logz = np.array([r['summary']['log_evidence'] for r in runs])
            efforts = np.array([r['summary']['initial_particles'] for r in runs])
            mixture = efforts * np.exp(logz - logz.max())
            mixture /= mixture.sum()
            points = np.concatenate([r['points'] for r in runs])
            weights = np.concatenate([m*r['weight'] for m, r in zip(mixture, runs)])
            e['pooled_cdf_at_truth'] = [float(weights[points[:, k] <= target[k]].sum()) for k in range(2)]
        entries.append(e)
    a.output.mkdir(parents=True, exist_ok=True)
    result = dict(status=state['status'], updated_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                  completed_data_sets=len(entries), planned_data_sets=len(design['fixtures']),
                  initial_candidates_per_run=design['initial_candidates_per_run'],
                  design_sha256=state['design_sha256'], executable_sha256=state['executable_sha256'],
                  summaries=summarize(entries), data_sets=entries,
                  scope='Prior-predictive numerical control; fuel '+('envelope conditioned' if fuel_enabled else 'disabled')+'; no accident calibration; coordinate intervals are not joint geographic areas',
                  method_reference=dict(url='https://sites.stat.columbia.edu/gelman/research/unpublished/sbc.pdf',
                      locator='pp. 3–5: prior-predictive repetition, empirical CDF limitations and computational scope'),
                  limitations=[f"Only {len(design['fixtures'])} generated data sets in this comparison; binomial uncertainty is substantial.",
                      'Weighted interacting particle rows are not independent posterior draws; these CDF diagnostics are not an exact independent-rank SBC test.',
                      'Generator shares flight and SATCOM equations with inference. Independent physical and equation checks remain necessary.',
                      fuel_note, proposal_note])
    reference_path = a.reference_summary or (Path(design['reference_summary']) if design.get('reference_summary') else None)
    reference = None
    if reference_path:
        reference = json.loads(reference_path.read_text())
        assert reference['design_sha256'] == design['original_design_sha256']
        if design.get('reference_summary_sha256'):
            assert digest(reference_path) == design['reference_summary_sha256']
        previous = {e['truth_seed']: e for e in reference['data_sets']}
        for e in entries:
            original = previous[e['truth_seed']]
            assert original['truth_sha256'] == e['truth_sha256']
            e['reference_pair_cdf_difference'] = original.get('independent_maximum_coordinate_cdf_difference')
            e['reference_pooled_cdf_at_truth'] = original.get('pooled_cdf_at_truth')
        result['reference_summary'] = str(reference_path.resolve())
        result['reference_summary_sha256'] = digest(reference_path)
        result['reference_candidates_per_run'] = reference['initial_candidates_per_run']
    (a.output / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout='constrained')
    for k, label, color in [(0, 'Latitude', '#00769c'), (1, 'Longitude', '#bf5427')]:
        xs = [i+1 for i, e in enumerate(entries) if 'pooled_cdf_at_truth' in e]
        axes[0].scatter(xs, [e['pooled_cdf_at_truth'][k] for e in entries if 'pooled_cdf_at_truth' in e],
                        label=label, s=22, alpha=.8, color=color, marker=['o', 'x'][k])
        axes[1].plot(xs, [100*e['independent_maximum_coordinate_cdf_difference'][k] for e in entries
                          if 'pooled_cdf_at_truth' in e], '.-', label=label, color=color)
    axes[0].set(xlabel='Completed generated data set', ylabel='Pooled CDF evaluated at generating truth', ylim=(-.03, 1.03))
    for y in [.05, .95]:
        axes[0].axhline(y, color='#777777', lw=.7, ls=':')
    axes[1].set(xlabel='Completed generated data set', ylabel='Largest independent-run CDF difference (pp)')
    for ax in axes:
        ax.grid(alpha=.15)
        ax.legend()
    for extension in ['svg', 'pdf', 'png']:
        fig.savefig(a.output / ('recovery-comparison.' + extension), dpi=160)
    plt.close(fig)
    comparison_svg = ''
    if reference is not None:
        fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout='constrained')
        for k, ax in enumerate(axes):
            matched = [e for e in entries if e.get('reference_pair_cdf_difference') is not None
                       and e.get('independent_maximum_coordinate_cdf_difference') is not None]
            x = np.arange(len(matched))
            ax.bar(x-.18, [100*e['reference_pair_cdf_difference'][k] for e in matched],
                   width=.35, label=f"Original {reference['initial_candidates_per_run']:,} / run", color='#9daab0')
            label = ('Observation-fitted proposal' if observation_fitted else 'Larger run') + f"; {design['initial_candidates_per_run']:,} / run"
            ax.bar(x+.18, [100*e['independent_maximum_coordinate_cdf_difference'][k] for e in matched],
                   width=.35, label=label, color=['#00769c', '#bf5427'][k])
            ax.set(xticks=x, xticklabels=[str(e['truth_seed'])[-2:] for e in matched],
                   xlabel='Original generated-data index', ylabel='Independent-pair CDF difference (pp)',
                   title=['Latitude', 'Longitude'][k])
            ax.legend(fontsize=8)
            ax.grid(axis='y', alpha=.15)
        for extension in ['svg', 'pdf', 'png']:
            fig.savefig(a.output / ('sampling-comparison.'+extension), dpi=160)
        plt.close(fig)
        comparison_svg = (a.output/'sampling-comparison.svg').read_text()
        comparison_svg = '<h2>Same generated data, different sampling</h2><p>Each bar compares an independent pair. The original data sets were selected by their pre-existing indices, without selecting on their recovery results. Smaller disagreement is useful evidence about numerical variation; agreement alone cannot establish correctness.</p>' + comparison_svg[comparison_svg.index('<svg'):]
    table = ''
    for s in result['summaries']:
        vals = []
        for interval in s['intervals']:
            ci = interval['wilson95_fraction_among_computed']
            text = f"{interval['inside']}/{s['computed_posteriors']}"
            if ci:
                text += f"; fraction uncertainty {100*ci[0]:.0f}–{100*ci[1]:.0f}%"
            vals.append(text)
        table += f"<tr><td>{s['replicate']+1}: {s['coordinate']}</td><td>{vals[0]}</td><td>{vals[1]}</td><td>{s['uncomputed_posteriors']}</td></tr>"
    details = ''
    for e in entries:
        vals = e.get('pooled_cdf_at_truth')
        diff = e.get('independent_maximum_coordinate_cdf_difference')
        details += '<tr>' + ''.join('<td>'+html.escape(str(x))+'</td>' for x in [e['truth_seed'],
            e['generating_mode'], '/'.join(map(str, e['generating_limited_manoeuvre_counts'])),
            ' / '.join(f'{v:.3f}' for v in vals) if vals else 'Uncomputed',
            ' / '.join(f'{100*v:.1f}' for v in diff) if diff else 'Uncomputed']) + '</tr>'
    svg = (a.output / 'recovery-comparison.svg').read_text()
    svg = svg[svg.index('<svg'):]
    command = shlex.join(['python', str(Path(__file__).resolve()), '--state', str(a.state.resolve()),
                         '--output', str(a.output.resolve()), '--inline-output', str(a.inline_output.resolve())])
    if a.reference_summary:
        command += ' --reference-summary ' + shlex.quote(str(a.reference_summary.resolve()))
    document = f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Cruise filter recovery controls</title>
<style>body{{max-width:1000px;margin:auto;padding:18px;font:17px/1.55 system-ui;color:#172a34}}svg{{width:100%;height:auto}}table{{border-collapse:collapse;font-size:14px}}td,th{{padding:9px;border-bottom:1px solid #ccd;text-align:left}}.scroll{{overflow-x:auto}}pre{{white-space:pre-wrap;font-size:12px}}li{{margin-bottom:8px}}</style></head><body>
<h1>Cruise filter recovery controls</h1><p>{len(entries)} of {len(design['fixtures'])} independently generated data sets have completed both inference runs. Each run starts with {design['initial_candidates_per_run']:,} candidates. Updated {result['updated_utc']}.</p>
<p>Every route and noisy contact sequence was generated before inference began. The estimator receives the generated measurements and original environment, with no access to its generating route. {html.escape(fuel_note)} {html.escape(proposal_note)}</p>
<p>The left plot shows where the generating location falls in each computed coordinate distribution. With exact inference over repeated prior-generated data, these values would spread uniformly from zero to one. The right plot measures disagreement between the two independent numerical runs. Large differences expose limited sampling resolution; they do not prove which run is closer to the exact answer.</p>{svg}
{comparison_svg}<h2>Repeated interval recovery</h2><p>Counts below use each replicate separately. The ranges describe 95% Wilson uncertainty in the observed recovery fraction. They do not measure an individual flight's geographic uncertainty. Uncomputed cases remain explicitly listed.</p>
<div class="scroll"><table><tr><th>Replicate / coordinate</th><th>Inside central 50% interval</th><th>Inside central 90% interval</th><th>Uncomputed</th></tr>{table}</table></div>
<p>This follows the repeated prior-predictive principle described by <a href="https://sites.stat.columbia.edu/gelman/research/unpublished/sbc.pdf">Talts and colleagues, pp. 3–5</a>. Because weighted particle rows share ancestors, the display is a finite-sample recovery diagnostic, not an exact independent-rank calibration test. Passing it would check computation under this model; it would not establish that this model describes MH370 correctly.</p>
<ul>{''.join('<li>'+html.escape(x)+'</li>' for x in result['limitations'])}</ul>
<details><summary>Individual generated data sets</summary><div class="scroll"><table><tr><th>Truth seed</th><th>Generating mode</th><th>Turns / Mach / altitude changes</th><th>Pooled truth CDF: lat / lon</th><th>Independent CDF difference: lat / lon (pp)</th></tr>{details}</table></div></details>
<details><summary>Reproduce this report</summary><pre>{html.escape(command)}</pre><p>Frozen executable SHA256: {state['executable_sha256']}. Full precision scores, input identities and vector figures accompany the report.</p></details></body></html>'''
    (a.output / 'index.html').write_text(document)
    a.inline_output.write_text(document)
    web = a.state.parent.parent / 'overnight-analysis/web' / a.inline_output.name
    if web.parent.exists():
        shutil.copyfile(a.inline_output, web)
        assert urllib.request.urlopen('http://127.0.0.1:8771/overnight/' + web.name).read() == a.inline_output.read_bytes()
        from report_index import generate
        generate(a.state.parent, a.inline_output.with_name('mh370-results.html'))
    print(json.dumps(dict(completed_pairs=len(entries), report=str(a.inline_output))))


if __name__ == '__main__':
    main()
