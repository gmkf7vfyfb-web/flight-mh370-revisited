# Coverage chart: expected arrival windows (travel time only) against the data held, per station.
# Run inside the python kernel after apply_figure_style() (figure-style skill).
import textwrap
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
from matplotlib.lines import Line2D

W = pd.read_csv('windows/arrival_windows_grid.csv')
SU = pd.read_csv('windows/arrival_windows_station_union.csv')
cov = pd.read_csv('station-data/coverage_blocks.csv')
pk = pd.read_parquet('station-data/picks_all.parquet')
NAME = {'H01W': 'Cape Leeuwin hydrophones', 'H08S': 'Diego Garcia South hydrophones', 'H08N': 'Diego Garcia North hydrophones',
        'IMOS3315': 'Perth Canyon logger 3315', 'IMOS3376': 'Perth Canyon logger 3376', 'IMOS3250': 'Scott Reef logger 3250',
        'IMOS3274': 'Portland logger 3274', 'IMOS3275': 'Portland logger 3275',
        'SWAMS1': 'South-west Amsterdam mooring 1', 'SWAMS2': 'South-west Amsterdam mooring 2',
        'SWAMS3': 'South-west Amsterdam mooring 3', 'SSEIR': 'South-east Indian Ridge mooring',
        'MAD': 'Madagascar Basin mooring', 'NCRO': 'North Crozet mooring', 'WKER': 'West Kerguelen mooring',
        'NEAMS': 'North-east Amsterdam mooring'}
ORDER = list(NAME)
COL = {'raw waveform (duty-cycled)': '#2166ac', 'digitised envelope (Kadri 2024 Fig. 9)': '#e08214',
       'digitised spectrogram (Royer 2016)': '#7b3294', 'digitised trace (CMST 2014)': '#35978f'}
LAB = {'raw waveform (duty-cycled)': 'Raw recording (307 s in every 15 min)',
       'digitised envelope (Kadri 2024 Fig. 9)': 'Trace digitised from Kadri 2024 Fig. 9',
       'digitised spectrogram (Royer 2016)': 'Spectrogram digitised from Royer 2016',
       'digitised trace (CMST 2014)': 'Trace digitised from Curtin report 2014'}
OFF = {'raw waveform (duty-cycled)': 0.0, 'digitised envelope (Kadri 2024 Fig. 9)': 0.16,
       'digitised spectrogram (Royer 2016)': -0.16, 'digitised trace (CMST 2014)': 0.16}
m = lambda s: s / 60.0          # seconds after 00:00 -> minutes after 00:00
X0, X1 = 15, 105

fig = plt.figure(figsize=(7.4, 8.8))
ax = fig.add_axes([0.30, 0.33, 0.56, 0.61])
for i, st in enumerate(ORDER):
    y = len(ORDER) - 1 - i
    w = W[W.station == st]
    ub, bl = w[w.path_class != 'blocked'], w[w.path_class == 'blocked']
    if len(ub):
        e3 = ub.earliest_mixed300_s.min(); e = ub.earliest_s.min(); l = ub.latest_s.max()
        ax.add_patch(Rectangle((m(e3), y - 0.36), m(e) - m(e3), 0.72, fc='#e6e6e6', ec='none', zorder=1))
        ax.add_patch(Rectangle((m(e), y - 0.36), m(l) - m(e), 0.72, fc='#bdbdbd', ec='none', zorder=1))
    if len(bl):
        e = bl.earliest_s.min(); l = bl.latest_s.max()
        ax.add_patch(Rectangle((m(e), y - 0.36), m(l) - m(e), 0.72, fc='none', ec='#7f7f7f', hatch='////', lw=0.0, zorder=2))
    c = cov[cov.station == st]
    for f, g in c.groupby('form'):
        for r in g.itertuples():
            a, b = max(r.t_start_s, X0 * 60), min(r.t_end_s, X1 * 60)
            if b > a:
                ax.add_patch(Rectangle((m(a), y + OFF[f] - 0.09), m(b - a), 0.18, fc=COL[f], ec='none', zorder=3))
    p = pk[(pk.site_id == st) & (pk.dataset_id == 'royer2016_table5_picks')]
    ax.plot(m(p.t_s), np.full(len(p), y + 0.30), ls='none', marker='|', ms=5, mew=0.9, color='black', zorder=4)
    su = SU[(SU.station == st) & (SU.subset == 'unblocked grid points')]
    if st == 'NEAMS':
        txt = 'no data (lost)'
    elif st == 'H08N':
        txt = 'no data held'
    elif su.union_cov_any.iloc[0] == 0:
        txt = 'picks only'
    else:
        txt = f'{100 * su.union_cov_any.iloc[0]:.0f} %'
    ax.text(X1 + 1.5, y, txt, va='center', ha='left', fontsize=7, clip_on=False)
