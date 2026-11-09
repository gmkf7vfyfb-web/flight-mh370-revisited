"""Drift evidence alone (flat prior per unit length along the 7th arc) against the core, corrected 9 Nov 2026. Working and JON versions."""
import os, textwrap, numpy as np, pandas as pd, matplotlib.pyplot as plt
_s = open('offline/final_figures_ramp.py').read(); OUT = 'figs-ramp'
exec(_s[_s.index('def finish'):_s.index('plt.rcParams.update')])
plt.rcParams.update({'font.size': 7, 'axes.spines.top': False, 'axes.spines.right': False, 'font.family': 'DejaVu Sans', 'pdf.fonttype': 42})
C = pd.read_csv('res-alone-ramp/drift-alone-curves.csv'); T = pd.read_csv('res-alone-ramp/drift-alone-and-tension.csv').set_index('case')
E = np.arange(-41.0, -19.49, 0.5); xc = 0.5 * (E[1:] + E[:-1])
def dens(col):
    h, _ = np.histogram(C.lat.values, E, weights=C[col].values / C[col].sum()); return h / 0.5
R3 = 'R3-allcoasts-4periods'; HD = f'{R3} | HEADLINE twelve items'
K = {'core': 'core', 'old': 'earlier drift alone (ledger v32, October surfaces)', 'head': f'{HD} | both models', 'au': f'{R3} | headline + Australia ratio 0.25 | both models',
     'gc': f'{HD} | GlobCurrent', 'gl': f'{HD} | GLORYS12', 'nomb': f'{R3} | headline without Mossel Bay | both models'}
TK = {'core': 'core (satellite and flight data)', 'old': 'earlier drift alone (ledger v32, October surfaces, 256 draws)'}
def md(k): return -float(T.loc[TK.get(k, K[k]), 'median'])
PA = [('core', 'Satellite and flight data', dict(color='0.55', lw=1.0, ls='-'), '#888888'),
      ('old', 'Drift alone, October 2026 calculation', dict(color='0.25', lw=1.0, ls='--'), '#4C72B0'),
      ('head', 'Drift alone, this calculation', dict(color='0.0', lw=2.0, ls='-'), '#C44E52'),
      ('au', 'Same, and no finds on Australian coasts', dict(color='0.15', lw=1.2, ls=':'), '#55A868')]
PB = [('head', 'Drift alone, two ocean models', dict(color='0.0', lw=2.0, ls='-'), '#C44E52'),
      ('gc', 'GlobCurrent only', dict(color='0.3', lw=1.0, ls='--'), '#4C72B0'),
      ('gl', 'GLORYS12 only', dict(color='0.3', lw=1.0, ls='-.'), '#8172B2'),
      ('nomb', 'Without the Mossel Bay item', dict(color='0.5', lw=1.2, ls=':'), '#55A868')]
h = T.loc[K['head']]
CAP = ("Probability density of the impact latitude on the 7th arc from the debris drift evidence alone, with a prior that is uniform along "
       "the arc, compared with the density from the satellite communication and flight data. (a) The drift evidence of twelve items on all "
       "western Indian Ocean coasts with four detection periods, the same with no finds on Australian coasts (detection on populated "
       "Australian coasts 0.25 of that on the find coasts), and the October 2026 calculation (nine finds, finds window to 30 June 2016). "
       "(b) The drift evidence by ocean model and without the Mossel Bay item. Medians: satellite and flight data "
       f"{md('core'):.1f} degrees south; drift alone {md('head'):.1f} (October calculation {md('old'):.1f}); without Mossel Bay {md('nomb'):.1f}. "
       f"Agreement of the drift evidence with the satellite and flight data: suspiciousness ln S = {h.lnS:.2f}, tension probability "
       f"{h.p:.2f} ({h.sigma:.1f} standard deviations).")
NOTE = ("Notes. Drift: two ocean models with equal weight (GLORYS12V1 currents at 0.494 m with ERA5 wind; Copernicus GlobCurrent with ERA5 wind, "
        "wind factor reduced for built-in wind drift). 84 release points from 40.25 to 19.92 S; densities outside this span are not computed. "
        "Finds scored to 30 Jan 2017; detection levels log-normal (sigma 1) per coast and period, prior median 0.1 before 29 Jul 2015, 0.5 to 1 Mar 2016, "
        "then 1; 16384 draws. Twelve items weighted by identification grade (confirmed 1, almost certain 0.98, highly likely 0.9). "
        "Core: end-of-flight run J, 00:19 data held out. Tension statistics after Handley and Lemos (2019) on the evidence-ledger bins. Provisional physics.")
def fig(grey):
    w = 127 / 25.4 if grey else 180 / 25.4; hh = 4.6 if grey else 6.2
    f, axs = plt.subplots(2, 1, figsize=(w, hh), sharex=True)
    f.subplots_adjust(left=0.11, right=0.98, top=0.98 if grey else 0.93, bottom=0.09 if grey else 0.2, hspace=0.12)
    for ax, P, tag in zip(axs, (PA, PB), ('a', 'b')):
        for k, lab, st, c in P:
            kw = dict(st)
            if not grey: kw['color'] = c
            ax.plot(-xc, dens(K[k]), label=lab, **kw)
        ax.set_xlim(41, 19.5); ax.set_ylim(0, None); ax.set_ylabel('Probability density (per degree)')
        ax.legend(frameon=False, loc='upper right', fontsize=6.3); ax.text(0.01, 0.95, f'({tag})', transform=ax.transAxes, fontweight='bold', va='top')
    axs[1].set_xlabel('Latitude on the 7th arc (degrees south)')
    if not grey:
        f.suptitle(f'Drift evidence alone favours about {md("head"):.0f} degrees south; the satellite and flight data favour about {md("core"):.0f} degrees south', x=0.01, ha='left', fontsize=8)
        f.text(0.01, 0.01, '\n'.join(textwrap.wrap(NOTE, 170)), fontsize=5.2, va='bottom')
    return f
for g in (False, True): finish(fig(g), 'drift-alone-latitude-density-2026-11-09', g, CAP)
print(CAP)
