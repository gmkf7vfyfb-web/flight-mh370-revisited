"""Figures for the AADC moorings note. Run inside the python kernel after loading the figure-style skill
(apply_figure_style, panel_letter come from that kernel plugin). Reads out/*.csv written by aadc_geometry.py."""
import os, sys, numpy as np, pandas as pd, matplotlib.pyplot as plt, matplotlib.dates as mdates
sys.path.append(os.getcwd()); import aadc_geometry as A
apply_figure_style()
geo = pd.read_csv('out/aadc-arc-path-geometry.csv'); acc = pd.read_csv('out/aadc-receiver-depth-screening.csv')
pa = pd.read_csv('out/aadc-predicted-arrivals-known-events.csv'); pa['t'] = pd.to_datetime(pa.pred_arrival_rule_utc)
roy = pd.read_csv('royer_events.csv'); ice = roy.event_class == 'icequake'
NAMES = {'Casey2014': 'Casey mooring 2014', 'Kerguelen2014': 'S Kerguelen Plateau mooring 2014', 'H01W1': 'Cape Leeuwin hydrophone (H01W)'}
COL = {'Casey2014': '#f2b705', 'Kerguelen2014': '#c2185b'}
def footnote(fig, plain, tech, y):
    fig.text(0.01, y, "Plain: " + plain + "\nTechnical: " + tech, ha='left', va='top', fontsize=6, wrap=True, color='#333333')
m = (A.alat <= -20) & (A.alat >= -40)
z = np.where(A.ealt < 0, -A.ealt, np.nan)
rise_lo, rise_hi = int(acc[acc.receiver == 'Kerguelen2014'].rise_depth_m.min()), int(acc[acc.receiver == 'Kerguelen2014'].rise_depth_m.max())
d_lo, d_hi = int(acc[acc.receiver == 'Kerguelen2014'].rise_dist_to_rx_km.min()), int(acc[acc.receiver == 'Kerguelen2014'].rise_dist_to_rx_km.max())
dmin, dmax = geo[geo.receiver.isin(COL)].dist_km.min(), geo[geo.receiver.isin(COL)].dist_km.max()

# ---- figure 1: map ----
fig, ax = plt.subplots(figsize=(7.2, 5.6))
pc = ax.pcolormesh(A.elon[::2], A.elat[::2], z[::2, ::2], cmap='Blues', vmin=0, vmax=6000, shading='auto', rasterized=True)
ax.contourf(A.elon[::2], A.elat[::2], (A.ealt[::2, ::2] >= 0).astype(float), levels=[0.5, 1.5], colors=['#bdb5a6'])
ax.contour(A.elon[::2], A.elat[::2], -A.ealt[::2, ::2], levels=[1500], colors=['#5d4037'], linewidths=0.5)
cb = fig.colorbar(pc, ax=ax, shrink=0.7, pad=0.02); cb.set_label('Seafloor depth (m)')
ax.plot(A.alon[m], A.alat[m], color='k', lw=2.2, label='Final satellite arc (7th arc), 20-40 S')
for la in [-20, -30, -40]:
    lo = float(np.interp(la, A.alat, A.alon))
    for r in COL:
        rl, ro, _, _ = A.RECEIVERS[r]; p = np.array(A.G.npts(lo, la, ro, rl, 200))
        ax.plot(p[:, 0], p[:, 1], color='k', lw=2.0, alpha=0.5); ax.plot(p[:, 0], p[:, 1], color=COL[r], lw=1.1)
for r in NAMES:
    rl, ro, _, _ = A.RECEIVERS[r]
    ax.plot(ro, rl, marker='^' if r.startswith('H') else 'o', ms=8, mfc=COL.get(r, '#444444'), mec='k', ls='none', label=NAMES[r], zorder=5)
