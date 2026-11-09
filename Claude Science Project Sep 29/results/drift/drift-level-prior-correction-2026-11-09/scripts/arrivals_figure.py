"""Figure: predicted date of discovery of the Mossel Bay engine cowling by release latitude, and the timing check of every find (9 Nov 2026).
Uses the tables of arrivals_timing.py (deskstar), validated against the module coefficients. Journal version (greyscale, no title or notes, 127 mm) and working version (colour, title, notes)."""
import os, textwrap, datetime as dt, numpy as np, pandas as pd, matplotlib.pyplot as plt
from matplotlib.lines import Line2D
exec(open('offline/arrivals_analysis.py').read().split('# ---------- 1.')[0])
OUT = 'figs-arr'; os.makedirs(OUT, exist_ok=True)
_s = open('offline/final_figures_ramp.py').read(); exec(_s[_s.index('def finish'):_s.index('plt.rcParams.update')])
plt.rcParams.update({'font.size': 7, 'axes.spines.top': False, 'axes.spines.right': False, 'font.family': 'DejaVu Sans', 'pdf.fonttype': 42})
def flatcurve(h, delay=60.0): g = pit_curve(h, delay) / NU; return g
def cum(g): c = np.cumsum(g); return c / c[-1]
BANDS = [(36, 40.3, '36 to 40'), (33, 36, '33 to 36'), (30, 33, '30 to 33'), (27, 30, '27 to 30'), (24, 27, '24 to 27')]
STY = [dict(color='0.0', ls='-', lw=1.0), dict(color='0.25', ls='--', lw=1.0), dict(color='0.4', ls='-.', lw=1.0), dict(color='0.5', ls=':', lw=1.3), dict(color='0.6', ls=(0, (6, 2, 1, 2, 1, 2)), lw=1.0)]
CLR = ['#4C72B0', '#55A868', '#C44E52', '#DD8452', '#8172B2']
DEC, MAR = day('2015-12-23') + 0.5, day('2016-03-22')
def tick_day(y, m): return day(f'{y}-{m:02d}-01')
TICKS = [(tick_day(2015, 7), 'Jul 2015'), (tick_day(2015, 10), 'Oct'), (tick_day(2016, 1), 'Jan 2016'), (tick_day(2016, 4), 'Apr'), (tick_day(2016, 7), 'Jul'), (tick_day(2016, 10), 'Oct'), (tick_day(2017, 1), 'Jan 2017')]
SHORT = {'reunion-right-flaperon': 'Réunion flaperon', 'mossel-bay-engine-cowling-roy': 'Mossel Bay engine cowling', 'paindane-right-flap-fairing': 'Paindane flap fairing', 'vilanculos-horizontal-stabilizer-panel': 'Vilanculos stabiliser panel',
         'mauritius-left-outboard-flap': 'Mauritius flap', 'rodrigues-door-closet-panel': 'Rodrigues cabin panel', 'chidenguele-right-fan-cowling': 'Chidenguele fan cowling', 'antsiraka-cabin-interior-panel': 'Antsiraka cabin panel',
         'pemba-right-outboard-flap': 'Pemba flap', 'linga-linga-vertical-stabilizer': 'Linga Linga stabiliser', 'nautilus-bay-right-aileron': 'Nautilus Bay aileron', 'mpame-right-flap-fairing': 'Mpame flap fairing'}
T5 = pd.read_csv('arr/tables/timing-pit-ramp-versus-flat-levels.csv').sort_values('find_day')
hc = (W[:, None] * Hb[:, mb, :]).sum(0)
pit_mb_flat = float(T5[T5.item == 'mossel-bay-engine-cowling-roy'].pit_flat_levels.iloc[0]); pit_mb_ramp = float(T5[T5.item == 'mossel-bay-engine-cowling-roy'].pit_ramp.iloc[0])
q50c = quant(flatcurve(hc), .5) if 'quant' in globals() else float(DAYS[np.searchsorted(cum(flatcurve(hc)), .5)])
CAP = ("(a) Predicted date of discovery of the Mossel Bay engine cowling, as a cumulative probability, for debris released from five ranges of latitude on the 7th arc "
       "(drift model, two ocean models with equal weight, equal detection level at all times). Heavy line: release latitudes weighted by the satellite communication and flight data. "
       "Vertical lines: 23 December 2015, the date of the photograph supplied to the Australian Transport Safety Bureau; 22 March 2016, the date given for the find. "
       "(b) For each find, the probability that the predicted date of discovery is not later than the observed date, with the satellite communication and flight data as weights for the release latitude. "
       "Filled circles: detection levels that rise with time (provisional); open circles: equal detection levels. Shaded: below 0.05 and above 0.95. A value near 0 means that the find is earlier than the model predicts; "
       f"the cowling gives {pit_mb_ramp:.2f} and {pit_mb_flat:.2f}. For finds near the end of the window (30 January 2017) the value is pushed towards 1.")