ax.text(X1 + 1.5, len(ORDER) - 0.35, 'Window\ncovered', va='bottom', ha='left', fontsize=7, clip_on=False)
ax.set_yticks(range(len(ORDER)))
ax.set_yticklabels([NAME[s] for s in ORDER][::-1])
ax.set_ylim(-0.7, len(ORDER) - 0.4)
ax.set_xlim(X0, X1)
xt = np.arange(15, 106, 15)
ax.set_xticks(xt)
ax.set_xticklabels([f'{int(t // 60):02d}:{int(t % 60):02d}' for t in xt])
ax.set_xlabel('Time on 8 March 2014 (UTC)')
ax.set_title('The data held covers all of the expected arrival time at three stations,\n'
             'most of it at Diego Garcia South, and about one third at the seabed loggers', loc='left')
hand = [Patch(fc='#bdbdbd', label='Expected arrival, clear or partly obstructed path'),
        Patch(fc='#e6e6e6', label='Earlier arrival if 300 km of the path is fast rock'),
        Patch(fc='none', ec='#7f7f7f', hatch='////', label='Expected arrival, path blocked by land or shallow water')]
hand += [Patch(fc=COL[f], label=LAB[f]) for f in COL]
hand += [Line2D([], [], ls='none', marker='|', ms=6, mew=1, color='black', label='Arrival time published by Royer 2016')]
fig.legend(handles=hand, loc='lower left', bbox_to_anchor=(0.02, 0.185), ncol=2, frameon=False, fontsize=7,
           handlelength=1.6, columnspacing=1.0)
foot = (
    'Notes. Expected arrival = impact time plus travel time only (no signal level is used). Impact positions: the 7th arc '
    '(sea-level arc at 00:19, file arcs-sea-level.csv) at every 1 degree from 20 S to 41 S, and 25 and 50 nautical miles '
    'to each side of the arc (110 positions). Impact time: 00:19:38 to 00:29:44 UTC. Travel time: shortest path on the '
    'WGS84 ellipsoid, made up to 5 % longer to allow for a path around obstacles, at a sound speed of 1.40 to 1.56 km/s. '
    'This speed range includes all sound speeds possible in sea water on these paths (1.44 to 1.558 km/s) and the speeds '
    'found from the arrivals Royer 2016 published (1.467 to 1.519 km/s, 105 paths). Light grey: a separate test in which '
    '300 km of the path next to the receiver goes through rock at up to 8.1 km/s. Blocked path: the line crosses land, or '
    'water shallower than the hydrophone or 200 m, more than 20 km from the receiver (GEBCO 2026 depths; the same rule as the '
    'project database, which it matches on 352 of 352 test paths). Diego Garcia North is blocked from 100 of 110 positions '
    'and is not used. Percent covered: part of the station window (clear or partly obstructed paths only) that has '
    'continuous data in any form. Recordings at Cape Leeuwin and Diego Garcia South are not held; only figures digitised '
    'from publications are held. Black ticks: arrival times in Royer 2016 Table 5, only for events Royer located. The Royer spectrogram is a reading of published colours; its colour scale saturates. '
    'The North-east Amsterdam mooring was deployed but its data was lost. Data source: project hydroacoustic database '
    '(hydro_data.sqlite) and the raw Curtin IMOS logger files.')
fig.text(0.02, 0.005, '\n'.join(textwrap.wrap(foot, 150)), fontsize=6, va='bottom', ha='left')
fig.savefig('windows/arrival-window-coverage.png', dpi=300)
fig.savefig('windows/arrival-window-coverage.pdf')
