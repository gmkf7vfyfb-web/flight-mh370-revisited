"""Composer views v3.2 with the Australian non-finds term (Pete, 21 Oct 2026): fig1 redrawn for two Australian versions, and headline rows.
(a) MEASURED: populated coast only (drift's measured ln_l_lev_populated column: city + inner regional coast at the find-coast level, every
    other Australian coast off) -> product ApopS.
(b) RECONSTRUCTED: Pete's 17 Oct scheme (ABS tiers major city + inner regional 1, outer regional 0.3, remote / very remote 0; 2014 level
    0.5 of the find-coast peak, constant in time) from ocean drift's per-node reconstruction (emulator k1), VALIDATION GATE FAILED
    (497677f; leave-one-out error RMS 0.09-0.27, max up to 1.32 ln per point) -> product Ar05S; levels 0.3 / 0.65 in the table only.
Base: v3.2 (exchange composer/run-j-views-v3.2-australia, compose_v3.py V32=1 DEXT=1 RULED=1; its DS etc. equal v3.2 exactly).
Run in a kernel with figure-style's apply_figure_style."""
import json, sys, pathlib, textwrap
import numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
HERE = pathlib.Path(globals().get('HERE_V3', '.')).resolve(); sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / 'composer-views-run-j'))
import views_common as V
EX = pathlib.Path('/Users/pete/Downloads/mh370-exchange/composer/run-j-views-v3.2-australia'); OUT = HERE / 'v3.2-australia'; OUT.mkdir(exist_ok=True)
R = json.load(open(EX / 'views-v3-run-j.json'))['cells']; MAPS = np.load(EX / 'maps-v3.npz')
try:
    apply_figure_style(sizes=(8, 7, 6))
except NameError:
    mpl.rcParams.update({'font.size': 8})
DK = [f'D{d}' for d in range(6)]
DNAME = {'D0': '00:19 data held out', 'D1': '00:19 BTO only (R600)', 'D2': '00:19 BTO + raw BFO (R600)', 'D3': '00:19 BTO + both BFOs as recorded',
         'D4': '00:19 BTO + both BFOs,\nHolland transient bias added', 'D5': '00:19 BTO + R600 and R1200 BFOs,\nHolland transient bias added'}
PRN = {'DS': 'All evidence without Australian non-finds (base)', 'ApopS': 'With Australian non-finds, MEASURED (populated coast only)',
       'Ar03S': 'With Australian non-finds, RECONSTRUCTED, level 0.3', 'Ar05S': 'With Australian non-finds, RECONSTRUCTED, level 0.5',
       'Ar065S': 'With Australian non-finds, RECONSTRUCTED, level 0.65'}
# ---------- table
rows = []
for d in DK:
    C = R[f'head|{d}|all|mix']
    for p in ('DS', 'ApopS', 'Ar05S', 'Ar03S', 'Ar065S'):
        x = C[p]; b = C['boot'][p]; pn = x['north_of_33S']; se = b['north33_se']
        rows.append({'option': d, 'treatment': DNAME[d].replace('\n', ' '), 'product': p, 'product_name': PRN[p],
                     'median_lat': x['median'], 'median_q025': b['median_q'][0], 'median_q975': b['median_q'][1], 'median_se': b['median_se'],
                     'hpd50_km2': x['hpd50_km2'], 'hpd90_km2': x['hpd90_km2'], 'hpd90_se': b['hpd90_se'], 'hpd95_km2': x['hpd95_km2'],
                     'north_of_33S': pn, 'north_of_33S_q025': b['north33_q'][0], 'north_of_33S_q975': b['north33_q'][1],
                     'eff_sample_north_of_33S_seed_scatter': pn * pn * (1 - pn) / se ** 2 if se > 0 else None, 'kish_ess_north_of_33S': x['kish_ess_north_of_33S'],
                     'p_on_searched_ground': x['p_on_searched_ground'], 'p_on_searched_ground_se': b['searched_se'], 'kish_ess': x['kish_ess'],
                     'lnE_given_core': x['lnE_given_core']})
T = pd.DataFrame(rows); T.to_csv(OUT / 'headline-australia-v3.2.csv', index=False)
md = ['| 00:19 treatment | product | median (95 % seed interval) | 50 / 90 / 95 % HPD, k km² | mass N of 33 S (95 % interval) | effective sample N of 33 S: seed scatter / outcome Kish | on searched ground (± SE) |',
      '|---|---|---|---|---|---|---|']
