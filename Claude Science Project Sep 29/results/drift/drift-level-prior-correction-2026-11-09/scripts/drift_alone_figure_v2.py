"""Drift evidence alone (uniform prior along the 7th arc) with the satellite and flight data: one-panel and two-panel versions, 9 Nov 2026.
Drift curves: ledger-bin masses re-binned to 0.5 deg (unsmoothed). Core: 0.25-deg density from the run J accumulators (latitude-densities.csv)."""
import os, textwrap, numpy as np, pandas as pd, matplotlib.pyplot as plt
_s = open('offline/final_figures_ramp.py').read(); OUT = 'figs-ramp'
exec(_s[_s.index('def finish'):_s.index('plt.rcParams.update')])
plt.rcParams.update({'font.size': 7, 'axes.spines.top': False, 'axes.spines.right': False, 'font.family': 'DejaVu Sans', 'pdf.fonttype': 42})
C = pd.read_csv('res-alone-ramp/drift-alone-curves.csv'); T = pd.read_csv('res-alone-ramp/drift-alone-and-tension.csv').set_index('case')
D = pd.read_csv('res-final-ramp/latitude-densities.csv'); xd = 0.5 * (D.lat_lo + D.lat_hi)
E = np.arange(-41.0, -19.49, 0.5); xc = 0.5 * (E[1:] + E[:-1])
def dens(col):
    h, _ = np.histogram(C.lat.values, E, weights=C[col].values / C[col].sum()); return h / 0.5
R3 = 'R3-allcoasts-4periods'; HD = f'{R3} | HEADLINE twelve items'
K = {'head': f'{HD} | both models', 'au': f'{R3} | headline + Australia ratio 0.25 | both models', 'gc': f'{HD} | GlobCurrent', 'gl': f'{HD} | GLORYS12',
     'nomb': f'{R3} | headline without Mossel Bay | both models'}
md = lambda k: -float(T.loc[K[k], 'median']); mdc = -float(T.loc['core (satellite and flight data)', 'median'])
ST = {'head': ('Drift alone, two ocean models', dict(color='0.0', lw=2.0, ls='-'), '#C44E52'),
      'au': ('Same, and no finds on Australian coasts', dict(color='0.0', lw=1.1, ls=':'), '#55A868'),
      'gc': ('GlobCurrent only', dict(color='0.35', lw=1.0, ls='--'), '#4C72B0'),
      'gl': ('GLORYS12 only', dict(color='0.35', lw=1.0, ls='-.'), '#8172B2'),
      'nomb': ('Without the Mossel Bay item', dict(color='0.55', lw=1.3, ls=(0, (7, 2.5))), '#DD8452')}
def core(ax, grey):
    y = D['core'].values; ax.fill_between(-xd, 0, y, color='0.85' if grey else '#d9d9d9', lw=0, label='Satellite and flight data', zorder=0)
def draw(ax, keys, grey):
    for k in keys:
        lab, st, c = ST[k]; kw = dict(st)
        if not grey: kw['color'] = c
        ax.plot(-xc, dens(K[k]), label=lab, zorder=3, **kw)
    ax.set_xlim(41, 19.5); ax.set_ylim(0, None); ax.set_ylabel('Probability density (per degree)')
h = T.loc[K['head']]
COMMON = ("Probability density of the impact latitude on the 7th arc from the debris drift evidence alone, with a prior that is uniform along the arc. "
          "Grey area: the density from the satellite communication and flight data. Drift evidence: twelve items on all western Indian Ocean coasts, "
          "with four detection periods; two ocean models with equal weight unless stated. No finds on Australian coasts: detection on populated "
          "Australian coasts 0.25 of that on the find coasts. The drift curves are not smoothed and contain sampling noise between neighbouring release points. ")
