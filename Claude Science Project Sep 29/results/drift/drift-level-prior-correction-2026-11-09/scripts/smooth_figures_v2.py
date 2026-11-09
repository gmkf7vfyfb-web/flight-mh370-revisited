"""Journal and working figures, 9 Nov 2026 (second set): drift standalone, satellite and flight data, and the combined density.
Combined density = satellite and flight density (final end of flight, Davey model + fuel, D0) x smoothed drift likelihood, normalised, on 0.1-degree latitude bins.
A: standalone drift curves with the satellite and flight data (legend wording as requested);  B: A plus the combined density;
C: reduced chart: satellite and flight data, drift standalone (two ocean models), combined;  D: combined with and without the Mossel Bay item (with the satellite and flight data);
E: two-panel version of A."""
import os, textwrap, numpy as np, pandas as pd, matplotlib.pyplot as plt, matplotlib.patches as mp
from matplotlib.lines import Line2D
_s = open('offline/final_figures_ramp.py').read(); OUT = 'figs-smooth2'; os.makedirs(OUT, exist_ok=True)
exec(_s[_s.index('def finish'):_s.index('plt.rcParams.update')])
plt.rcParams.update({'font.size': 7, 'axes.spines.top': False, 'axes.spines.right': False, 'font.family': 'DejaVu Sans', 'pdf.fonttype': 42, 'hatch.linewidth': 0.5})
C = pd.read_csv('res-smooth/smoothed-drift-alone-curves.csv'); S = pd.read_csv('res-smooth/smoothed-drift-alone-summary.csv').set_index('case')
X, pi, pc = C.lat.values, C.prior.values, C.core.values; DX = 0.1
dens = lambda p: p / DX
def stats(p):
    p = p / p.sum(); c = np.cumsum(p); q = lambda f: float(X[np.searchsorted(c, f)]); return dict(mean=float((p * X).sum()), median=q(.5), N33=100 * float(p[X >= -33].sum()))
def combined(case): LB = np.where(pi > 0, C[case].values / pi, 0.0); p = pc * LB; return p / p.sum()
CASE = {'head': 'Two ocean models', 'au': 'No finds on Australian coasts (0.25)', 'gc': 'GlobCurrent only', 'gl': 'GLORYS12 only', 'nomb': 'Without Mossel Bay'}
Y = {k: dens(C[v].values) for k, v in CASE.items()}; Y['core'] = dens(pc); Y['comb'] = dens(combined(CASE['head'])); Y['comb_nomb'] = dens(combined(CASE['nomb']))
ST = {k: stats(Y[k] * DX) for k in Y}; sg = lambda k: float(S.loc[CASE[k], 'sigma']); sg5 = float(S.loc['Two ocean models', 'sigma_b05']); sg95 = float(S.loc['Two ocean models', 'sigma_b95'])
LAB = {'core': 'Satellite and flight data only', 'head': 'Drift model standalone (two ocean models)', 'au': 'Two ocean models and no finds on Australian coasts', 'gc': 'Drift model: GlobCurrent only',
       'gl': 'Drift model: GLORYS12 only', 'nomb': 'Two ocean models excluding Mossel Bay item', 'comb': 'Satellite and flight data combined with drift model (two ocean models)',
       'comb_nomb': 'Combined, excluding Mossel Bay item'}
LN = {'head': (dict(color='0.0', lw=2.0, ls='-'), '#C44E52'), 'au': (dict(color='0.0', lw=1.2, ls=':'), '#55A868'), 'gc': (dict(color='0.3', lw=1.1, ls='--'), '#4C72B0'),
      'gl': (dict(color='0.3', lw=1.1, ls='-.'), '#8172B2'), 'nomb': (dict(color='0.5', lw=1.4, ls=(0, (7, 2.5))), '#DD8452')}
CBC, CBC2 = '#8C564B', '#C7A087'
def handles_core(ax, grey):
    ax.fill_between(-X, 0, Y['core'], color='0.86' if grey else '#d9d9d9', lw=0, zorder=0); ax.plot(-X, Y['core'], color='0.55', lw=0.6, zorder=1)
    return mp.Patch(facecolor='0.86' if grey else '#d9d9d9', edgecolor='0.55', lw=0.6, label=LAB['core'])
def handles_line(ax, k, grey, label=None):
    st, c = LN[k]; kw = dict(st)
    if not grey: kw['color'] = c
    ax.plot(-X, Y[k], zorder=3, **kw); return Line2D([], [], label=label or LAB[k], **kw)
