"""Attribute saved terminal concentration; never simulate or release a PDF."""
from pathlib import Path
import csv
import hashlib
import json
import sys
import time
import numpy as np


def normalized(logw):
    w = np.exp(logw - np.max(logw))
    return w / w.sum()


def run(path):
    with (path / 'posterior.csv').open() as f:
        rows = list(csv.DictReader(f))
    states = json.loads((path / 'particles.json').read_text())['particles']
    assert len(rows) == len(states)
    positive = np.array([float(r['weight']) > 0 for r in rows])
    rows = [r for r, keep in zip(rows, positive) if keep]
    states = [p for p, keep in zip(states, positive) if keep]
    # Record order is the runner's final-particle order. Verify that alignment
    # against independently formatted CSV coordinates before using fields.
    assert all(abs(float(r['latitude_deg']) - p['flight']['aircraft']['position']['latitude']) < 1e-8
               and abs(float(r['longitude_deg']) - p['flight']['aircraft']['position']['longitude']) < 1e-8
               for r, p in zip(rows, states))
    logw = np.log([float(r['weight']) for r in rows])
    correction = np.array([p['initial_proposal_log_correction'] for p in states])
    fuel = np.array([float(r['fuel_log_factor']) for r in rows])
    roots = np.array([int(r['root']) for r in rows])
    xy = np.array([[float(r[k]) for k in ['latitude_deg', 'longitude_deg']] for r in rows])
    modes = np.array([r['initial_mode'] for r in rows])
    physical_weights = normalized(logw)
    influential_root = int(np.argmax(np.bincount(roots, weights=physical_weights)))
    results, variants = {}, {}
    for name, logs in [
        ('original', logw),
        ('retaining_initial_proposal_guidance', logw - correction),
        ('without_fuel_factor_on_positive_fuel_support', logw - fuel),
        ('without_both_factors_on_positive_fuel_support', logw - fuel - correction),
    ]:
        w = normalized(logs)
        variants[name] = (xy, w)
        rw = np.bincount(roots, weights=w)
        results[name] = {
            'largest_ancestry_fraction': float(rw.max()),
            'original_influential_root_fraction': float(rw[influential_root]),
            'inverse_ancestry_concentration': float(1 / np.square(rw).sum()),
            'initial_mode_mass': {m: float(w[modes == m].sum()) for m in sorted(set(modes))},
        }
    selected = roots == influential_root
    result = {
        'run': path.name,
        'positive_weight_rows': len(rows),
        'total_rows': len(positive),
        'original_influential_root': influential_root,
        'influential_root_initial_log_p_over_q_range': [float(correction[selected].min()), float(correction[selected].max())],
        'terminal_guidance_zero': all(p['initial_proposal_potential'] == 0 for p in states),
        'variants': results,
        'source_sha256': {n: hashlib.sha256((path / n).read_bytes()).hexdigest()
                          for n in ['posterior.csv', 'summary.json']},
    }
    return result, variants


def main(paths):
    start = time.perf_counter()
    results, populations = [], []
    for path in paths:
        result, population = run(path)
        results.append(result)
        populations.append(population)
    comparisons = {}
    for name in populations[0]:
        diffs = []
        for k in range(2):
            grid = np.sort(np.concatenate([p[name][0][:, k] for p in populations]))
            cdfs = []
            for p in populations:
                xy, w = p[name]
                order = np.argsort(xy[:, k])
                cdfs.append(np.r_[0., np.cumsum(w[order])][np.searchsorted(xy[order, k], grid, side='right')])
            diffs.append(float(np.max(np.abs(cdfs[0] - cdfs[1]))))
        comparisons[name] = {'coordinate_cdf_differences': diffs}
    return {
        'runs': results, 'comparisons': comparisons,
        'elapsed_postprocessing_seconds': time.perf_counter() - start,
        'limitation': ('Counterfactual weighting diagnostics on the saved positive-weight support only. '
                       'Removing the fuel factor cannot recover fuel-excluded or earlier extinct routes; '
                       'retaining proposal guidance changes the scientific target and is not a proposed fix. '
                       'Ancestry concentration is not independent Monte Carlo ESS. No flight is rerun.'),
    }


if __name__ == '__main__':
    paths = [Path(p) for p in sys.argv[1:3]]
    result = main(paths)
    (paths[0].parent.parent / 'terminal-weight-attribution.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
