"""Per-candidate views at every other site with an unblocked path from the implied source.
Window at each site: earliest arrival at 1.56 km/s to latest at 1.40 km/s with 5 % path detour, over all impact
points and times consistent with the candidate (impact 00:19:38-00:55:00), then widened by 20 % of its length at each end."""
import sys, os, textwrap, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy import signal
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.join(os.getcwd(), 'ns'))
import network14 as N, imosdet as ID
VMIN, VMAX, DET = N.V_MIN_S, N.V_MAX_S, N.DET_S; EXT = 0.20
VMINc, VMAXc, DETc = N.V_MIN, N.V_MAX, N.DET
NAMES = {'H01W': 'Cape Leeuwin', 'H08S': 'Diego Garcia South', 'IMOS3250': 'Scott Reef (IMOS 3250)', 'IMOS3274': 'Portland 1 (IMOS 3274)',
         'IMOS3275': 'Portland 2 (IMOS 3275)', 'IMOS3315': 'Perth Canyon 2 (IMOS 3315)', 'IMOS3376': 'Perth Canyon 1 (IMOS 3376)'}
ser = pd.read_csv('run14v3_eqclean/station_point_series.csv'); G = pd.read_csv('grid_ext_paths_wide.csv').set_index(['station', 'point_id'])
E = pd.read_csv('cand_all.csv'); CACHE = N.CACHE
ok = E[E.n_points > 0].head(10).reset_index(drop=True); miss = E[(E.n_points == 0) & (E.index <= E[E.n_points > 0].index[min(9, (E.n_points > 0).sum() - 1)])]
def cache(lg):
    z = np.load(f'{CACHE}/{lg.lower()}_mh370_day.npz', allow_pickle=True); return z['x'], z['n'], z['t_start_s']
CA = {lg: cache(lg) for lg in N.LOGGERS}
rows = []
def site_windows(r):
    pts = r.points.split(';'); st0 = r.station; out = {}
    g0 = G.loc[st0].loc[pts]
    lo_imp = np.maximum(r.t - g0.dist_km.values * (1 + DET) / VMIN, N.H2[0]); hi_imp = np.minimum(r.t - g0.dist_km.values / VMAX, N.H2[1])
    lo_c = np.maximum(r.t - g0.dist_km.values * (1 + DETc) / VMINc, N.H2[0]); hi_c = np.minimum(r.t - g0.dist_km.values / VMAXc, N.H2[1])
    for st in N.STATIONS:
        if st == st0: continue
        g = G.loc[st].loc[pts]; open_ = (g.path_class.values != 'blocked')
        if not open_.any(): out[st] = None; continue
        d = g.dist_km.values
        a = (lo_imp + d / VMAX)[open_].min(); b = (hi_imp + d * (1 + DET) / VMIN)[open_].max()
        ac = (lo_c + d / VMAXc)[open_ & (hi_c >= lo_c)]; bc = (hi_c + d * (1 + DETc) / VMINc)[open_ & (hi_c >= lo_c)]
        L = b - a; out[st] = dict(a=a - EXT * L, b=b + EXT * L, a0=a, b0=b, ac=ac.min() if len(ac) else np.nan, bc=bc.max() if len(bc) else np.nan,
                                  classes=', '.join(sorted(set(g.path_class.values[open_]))), n_open=int(open_.sum()), n_pts=len(pts))
    return out
def foot(fig, txt):
    fig.text(0.02, 0.01, "\n".join(textwrap.wrap(txt, 190)), fontsize=5.3, va='bottom', color='#374151')
FOOT = ("Window: earliest arrival at 1.56 km/s to latest at 1.40 km/s with 5 % path detour, over every impact point and time consistent with the candidate "
        "(corrected bearing within its tolerance when one is published; impact 00:19:38 to 00:55:00 UTC; 7th arc 15° S to 43° S within 150 NM, 20° S to 41° S when there is no bearing), then widened by 20 % of its length at each end (outer dotted lines mark the unwidened span). "
        "Shaded: span for the primary sound speed 1.465 to 1.520 km/s with 2 % detour. Sites shown: every site with an unblocked path (GEBCO 2026 screen) from at least one consistent point. "
        "IMOS loggers record 307 s in every 15 min; grey gaps have no data. Spectrogram: 2 s segments, power over the median of the same record at each frequency (dB). "
        "Lower panels: chance that noise alone scores this high at one 5 s look (−log10), from 14 days of noise (1 to 15 March 2014) or, for 3275 and 3315, 8 March records outside 00:15 to 02:00; "
        "band energy 8 to 40 Hz in 30 s; impact-pattern correlation from the whitened waveform; combined = Fisher sum of all five scores. Noise calibration with USGS M≥3.5 earthquake arrival windows and faulty records removed (14-19 % of records). "
        "Window p: chance that noise alone gives a maximum this high over the looks in the window (calibrated for the look count). Cape Leeuwin and Diego Garcia South: only the digitised Kadri (2024) Figure 9 envelopes (no waveform).")