def handles_comb(ax, k, grey, hatch='////', lab=None, dashed=False):
    col = ('0.15' if k == 'comb' else '0.4') if grey else (CBC if k == 'comb' else CBC2)
    ax.fill_between(-X, 0, Y[k], facecolor='none', edgecolor=col, hatch=hatch, lw=0, zorder=2); ax.plot(-X, Y[k], color=col, lw=1.4 if k == 'comb' else 1.5, ls=(0, (7, 2.5)) if dashed else '-', zorder=4)
    return mp.Patch(facecolor='none', edgecolor=col, hatch=hatch, lw=0, label=lab or LAB[k])
def axes_cfg(ax, ytop, hs, fs=5.8):
    ax.set_xlim(41, 19.5); ax.set_ylim(0, ytop); ax.set_ylabel('Probability density (per degree)'); ax.legend(handles=hs, frameon=False, loc='upper right', fontsize=fs, handlelength=2.6)
m = lambda k: -ST[k]['median']; mm = lambda k: -ST[k]['mean']
rng_s = f"{min(sg('head'), sg('gl'), sg('au')):.1f} to {max(sg('head'), sg('gl'), sg('au')):.1f}"
BASE = ("Probability density of the impact latitude on the 7th arc. Grey area: the satellite communication and flight data (Davey model with the fuel model; no measurement at 00:19 used). "
        "Drift model: twelve items on all western Indian Ocean coasts with four detection periods, two ocean models with equal weight unless stated, with a prior that is uniform along the arc, "
        "smoothed along the arc by a Gaussian-process fit to the 84 release points. No finds on Australian coasts: detection on populated Australian coasts 0.25 of that on the find coasts. ")
MEDS = (f"Medians (degrees south): satellite and flight data {m('core'):.1f}; drift model {m('head'):.1f}; with no finds on Australian coasts {m('au'):.1f}; GlobCurrent only {m('gc'):.1f}; "
        f"GLORYS12 only {m('gl'):.1f}; excluding Mossel Bay {m('nomb'):.1f}. ")
TEN = (f"Disagreement between the drift model (two ocean models) and the satellite and flight data: {sg('head'):.1f} standard deviations ({sg5:.1f} to {sg95:.1f} over ocean samples; {rng_s} over ocean models and the Australian assumption). ")
COMBX = (f"The combined density is the satellite and flight density multiplied by the drift likelihood and normalised; its median is {m('comb'):.1f} degrees south and its mean {mm('comb'):.1f}, "
         f"against {m('core'):.1f} and {mm('core'):.1f} for the satellite and flight data alone. ")
CAP = {'A': BASE + MEDS + TEN,
       'B': BASE + "Hatched area: the satellite and flight data combined with the drift model (two ocean models). " + COMBX + MEDS + TEN,
       'C': ("Probability density of the impact latitude on the 7th arc. Grey area: the satellite communication and flight data (Davey model with the fuel model; no measurement at 00:19 used). "
             "Solid line: the drift model alone (twelve items, two ocean models with equal weight, prior uniform along the arc, smoothed along the arc). Hatched area: the two combined. " + COMBX + TEN),
       'D': ("Probability density of the impact latitude on the 7th arc. Grey area: the satellite communication and flight data (Davey model with the fuel model; no measurement at 00:19 used). "
             "Hatched area with solid line: these data combined with the drift model (twelve items, two ocean models). Dashed line: the same combination excluding the Mossel Bay item. "
             f"Medians (degrees south): satellite and flight data {m('core'):.1f}; combined {m('comb'):.1f}; combined excluding Mossel Bay {m('comb_nomb'):.1f}. "
             f"Means: {mm('core'):.1f}; {mm('comb'):.1f}; {mm('comb_nomb'):.1f}. Share of the probability north of 33 degrees south: {ST['core']['N33']:.0f}, {ST['comb']['N33']:.0f} and {ST['comb_nomb']['N33']:.0f} per cent.")}
CAP['E'] = BASE + "(a) Drift model with two ocean models, and with no finds on Australian coasts. (b) Drift model by ocean model, and excluding the Mossel Bay item. " + MEDS + TEN
NOTE = ("Notes. Drift: GLORYS12V1 currents at 0.494 m with ERA5 wind; Copernicus GlobCurrent with ERA5 wind, wind factor reduced for built-in wind drift; 84 release points from 40.25 to 19.92 S; finds scored to 30 Jan 2017; "
        "Mossel Bay dated at its first beaching (23 Dec 2015); detection levels log-normal (sigma 1) per coast and period, prior median 0.1 before 29 Jul 2015, 0.5 to 1 Mar 2016, then 1 (provisional); 262144 level draws; "
        "16 ocean samples (32 south of 33.25 S); items weighted by identification grade (1 / 0.98 / 0.9). Smoothing: Matern 3/2 Gaussian process, results unchanged for fixed length scales of 2, 4 and 8 degrees; "
        "0.1-degree latitude bins. Combined density: core x smoothed drift likelihood (one-dimensional, along the arc); the per-point reweighting of the two-dimensional core samples gives a shift of the mean of +1.43 degrees "
        "(eight draw seeds +1.17 to +1.68) against +%.2f here. Core: end of flight, Davey model + fuel, log-on event only. Provisional physics." % (ST['comb']['mean'] - ST['core']['mean']))