ax.plot(roy.lon_deg[ice], roy.lat_deg[ice], 'D', ms=4, mfc='white', mec='#6a1b9a', ls='none', label='Royer 2016 icequakes (8 Mar)', zorder=4)
ax.plot(roy.lon_deg[~ice], roy.lat_deg[~ice], 'x', ms=4, color='#6a1b9a', ls='none', label='Royer 2016 other located events', zorder=4)
ax.axhline(-50, color='#333333', ls='--', lw=0.7); ax.text(61, -49.4, '50 S: assumed Polar Front (screening)', fontsize=6, color='#222222')
ax.plot([], [], color='#5d4037', lw=0.8, label='1500 m depth contour')
ax.set_xlim(60, 130); ax.set_ylim(-70, -15); ax.set_xlabel('Longitude (deg E)'); ax.set_ylabel('Latitude (deg N)')
ax.set_title(f'Paths from the arc to the two Antarctic moorings are {dmin:,.0f} to {dmax:,.0f} km long', loc='left')
ax.legend(loc='upper left', fontsize=6, frameon=True, framealpha=0.85); ax.set_aspect(1 / np.cos(np.radians(42)))
footnote(fig,
 f"The map shows the two Australian Antarctic moorings that recorded on 8 March 2014. The lines show the shortest paths from the arc at 20, 30 and 40 S.\nThe paths are {dmin:,.0f} to {dmax:,.0f} km long. All paths to the S Kerguelen mooring cross seafloor at {rise_lo:,} to {rise_hi:,} m depth, which is shallower than that mooring.\nThe recordings exist, but you must ask by email to get them. We did not get them.",
 "Great-circle paths (WGS84). Bathymetry ETOPO1 (ERDDAP etopo180, 3 arc-min stride). Arc: ATSB 7th arc at FL400. Moorings: Miller et al. 2018 Table 3\n(Casey2014 63.7955 S 111.7871 E, 2700 m; Kerguelen2014 62.3801 S 81.7968 E, 2000 m). Royer 2016 Table 4 events (n = 20). Polar Front fixed at 50 S for\nscreening only. No waveform data analysed (AADC download is email-gated). Exploratory.", y=-0.01)
fig.savefig('out/aadc-moorings-map.png', dpi=200, bbox_inches='tight'); plt.close(fig)

# ---- figure 2: path sections ----
shade = {-20: '#9e9e9e', -30: '#000000', -40: '#6d6d6d'}; ls = {-20: ':', -30: '-', -40: '--'}
fig, axs = plt.subplots(2, 1, figsize=(7.2, 6.0))
for ax, r, letter in zip(axs, ['Kerguelen2014', 'Casey2014'], 'ab'):
    rz = A.RECEIVERS[r][2]
    for la in [-20, -30, -40]:
        lo = float(np.interp(la, A.alat, A.alon))
        mm, (s, plat, plon, zz, axd, axc) = A.path_metrics(la, lo, r); x = mm['dist_km'] - s
        ax.plot(x, -np.minimum(zz, 0), color=shade[la], ls=ls[la], lw=1.0, label=f'Seafloor, path from {abs(la)} S')
        if la == -30: ax.plot(x, axd, color='#1b9e77', lw=1.4, label='Sound-speed minimum depth, path from 30 S')
    ax.plot(0, rz, marker='o', ms=8, mfc=COL[r], mec='k', ls='none', label=f'Hydrophone depth ({int(rz)} m)', zorder=5)
    if r == 'Kerguelen2014':
        ax.axhline(rz, color=COL[r], lw=0.7, ls='-.')
        ax.annotate(f'Rise at {rise_lo:,}-{rise_hi:,} m,\n{d_lo}-{d_hi} km before the mooring', xy=(205, 1480), xytext=(900, 600), fontsize=6, arrowprops=dict(arrowstyle='-', lw=0.6))
    ax.set_xlim(5200, -50); ax.set_ylim(6500, 0); ax.set_ylabel('Depth (m)')
    ax.set_title('S Kerguelen Plateau mooring: every path rises above the hydrophone depth before it arrives' if r == 'Kerguelen2014'
                 else 'Casey mooring: the hydrophone is far below the polar sound-speed minimum', loc='left')
    panel_letter(ax, letter)
axs[1].set_xlabel('Distance from mooring (km)'); axs[0].legend(loc='lower left', fontsize=6, frameon=False, ncol=2)
fig.tight_layout()
footnote(fig,
 f"Each panel shows the seafloor depth along the paths from the arc to one mooring. The green line shows the depth of slowest sound. North of about 50 S that depth is about 1,000 m. Near Antarctica it is near the surface. The S Kerguelen hydrophone is at 2,000 m, but each path first crosses a rise at {rise_lo:,} to {rise_hi:,} m. Sound from the arc must touch the seafloor there to reach it. The Casey hydrophone is at 2,700 m. Only steeper sound rays reach that depth. Two of nine paths (from 35 and 37.5 S, not drawn) cross a rise shallower than 2,700 m.",
 "Seafloor: ETOPO1 (3 arc-min, nearest node) along WGS84 great circles from the ATSB 7th arc (FL400) at 20, 30, 40 S. Sound speed: WOA23 decav 1.00 deg, Jan-Mar (season 13), Mackenzie (1981); minimum-c depth from nearest WOA cell every 50 km. Screening with a conserved turning speed (range-independent); receiver depths from Miller et al. 2018. Exploratory; no waveform data.", y=-0.01)
