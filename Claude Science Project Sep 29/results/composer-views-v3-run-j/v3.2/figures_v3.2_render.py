# exact source used to render the v3.2 figures (figures_v3.py with the v3.2 text substitutions)
HERE_V3 = '.'; EX_V3 = '/Users/pete/Downloads/mh370-exchange/composer/run-j-views-v3.2'; OUT_V3 = 'v3.2'; SUF_V3 = '-v3.2'
DRIFT_NOTE = 'drift: arc-latitude profile 20-40 S, not computed north of 19.9 S (0.26 of the span, carried at the mean)'
TECH_ADD = " Views v3.2: waypoint routes use the run J northern supplement (rule B; settling d0660ec2, searched areas a8e7e28), stratified at 33 S by impact latitude, with A1 under D3-D5 from end of flight's two conditional strata (end-of-flight share); drift arc-latitude profile extended to 20-40 S (181a5fa). D5 waypoints at BFO error 4.3177 Hz; other strata as before."
"""Composer views v3: figures (PNG + PDF). Run in a kernel with figure-style's apply_figure_style (falls back to plain rcParams).
Inputs: EX/views-v3-run-j.json, pdf01-v3.npz, maps-v3.npz, view-a-i-v3.npz; v2 views_common grid."""
import json, sys, pathlib
import numpy as np, matplotlib as mpl, matplotlib.pyplot as plt
HERE = pathlib.Path(globals().get('HERE_V3', '.')).resolve(); sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / 'composer-views-run-j'))
import views_common as V, views_lib as VL
EX = pathlib.Path(globals().get('EX_V3', '/Users/pete/Downloads/mh370-exchange/composer/run-j-views-v3'))
OUTD = pathlib.Path(globals().get('OUT_V3', str(HERE))); SUF = globals().get('SUF_V3', '')
R = json.load(open(EX / 'views-v3-run-j.json')); PDF = np.load(EX / 'pdf01-v3.npz'); MAPS = np.load(EX / 'maps-v3.npz'); VAI = np.load(EX / 'view-a-i-v3.npz')
try:
    apply_figure_style(sizes=(8, 7, 6))
except NameError:
    mpl.rcParams.update({'font.size': 8, 'axes.spines.top': False, 'axes.spines.right': False})
DK = [f'D{d}' for d in range(6)]
DNAME = {'D0': '00:19 data held out', 'D1': '00:19 BTO only (R600)', 'D2': '00:19 BTO + raw BFO (R600)',
         'D3': '00:19 BTO + both BFOs as recorded', 'D4': '00:19 BTO + both BFOs,\nHolland transient bias added',
         'D5': '00:19 BTO + R600 and R1200 BFOs,\nHolland transient bias added'}
DCOL = dict(zip(DK, ['#1b4f72', '#2e86c1', '#76b7e5', '#a04000', '#e67e22', '#f5b041']))
STE_BASE = ('Note (STE100): This chart shows where the aircraft can be on the sea floor, from the evidence that we use. Satellite data, flight '
            'models, debris drift and the searched areas give the result. The searched areas remove probability where the search was good. '
            'We do not use the hydrophone data. The Pleiades objects and the Australian coast are given only as separate cases.')
TECH_BASE = ("Technical: core run J (tag 1244b7c; split-half accepted by ruling 16 Oct 2026), prior track = four-stratum mixture (waypoint "
             "routes 0.998, free flight, descent-climb, Davey dynamics with radar); log-on cause: competing causes, prior odds 1/3, other cause silent; "
             "end-of-flight uncontrolled arm not calibrated; settling run J (breakup table provisional); seabed = settled pieces. Searched areas: per-cell "
             "detection model V1 central (q 0.95 / 0.70 by ATSB Fig. 73 lower-confidence fraction, rho = 0.05 x terrain weight, cap 0.95), Ocean "
             "Infinity coverage inferred (grade C), included as best estimate. Drift: finds only, dedicated arc-latitude run 20-40 S (run A outside), "
             "GLORYS12 + GlobCurrent marginalised jointly. Hydroacoustics zero weight by ruling; Pleiades conditional; Australian non-recovery excluded "
             "(sensitivity); planned next Ocean Infinity area is a map layer only. North of 33 S includes the run J northern supplement; "
             "north of 33 S under-sampled (effective sample in the tables)." + globals().get('TECH_ADD', ''))

def footnotes(fig, ste, tech, y=0.005, width=190):
    import textwrap
    t = textwrap.fill(ste, width) + '\n' + textwrap.fill(tech, width)
    fig.text(0.01, y, t, ha='left', va='bottom', fontsize=5.5, color='#333333')

