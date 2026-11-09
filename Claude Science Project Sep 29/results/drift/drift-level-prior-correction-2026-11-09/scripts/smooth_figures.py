"""Drift evidence alone (uniform prior along the 7th arc), smoothed, against the satellite and flight data (final end of flight, Davey model + fuel, D0).
One-panel and two-panel figures, working (colour, notes) and Journal of Navigation (greyscale, no title, no notes, 127 mm, caption beneath) versions."""
import os, textwrap, numpy as np, pandas as pd, matplotlib.pyplot as plt
_s = open('offline/final_figures_ramp.py').read(); OUT = 'figs-smooth'; os.makedirs(OUT, exist_ok=True)
exec(_s[_s.index('def finish'):_s.index('plt.rcParams.update')])
plt.rcParams.update({'font.size': 7, 'axes.spines.top': False, 'axes.spines.right': False, 'font.family': 'DejaVu Sans', 'pdf.fonttype': 42})
C = pd.read_csv('res-smooth/smoothed-drift-alone-curves.csv'); S = pd.read_csv('res-smooth/smoothed-drift-alone-summary.csv').set_index('case')
X = C.lat.values; xc = X; core = C.core.values / 0.1                  # uniform 0.1-degree latitude bins; density per degree = bin mass / 0.1
def dens(col): return C[col].values / 0.1
def med(y): c = np.cumsum(y) * 0.1; return float(X[np.searchsorted(c, 0.5)])
chk = {k: (med(dens(k)), -float(S.loc[k, 'median'])) for k in ('Two ocean models', 'Without Mossel Bay')}; print('median of plotted curve vs ledger-bin median', chk)
for k, (a, b) in chk.items(): assert abs(a + b) < 0.11, (k, a, b)
medc = float(xc[np.searchsorted(np.cumsum(core) * 0.1, 0.5)]); assert abs(core.sum() * 0.1 - 1) < 1e-6; print('core median', medc, 'core integral', core.sum() * 0.1)
K = {'head': 'Two ocean models', 'au': 'No finds on Australian coasts (0.25)', 'gc': 'GlobCurrent only', 'gl': 'GLORYS12 only', 'nomb': 'Without Mossel Bay'}
LAB = {'head': 'Drift alone, two ocean models', 'au': 'Same, and no finds on Australian coasts', 'gc': 'GlobCurrent only', 'gl': 'GLORYS12 only', 'nomb': 'Without the Mossel Bay item'}
ST = {'head': (dict(color='0.0', lw=2.0, ls='-'), '#C44E52'), 'au': (dict(color='0.0', lw=1.2, ls=':'), '#55A868'), 'gc': (dict(color='0.3', lw=1.1, ls='--'), '#4C72B0'),
      'gl': (dict(color='0.3', lw=1.1, ls='-.'), '#8172B2'), 'nomb': (dict(color='0.5', lw=1.4, ls=(0, (7, 2.5))), '#DD8452')}
m = lambda k: -float(S.loc[K[k], 'median']); sg = lambda k: float(S.loc[K[k], 'sigma']); sg5 = lambda k: float(S.loc[K[k], 'sigma_b05']); sg95 = lambda k: float(S.loc[K[k], 'sigma_b95'])
def core_fill(ax, grey): ax.fill_between(-xc, 0, core, color='0.86' if grey else '#d9d9d9', lw=0, label='Satellite and flight data', zorder=0); ax.plot(-xc, core, color='0.55', lw=0.6, zorder=1)
def band(ax, k, grey): ax.fill_between(-X, dens(K[k] + ' | b05'), dens(K[k] + ' | b95'), color='0.6' if grey else '#e6b8ba', alpha=0.55 if grey else 0.7, lw=0, zorder=2, label='Range from resampling of ocean samples')
def draw(ax, keys, grey):
    for k in keys:
        st, c = ST[k]; kw = dict(st)
        if not grey: kw['color'] = c
        ax.plot(-X, dens(K[k]), label=LAB[k], zorder=3, **kw)
    ax.set_xlim(41, 19.5); ax.set_ylim(0, None); ax.set_ylabel('Probability density (per degree)')
rng_s = f"{min(sg('head'), sg('gl'), sg('au')):.1f} to {max(sg('head'), sg('gl'), sg('au')):.1f}"
COMMON = ("Probability density of the impact latitude on the 7th arc from the debris drift evidence alone, with a prior that is uniform along the arc, "
          "compared with the density from the satellite communication and flight data (Davey model with the fuel model; no measurement at 00:19 used). "
          "Drift evidence: twelve items on all western Indian Ocean coasts with four detection periods; two ocean models with equal weight unless stated. "
          "The drift curves are smoothed along the arc by a Gaussian-process fit to the 84 release points. "
          "No finds on Australian coasts: detection on populated Australian coasts 0.25 of that on the find coasts. ")