def mk(kind, grey):
    w = 127 / 25.4 if grey else 180 / 25.4
    if kind == 'E':
        f, axs = plt.subplots(2, 1, figsize=(w, 4.8 if grey else 6.4), sharex=True); f.subplots_adjust(left=0.1, right=0.98, top=0.98 if grey else 0.93, bottom=0.09 if grey else 0.2, hspace=0.12)
        h0 = handles_core(axs[0], grey); h1 = handles_line(axs[0], 'head', grey); h2 = handles_line(axs[0], 'au', grey); axes_cfg(axs[0], 0.40, [h0, h1, h2])
        g0 = handles_core(axs[1], grey); g1 = handles_line(axs[1], 'head', grey); g2 = handles_line(axs[1], 'gc', grey); g3 = handles_line(axs[1], 'gl', grey); g4 = handles_line(axs[1], 'nomb', grey); axes_cfg(axs[1], 0.40, [g0, g1, g2, g3, g4])
        for ax, t in zip(axs, 'ab'): ax.text(0.01, 0.95, f'({t})', transform=ax.transAxes, fontweight='bold', va='top')
        axs[1].set_xlabel('Latitude on the 7th arc (degrees south)'); ax_ = axs[0]
    else:
        f, ax = plt.subplots(figsize=(w, 3.3 if grey else 4.7)); f.subplots_adjust(left=0.1, right=0.98, top=0.97 if grey else 0.9, bottom=0.14 if grey else 0.3)
        hs = [handles_core(ax, grey)]
        if kind in ('A', 'B'):
            for k in ('head', 'au', 'gc', 'gl', 'nomb'): hs.append(handles_line(ax, k, grey))
            if kind == 'B': hs.append(handles_comb(ax, 'comb', grey))
            axes_cfg(ax, 0.40 if kind == 'A' else 0.50, hs)
        elif kind == 'C':
            hs.append(handles_line(ax, 'head', grey)); hs.append(handles_comb(ax, 'comb', grey)); axes_cfg(ax, 0.46, hs, 6.2)
        else:
            hs.append(handles_comb(ax, 'comb', grey, lab='Combined: satellite and flight data and drift model (two ocean models)'))
            colx = '0.4' if grey else CBC2; ax.plot(-X, Y['comb_nomb'], color=colx, lw=1.9, ls=(0, (7, 2.5)), zorder=4)
            hs.append(Line2D([], [], color=colx, lw=1.9, ls=(0, (7, 2.5)), label='Combined, excluding Mossel Bay item')); axes_cfg(ax, 0.46, hs, 6.2)
        ax.set_xlabel('Latitude on the 7th arc (degrees south)'); ax_ = ax
    if not grey:
        ttl = {'A': f'Drift model alone favours about {m("head"):.0f} degrees south; satellite and flight data about {m("core"):.0f}', 'B': f'Combined density: median {m("comb"):.1f} degrees south (satellite and flight data alone {m("core"):.1f})',
               'C': f'Combined density: median {m("comb"):.1f} degrees south (satellite and flight data alone {m("core"):.1f})', 'D': f'Excluding Mossel Bay moves the combined median from {m("comb"):.1f} to {m("comb_nomb"):.1f} degrees south',
               'E': f'Drift model alone favours about {m("head"):.0f} degrees south; satellite and flight data about {m("core"):.0f}'}[kind]
        (f.suptitle(ttl, x=0.01, ha='left', fontsize=8) if kind == 'E' else ax_.set_title(ttl, loc='left', fontsize=8)); f.text(0.01, 0.01, '\n'.join(textwrap.wrap(NOTE, 170)), fontsize=5.2, va='bottom')
    return f
NAMES = {'A': 'drift-standalone-and-satellite-flight-one-panel', 'B': 'drift-standalone-satellite-flight-and-combined-one-panel', 'C': 'satellite-flight-drift-standalone-and-combined-reduced',
         'D': 'combined-with-and-without-mossel-bay', 'E': 'drift-standalone-and-satellite-flight-two-panel'}
for k in 'ABCDE':
    for g in (False, True): finish(mk(k, g), NAMES[k] + '-2026-11-09', g, CAP[k])
print({k: {a: round(b, 2) for a, b in v.items()} for k, v in ST.items()}); print(CAP['B'])