MED = (f"Medians: satellite and flight data {mdc:.1f} degrees south; drift alone {md('head'):.1f}; with no finds on Australian coasts {md('au'):.1f}; "
       f"GlobCurrent only {md('gc'):.1f}; GLORYS12 only {md('gl'):.1f}; without Mossel Bay {md('nomb'):.1f}. "
       f"Agreement of the drift evidence with the satellite and flight data: suspiciousness ln S = {h.lnS:.2f}, tension probability {h.p:.2f} "
       f"({h.sigma:.1f} standard deviations).")
CAP1 = COMMON + "The two-model curve lies close to the GlobCurrent curve. " + MED
CAP2 = COMMON.replace("Grey area:", "(a) Grey area:").replace("Drift evidence: twelve", "(b) The drift evidence by ocean model and without the Mossel Bay item. Drift evidence: twelve") + MED
NOTE = ("Notes. Drift: GLORYS12V1 currents at 0.494 m with ERA5 wind; Copernicus GlobCurrent with ERA5 wind, wind factor reduced for built-in wind drift; "
        "84 release points from 40.25 to 19.92 S; finds scored to 30 Jan 2017; Mossel Bay dated at its first beaching (23 Dec 2015); detection levels log-normal "
        "(sigma 1) per coast and period, prior median 0.1 before 29 Jul 2015, 0.5 to 1 Mar 2016, then 1; 16384 draws; items weighted by identification grade "
        "(1 / 0.98 / 0.9). Core: end-of-flight run J, 00:19 data held out. Tension statistics after Handley and Lemos (2019). Provisional physics.")
def fig1(grey):
    w = 127 / 25.4 if grey else 180 / 25.4; hh = 3.0 if grey else 4.4
    f, ax = plt.subplots(figsize=(w, hh)); f.subplots_adjust(left=0.1, right=0.98, top=0.97 if grey else 0.9, bottom=0.15 if grey else 0.3)
    core(ax, grey); draw(ax, ['head', 'au', 'gc', 'gl', 'nomb'], grey); ax.set_xlabel('Latitude on the 7th arc (degrees south)')
    ax.legend(frameon=False, loc='upper right', fontsize=6.0)
    if not grey:
        ax.set_title(f'Drift evidence alone favours about {md("head"):.0f} degrees south; the satellite and flight data favour about {mdc:.0f} degrees south', loc='left', fontsize=8)
        f.text(0.01, 0.01, '\n'.join(textwrap.wrap(NOTE, 170)), fontsize=5.2, va='bottom')
    return f
def fig2(grey):
    w = 127 / 25.4 if grey else 180 / 25.4; hh = 4.6 if grey else 6.2
    f, axs = plt.subplots(2, 1, figsize=(w, hh), sharex=True); f.subplots_adjust(left=0.1, right=0.98, top=0.98 if grey else 0.93, bottom=0.09 if grey else 0.2, hspace=0.12)
    core(axs[0], grey); draw(axs[0], ['head', 'au'], grey)
    core(axs[1], grey); draw(axs[1], ['head', 'gc', 'gl', 'nomb'], grey)
    for ax, t in zip(axs, 'ab'):
        ax.legend(frameon=False, loc='upper right', fontsize=6.0); ax.text(0.01, 0.95, f'({t})', transform=ax.transAxes, fontweight='bold', va='top')
    axs[1].set_xlabel('Latitude on the 7th arc (degrees south)')
    if not grey:
        f.suptitle(f'Drift evidence alone favours about {md("head"):.0f} degrees south; the satellite and flight data favour about {mdc:.0f} degrees south', x=0.01, ha='left', fontsize=8)
        f.text(0.01, 0.01, '\n'.join(textwrap.wrap(NOTE, 170)), fontsize=5.2, va='bottom')
    return f
for g in (False, True):
    finish(fig1(g), 'drift-alone-latitude-density-one-panel-2026-11-09', g, CAP1)
    finish(fig2(g), 'drift-alone-latitude-density-two-panel-2026-11-09', g, CAP2)
print('core density integral', round(float((D['core'] * (D.lat_hi - D.lat_lo)).sum()), 4)); print(CAP1); print(CAP2)