with PdfPages(os.environ.get('PDFOUT', 'candidate_views_cl_dg.pdf')) as pdf:
    # summary page
    fig = plt.figure(figsize=(11, 8.5)); ax = fig.add_axes([0.02, 0.12, 0.96, 0.8]); ax.axis('off')
    cols = ['Rank', 'Station', 'Arrival', 'Bearing, published / corrected', 'Found by', 'Envelope p', 'Arc latitude (° S)', 'Implied impact', 'Steep dive', 'Catalogue label (4 Nov)']
    tab = [[i + 1, NAMES[r.station].split(' (')[0].replace('Diego Garcia South', 'Diego Garcia S.'), r.t_utc[:8], (f'{r.bearing_published:.1f}° / {r.bearing:.1f}° (±{r.tol:.1f}°)') if np.isfinite(r.bearing) else 'none', r.source, '%.3f' % r.envelope_p,
            (r.arc_lat_S_on_arc + (' (outside 20-41)' if r.outside_ruled_arc_range is True or r.outside_ruled_arc_range == 'True' else '')), f'{r.t_imp_first[:8]}–{r.t_imp_last[:8]}', 'yes' if r.steep_dive_fits else 'no', (r.screening_known_label if isinstance(r.screening_known_label, str) else '')[:70]] for i, r in ok.iterrows()]
    t = ax.table(cellText=tab, colLabels=cols, loc='upper center', cellLoc='left'); t.auto_set_font_size(False); t.set_fontsize(6.5); t.scale(1, 1.5)
    for (rr, cc), cell in t.get_celld().items():
        cell.set_width([0.035,0.085,0.06,0.155,0.085,0.05,0.135,0.105,0.05,0.24][cc])
    ax.set_title('Ten strongest Cape Leeuwin and Diego Garcia South candidates with an implied source on the 7th arc', loc='left', fontsize=10)
    mtxt = '; '.join(f'{r.t_utc[:8]} (published {r.bearing_published:.1f}°, corrected {r.bearing:.1f}°; envelope p {r.envelope_p:.3f}): {r.exclusion_reason}' for r in miss.itertuples())
    foot(fig, "Ranking: envelope evidence at the station itself (band energy and persistence on the digitised Kadri (2024) Figure 9 envelope, smallest p within ±15 s; within-trace null). "
         "This is weak evidence: the p floor is about 1/355 and the 19 Kadri times are not corrected for multiple looks. Sources: Kadri Table 1; ours = combined-detector best looks on the envelopes and 4 Nov screening picks (merged within 30 s of a Kadri time, or 45 s of each other). "
         f"Bearings: Kadri's published bearings corrected for the H01W array-position bias (calibration from 144 earthquakes, ruling B1; corrections -4.4 to -13.8°); tolerance ±1.645σ with σ = calibrated sector error and a 1.2° weak-signal term. Stronger candidates not shown: {mtxt}. Implied impact: arc points 15-43° S within the bearing tolerance (no bearing: 20-41° S), sound speed 1.40 to 1.56 km/s, 5 % detour, "
         "inside 00:19:38 to 00:55:00. Steep dive: impact 00:19:38 to 00:29:44 within 25 NM. Catalogue labels are associations below 0.95 probability (label only, not removed).")
    pdf.savefig(fig); plt.close(fig)
    for i, r in ok.iterrows():
        W = site_windows(r)
        for st, w in W.items():
            if w is None:
                rows.append(dict(rank=i + 1, cand=r.t_utc, cand_station=r.station, site=st, status='all paths blocked')); continue
            if st in ('H01W', 'H08S'):
                s = ser[(ser.station == st) & (ser.t_s >= w['a']) & (ser.t_s <= w['b'])]
            else:
                s = ser[(ser.station == st) & (ser.t_s >= w['a']) & (ser.t_s <= w['b'])]
            wc_n = len(s)
            if st in N.LOGGERS:
                import pickle, __main__, imos_calib as IC; __main__.TailMap = IC.TailMap
                if 'CAL' not in globals(): globals()['CAL'] = pickle.load(open('imos_calib_eqclean.pkl', 'rb'))
                pw = N.WindowCal(st, cal=CAL[st]).p(s.F.max(), wc_n) if wc_n else np.nan
            else:
                pw = N.WindowCal(st, series=ser[ser.station == st]).p(s.F.max(), wc_n) if wc_n else np.nan
            rows.append(dict(rank=i + 1, cand=r.t_utc, cand_station=r.station, site=st, status='data' if wc_n else 'no data in window',
                             win_start=N.hms(w['a']), win_end=N.hms(w['b']), path_classes=w['classes'], n_looks=wc_n, window_p=pw,
                             best_look_utc=N.hms(s.loc[s.p_F.idxmin(), 't_s']) if wc_n else '', best_look_pF=s.p_F.min() if wc_n else np.nan,
                             best_corr_p=(s.p_cimp.min() if wc_n and 'p_cimp' in s and s.p_cimp.notna().any() else np.nan)))
            if not wc_n: continue
            fig = plt.figure(figsize=(11, 8.5))
            gs = fig.add_gridspec(4, 1, height_ratios=[1.6, 1, 1, 1], hspace=0.25, left=0.08, right=0.92, top=0.9, bottom=0.2)
            axs = [fig.add_subplot(gs[k]) for k in range(4)]
            tmin, tmax = w['a'], w['b']
            if st in N.LOGGERS:
                X, nn, t0 = CA[st]
                for j in np.where((t0 + 307 >= tmin) & (t0 <= tmax))[0]:
                    x = X[j].astype(float); x -= x.mean()
                    f, tt, P = signal.spectrogram(x, fs=ID.FS, nperseg=512, noverlap=384)
                    m = (f >= 2) & (f <= 100); Pd = 10 * np.log10(P[m] / np.median(P[m], axis=1, keepdims=True))
                    im = axs[0].pcolormesh(t0[j] + tt, f[m], Pd, vmin=-3, vmax=15, cmap='magma', shading='auto', rasterized=True)
                axs[0].set_ylabel('Frequency (Hz)'); axs[0].set_ylim(2, 100)
                p0 = axs[0].get_position(); cax = fig.add_axes([0.94, p0.y0, 0.008, p0.height]); cb = fig.colorbar(im, cax=cax); cb.set_label('dB over record median', fontsize=6); cb.ax.tick_params(labelsize=6)
                for k, (col, lab) in enumerate((('p_d0', 'Band energy'), ('p_cimp', 'Impact-pattern\ncorrelation'), ('p_F', 'Combined'))):
                    for rec, g in s.groupby('rec'):
                        axs[k + 1].plot(g.t_s, -np.log10(g[col]), color=['#6b7280', '#ea580c', '#111827'][k], lw=1)
                    axs[k + 1].set_ylabel(lab + '\n(−log10 p)', fontsize=7)
            else:
                axs[0].plot(s.t_s, s.E, color='#1d4ed8'); axs[0].set_ylabel('Envelope level\n(digitised, dB)', fontsize=7)
                axs[1].plot(s.t_s, -np.log10(s.p_E), color='#6b7280'); axs[1].set_ylabel('Band energy\n(−log10 p)', fontsize=7)
                axs[2].text(0.5, 0.5, 'Not available: no waveform (envelope only)', transform=axs[2].transAxes, ha='center', va='center', fontsize=8, color='#6b7280')
                axs[2].set_ylabel('Impact-pattern\ncorrelation', fontsize=7)
                axs[3].plot(s.t_s, -np.log10(s.p_F), color='#111827'); axs[3].set_ylabel('Combined\n(band energy +\npersistence)', fontsize=7)
            for a_ in axs:
                a_.set_xlim(tmin, tmax)
                if np.isfinite(w['ac']): a_.axvspan(w['ac'], w['bc'], color='#bfdbfe', alpha=0.35, zorder=0)
                a_.axvline(w['a0'], color='k', ls=':', lw=0.7); a_.axvline(w['b0'], color='k', ls=':', lw=0.7)
            for a_ in axs[1:]:
                a_.axhline(-np.log10(0.05), color='#9ca3af', ls='--', lw=0.6); a_.set_ylim(bottom=0)
            span = tmax - tmin; step = 60 if span < 1200 else (300 if span < 5400 else 900)
            tk = np.arange(np.ceil(tmin / step) * step, tmax, step)
            for a_ in axs: a_.set_xticks(tk); a_.set_xticklabels([])
            axs[-1].set_xticklabels([N.hms(x)[:5 if step >= 300 else 8] for x in tk], fontsize=6); axs[-1].set_xlabel('Time at this site (UTC, 8 March 2014)')
            src = f"{r.source}; bearing {r.bearing:.1f}° corrected, {r.bearing_published:.1f}° published" if np.isfinite(r.bearing) else f"{r.source}; no bearing"
            fig.suptitle(f"Candidate {i + 1}: {NAMES[r.station]} {r.t_utc[:8]} ({src}). Implied impact {r.t_imp_first[:8]}–{r.t_imp_last[:8]} UTC, " + (f"arc {r.arc_lat_S_on_arc}° S" if np.isfinite(r.bearing) else "any arc latitude (no bearing)"),
                         x=0.08, ha='left', fontsize=9)
            axs[0].set_title(f"{NAMES[st]}: window {N.hms(tmin)[:8]}–{N.hms(tmax)[:8]}; paths {w['classes']} ({w['n_open']} of {w['n_pts']} points); "
                             f"{wc_n} looks; window p (combined) = {pw:.3g}", loc='left', fontsize=8)
            foot(fig, FOOT); pdf.savefig(fig); plt.close(fig)
R = pd.DataFrame(rows); R.to_csv(os.environ.get('SITESOUT', 'candidate_views_sites.csv'), index=False)
pd.set_option('display.width', 250); print(R.drop(columns=['cand_station']).to_string())