MED = (f"Medians: satellite and flight data {-medc:.1f} degrees south; drift alone {m('head'):.1f}; with no finds on Australian coasts {m('au'):.1f}; "
       f"GlobCurrent only {m('gc'):.1f}; GLORYS12 only {m('gl'):.1f}; without Mossel Bay {m('nomb'):.1f}. "
       f"Range of the drift-alone median from resampling the ocean samples (5 to 95 per cent): {-float(S.loc[K['head'], 'median_b95']):.1f} to {-float(S.loc[K['head'], 'median_b05']):.1f} degrees south. "
       f"Disagreement between the drift evidence (two ocean models) and the satellite and flight data: {sg('head'):.1f} standard deviations "
       f"({sg5('head'):.1f} to {sg95('head'):.1f} over ocean samples; {rng_s} over ocean models and the Australian assumption).")
CAP1 = COMMON + "The two-model curve lies close to the GlobCurrent curve. " + MED
CAP2 = COMMON + "(a) Drift evidence with two ocean models, and with no finds on Australian coasts. (b) Drift evidence by ocean model, and without the Mossel Bay item. " + MED
NOTE = ("Notes. Drift: GLORYS12V1 currents at 0.494 m with ERA5 wind; Copernicus GlobCurrent with ERA5 wind, wind factor reduced for built-in wind drift; 84 release points from 40.25 to 19.92 S; "
        "finds scored to 30 Jan 2017; Mossel Bay dated at its first beaching (23 Dec 2015); detection levels log-normal (sigma 1) per coast and period, prior median 0.1 before 29 Jul 2015, 0.5 to 1 Mar 2016, then 1 (provisional); "
        "262144 level draws; 16 ocean samples (32 south of 33.25 S); items weighted by identification grade (1 / 0.98 / 0.9). Smoothing: Matern 3/2 Gaussian process, constant mean, length scale and nugget by "
        "marginal likelihood; results unchanged for fixed length scales of 2, 4 and 8 degrees; ocean-sample range from 400 resamples (same samples at all points); latitude bins of 0.1 degree, arc prior from the ledger bin count. Core: end of flight, Davey model + fuel, log-on event only. Provisional physics.")
def fig1(grey):
    w_ = 127 / 25.4 if grey else 180 / 25.4; hh = 3.0 if grey else 4.4
    f, ax = plt.subplots(figsize=(w_, hh)); f.subplots_adjust(left=0.1, right=0.98, top=0.97 if grey else 0.9, bottom=0.15 if grey else 0.3)
    core_fill(ax, grey); draw(ax, ['head', 'au', 'gc', 'gl', 'nomb'], grey); ax.set_xlabel('Latitude on the 7th arc (degrees south)'); ax.legend(frameon=False, loc='upper right', fontsize=6.0)
    if not grey:
        ax.set_title(f'Drift evidence alone favours about {m("head"):.0f} degrees south; the satellite and flight data favour about {-medc:.0f} degrees south', loc='left', fontsize=8)
        f.text(0.01, 0.01, '\n'.join(textwrap.wrap(NOTE, 170)), fontsize=5.2, va='bottom')
    return f
def fig2(grey):
    w_ = 127 / 25.4 if grey else 180 / 25.4; hh = 4.6 if grey else 6.2
    f, axs = plt.subplots(2, 1, figsize=(w_, hh), sharex=True); f.subplots_adjust(left=0.1, right=0.98, top=0.98 if grey else 0.93, bottom=0.09 if grey else 0.2, hspace=0.12)
    core_fill(axs[0], grey); draw(axs[0], ['head', 'au'], grey); core_fill(axs[1], grey); draw(axs[1], ['head', 'gc', 'gl', 'nomb'], grey)
    for ax, t in zip(axs, 'ab'): ax.legend(frameon=False, loc='upper right', fontsize=6.0); ax.text(0.01, 0.95, f'({t})', transform=ax.transAxes, fontweight='bold', va='top')
    axs[1].set_xlabel('Latitude on the 7th arc (degrees south)')
    if not grey:
        f.suptitle(f'Drift evidence alone favours about {m("head"):.0f} degrees south; the satellite and flight data favour about {-medc:.0f} degrees south', x=0.01, ha='left', fontsize=8)
        f.text(0.01, 0.01, '\n'.join(textwrap.wrap(NOTE, 170)), fontsize=5.2, va='bottom')
    return f
for g_ in (False, True):
    finish(fig1(g_), 'drift-alone-smoothed-one-panel-2026-11-09', g_, CAP1); finish(fig2(g_), 'drift-alone-smoothed-two-panel-2026-11-09', g_, CAP2)
print(CAP1); print(); print(CAP2)