fig.savefig('out/aadc-path-sections.png', dpi=200, bbox_inches='tight'); plt.close(fig)

# ---- figure 3: timeline ----
g2 = geo[geo.receiver.isin(COL)]; pct = (g2.t_axis_speed_s / g2.t_rule_s - 1) * 100
T0 = pd.Timestamp('2014-03-07 23:00'); T1 = pd.Timestamp('2014-03-08 04:00')
fig, ax = plt.subplots(figsize=(7.2, 3.4)); rows = {'Kerguelen2014': 1, 'Casey2014': 0}; neq = {}
for r, y in rows.items():
    g = geo[geo.receiver == r]
    a0 = pd.Timestamp('2014-03-08 00:15') + pd.to_timedelta(g.t_rule_s.min(), unit='s')
    a1 = pd.Timestamp('2014-03-08 01:05') + pd.to_timedelta(g.t_rule_s.max(), unit='s')
    a2 = pd.Timestamp('2014-03-08 02:00') + pd.to_timedelta(g.t_rule_s.max(), unit='s')
    ax.barh(y, a1 - a0, left=a0, height=0.5, color=COL[r], alpha=0.55, edgecolor='k', lw=0.5)
    ax.barh(y, a2 - a1, left=a1, height=0.5, color=COL[r], alpha=0.2, edgecolor='k', lw=0.5, hatch='///')
    ax.text(a0, y + 0.3, f'impact arrivals if impact 00:15-01:05 (core) / to 02:00 (tail): {a0:%H:%M}-{a1:%H:%M} / to {a2:%H:%M}', fontsize=6, va='bottom')
    e = pa[(pa.receiver == r) & (pa.t >= T0) & (pa.t <= T1)]
    ri = e[e.source.str.startswith('Royer') & (e.source_class == 'icequake')]; ro_ = e[e.source.str.startswith('Royer') & (e.source_class != 'icequake')]
    q = e[~e.source.str.startswith('Royer')]; neq[r] = len(q)
    ax.plot(ri.t, [y - 0.05] * len(ri), 'D', ms=4, mfc='white', mec='#6a1b9a', ls='none', label='Royer 2016 icequake' if y == 1 else None)
    ax.plot(ro_.t, [y - 0.05] * len(ro_), 'x', ms=4, color='#6a1b9a', ls='none', label='Royer 2016 other event' if y == 1 else None)
    ax.plot(q.t, [y - 0.18] * len(q), '|', ms=8, color='#333333', ls='none', label='Catalogued earthquake' if y == 1 else None)
for h in pd.date_range(T0, T1, freq='h'): ax.axvline(h, color='#bbbbbb', lw=0.5, zorder=0)
ax.set_yticks([0, 1]); ax.set_yticklabels(['Casey mooring 2014', 'S Kerguelen Plateau\nmooring 2014'])
ax.set_ylim(-0.6, 1.75); ax.set_xlim(T0, T1); ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.set_xlabel('Predicted arrival time, 7-8 March 2014 (UTC)')
ax.set_title('Impact arrivals at the moorings would fall in the 00:00-03:00 UTC files, mixed with ice events', loc='left')
ax.legend(loc='lower right', fontsize=6, frameon=False, ncol=3, bbox_to_anchor=(1, -0.02))
footnote(fig,
 "The bars show when sound from an impact on the arc (20 to 40 S) would arrive at each mooring. The marks show when known events would arrive. The grey lines show the 1-hour file limits. The files exist for all these hours, but you must ask by email to get them. We did not get them, so we made no detection.",
 f"Rule: great-circle distance / 1.48 km/s, no seismic leg for earthquakes. Path-mean WOA23 minimum-speed times are {pct.min():.1f}-{pct.max():.1f}% later (in CSV). Impact times 00:15-01:05 UTC core, tail to 02:00. Royer 2016 Table 4 (n = 20, all shown). Catalogued earthquakes in span: {neq['Kerguelen2014']} (S Kerguelen), {neq['Casey2014']} (Casey); merged ISC/USGS/EMSC/GEOFON/GCMT list. Exploratory; arrivals are predictions only.", y=-0.03)
fig.savefig('out/aadc-predicted-arrival-timeline.png', dpi=200, bbox_inches='tight'); plt.close(fig)
print('figures written', dmin, dmax, rise_lo, rise_hi, d_lo, d_hi, pct.min(), pct.max(), neq)