NOTE = ("Notes. Drift: GLORYS12V1 and GlobCurrent ocean models with ERA5 wind, 84 release points from 40.25 to 19.92 S, 16 ocean samples (32 south of 33.25 S), 6250 particles per class; kernel 50 km; discovery delay exponential, mean 60 days; "
        "arrival times from the stored beachings (83.4 and 81.4 million records), reproduced the module coefficients of the nine finds to a relative difference of 2e-8. Rising detection levels: medians 0.1, 0.5, 1, 1 (provisional). "
        "Release latitude weights: end of flight, Davey model with fuel, log-on event only. Mossel Bay date of find 22 Mar 2016 (ATSB); photograph 23 Dec 2015.")
def mk(grey):
    w = 127 / 25.4 if grey else 7.2
    f, (a, b) = plt.subplots(2, 1, figsize=(w, 6.0 if grey else 7.4), gridspec_kw=dict(height_ratios=[1.0, 1.05]))
    f.subplots_adjust(left=0.30 if grey else 0.27, right=0.97, top=0.955 if grey else 0.92, bottom=0.085 if grey else 0.2, hspace=0.62)
    hs = []
    kw0 = dict(color='0.0', lw=2.4, ls='-') if grey else dict(color='k', lw=2.4); a.plot(DAYS, cum(flatcurve(hc)), zorder=1, **kw0)
    for k, (lo, hi, lab) in enumerate(BANDS):
        sel = (LAT >= -hi) & (LAT < -lo); g = flatcurve(Hb[sel, mb, :].sum(0)); kw = STY[k] if grey else dict(color=CLR[k], lw=1.2, ls='-')
        a.plot(DAYS, cum(g), zorder=3, **kw); hs.append(Line2D([], [], label=lab, **kw))
    hs.append(Line2D([], [], label='Weighted by the satellite and flight data', **kw0))
    for d_, ls in ((DEC, '-'), (MAR, '--')): a.axvline(d_, color='0.5', lw=0.9, ls=ls)
    a.text(DEC - 4, 0.985, '23 Dec 2015', rotation=90, va='top', ha='right', fontsize=6, color='0.3'); a.text(MAR + 4, 0.985, '22 Mar 2016', rotation=90, va='top', ha='left', fontsize=6, color='0.3')
    a.set_xlim(tick_day(2015, 6), day('2017-01-30')); a.set_ylim(0, 1); a.set_xticks([t for t, _ in TICKS]); a.set_xticklabels([l for _, l in TICKS]); a.set_ylabel('Probability that the discovery\nis not later than the date')
    a.legend(handles=hs, title='Release latitude on the 7th arc, degrees south (ranges), and weighted mean', loc='upper center', bbox_to_anchor=(0.45, -0.17), ncol=3, fontsize=5.8, title_fontsize=6, frameon=False, handlelength=3.2, columnspacing=1.2)
    a.text(0.0, 1.02, '(a)', transform=a.transAxes, fontweight='bold', fontsize=8)
    y = np.arange(len(T5))[::-1]
    b.axvspan(0, 0.05, color='0.9' if grey else '#f2dede', lw=0); b.axvspan(0.95, 1, color='0.9' if grey else '#f2dede', lw=0)
    b.scatter(T5.pit_flat_levels, y, s=22, facecolors='white', edgecolors='0.0' if grey else '#4C72B0', linewidths=0.9, zorder=3)
    b.scatter(T5.pit_ramp, y, s=22, color='0.0' if grey else '#C44E52', zorder=4)
    for yy, p1, p2 in zip(y, T5.pit_ramp, T5.pit_flat_levels): b.plot([p1, p2], [yy, yy], color='0.6', lw=0.7, zorder=2)
    b.set_yticks(y); b.set_yticklabels([SHORT[i] for i in T5.item], fontsize=6.3); b.set_xlim(0, 1); b.set_xlabel('Probability that the predicted discovery date\nis not later than the observed date')
    b.legend(handles=[Line2D([], [], marker='o', ls='', color='0.0' if grey else '#C44E52', label='Detection levels rising with time'), Line2D([], [], marker='o', ls='', mfc='white', mec='0.0' if grey else '#4C72B0', label='Equal detection levels')], loc='upper right', fontsize=5.8, frameon=True, framealpha=1, edgecolor='0.8')
    b.text(0.0, 1.03, '(b)', transform=b.transAxes, fontweight='bold', fontsize=8)
    if not grey:
        f.suptitle(f'Cowling found at day 655; model median day {q50c:.0f}; probability of a find this early {pit_mb_flat:.2f}', x=0.01, ha='left', fontsize=7.5)
        f.text(0.01, 0.01, '\n'.join(textwrap.wrap(NOTE, 150)), fontsize=5.2, va='bottom')
    return f
for g in (False, True): finish(mk(g), 'arrival-timing-mossel-bay-and-all-finds-2026-11-09', g, CAP)
print('written', sorted(os.listdir(OUT))); print(CAP)
