"""Pool independent saved SMC runs and report airborne geographic density.

No inference, smoothing, or probability threshold is imposed by this report.
Run weights are proportional to initial effort times estimated normalizers.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
from pathlib import Path
import shlex

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.patches import Polygon
import numpy as np

A_KM = 6378.137
E2 = (1 / 298.257223563) * (2 - 1 / 298.257223563)
E = np.sqrt(E2)
K0 = np.cos(np.deg2rad(35)) / np.sqrt(1 - E2 * np.sin(np.deg2rad(35)) ** 2)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def q(phi):
    s = np.sin(phi)
    return (1 - E2) * (s / (1 - E2 * s * s) + np.arctanh(E * s) / E)


def project(latitude, longitude):
    """WGS84 ellipsoidal cylindrical equal-area coordinates, kilometres."""
    return (A_KM * K0 * np.deg2rad(np.asarray(longitude) - 90),
            A_KM * (q(np.deg2rad(latitude)) - q(np.deg2rad(-35))) / (2 * K0))


def inverse(x, y):
    target = np.asarray(y) * 2 * K0 / A_KM + q(np.deg2rad(-35))
    lo, hi = np.full_like(target, -np.pi / 2), np.full_like(target, np.pi / 2)
    for _ in range(52):
        mid = (lo + hi) / 2
        less = q(mid) < target
        lo, hi = np.where(less, mid, lo), np.where(less, hi, mid)
    return np.rad2deg((lo + hi) / 2), np.rad2deg(np.asarray(x) / (A_KM * K0)) + 90


def read_run(path):
    summary = json.loads((path / 'summary.json').read_text())
    config = json.loads((path / 'resolved-config.json').read_text())
    if 'sampling' in config:
        config['branching'] = config['sampling']  # archived report metadata key
    provenance = json.loads((path / 'provenance.json').read_text())
    if not summary.get('posterior_available'):
        raise ValueError(f'No completed estimate in {path}')
    if digest(path / 'posterior.csv') != summary['posterior_csv_sha256']:
        raise ValueError(f'Posterior checksum mismatch: {path}')
    with (path / 'posterior.csv').open() as f:
        rows = list(csv.DictReader(f))
    xy = np.array([[float(r[k]) for k in ['latitude_deg', 'longitude_deg']] for r in rows])
    w = np.array([float(r['weight']) for r in rows])
    if not np.all(np.isfinite(w)) or np.any(w < 0) or abs(w.sum() - 1) > 1e-8:
        raise ValueError('Invalid saved probability weights')
    w /= w.sum()
    return dict(path=path, summary=summary, config=config, provenance=provenance,
                points=xy, weight=w, rows=rows,
                initial_modes=np.array([r['initial_mode'] for r in rows]),
                final_modes=np.array([r['final_mode'] for r in rows]))


def physical_identity(run):
    cfg = run['config']
    model = json.loads(json.dumps(cfg['model']))
    model.pop('proposal_guide', None)
    model['dynamics'].pop('marginalize_manoeuvre_rate', None)
    return dict(model=model, inputs=run['provenance']['inputs'], modes=cfg['modes'],
                mode_probabilities=cfg['mode_probabilities'], input_settings=cfg['inputs'],
                scientific_source=run['provenance']['scientific_source_sha256'])


def mix_weights(runs, equal=False):
    effort=np.array([r['summary']['initial_particles'] for r in runs],dtype=float)
    if not np.all(np.isfinite(effort)) or np.any(effort<=0):
        raise ValueError('Runs must record positive initial effort')
    logz = np.array([r['summary']['log_evidence'] for r in runs])
    if not np.all(np.isfinite(logz)):
        raise ValueError('Missing finite normalizer estimate')
    weights = np.ones(len(runs)) if equal else effort*np.exp(logz-logz.max())
    return weights / weights.sum()


def pool(runs, equal=False):
    alpha = mix_weights(runs, equal)
    return (np.concatenate([r['points'] for r in runs]),
            np.concatenate([r['weight'] * a for r, a in zip(runs, alpha)]))


def quantiles(points, weights, ps=(.05, .5, .95)):
    out = []
    for col in range(2):
        order = np.argsort(points[:, col])
        cumulative = np.cumsum(weights[order])
        out.append(points[order, col][np.searchsorted(cumulative, ps).clip(max=len(order)-1)].tolist())
    return out


def cdf_difference(first, second):
    out = []
    for col in range(2):
        grid = np.sort(np.r_[first[0][:, col], second[0][:, col]])
        cdfs = []
        for xy, w in [first, second]:
            order = np.argsort(xy[:, col])
            cdfs.append(np.r_[0, np.cumsum(w[order])][np.searchsorted(xy[order, col], grid, 'right')])
        out.append(float(np.max(np.abs(cdfs[0] - cdfs[1]))))
    return out


def region_masses(points, weights):
    lat = points[:, 0]
    return {'south_of_35S': float(weights[lat < -35].sum()),
            'between_35S_and_38S': float(weights[(lat >= -38) & (lat <= -35)].sum()),
            'north_of_35S': float(weights[lat > -35].sum()),
            'north_of_30S': float(weights[lat > -30].sum()),
            'south_of_38S': float(weights[lat < -38].sum())}


def area_grid(points, weights, cell_km, bounds=None):
    x, y = project(points[:, 0], points[:, 1])
    positive = weights > 0
    if bounds is None:
        bounds = [x[positive].min(), x[positive].max(), y[positive].min(), y[positive].max()]
    xe = np.arange(np.floor(bounds[0] / cell_km) - 1,
                   np.ceil(bounds[1] / cell_km) + 2) * cell_km
    ye = np.arange(np.floor(bounds[2] / cell_km) - 1,
                   np.ceil(bounds[3] / cell_km) + 2) * cell_km
    mass = np.histogram2d(y, x, bins=[ye, xe], weights=weights)[0]
    if not np.isclose(mass.sum(), 1, atol=1e-10, rtol=0):
        raise ValueError('Grid excludes probability mass')
    return xe, ye, mass


def ranked_area(mass, cell_km):
    ordered = np.sort(mass.ravel())[::-1]
    cumulative = np.cumsum(ordered)
    return {str(p): {'area_km2': float((np.searchsorted(cumulative, p) + 1) * cell_km ** 2),
                     'probability_in_selected_cells': float(cumulative[np.searchsorted(cumulative, p)])}
            for p in [.5, .8, .9, .95]}


def reference_arc(config):
    """Eastern BTO branch at 35,000 ft; annotation only, no projection of samples."""
    with Path(config['inputs']['observations']).open() as f:
        obs = list(csv.DictReader(f))[-1]
    with Path(config['inputs']['satellite_ephemeris']).open() as f:
        sat = next(r for r in csv.DictReader(f) if r['epoch_id'] == obs['epoch_id'])
    s = np.array([float(sat[k]) for k in ['x_km', 'y_km', 'z_km']])
    g = np.array([config['inputs']['ground_station_position_km'][k] for k in ['x', 'y', 'z']])
    c = config['model']['satcom']['bto']
    distance = ((float(obs['bto_us']) + c['nominal_delay_us'] - c['channel_term_us'])
                * 1e-6 * c['speed_of_light_km_s'] / 2 - np.linalg.norm(s-g))
    lat = np.linspace(-55, 20, 15001)
    phi = np.deg2rad(lat)
    n = A_KM / np.sqrt(1 - E2 * np.sin(phi) ** 2)
    rho = (n + 35000 * .0003048) * np.cos(phi)
    z = (n * (1 - E2) + 35000 * .0003048) * np.sin(phi)
    cosine = (np.dot(s, s) + rho*rho + z*z - 2*s[2]*z - distance*distance) / (2*rho*np.hypot(s[0], s[1]))
    valid = np.abs(cosine) <= 1
    longitude = np.rad2deg(np.arctan2(s[1], s[0]) + np.arccos(cosine[valid]))
    return lat[valid], longitude, {'time_utc': obs['time_utc'], 'bto_us': float(obs['bto_us']),
                                 'altitude_ft': 35000, 'satellite_aircraft_range_km': float(distance)}


def save_figure(fig, output, name):
    fig.savefig(output / f'{name}.svg', bbox_inches='tight')
    fig.savefig(output / f'{name}.pdf', bbox_inches='tight', dpi=220)
    fig.savefig(output / f'{name}.png', bbox_inches='tight', dpi=145)
    stream = io.StringIO()
    fig.savefig(stream, format='svg', bbox_inches='tight')
    plt.close(fig)
    svg = stream.getvalue()
    return svg[svg.index('<svg'):]


def draw_land(ax):
    path = Path(__file__).parents[1] / 'assets/ne_110m_land.geojson'
    data = json.loads(path.read_text())
    for feature in data['features']:
        g = feature.get('geometry') or {}
        polygons = [g['coordinates']] if g.get('type') == 'Polygon' else g.get('coordinates', [])
        for rings in polygons:
            if rings:
                ax.add_patch(Polygon(rings[0], facecolor='#e4e4d9', edgecolor='#9ca69b', linewidth=.4, zorder=1))


def map_figure(points, weights, grid, arc, output, n, run_count, altitude_range_ft, condition_label=None):
    xe, ye, mass = grid
    lat_edges, lon_edges = inverse(xe, ye)
    density = mass / 25
    positive = density[density > 0]
    norm = LogNorm(vmin=max(positive.max() / 10000, 1e-10), vmax=positive.max())
    fig, axes = plt.subplots(1, 2, figsize=(10, 7.4), gridspec_kw={'width_ratios': [1.15, 1]})
    views = [(83, 101, -40.5, -31.5), (72, 122, -45, 12)]
    titles = ['Southern concentration', 'Northern tail and regional context']
    for ax, view, title in zip(axes, views, titles):
        ax.set_facecolor('#f0f5f8')
        draw_land(ax)
        shown = np.ma.masked_where(mass <= 0, density)
        picture = ax.pcolormesh(lon_edges, lat_edges, shown, cmap='magma_r', norm=norm,
                               rasterized=True, zorder=3, shading='flat')
        ax.plot(arc[1], arc[0], color='#16858a', lw=.8, ls='--', zorder=2,
                label='Reference line only · 35,000 ft')
        inside = ((points[:, 1] >= view[0]) & (points[:, 1] <= view[1]) &
                  (points[:, 0] >= view[2]) & (points[:, 0] <= view[3]))
        ax.set(xlim=view[:2], ylim=view[2:], xlabel='Longitude (°E)', ylabel='Latitude (°)',
               title=f'{title}\n{100*weights[inside].sum():.2f}% of pooled mass in frame')
        ax.set_aspect(1 / np.cos(np.deg2rad(-35)))
        ax.grid(alpha=.18, linewidth=.5)
    axes[0].legend(loc='upper left', fontsize=7)
    fig.suptitle(f'Airborne area probability density at 00:10:59 UTC\n{n:,} initial candidates across {run_count} runs', fontsize=13)
    fig.subplots_adjust(bottom=.25, top=.78, wspace=.30)
    cax = fig.add_axes([.22, .13, .56, .023])
    bar = fig.colorbar(picture, cax=cax, orientation='horizontal')
    bar.set_label('Probability density (km⁻²) · logarithmic colour scale', fontsize=9)
    if condition_label:
        fig.text(.5,.055,condition_label,ha='center',fontsize=8)
    fig.text(.5, .023, '5 × 5 km equal-area cells; no added smoothing. All sample weights retained.\n'
             f'BTO/BFO + fuel condition. Sample altitudes span {altitude_range_ft[0]:,.0f}–{altitude_range_ft[1]:,.0f} ft; '
             '35,000 ft is the reference line only.',
             ha='center', fontsize=8)
    return save_figure(fig, output, 'area-density-0011')


def comparison_figure(runs, output, baseline_runs):
    baseline, additional, total = pool(runs[:baseline_runs]), pool(runs[baseline_runs:]), pool(runs)
    count = lambda group: sum(r['summary']['initial_particles'] for r in group)
    series = [(baseline, f'Original {baseline_runs} runs · {count(runs[:baseline_runs]):,}', '#337ea1', '-'),
              (additional, f'Additional runs · {count(runs[baseline_runs:]):,}', '#d57927', '--'),
              (total, f'All {len(runs)} runs · {count(runs):,}', '#273647', '-')]
    fig, axes = plt.subplots(2, 1, figsize=(7, 7))
    for col, ax in enumerate(axes):
        for (xy, w), label, colour, style in series:
            order = np.argsort(xy[:, col]); sx = xy[order, col]; cumulative = np.cumsum(w[order])
            selected = np.unique(np.r_[0, np.searchsorted(cumulative, np.linspace(0, 1, 2501)).clip(max=len(w)-1), len(w)-1])
            ax.step(sx[selected], cumulative[selected], where='post', label=label,
                    color=colour, ls=style, linewidth=1.6)
        lo, hi = np.array(quantiles(*total, ps=(.0001, .9999)))[col]
        ax.set(xlim=(lo-.3, hi+.3), ylim=(0, 1),
               xlabel=['Latitude (°; negative values are south)', 'Longitude (°E)'][col],
               ylabel='Cumulative probability')
        ax.grid(alpha=.2); ax.legend(fontsize=8)
    axes[0].axvspan(-38, -35, color='#7aa39a', alpha=.14)
    fig.suptitle('Cumulative comparison as the ensemble grows', fontsize=12)
    fig.tight_layout(rect=(0, .03, 1, .95))
    fig.text(.5, .012, 'No five-point pass/fail rule. These curves describe finite-sample estimates under the same physical model.',
             ha='center', fontsize=8)
    return save_figure(fig, output, 'cumulative-comparison-0011')


def latitude_figure(runs, output):
    points, weights = pool(runs)
    edges = np.arange(-50, 25.0001, .25)
    centers = (edges[:-1] + edges[1:]) / 2
    fig, axes = plt.subplots(2, 1, figsize=(7, 6), gridspec_kw={'height_ratios': [1.5, 1]})
    pooled = np.histogram(points[:, 0], bins=edges, weights=weights)[0] / .25
    for i, run in enumerate(runs):
        single = np.histogram(run['points'][:, 0], bins=edges, weights=run['weight'])[0] / .25
        axes[0].step(centers, single, where='mid', lw=.8, alpha=.6, label=f'Run {i+1}')
    axes[0].step(centers, pooled, where='mid', color='#26364a', lw=1.8, label='Combined')
    axes[0].set(xlim=(-40, -30), ylabel='Probability density per degree', title='Distribution along the arc, expressed by latitude')
    axes[0].axvspan(-38, -35, color='#7aa39a', alpha=.14);axes[0].legend(fontsize=7, ncol=3)
    axes[1].step(centers, pooled, where='mid', color='#26364a', lw=1.5)
    axes[1].set(yscale='log', xlim=(-40, 12), ylim=(1e-7, max(pooled)*2),
                xlabel='Latitude (°; negative values are south)', ylabel='Density · logarithmic scale', title='Northern tail at a wider scale')
    for ax in axes:ax.grid(alpha=.2)
    fig.tight_layout(rect=(0, .04, 1, 1))
    fig.text(.5, .012, 'Quarter-degree bins; no kernel smoothing. Latitude density integrates across longitude; the area map retains both dimensions.',
             ha='center', fontsize=8)
    return save_figure(fig, output, 'latitude-density-0011')


def scalar_quantiles(values, weights):
    order = np.argsort(values)
    index = np.searchsorted(np.cumsum(weights[order]), [.05, .5, .95]).clip(max=len(order)-1)
    return values[order][index].tolist()


def operating_state(runs):
    alpha = mix_weights(runs)
    weights = np.concatenate([r['weight'] * a for r, a in zip(runs, alpha)])
    result = {}
    columns = {}
    for name in ['altitude_ft', 'mach']:
        values = np.array([float(row[name]) for run in runs for row in run['rows']])
        columns[name] = values
        result[name] = dict(quantiles_05_50_95=scalar_quantiles(values, weights),
                            positive_weight_range=[float(values[weights > 0].min()),
                                                   float(values[weights > 0].max())])
    result['altitude_ft']['probability_exactly_35000'] = float(weights[columns['altitude_ft'] == 35000].sum())
    for name in ['limited_turns', 'limited_speed_changes', 'limited_altitude_changes']:
        values = np.array([int(row[name]) for run in runs for row in run['rows']])
        result[name] = {str(v): float(weights[values == v].sum()) for v in np.unique(values)}
    return result, columns, weights


def operating_figure(columns, weights, output):
    fig, axes = plt.subplots(2, 1, figsize=(7, 6))
    settings = [('altitude_ft', 1000., 'Altitude at 00:11 (ft)', 'Probability per 1,000 ft bin (%)'),
                ('mach', .005, 'Mach number at 00:11', 'Probability per 0.005 Mach bin (%)')]
    for ax, (name, width, xlabel, ylabel) in zip(axes, settings):
        v = columns[name]
        low, high = v[weights > 0].min(), v[weights > 0].max()
        edges = np.arange(np.floor(low/width)-.5, np.ceil(high/width)+1) * width
        h = np.histogram(v, bins=edges, weights=weights)[0]
        if not np.isclose(h.sum(), 1., atol=1e-10, rtol=0):
            raise ValueError('Operating-state histogram excludes probability')
        ax.bar((edges[:-1]+edges[1:])/2, 100*h, width=.9*width, color='#337ea1')
        ax.set(xlabel=xlabel, ylabel=ylabel)
        ax.grid(axis='y', alpha=.2)
    axes[0].axvline(35000, color='#16858a', ls='--', lw=1, label='Map reference altitude only')
    axes[0].legend(fontsize=8)
    fig.suptitle('Candidate altitude and speed retain their distributions at 00:11', fontsize=12)
    fig.tight_layout(rect=(0, .04, 1, .95))
    fig.text(.5, .012, 'Weighted terminal states under the stated flight, SATCOM and fuel model; these are calculated distributions, not measurements.',
             ha='center', fontsize=7)
    return save_figure(fig, output, 'altitude-mach-0011')


def complexity_by_latitude(latitude, weights, counts, width=2.5):
    positive = weights > 0
    centers = np.arange(np.floor(latitude[positive].min()/width),
                        np.ceil(latitude[positive].max()/width)+1) * width
    edges = np.r_[centers-width/2, centers[-1]+width/2]
    # Accumulate each bin directly. Subtracting cumulative near-unit weights
    # loses precision in the very small northern tail.
    slots = np.searchsorted(edges, latitude[positive], side='right') - 1
    if np.any((slots < 0) | (slots >= len(centers))):
        raise ValueError('Complexity grid excludes a positive-weight state')
    joint = np.bincount(counts[positive] * len(centers) + slots,
                        weights=weights[positive],
                        minlength=(int(counts.max())+1)*len(centers)).reshape(-1, len(centers))
    marginal = joint.sum(axis=0)
    conditional = np.divide(joint, marginal[None, :], out=np.zeros_like(joint), where=marginal[None, :] > 0)
    if not np.isclose(joint.sum(), 1, atol=1e-10, rtol=0):
        raise ValueError('Complexity grid excludes probability')
    return centers, edges, marginal, joint, conditional


def complexity_figures(runs, output):
    points, weights = pool(runs)
    fields = [('limited_turns', 'Turn starts'), ('limited_speed_changes', 'Mach change starts'),
              ('limited_altitude_changes', 'Altitude change starts')]
    data = []
    fig, axes = plt.subplots(4, 1, figsize=(8, 9), sharex=True,
                             gridspec_kw={'height_ratios':[1,1.4,1.1,1.1]})
    other, density_axes = plt.subplots(3, 1, figsize=(8, 8), sharex=True)
    rows = []
    for i, (field, label) in enumerate(fields):
        counts = np.array([int(row[field]) for run in runs for row in run['rows']])
        centers, edges, marginal, joint, conditional = complexity_by_latitude(points[:,0], weights, counts)
        data.append(dict(field=field, count_values=list(range(joint.shape[0])),
                         latitude_bin_centers_deg=centers.tolist(), latitude_bin_edges_deg=edges.tolist(),
                         latitude_bin_probability=marginal.tolist(), joint_probability=joint.tolist(),
                         count_probability_given_latitude_bin=conditional.tolist()))
        if i == 0:
            axes[0].bar(centers, 100*marginal, width=2.25, color='#337ea1')
            axes[0].set(ylabel='Bin probability (%)', title='Endpoint probability in each 2.5° latitude bin')
            axes[0].grid(axis='y', alpha=.2)
        masked = np.ma.masked_where(np.broadcast_to(marginal[None,:] == 0, conditional.shape), conditional)
        plot = axes[i+1].pcolormesh(edges, np.arange(joint.shape[0]+1)-.5, masked,
                                   vmin=0, vmax=1, cmap='Blues', shading='flat')
        axes[i+1].set(ylabel=label, yticks=np.arange(joint.shape[0]))
        for n in range(joint.shape[0]):
            count_mass = float(joint[n].sum())
            for j, center in enumerate(centers):
                rows.append([field,n,float(center),float(marginal[j]),float(joint[n,j]),
                             None if marginal[j] == 0 else float(conditional[n,j])])
            if count_mass > 0:
                density_axes[i].step(centers, joint[n]/(2.5*count_mass), where='mid',
                                     label=f'{n} starts · {100*count_mass:.1f}% of pool')
        density_axes[i].set(ylabel='Density per degree', title=label)
        density_axes[i].grid(alpha=.2);density_axes[i].legend(fontsize=7, ncol=2)
    axes[-1].set_xlabel('Latitude at 00:11 (°; negative values are south)')
    fig.suptitle('Trajectory complexity and terminal latitude', fontsize=13)
    fig.tight_layout(rect=(0,.10,.88,.97))
    bar=fig.colorbar(plot, cax=fig.add_axes([.90,.2,.018,.52]))
    bar.set_label('Probability of count, conditional on latitude bin')
    fig.text(.5,.015,'Counts begin after 18:25:34. Top panel shows how much probability supports each latitude bin.\n'
             'The lower panels describe the relative mix within each bin; rare northern bins have less sampling support.\n'
             'These are results within the declared manoeuvre caps and prior, not evidence for imposing those caps.',
             ha='center',fontsize=8)
    density_axes[-1].set_xlabel('Latitude at 00:11 (°; negative values are south)')
    other.suptitle('Latitude distributions conditional on each manoeuvre count',fontsize=12)
    other.tight_layout(rect=(0,.06,1,.95))
    other.text(.5,.015,'Each nonempty count curve integrates to one; the legend gives its probability in the full ensemble.\n'
               'Turns, Mach changes and altitude changes are reported separately; no subjective combined simplicity score is imposed.',
               ha='center',fontsize=8)
    with (output/'complexity-by-latitude.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['count_type','count','latitude_bin_center_deg','latitude_bin_probability',
                                            'joint_probability','count_probability_given_latitude_bin']);writer.writerows(rows)
    return data, [save_figure(fig,output,'trajectory-complexity-0011'),
                  save_figure(other,output,'latitude-by-manoeuvre-count-0011')]


def replication_figure(runs, output, groups):
    fig, axes = plt.subplots(2, 1, figsize=(7, 7))
    total = pool(runs)
    colours = ['#337ea1', '#d57927', '#7d5b9d', '#33836e']
    series = [(pool(runs[g['start']:g['stop']]),
               f'Runs {g["start"]+1}–{g["stop"]} · {g["initial_candidates"]:,}', colours[i % len(colours)], .95)
              for i, g in enumerate(groups)]
    series.append((total, 'All runs combined', '#24323f', 1.7))
    for col, ax in enumerate(axes):
        for (xy, w), label, colour, width in series:
            order = np.argsort(xy[:, col]); sx = xy[order, col]; c = np.cumsum(w[order])
            selected = np.unique(np.r_[0, np.searchsorted(c, np.linspace(0, 1, 2001)).clip(max=len(w)-1), len(w)-1])
            ax.step(sx[selected], c[selected], where='post', color=colour, lw=width, label=label)
        lo, hi = np.array(quantiles(*total, ps=(.001, .999)))[col]
        ax.set(xlim=(lo-.2, hi+.2), ylim=(0, 1), ylabel='Cumulative probability',
               xlabel=['Latitude (°)', 'Longitude (°E)'][col])
        ax.grid(alpha=.2); ax.legend(fontsize=7)
    fig.suptitle('Separate groups of runs: a comparison without shared particles', fontsize=12)
    fig.tight_layout(rect=(0, .045, 1, .95))
    fig.text(.5, .012, 'Groups follow acquisition order; their actual candidate counts are stated.\n'
             'Differences describe Monte Carlo variability conditional on the common physical model and frozen proposal banks.',
             ha='center', fontsize=7)
    return save_figure(fig, output, 'independent-groups-0011')


def report(paths, output, inline_output=None, baseline_runs=None, extension_state=None):
    output.mkdir(parents=True, exist_ok=True)
    runs = [read_run(p) for p in paths]
    if len(runs) < 2 or len({r['summary']['seed'] for r in runs}) != len(runs):
        raise ValueError('Supply at least two distinct seeds for a comparison, in acquisition order')
    if any(physical_identity(r) != physical_identity(runs[0]) for r in runs[1:]):
        raise ValueError('Scientific source or physical model/input mismatch')
    model = runs[0]['config']['model']
    dynamics = model['dynamics']
    limits = dynamics['manoeuvre_limits']['maximum_counts']
    nominal_altitude = dynamics['altitude_bounds_ft']
    nominal_mach = dynamics['mach_bounds']
    vertical_doppler = model.get('include_vertical_doppler', False)
    if baseline_runs is None:
        baseline_runs = min(3, len(runs) - 1)
    if not 1 <= baseline_runs < len(runs):
        raise ValueError('The baseline must leave at least one additional run')
    baseline, additional, total = pool(runs[:baseline_runs]), pool(runs[baseline_runs:]), pool(runs)
    equal = pool(runs, equal=True)
    run_alpha = mix_weights(runs)
    initial_count = sum(r['summary']['initial_particles'] for r in runs)
    regions = region_masses(*total)
    grids = {s: area_grid(*total, s) for s in [5, 10, 20]}
    areas = {str(s): ranked_area(g[2], s) for s, g in grids.items()}
    leave_one_out = []
    for i in range(len(runs)):
        p = pool([r for j, r in enumerate(runs) if i != j])
        leave_one_out.append(dict(omitted_seed=runs[i]['summary']['seed'], regions=region_masses(*p),
                                  cdf_difference_from_all=cdf_difference(p, total),
                                  quantiles_05_50_95_deg=quantiles(*p)))
    summaries = []
    for i, r in enumerate(runs):
        roots = np.array([int(row['root']) for row in r['rows']])
        rootmass = np.bincount(roots, weights=r['weight'])
        summaries.append(dict(name=r['path'].name, seed=r['summary']['seed'],
                              initial_candidates=r['summary']['initial_particles'],
                              elapsed_seconds=r['summary']['elapsed_seconds'],
                              peak_memory=r['summary'].get('peak_memory'),
                              log_evidence=r['summary']['log_evidence'],
                              pooling_fraction=float(run_alpha[i]), regions=region_masses(r['points'], r['weight']),
                              largest_ancestry_fraction=float(rootmass.max()),
                              quantiles_05_50_95_deg=quantiles(r['points'], r['weight']),
                              provenance=r['provenance'],
                              source_files_sha256={p:digest(r['path']/p) for p in ['posterior.csv','summary.json','resolved-config.json','provenance.json']}))
    modes = {}
    for field in ['initial_modes', 'final_modes']:
        labels = sorted({m for r in runs for m in r[field]})
        modes[field] = {label: float(sum(a*r['weight'][r[field] == label].sum() for r,a in zip(runs,run_alpha))) for label in labels}
    groups = []
    group_size = 3 if len({r['summary']['initial_particles'] for r in runs}) == 1 else 1
    for start in range(0, len(runs), group_size):
        stop = min(start+group_size, len(runs))
        p = pool(runs[start:stop])
        groups.append(dict(start=start, stop=stop, seeds=[r['summary']['seed'] for r in runs[start:stop]],
                           initial_candidates=sum(r['summary']['initial_particles'] for r in runs[start:stop]),
                           regions=region_masses(*p), quantiles_05_50_95_deg=quantiles(*p)))
    group_comparisons = []
    for i in range(len(groups)):
        for j in range(i+1, len(groups)):
            a, b = groups[i], groups[j]
            group_comparisons.append(dict(groups=[i,j],
                equal_initial_effort=a['initial_candidates'] == b['initial_candidates'],
                cdf_difference=cdf_difference(pool(runs[a['start']:a['stop']]), pool(runs[b['start']:b['stop']]))))
    cumulative = []
    previous = None
    for stop in range(1, len(runs)+1):
        p = pool(runs[:stop])
        cumulative.append(dict(run_count=stop, initial_candidates=sum(r['summary']['initial_particles'] for r in runs[:stop]),
                               regions=region_masses(*p),
                               new_run_vs_previous_cdf_difference=None if previous is None else cdf_difference(pool(runs[stop-1:stop]),previous),
                               combined_vs_previous_cdf_difference=None if previous is None else cdf_difference(p,previous)))
        previous = p
    split = len(runs)//2
    halves = dict(first_seeds=[r['summary']['seed'] for r in runs[:split]],
                  second_seeds=[r['summary']['seed'] for r in runs[split:]],
                  first_initial_candidates=sum(r['summary']['initial_particles'] for r in runs[:split]),
                  second_initial_candidates=sum(r['summary']['initial_particles'] for r in runs[split:]),
                  equal_initial_effort=sum(r['summary']['initial_particles'] for r in runs[:split]) == sum(r['summary']['initial_particles'] for r in runs[split:]),
                  cdf_difference=cdf_difference(pool(runs[:split]),pool(runs[split:])),
                  first_regions=region_masses(*pool(runs[:split])),second_regions=region_masses(*pool(runs[split:])))
    operating, operating_columns, operating_weights = operating_state(runs)
    arc = reference_arc(runs[0]['config'])
    result = dict(generated_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                  status='provisional conditional PDF; Monte Carlo variation reported without a fixed pass/fail threshold',
                  runs=summaries, total_initial_candidates=initial_count,
                  positive_weight_output_rows=int(sum(np.count_nonzero(r['weight']) for r in runs)),
                  total_sampling_run_elapsed_seconds=sum(r['summary']['elapsed_seconds'] for r in runs),
                  pooling='alpha_r = N_r exp(logZ_r) / sum_s N_s exp(logZ_s), N_r is initial effort; within-run weights retained',
                  regions=regions, equal_run_regions=region_masses(*equal),
                  equal_run_pooling_cdf_difference=cdf_difference(total,equal),
                  baseline_run_count=baseline_runs, baseline_regions=region_masses(*baseline),
                  additional_regions=region_masses(*additional),
                  additional_vs_baseline_cdf_difference=cdf_difference(baseline,additional),
                  combined_vs_baseline_cdf_difference=cdf_difference(baseline,total),
                  quantiles_05_50_95_deg=quantiles(*total), modes=modes,
                  leave_one_out=leave_one_out, cell_ranked_probability_areas=areas,
                  independent_groups=groups, independent_group_comparisons=group_comparisons,
                  independent_halves=halves, cumulative_history=cumulative,
                  terminal_operating_state=operating,
                  enabled_spokes=runs[0]['provenance']['enabled_spokes'],
                  include_vertical_doppler=vertical_doppler,
                  reference_arc=arc[2], report_source_sha256=digest(__file__),
                  limitations=[f'{initial_count:,} initial candidates are not {initial_count:,} independent posterior draws.',
                               'Replication diagnostics do not establish calibrated sampling-error confidence bands.',
                               'Combining runs is not equivalent to a single larger interacting filter.',
                               'Finite-sample highest-density areas depend on displayed cell size; no added smoothing.',
                               f'Airborne location at 00:11 under the stated {limits[0]}/{limits[1]}/{limits[2]} cruise, SATCOM and fuel conditions, not an impact/search-area posterior.',
                               'Aircraft performance and fuel-model calibration remain incomplete.'] +
                              ([] if vertical_doppler else ['The vertical-speed contribution to BFO is disabled in this frozen configuration.']))
    if extension_state:
        state = json.loads(extension_state.read_text())
        result['sampling_status_at_generation'] = {k:state.get(k) for k in
            ['status','completed_initial_candidates','target_initial_candidates','active_seed','updated_utc']}
    with (output/'pooled-particles.csv').open('w',newline='') as f:
        fields=['run_seed','run_fraction','within_run_weight']+list(runs[0]['rows'][0])
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for run,a in zip(runs,run_alpha):
            for row,w in zip(run['rows'],run['weight']):
                writer.writerow(dict(row,run_seed=run['summary']['seed'],run_fraction=f'{a:.17g}',
                                     within_run_weight=f'{w:.17g}',weight=f'{a*w:.17g}'))
    xe,ye,mass=grids[5]
    latc,lonc=inverse((xe[:-1]+xe[1:])/2,(ye[:-1]+ye[1:])/2)
    with (output/'area-density-5km.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['latitude_deg','longitude_deg','cell_area_km2','probability_mass','probability_density_per_km2'])
        for j,i in np.argwhere(mass>0):writer.writerow([f'{latc[j]:.9f}',f'{lonc[i]:.9f}',25,f'{mass[j,i]:.17g}',f'{mass[j,i]/25:.17g}'])
    np.savez_compressed(output/'area-density-5km.npz',x_edges_km=xe,y_edges_km=ye,
                        probability_mass=mass,probability_density_per_km2=mass/25)
    complexity, complexity_visuals = complexity_figures(runs, output)
    result['complexity_by_latitude'] = complexity
    visuals=[map_figure(*total,grids[5],arc,output,initial_count,len(runs),operating['altitude_ft']['positive_weight_range'],
                       condition_label=f'Post-18:25 turn / Mach / altitude caps: {limits[0]} / {limits[1]} / {limits[2]} · vertical BFO {"on" if vertical_doppler else "off"}'),
             comparison_figure(runs,output,baseline_runs),latitude_figure(runs,output),
             operating_figure(operating_columns,operating_weights,output),replication_figure(runs,output,groups)] + complexity_visuals
    visuals=[('<button type="button" class="zoom" aria-pressed="false" '
              'onclick="const on=this.parentElement.classList.toggle(\'enlarged\');'
              'this.setAttribute(\'aria-pressed\',on);this.textContent=on?\'Fit chart\':\'Enlarge chart\';">'
              'Enlarge chart</button>'+v) for v in visuals]
    labels={'between_35S_and_38S':'35–38°S','north_of_35S':'North of 35°S',
            'north_of_30S':'North of 30°S','south_of_38S':'South of 38°S'}
    rows=''
    for key,label in labels.items():
        values=[result['baseline_regions'][key],result['additional_regions'][key],regions[key]]
        rows+=f'<tr><td>{label}</td>'+''.join(f'<td>{100*v:.1f}%</td>' for v in values)+'</tr>'
    run_rows=''
    for i,s in enumerate(summaries):
        run_rows+=(f'<tr><td>{i+1} · {s["seed"]}</td><td>{s["elapsed_seconds"]/60:.2f}</td>'
                   f'<td>{100*s["pooling_fraction"]:.1f}%</td><td>{100*s["regions"]["between_35S_and_38S"]:.1f}%</td>'
                   f'<td>{100*s["regions"]["north_of_30S"]:.2f}%</td></tr>')
    group_rows=''
    for g in groups:
        group_rows+=(f'<tr><td>{g["start"]+1}–{g["stop"]}</td><td>{g["initial_candidates"]:,}</td>'
                     f'<td>{100*g["regions"]["between_35S_and_38S"]:.1f}%</td>'
                     f'<td>{100*g["regions"]["north_of_35S"]:.1f}%</td>'
                     f'<td>{100*g["regions"]["north_of_30S"]:.2f}%</td></tr>')
    growth_rows=''
    for c in cumulative:
        d=c['combined_vs_previous_cdf_difference']
        movement='—' if d is None else f'{100*d[0]:.1f} / {100*d[1]:.1f}'
        growth_rows+=(f'<tr><td>{c["initial_candidates"]:,}</td><td>{100*c["regions"]["between_35S_and_38S"]:.1f}%</td>'
                      f'<td>{100*c["regions"]["north_of_30S"]:.2f}%</td><td>{movement}</td></tr>')
    area_rows=''
    for s in ['5','10','20']:
        area_rows+=f'<tr><td>{s} × {s} km</td>'+''.join(f'<td>{areas[s][str(p)]["area_km2"]:,.0f}</td>' for p in [.5,.8,.9,.95])+'</tr>'
    loo=[d['regions']['between_35S_and_38S'] for d in leave_one_out]
    diff=result['additional_vs_baseline_cdf_difference'];added=result['combined_vs_baseline_cdf_difference']
    alt=operating['altitude_ft']['quantiles_05_50_95']
    cite='https://www.stats.ox.ac.uk/~doucet/andrieu_doucet_holenstein_PMCMC.pdf'
    sampling=''
    if extension_state:
        s=result['sampling_status_at_generation']
        sampling=(f'<p class="status">Sampling status when generated: {s["status"].replace("_"," ")}. '
                  f'This report includes {initial_count:,} of the planned {s["target_initial_candidates"]:,} initial candidates. '
                  'Refresh the report to see newly completed batches.</p>')
    body=(f'<h1>00:11 area probability density</h1><p class="lead">{len(runs)} runs, {initial_count:,} initial candidates. '
          f'<strong>{100*regions["between_35S_and_38S"]:.1f}%</strong> of pooled probability lies between 35°S and 38°S; '
          f'<strong>{100*regions["north_of_35S"]:.1f}%</strong> lies farther north.</p>'+sampling+
          '<p>A provisional PDF under the declared flight and evidence conditions. Independent runs show sampling variation; '
          'a fixed five-point threshold is not used to withhold the estimate.</p>'
          '<section>'+visuals[0]+'</section>'
          '<h2>Altitude is a distribution, including at 00:11</h2>'
          '<p><strong>35,000 ft is only the altitude of the dashed reference line on the map.</strong> '
          'Each candidate retains its own altitude in the SATCOM calculation and in the area PDF. '
          f'The model allows nominal levels from {nominal_altitude[0]:,.0f} to {nominal_altitude[1]:,.0f} ft '
          f'and up to {limits[2]} altitude changes after 18:25.</p>'
          f'<p>The weighted median terminal altitude is {alt[1]:,.0f} ft; the 5th–95th percentiles are '
          f'{alt[0]:,.0f}–{alt[2]:,.0f} ft. These are calculated results under the model, not observed altitudes.</p>'
          '<section>'+visuals[3]+'</section>'
          '<h2>How trajectory complexity relates to latitude</h2>'
          '<p>The first graphic shows the turn, Mach and altitude change counts within each 2.5° latitude bin. '
          'Its top panel shows the probability assigned to each bin, so an extremely rare tail is not mistaken for a major part of the estimate. '
          'The second shows the latitude distribution after conditioning on each count separately. '
          'These comparisons describe the current prior and manoeuvre caps; increasing the caps is a separate sensitivity calculation.</p>'
          '<section>'+visuals[5]+'</section><section>'+visuals[6]+'</section>'
          '<h2>What changed as the ensemble grew?</h2>'
          f'<p>Compared with the original {baseline_runs} runs combined, the additional runs have maximum latitude/longitude '
          f'cumulative differences of {100*diff[0]:.1f}/{100*diff[1]:.1f} percentage points. '
          f'Combining all {len(runs)} moves the original curves by {100*added[0]:.1f}/{100*added[1]:.1f} points.</p>'
          '<p>Pooling reduces the influence of each new run mechanically. Small successive changes alone do not prove convergence; '
          'the separate groups below provide a comparison without shared particles.</p>'
          f'<div class="scroll"><table><thead><tr><th>Region</th><th>Original {baseline_runs}</th><th>Additional</th><th>All {len(runs)}</th></tr></thead><tbody>'+rows+'</tbody></table></div>'
          f'<p>Leaving out one run at a time puts the 35–38°S mass between {100*min(loo):.1f}% and {100*max(loo):.1f}%. '
          'This is a sensitivity range, not a confidence interval.</p><section>'+visuals[1]+'</section><section>'+visuals[2]+'</section>'
          '<h2>Independent groups of candidate trajectories</h2>'
          f'<p>Runs are grouped in acquisition order, {group_size} per group. Actual initial candidate counts are listed below. '
          'No group shares a run with another. All use the same physical target and frozen proposal banks.</p>'
          '<div class="scroll"><table><thead><tr><th>Runs</th><th>Candidates</th><th>35–38°S</th><th>North of 35°S</th><th>North of 30°S</th></tr></thead><tbody>'+group_rows+'</tbody></table></div>'
          '<section>'+visuals[4]+'</section>'
          f'<p>The first {split} runs versus the remaining {len(runs)-split} have maximum latitude/longitude CDF differences '
          f'of {100*halves["cdf_difference"][0]:.1f}/{100*halves["cdf_difference"][1]:.1f} percentage points. '
          'These numerical differences are reported directly, without treating a chosen tolerance as a significance test.</p>'
          '<h2>Area and map resolution</h2><p>Area in km² of cells with the largest estimated densities, '
          'until the indicated cumulative probability is reached. Cell boundaries and finite sampling affect these areas. '
          'These airborne areas are not impact locations or proposed search boxes.</p>'
          '<div class="scroll"><table><thead><tr><th>Cell size</th><th>50%</th><th>80%</th><th>90%</th><th>95%</th></tr></thead><tbody>'+area_rows+'</tbody></table></div>'
          '<details><summary>Results as each run was added</summary>'
          '<p>Cumulative probabilities and the largest latitude/longitude CDF movement from the previous pool, in percentage points. '
          'The new-run-versus-previous-pool comparisons are also saved in summary.json.</p>'
          '<div class="scroll"><table><thead><tr><th>Candidates</th><th>35–38°S</th><th>North of 30°S</th><th>CDF movement (pp)</th></tr></thead><tbody>'+growth_rows+'</tbody></table></div></details>'
          '<details><summary>Each independent run</summary>'
          '<div class="scroll"><table><thead><tr><th>Run · seed</th><th>Minutes</th><th>Contribution</th><th>35–38°S</th><th>North of 30°S</th></tr></thead><tbody>'+run_rows+'</tbody></table></div></details>'
          '<details><summary>How the runs are combined</summary><p>Each run retains its candidate weights. '
          'The main estimate combines runs’ unnormalized probability measures in proportion to their initial candidate counts, then normalizes the result. '
          'Each run therefore contributes in proportion to its initial candidate count multiplied by its estimated normalizing constant.</p>'
          f'<p>An equal-run average gives {100*result["equal_run_regions"]["between_35S_and_38S"]:.1f}% in 35–38°S; '
          f'the maximum coordinate-CDF difference from the main pooling is {100*max(result["equal_run_pooling_cdf_difference"]):.1f} points.</p>'
          f'<p><a href="{cite}">Andrieu, Doucet and Holenstein (2010), §4–5 and p. 298</a> establishes the SMC normalizer identities '
          'under its stated assumptions. This pooling is the ratio of sums of saved unnormalized estimates. '
          'A finite ratio is not claimed to be unbiased, and the paper does not establish convergence of this implementation.</p></details>'
          '<details><summary>Conditions, interpretation and reproducibility</summary>'
          f'<p>The target allows at most {limits[0]} turn starts, {limits[1]} Mach starts and {limits[2]} altitude starts after 18:25:34. '
          f'{len(runs[0]["config"]["modes"])} navigation families remain in the prior. '
          f'Nominal Mach {nominal_mach[0]:.2f}–{nominal_mach[1]:.2f} and altitude '
          f'{nominal_altitude[0]:,.0f}–{nominal_altitude[1]:,.0f} ft are model conditions; '
          'small cruise fluctuations are additional. BTO/BFO through 00:10:59 and the declared fuel compatibility are enabled. '
          f'The vertical-speed contribution to BFO is {"enabled" if vertical_doppler else "disabled"} in this frozen configuration. '
          'The fuel continuation assumes exhaustion between 00:15 and 00:19 and gives an outer 0.2–1.9 tonne usable-fuel envelope. '
          'This uses Martin/BSM LRC coefficients plus a declared extension; full performance and fuel calibration remain incomplete.</p>'
          f'<p>The {initial_count:,} initial candidates evolve through resampling, so their descendants are correlated. '
          f'Pooling {len(runs)} runs is different from running one interacting filter with {initial_count:,} particles. '
          'Replication helps assess sampling variation but does not establish that all feasible routes were explored, '
          'or that these conditional probabilities represent all physical uncertainty.</p>'
          '<p>End-of-flight, antenna gain, ocean drift, hydroacoustics, Pleiades, WSPR and searched-area evidence are not enabled in this estimate.</p>'
          '<p>The map is an unsmoothed weighted histogram on a WGS84 equal-area grid. All sample mass is retained in the grid; '
          'each figure states the mass inside its displayed frame. Altitude and across-arc position spread are retained.</p>'
          '<p>The output directory includes summary.json, pooled-particles.csv, area-density-5km.csv/npz and SVG/PDF/PNG figures. '
          'Its README gives one command to regenerate them without running the filter.</p></details>'
          f'<p class="stamp">Generated from saved artifacts {result["generated_utc"]}</p>')
    css='body{margin:0;background:#f5f7f8;color:#193240;font:17px/1.55 system-ui,sans-serif}main{max-width:980px;margin:auto;padding:22px}h1{font-size:1.8em}h2{font-size:1.25em;margin-top:30px}.lead{font-size:1.12em}section{background:white;padding:10px;margin:24px 0}svg{display:block;width:100%;height:auto}.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;background:white;font-size:.88rem}td,th{padding:10px;border-bottom:1px solid #dce3e8;text-align:right}td:first-child,th:first-child{text-align:left}details{padding:15px;background:white;margin:14px 0}summary{cursor:pointer;font-weight:600}.stamp{font-size:12px;color:#617786}a{color:#086c8c}.status{padding:12px;background:#e7eff2}'
    css+='section{overflow-x:auto}.zoom{position:sticky;left:0;border:1px solid #acc0ca;background:#edf4f6;color:#193240;padding:7px 12px;border-radius:5px;font:inherit;font-size:.85rem;cursor:pointer}.enlarged svg{width:1100px;max-width:none}'
    html='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MH370 pooled 00:11 density</title><style>'+css+'</style><main>'+body+'</main></html>'
    for path in [output/'index.html'] + ([inline_output] if inline_output else []):
        temporary=path.with_suffix(path.suffix+'.tmp');temporary.write_text(html);temporary.replace(path)
    command=shlex.join(['python',str(Path(__file__).resolve()),'--runs']+[str(p.resolve()) for p in paths]+
                       ['--output',str(output.resolve()),'--baseline-runs',str(baseline_runs)])
    (output/'README.md').write_text('# Pooled 00:11 area density\n\nProvisional conditional PDF of airborne position.\n\n'
        'Regenerate all figures and numerical artifacts, without sampling:\n\n```bash\n'+command+'\n```\n\n'
        'Requires NumPy and Matplotlib. Input identities, seeds, normalizers, source identity and comparisons are in summary.json. '
        'The 35,000 ft map label is a reference line, not a terminal altitude constraint. '
        'All initial candidates are counted, but resampled descendants are correlated. Independent nonoverlapping groups are reported separately.\n')
    verification=dict(source_and_physical_identity_checks=True, distinct_run_count=len(runs),
                      initial_candidates=initial_count, output_rows=sum(len(r['rows']) for r in runs),
                      pooled_weight_sum=float(total[1].sum()),
                      area_density_integral=float((mass/25*25).sum()),
                      inline_bytes=len(html.encode()), embedded_svg_count=html.count('<svg'),
                      reference_altitude_is_not_a_terminal_constraint=True)
    (output/'verification.json').write_text(json.dumps(verification,indent=2)+'\n')
    result['output_files_sha256']={p.name:digest(p) for p in output.iterdir() if p.is_file() and p.name!='summary.json'}
    temporary=output/'summary.json.tmp';temporary.write_text(json.dumps(result,indent=2)+'\n');temporary.replace(output/'summary.json')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs',nargs='+',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--inline-output',type=Path)
    parser.add_argument('--baseline-runs',type=int)
    parser.add_argument('--extension-state',type=Path)
    args=parser.parse_args()
    result=report(args.runs,args.output,args.inline_output,args.baseline_runs,args.extension_state)
    print(json.dumps({k:result[k] for k in ['status','total_initial_candidates','regions',
        'additional_vs_baseline_cdf_difference','combined_vs_baseline_cdf_difference',
        'terminal_operating_state','cell_ranked_probability_areas']},indent=2))