for _, r in T.iterrows():
    md.append(f"| {r.treatment} | {r.product_name} | {-r.median_lat:.2f} S ({-r.median_q975:.2f}–{-r.median_q025:.2f}) | {r.hpd50_km2/1e3:.0f} / {r.hpd90_km2/1e3:.0f} / {r.hpd95_km2/1e3:.0f} | "
              f"{r.north_of_33S:.3f} ({r.north_of_33S_q025:.3f}–{r.north_of_33S_q975:.3f}) | {r.eff_sample_north_of_33S_seed_scatter:.0f} / {r.kish_ess_north_of_33S:.0f} | {r.p_on_searched_ground:.3f} ± {r.p_on_searched_ground_se:.3f} |")
(OUT / 'headline-australia-v3.2.md').write_text('\n'.join(md) + '\n')
# ---------- figures
LON_E = V.LON0 + np.arange(V.NX + 1) * V.STEP; LAT_E = V.ROW_EDGES
def hpd_levels(m, levels=(0.5, 0.9, 0.99)):
    p = m.ravel() / m.sum(); o = np.argsort(-p); c = np.cumsum(p[o]); lev = np.zeros(p.size)
    for L in sorted(levels, reverse=True):
        lev[o[:np.searchsorted(c, L) + 1]] = L
    return lev.reshape(m.shape)
alat, alon = V.arc_point(np.linspace(800, 2600, 400))
greys = mpl.colors.ListedColormap(['#ffffff', '#d9d9d9', '#969696', '#404040'])
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
TECH_COMMON = ("core run J (tag 1244b7c; split-half accepted by ruling 16 Oct 2026); prior track = four-stratum mixture (waypoint routes 0.998, free flight, "
               "descent-climb, Davey dynamics with radar); waypoint routes with the run J northern supplement (rule B), stratified at 33 S; log-on cause: competing "
               "causes, prior odds 1/3, other cause silent; end-of-flight uncontrolled arm not calibrated; settling run J (breakup table provisional); seabed = settled "
               "pieces. Searched areas: per-cell detection model V1 central, Ocean Infinity coverage inferred (grade C), included as best estimate. Drift: finds, "
               "arc-latitude profile 20-40 S, GLORYS12 + GlobCurrent marginalised jointly. Hydroacoustics zero weight by ruling; Pleiades not used. Australian "
               "non-finds are a LABELLED SENSITIVITY for the decision table (Pete, 21 Oct 2026), not the headline. North of 33 S is under-sampled "
               "(effective sample from the seed scatter 168-341 for these two products, below the 1,000 target; table). HPD regions on the 769 km2 equal-area grid; planned next Ocean "
               "Infinity area is a map layer only (not drawn).")