def save(fig, name):
    for ext in ('png', 'pdf'):
        fig.savefig(OUTD / f'{name}{SUF}.{ext}', dpi=300 if ext == 'png' else None)

def smooth(h, k=25):
    ker = np.ones(k) / k; return np.convolve(h, ker, mode='same')

LON_E = V.LON0 + np.arange(V.NX + 1) * V.STEP; LAT_E = V.ROW_EDGES
def hpd_levels(m, levels=(0.5, 0.9, 0.99)):
    p = m.ravel() / m.sum(); o = np.argsort(-p); c = np.cumsum(p[o]); lev = np.zeros(p.size)
    for L in sorted(levels, reverse=True):
        sel = o[:np.searchsorted(c, L) + 1]; lev[sel] = L
    return lev.reshape(m.shape)
def arc_line():
    s = np.linspace(800, 2600, 400); return V.arc_point(s)

# ---------- Figure 1: maps per 00:19 treatment, all evidence, grey 50/90/99 % bands, 7th arc, core 90 % outline
fig, axs = plt.subplots(2, 3, figsize=(7.2, 6.2), sharex=True, sharey=True)
alat, alon = arc_line(); greys = mpl.colors.ListedColormap(['#ffffff', '#d9d9d9', '#969696', '#404040'])
for ax, d in zip(axs.ravel(), DK):
    m = MAPS[f'{d}|DS'].reshape(V.NY, V.NX).astype(float); lv = hpd_levels(m)
    code = np.select([lv == 0.5, lv == 0.9, lv == 0.99], [3, 2, 1], 0)
    ax.pcolormesh(LON_E, LAT_E, code, cmap=greys, vmin=-0.5, vmax=3.5, shading='flat', rasterized=True)
    mc = MAPS[f'{d}|core'].reshape(V.NY, V.NX).astype(float); lc = hpd_levels(mc, (0.9,))
    ax.contour(0.5 * (LON_E[1:] + LON_E[:-1]), 0.5 * (LAT_E[1:] + LAT_E[:-1]), (lc > 0).astype(float), levels=[0.5], colors=['#c0392b'], linewidths=0.7)
    ax.plot(alon, alat, color='#1f4e9c', lw=0.8)
    x = R['cells'][f'head|{d}|all|mix']['DS']; ax.set_title(DNAME[d], loc='left', fontsize=7)
    ax.set_xlim(84, 108); ax.set_ylim(-41, -20); ax.set_aspect(1 / np.cos(np.radians(-31)))
for ax in axs[:, 0]:
    ax.set_ylabel('Latitude (°)')
for ax in axs[-1]:
    ax.set_xlabel('Longitude (°E)')
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
h = [Patch(fc='#404040', label='All evidence, 50 % region'), Patch(fc='#969696', label='All evidence, 90 % region'), Patch(fc='#d9d9d9', ec='#bbbbbb', label='All evidence, 99 % region'),
     Line2D([], [], color='#c0392b', lw=0.8, label='Satellite data and flight only, 90 % region'), Line2D([], [], color='#1f4e9c', lw=0.8, label='7th arc (00:19:29)')]
fig.legend(handles=h, loc='upper center', ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.995), fontsize=6.5)
fig.suptitle('With all evidence, the probable sea-floor region moves north of the satellite-only region and becomes larger', x=0.01, y=0.94, ha='left', fontsize=8)
fig.subplots_adjust(left=0.08, right=0.99, top=0.86, bottom=0.25, wspace=0.08, hspace=0.25)
footnotes(fig, STE_BASE + ' Dark grey: 50 % of the probability; mid grey: 90 %; light grey: 99 %. Red line: 90 % without drift and searches.',
          TECH_BASE + ' HPD regions on the 769 km2 equal-area grid; seed-bootstrap intervals in the tables.')
save(fig, 'fig1-seabed-hpd-by-0019-treatment'); plt.close(fig)

# ---------- Figure 2: waypoints vs free flight latitude PDFs
fig, axs = plt.subplots(2, 3, figsize=(7.2, 5.4), sharex=True)
mids = PDF['mids']
for ax, d in zip(axs.ravel(), DK):
    for ctx, col, nm in (('run-j-waypoints', '#1f4e9c', 'Waypoint routes'), ('run-j-free', '#d35400', 'Free flight')):
        for p, ls in (('core', '--'), ('DS', '-')):
            h = PDF[f'{d}|{ctx}|{p}']; h = smooth(h / h.sum() / 0.01)
            ax.plot(mids, h, color=col, ls=ls, lw=1.0 if p == 'DS' else 0.7)
    ax.set_title(DNAME[d], loc='left', fontsize=7); ax.set_xlim(-41, -22); ax.margins(y=0.04)
for ax in axs[-1]:
    ax.set_xlabel('Latitude of the sea-floor position (°)')