VERS = {
 'ApopS': dict(name='measured', title='With Australian non-finds (measured, populated coast only), the sea-floor region moves north of the result without them',
   ste=("Note (STE100): This chart shows where the aircraft can be on the sea floor. It uses the satellite data, flight models, debris drift, the searched "
        "areas and the Australian coasts where no debris was found. Only the coast near the cities and inner regional towns counts, at the same level as "
        "the coasts where debris was found. All other Australian coast is not used. This Australian part is a separate case, not the main result. There are "
        "few samples north of 33 S."),
   tech=("Technical: Australian non-finds MEASURED by ocean drift, populated coast only (column ln_l_lev_populated: ABS major city + inner regional "
         "coast at the find-coast level, outer regional and remote coast off; Pete's ruling 15 Oct 2026), dedicated arc-latitude run 20-40 S, both ocean "
         "models. ")),
 'Ar05S': dict(name='reconstructed-level-0.5', title='With Australian non-finds (reconstructed, ruled tiers, level 0.5), the sea-floor region moves north of the result without them',
   ste=("Note (STE100): This chart shows where the aircraft can be on the sea floor. It uses the satellite data, flight models, debris drift, the searched "
        "areas and the Australian coasts where no debris was found. City and inner regional coast count fully, outer regional coast counts 0.3, remote "
        "coast does not count, all at half of the peak level of the coasts where debris was found. These Australian values are estimated from stored "
        "tables. The check of this estimate failed, so the values are not exact. This Australian part is a separate case, not the main result. There are "
        "few samples north of 33 S."),
   tech=("Technical: Australian non-finds RECONSTRUCTED, validation gate failed; leave-one-out error RMS 0.09-0.27, max up to 1.32 ln per point "
         "(ocean drift 497677f, emulator k1, mh370-exchange/debris-drift/arclat-ruled-australia-2026-10-21). Scheme (Pete, 17 Oct 2026): ABS tiers major city + "
         "inner regional 1, outer regional 0.3, remote / very remote 0, times a 2014 level of 0.5 of the find-coast peak (range 0.3-0.65), constant in time; "
         "84 arc-latitude points 20-40 S, both ocean models. ")),
}
for p, cfg in VERS.items():
    fig, axs = plt.subplots(2, 3, figsize=(7.2, 6.6), sharex=True, sharey=True)
    for ax, d in zip(axs.ravel(), DK):
        m = MAPS[f'{d}|{p}'].reshape(V.NY, V.NX).astype(float); lv = hpd_levels(m)
        code = np.select([lv == 0.5, lv == 0.9, lv == 0.99], [3, 2, 1], 0)
        ax.pcolormesh(LON_E, LAT_E, code, cmap=greys, vmin=-0.5, vmax=3.5, shading='flat', rasterized=True)
        mc = MAPS[f'{d}|core'].reshape(V.NY, V.NX).astype(float); lc = hpd_levels(mc, (0.9,))
        ax.contour(0.5 * (LON_E[1:] + LON_E[:-1]), 0.5 * (LAT_E[1:] + LAT_E[:-1]), (lc > 0).astype(float), levels=[0.5], colors=['#c0392b'], linewidths=0.7)
        ax.plot(alon, alat, color='#1f4e9c', lw=0.8); ax.set_title(DNAME[d], loc='left', fontsize=7)
        ax.set_xlim(84, 108); ax.set_ylim(-41, -20); ax.set_aspect(1 / np.cos(np.radians(-31)))
    for ax in axs[:, 0]:
        ax.set_ylabel('Latitude (°)')
    for ax in axs[-1]:
        ax.set_xlabel('Longitude (°E)')
    lab = 'measured' if p == 'ApopS' else 'reconstructed'
    h = [Patch(fc='#404040', label=f'With Australian non-finds ({lab}), 50 % region'), Patch(fc='#969696', label=f'With Australian non-finds ({lab}), 90 % region'),
         Patch(fc='#d9d9d9', ec='#bbbbbb', label=f'With Australian non-finds ({lab}), 99 % region'), Line2D([], [], color='#c0392b', lw=0.8, label='Satellite data and flight only, 90 % region'),
         Line2D([], [], color='#1f4e9c', lw=0.8, label='7th arc (00:19:29)')]
    fig.legend(handles=h, loc='upper center', ncol=2, frameon=False, bbox_to_anchor=(0.5, 0.995), fontsize=6.5)
    fig.suptitle(cfg['title'], x=0.01, y=0.915, ha='left', fontsize=8)
    if p != 'ApopS':
        fig.text(0.01, 0.885, 'Reconstructed, validation gate failed; leave-one-out error RMS 0.09-0.27, max up to 1.32 ln per point', ha='left', fontsize=7, color='#c0392b')
    fig.subplots_adjust(left=0.08, right=0.99, top=0.83, bottom=0.31, wspace=0.08, hspace=0.25)
    t = textwrap.fill(cfg['ste'] + ' Dark grey: 50 % of the probability; mid grey: 90 %; light grey: 99 %. Red line: 90 % without drift, searches and Australia.', 175) + '\n' + \
        textwrap.fill(cfg['tech'] + TECH_COMMON, 175)
    fig.text(0.01, 0.005, t, ha='left', va='bottom', fontsize=5.5, color='#333333')
    for ext in ('png', 'pdf'):
        fig.savefig(OUT / f"fig1-seabed-hpd-with-australian-non-finds-{cfg['name']}.{ext}", dpi=300 if ext == 'png' else None)
    plt.close(fig)
np.savez_compressed(OUT / 'maps-australia-v3.2.npz', NY=V.NY, NX=V.NX, **{f'{d}|{p}': MAPS[f'{d}|{p}'] for d in DK for p in ('core', 'DS', 'ApopS', 'Ar03S', 'Ar05S', 'Ar065S')})
print('\n'.join(md))