for ax in axs[:, 0]:
    ax.set_ylabel('Probability density (per °)')
h = [Line2D([], [], color='#1f4e9c', lw=1, label='Waypoint routes, all evidence'), Line2D([], [], color='#1f4e9c', lw=0.7, ls='--', label='Waypoint routes, satellite data and flight only'),
     Line2D([], [], color='#d35400', lw=1, label='Free flight, all evidence'), Line2D([], [], color='#d35400', lw=0.7, ls='--', label='Free flight, satellite data and flight only')]
fig.legend(handles=h, loc='upper center', ncol=2, frameon=False, bbox_to_anchor=(0.5, 0.995), fontsize=6.5)
fig.suptitle('Free flight puts more probability north than waypoint routes, and the two medians agree within 0.8°', x=0.01, y=0.915, ha='left', fontsize=8)
fig.subplots_adjust(left=0.08, right=0.99, top=0.84, bottom=0.27, wspace=0.18, hspace=0.3)
footnotes(fig, STE_BASE + ' Each line is for one type of flight path. Each type is given on its own (the mixture is almost all waypoint routes).',
          TECH_BASE + ' Each stratum conditional on itself; latitude PDFs from settled pieces, 0.01° bins, 0.25° running mean.')
save(fig, 'fig2-waypoints-vs-free-flight'); plt.close(fig)

# ---------- Figure 3: sensitivity to the search-model level (rho field scale; q levels; OI rows)
H = {d: R['cells'][f'head|{d}|all|mix'] for d in DK}
met = [('median', 'median_se', 'Median latitude (°)', 1), ('north_of_33S', 'north33_se', 'Mass north of 33° S', 1),
       ('p_on_searched_ground', 'searched_se', 'Mass on searched ground', 1), ('hpd90_km2', 'hpd90_se', '90 % HPD area (thousand km²)', 1e-3)]
fig, axs = plt.subplots(2, 4, figsize=(7.2, 5.6))
RS = [('DS_r0', 0), ('DS', 1), ('DS_r5', 5), ('DS_r10', 10)]
QS = [('DS_V3', 'Optimistic'), ('DS', 'Central'), ('DS_V0', 'Scalar'), ('DS_V2', 'Pessimistic'), ('DS_oiu', 'OI fractions'), ('DS_nooi', 'No OI')]
for j, (k, sek, lab, sc) in enumerate(met):
    ax = axs[0, j]
    for d in DK:
        y = [H[d][p][k] * sc for p, _ in RS]; e = [(H[d]['boot'].get(p, {}).get(sek) or 0) * sc for p, _ in RS]
        ax.errorbar([x for _, x in RS], y, yerr=e, color=DCOL[d], lw=0.9, marker='o', ms=2.5, capsize=1.5)
    ax.set_xticks([0, 1, 5, 10]); ax.set_xticklabels(['0', '1', '5', '10']); ax.set_ylabel(lab); ax.margins(0.06); ax.yaxis.label.set_size(7)
    ax = axs[1, j]; xs = np.arange(len(QS))
    for i, d in enumerate(DK):
        y = [H[d][p][k] * sc for p, _ in QS]; e = [(H[d]['boot'].get(p, {}).get(sek) or 0) * sc for p, _ in QS]
        ax.errorbar(xs[:4] + (i - 2.5) * 0.06, y[:4], yerr=e[:4], color=DCOL[d], lw=0.9, marker='o', ms=2.5, capsize=1.5)
        ax.errorbar(xs[4:] + (i - 2.5) * 0.06, y[4:], yerr=e[4:], color=DCOL[d], lw=0, marker='s', ms=2.5, mfc='white', capsize=1.5, elinewidth=0.8)
    ax.axvline(3.5, color='#999999', lw=0.5, ls=':')
    ax.set_xticks(xs); ax.set_xticklabels([q for _, q in QS], rotation=60, ha='right', fontsize=6); ax.set_ylabel(lab, fontsize=7); ax.margins(0.06)
axs[0, 0].set_title('a  Chance of a missed wreck (terrain-shaped field), × the central value', loc='left', fontsize=7)
axs[1, 0].set_title('b  Detection level of the search model', loc='left', fontsize=7)
h = [Line2D([], [], color=DCOL[d], marker='o', ms=3, lw=0.9, label=DNAME[d].replace('\n', ' ')) for d in DK]
fig.legend(handles=h, loc='upper center', ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.995), fontsize=6)
fig.suptitle('A higher chance of a missed wreck moves the median south and puts more probability on searched ground', x=0.01, y=0.915, ha='left', fontsize=8)
fig.subplots_adjust(left=0.07, right=0.99, top=0.84, bottom=0.35, wspace=0.55, hspace=0.6)
footnotes(fig, STE_BASE + ' Top: the chance that the search did not find a wreck that was there, at 0, 1, 5 and 10 times the central value. '
          'Bottom: four levels of search quality; the open squares show two other ways to model the Ocean Infinity searches.',
          TECH_BASE + ' rho0 = 0 / 0.05 / 0.25 / 0.5 with the same terrain weight (V1_rho0, V1_central, V1_rho0.25, V1_rho0.5); levels V3, V1, V0, V2 '
          'of the per-cell model (237090ab); OI rows: uniform coverage fractions 0.889 / 0.7808, and without OI (sensitivity rows only). Error bars: seed-bootstrap SE (400 draws).')
save(fig, 'fig3-search-model-sensitivity'); plt.close(fig)

# ---------- Figure 4: evidence alone along the arc, and influence (KL share) by factor
fig = plt.figure(figsize=(7.2, 5.2)); gs = fig.add_gridspec(1, 2, width_ratios=[1.35, 1], wspace=0.75)
ax = fig.add_subplot(gs[0]); mids = VAI['mids']
for E, col, nm in (('U', '#999999', 'Uniform along the arc (prior)'), ('D', '#117a65', 'Debris drift alone'), ('S', '#7d3c98', 'Searched areas alone'),
                   ('P', '#b9770e', 'Pleiades objects alone (if debris)')):
    hh = VAI[E]; hh = smooth(hh / hh.sum() / 0.01)
    ax.plot(mids, hh, color=col, lw=1.0 if E != 'U' else 0.8, ls='-' if E != 'U' else ':', label=nm)
hc = PDF['D0|all|core']; ax.plot(mids, smooth(hc / hc.sum() / 0.01), color='#c0392b', lw=0.8, ls='--', label='Satellite data and flight only')
ha = PDF['D0|all|DS']; ax.plot(mids, smooth(ha / ha.sum() / 0.01), color='black', lw=1.2, label='All evidence')
ax.set_xlim(-41, -12); ax.text(0.0, -0.13, '00:19 data held out', transform=ax.transAxes, fontsize=6, va='top'); ax.set_yscale('log'); ax.set_ylim(5e-3, 5); ax.set_xlabel('Latitude (°)'); ax.set_ylabel('Probability density (per °, log scale)')
ax.legend(frameon=False, fontsize=6, loc='upper right'); ax.set_title('a  Each evidence type alone favours a different part of the arc', loc='left', fontsize=7)
ax2 = fig.add_subplot(gs[1]); y = np.arange(len(DK))
for k, (key, col, nm) in enumerate((('S|DS', '#7d3c98', 'Searched areas'), ('D|DS', '#117a65', 'Debris drift'))):
    v = [H[d]['loo'][key]['KL_share_of_total'] for d in DK]
    se = [H[d]['boot_KL'].get('DS|' + H[d]['loo'][key]['leave_out_product'], {}).get('se', 0) / H[d]['loo'][key]['KL_all_vs_core'] for d in DK]
    ax2.errorbar(v, y + (k - 0.5) * 0.2, xerr=se, color=col, marker='o', ms=3, lw=0, elinewidth=0.8, capsize=1.5, label=nm)
ax2.axvline(0.5, color='#999999', lw=0.6, ls=':'); ax2.set_yticks(y); ax2.set_yticklabels([DNAME[d] if '\n' in DNAME[d] else DNAME[d].replace(' + ', '\n+ ', 1) for d in DK], fontsize=6); ax2.invert_yaxis()
ax2.set_xlabel('Share of KL(all evidence ‖ satellite only)\nlost when the factor is removed'); ax2.set_xlim(0, 0.85)
ax2.legend(frameon=False, fontsize=6, loc='center left'); ax2.set_title('b  The searched areas carry half or more in every treatment (0.50-0.69)', loc='left', fontsize=7)
fig.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.36)
footnotes(fig, STE_BASE + ' Left: each line is one type of evidence on its own, with the same probability everywhere along the arc before the evidence. '
          'Right: how much of the change from the satellite-only result each type of evidence causes.',
          TECH_BASE + " Left: view (a)(i), sampling-free surfaces on the 7th-arc span 40.6-11.8 S with one fixed end-of-flight displacement; searched areas as a "
          "point target at the impact (no settling in this view); " + globals().get('DRIFT_NOTE', 'drift not computed north of 21.2 S (0.30 of the span, carried at the mean)') + ". Right: "
          "KL(all || all without factor) / KL(all || core), seed-bootstrap SE; dotted line = the brief's 0.5 flag.")
save(fig, 'fig4-evidence-alone-and-influence'); plt.close(fig)
print('figures written')
