# Published-bearing candidate pages (CL 00:49:58 at 260.4 deg + DGS 01:10:15), same layout as candidate_views_cl_dg_final.pdf v4.
# Runs inside the mh370-hydro kernel after the Monte Carlo cells (uses D, PRp, PRk, FT, ser, CAL, CA, N, ID, G, c6, dg, E, K17, ...).
SUPT = (f"Published-bearing case: Cape Leeuwin 00:49:58 (260.4° published) with Diego Garcia South 01:10:15. "
        f"Source {-D.lat.median():.1f}° S {D.lon.median():.1f}° E, impact {hms(np.percentile(D.t0, 5))}–{hms(np.percentile(D.t0, 95))} UTC")
DGNOTE = (f" Bearing from Diego Garcia South to this source: {np.percentile(az_dg, 2.5):.1f}-{np.percentile(az_dg, 97.5):.1f}° (95 %); for the corrected-bearing source {np.percentile(az_dg_c, 2.5):.1f}-{np.percentile(az_dg_c, 97.5):.1f}°. "
          "Preliminary, not checked: the other thread's digitisation of Kadri (2019) Fig. 4 (in progress, not yet reported) lists for 01:09:34-01:10:18 a dominant bearing of 311° (the shot-train direction of Kadri 2019 Fig. 1) "
          "and a strongest non-shot bearing of 39-42°; neither is near 150°. This page will be updated when that work is reported.")
rows = []
with PdfPages(pdfout) as pdf:
    # ---- page 1: summary table
    fig = plt.figure(figsize=(11, 8.5)); ax = fig.add_axes([0.02, 0.2, 0.96, 0.62]); ax.axis('off')
    cols = ['Site', 'Path', 'Expected arrival,\nphysical bounds (95 %)', 'Expected arrival,\nKadri speeds (95 %)', 'Recorded data\nin window', 'Window p\n(combined)', 'Best look\n(p)',
            'Events noted earlier: time, position in expected range (physical / Kadri)']
    tab = []
    for s_ in N.STATIONS:
        w = win(s_); a = PRp[s_]
        path = 'blocked (all draws)' if (a.pc == 'blocked').all() else ', '.join(sorted(a.pc.dropna().unique()))
        if s_ in N.LOGGERS:
            t0 = recs[s_]; m = (t0 + 307 >= w['a0']) & (t0 <= w['b0'])
            cov = sum(max(0, min(w['b0'], x + 307) - max(w['a0'], x)) for x in t0[m]) / (w['b0'] - w['a0'])
            s = ser[(ser.station == s_) & (ser.t_s >= w['a']) & (ser.t_s <= w['b'])]
            pw = N.WindowCal(s_, cal=CAL[s_]).p(s.F.max(), len(s)) if len(s) else np.nan
            bl = f"{hms(s.loc[s.p_F.idxmin(), 't_s'])} ({s.p_F.min():.3f})" if len(s) else '—'
            dat = f"{100 * cov:.0f} %"
            ev = FT[(FT.site == s_) & (FT.speeds == 'physical bounds')]
            evs = '; '.join(f"{r.event_utc[:8]}: {r.percentile:.0f} / {FT[(FT.site == s_) & (FT.event_utc == r.event_utc) & (FT.speeds != 'physical bounds')].percentile.iloc[0]:.0f} %" + (' (inside)' if r.inside_95 else '') for r in ev.itertuples())
        else:
            pw = np.nan; bl = 'defining event'; dat = 'Kadri trace'; evs = 'defines the candidate'
        rows.append(dict(site=s_, path=path, phys_2p5=hms(w['a0']), phys_97p5=hms(w['b0']), kadri_2p5=hms(w['ac']), kadri_97p5=hms(w['bc']), data_cover=dat, window_p=pw, best_look=bl, noted=evs))
        tab.append([NAMES[s_].split(' (')[0], path, f"{hms(w['a0'])}–{hms(w['b0'])}", f"{hms(w['ac'])}–{hms(w['bc'])}", dat, '—' if not np.isfinite(pw) else f'{pw:.3f}', bl, "\n".join(textwrap.wrap(evs, 62))])
    t = ax.table(cellText=tab, colLabels=cols, loc='upper center', cellLoc='left'); t.auto_set_font_size(False); t.set_fontsize(6.3)
    for (rr, cc), cell in t.get_celld().items():
        cell.set_width([0.11, 0.11, 0.11, 0.11, 0.065, 0.06, 0.10, 0.335][cc]); cell.set_height(0.10 if rr == 0 else 0.115)
    fig.text(0.02, 0.94, 'Published-bearing case: Cape Leeuwin 00:49:58 and Diego Garcia South 01:10:15 as one impact near 35.9° S, 92.7° E', fontsize=10)
    fig.text(0.02, 0.86, "\n".join(textwrap.wrap(CAND, 200)), fontsize=6.6)
    foot(fig, "Position in expected range: percentile of the noted event time within the predicted arrival distribution (0 % = earlier than every draw, 100 % = later than every draw); 'inside' = within the 95 % range. "
         "Events noted earlier come from the Cape Leeuwin / Diego Garcia South candidate questions of 7 Nov 2026 (Scott Reef low-frequency band 00:45-00:48; Portland 1 just before 01:01, about 01:15, about 01:33; Portland 2 01:07 and about 01:21; "
         "Perth Canyon 1 correlation 00:35-00:36), the Scott Reef picks in Kadri, Crivelli and Parsons (2017) ATSB report Fig. 6 (logger time corrected by -15.1 s), and the best combined looks of earlier candidate windows. "
         "The published bearing is the sensitivity case; with the corrected bearing (246.8°, primary under ruling B1) the source lies 122-202 NM from the arc and needs at least 849 kt mean ground speed in every draw. "
         "Recorded data in window: share of the physical 95 % range covered by logger records. Window p uses the widened window on each site page and is not corrected for the number of candidates and sites examined. "
         "Cape Leeuwin and Diego Garcia South: digitised Kadri (2024) Figure 9 envelopes only." + DGNOTE)
    pdf.savefig(fig); plt.close(fig)
    # ---- page 2: timeline
    fig, ax = plt.subplots(figsize=(11, 8.5)); fig.subplots_adjust(left=0.2, right=0.97, top=0.9, bottom=0.27)
    order = ['H01W', 'H08S', 'IMOS3376', 'IMOS3315', 'IMOS3274', 'IMOS3275', 'IMOS3250']
    for i, s_ in enumerate(order):
        y = len(order) - i; w = win(s_)
        if s_ in N.LOGGERS:
            for x in recs[s_]:
                if 30 * 60 <= x <= 95 * 60: ax.plot([x, x + 307], [y - 0.32, y - 0.32], color='#111827', lw=2.2, solid_capstyle='butt')
        ax.plot([w['a0'], w['b0']], [y, y], color='#9ca3af', lw=9, solid_capstyle='butt', alpha=0.8)
        ax.plot([w['ac'], w['bc']], [y + 0.18, y + 0.18], color='#1d4ed8', lw=1.6, solid_capstyle='butt')
        if (PRp[s_].pc == 'blocked').all(): ax.text(w['b0'] + 40, y, 'path blocked by seabed (all draws)', fontsize=6.5, va='center', color='#6b7280')
        for r in FT[(FT.site == s_) & (FT.speeds == 'physical bounds')].itertuples():
            tt = ts_(r.event_utc); ax.plot(tt, y, marker='v', color='#ea580c', ms=6, zorder=5); ax.text(tt, y + 0.3, r.event_utc[:8], fontsize=5.5, ha='center', color='#9a3412')
    ax.set_yticks(range(len(order), 0, -1)); ax.set_yticklabels([NAMES[s] for s in order]); ax.set_ylim(0.4, len(order) + 0.8)
    tk = np.arange(30 * 60, 95 * 60 + 1, 300); ax.set_xticks(tk); ax.set_xticklabels([hms(x)[:5] for x in tk]); ax.set_xlim(30 * 60, 95 * 60); ax.set_xlabel('Time (UTC, 8 March 2014)')
    ax.set_title('Expected arrivals for the published-bearing source against the recorded data and the events noted earlier', loc='left', fontsize=10)
    ax.text(0.0, -0.12, 'Wide grey bar: expected arrival, physical bounds (95 %). Thin blue bar: Kadri speeds (95 %).\nBlack segments under each row: IMOS logger records. Orange triangles: events noted earlier (label only).', transform=ax.transAxes, fontsize=6.5, va='top')
    foot(fig, CAND + " Cape Leeuwin and Diego Garcia South rows show the arrival spans that define the candidate. " + FOOT)
    pdf.savefig(fig); plt.close(fig)
    # ---- primary-site pages
    for s_, tc, tpk, lab in [('H01W', c6.t, c6.t_peak, 'Kadri Table 1 onset 00:49:58'), ('H08S', dg.t, dg.t_peak, 'envelope peak 01:10:15 (our detector)')]:
        tA, tB = tc - 480, tc + 480; s0 = ser[(ser.station == s_) & (ser.t_s >= tA) & (ser.t_s <= tB)]
        fig = plt.figure(figsize=(11, 8.5)); gs = fig.add_gridspec(3, 1, height_ratios=[1.4, 1, 1], hspace=0.2, left=0.08, right=0.92, top=0.86, bottom=0.22); a3 = [fig.add_subplot(gs[k]) for k in range(3)]
        a3[0].plot(s0.t_s, s0.E, color='#1d4ed8'); a3[0].set_ylabel('Envelope level\n(digitised, dB)', fontsize=7)
        a3[1].plot(s0.t_s, -np.log10(s0.p_E), color='#6b7280'); a3[1].set_ylabel('Band energy\n(−log10 p)', fontsize=7)
        a3[2].plot(s0.t_s, -np.log10(s0.p_F), color='#111827'); a3[2].set_ylabel('Combined\n(band energy +\npersistence)', fontsize=7)
        ta, tb = (c6.t_a, c6.t_b) if s_ == 'H01W' else (dg.t_a, dg.t_b)
        for a_ in a3:
            a_.axvspan(ta, tb, color='#fecaca', alpha=0.6, zorder=0); a_.axvline(tc, color='#b91c1c', lw=0.9); a_.axvline(tpk, color='#7f1d1d', lw=0.9, ls='--'); a_.set_xlim(tA, tB)
        for a_ in a3[1:]: a_.axhline(-np.log10(0.05), color='#9ca3af', ls='--', lw=0.6); a_.set_ylim(bottom=0)
        extra = ''
        if s_ == 'H01W':
            yl = a3[0].get_ylim()
            for r in K17.itertuples():
                x = r.minute_after_0000 * 60 + 30
                if tA <= x <= tB:
                    a3[0].plot(x, yl[1] * 0.97, marker='v', color='#ea580c', ms=5); a3[0].text(x, yl[1] * 0.84, f"{r.bearing_raw_deg:.0f}°", fontsize=5.5, ha='center', color='#9a3412')
            extra = (" Orange triangles: Cape Leeuwin detections in Kadri, Crivelli and Parsons (2017) ATSB report Fig. 3 (minute resolution, drawn at the minute centre) with their published bearings (label only). "
                     "Our check does not reconcile this list with the 2024 Table 1 except at 00:50; cause not known; it can be our error.")
        else:
            extra = DGNOTE
        tk = np.arange(np.ceil(tA / 60) * 60, tB, 60)
        for a_ in a3: a_.set_xticks(tk); a_.set_xticklabels([])
        a3[-1].set_xticklabels([hms(x) for x in tk], fontsize=6); a3[-1].set_xlabel(f'Time at {NAMES[s_]} (UTC, 8 March 2014)')
        fig.suptitle(SUPT, x=0.08, ha='left', fontsize=9)
        ep = E[(E.station == s_) & (np.abs(E.t - tc) < 1)].envelope_p.iloc[0]
        a3[0].set_title(f"Primary site, {NAMES[s_]}. Solid red line: {lab}. Dashed line: envelope peak {hms(tpk)}. Red band: arrival span used for timing, {hms(ta)}–{hms(tb)}.\n"
                        f"Envelope evidence p = {ep:.3g} (smallest within ±15 s; within-trace null, not corrected for multiple looks).", loc='left', fontsize=7)
        foot(fig, "Primary-site page. Data: digitised envelope of Kadri (2024) Figure 9 (no raw waveform is held for 8 March 2014). Band energy: level over the local background, scored against the rest of the same trace. Combined: band energy and persistence (Fisher). "
             "Arrival span: onset minus 20 s to the envelope peak (project convention of 7 Nov 2026). The p floor is about 1/355 at Cape Leeuwin and 1/234 at Diego Garcia South. Grey dashed line: p = 0.05." + extra + " " + CAND)
        pdf.savefig(fig); plt.close(fig)
    # ---- other-site pages
    for s_ in ['IMOS3376', 'IMOS3274', 'IMOS3315', 'IMOS3275', 'IMOS3250']:
        w = win(s_); tmin, tmax = w['a'], w['b']; s = ser[(ser.station == s_) & (ser.t_s >= tmin) & (ser.t_s <= tmax)]
        a = PRp[s_]; blocked = (a.pc == 'blocked').all()
        fig = plt.figure(figsize=(11, 8.5)); gs = fig.add_gridspec(5, 1, height_ratios=[0.9, 1.6, 1, 1, 1], hspace=0.25, left=0.08, right=0.9, top=0.86, bottom=0.25)
        axs = [fig.add_subplot(gs[k]) for k in range(5)]; ax0 = axs[0]; axs = axs[1:]
        LS = lat_spans(s_)
        for key, L, a_, b_ in LS: ax0.plot([a_, b_], [L, L], color='#9ca3af' if key == 'p' else '#1d4ed8', lw=4.5 if key == 'p' else 1.3, solid_capstyle='butt')
        Ls = sorted(set(x[1] for x in LS)); ax0.set_ylim(max(Ls) + 0.2, min(Ls) - 0.2); ax0.set_yticks(Ls[::2]); ax0.tick_params(axis='y', labelsize=6); ax0.set_ylabel('Arc latitude\n(° S)', fontsize=7)
        ax0.text(1.005, 0.95, 'wide grey: physical\nbounds\nthin blue: Kadri', transform=ax0.transAxes, fontsize=6, va='top')
        X, nn, t0 = CA[s_]; im = None
        for j in np.where((t0 + 307 >= tmin) & (t0 <= tmax))[0]:
            x = X[j].astype(float); x -= x.mean(); f, tt, P = signal.spectrogram(x, fs=ID.FS, nperseg=512, noverlap=384)
            mm = (f >= 2) & (f <= 100); Pd = 10 * np.log10(P[mm] / np.median(P[mm], axis=1, keepdims=True))
            im = axs[0].pcolormesh(t0[j] + tt, f[mm], Pd, vmin=-3, vmax=15, cmap='magma', shading='auto', rasterized=True)
        axs[0].set_ylabel('Frequency (Hz)'); axs[0].set_ylim(2, 100)
        if im is not None:
            p0 = axs[0].get_position(); cax = fig.add_axes([0.915, p0.y0, 0.008, p0.height]); cb = fig.colorbar(im, cax=cax); cb.set_label('dB over record median', fontsize=6); cb.ax.tick_params(labelsize=6)
        else:
            axs[0].text(0.5, 0.5, 'No logger record in this window', transform=axs[0].transAxes, ha='center', va='center', color='#6b7280')
        tw = axs[1].twinx()
        for tr, eb in raw_band_db(s_, tmin, tmax): tw.plot(tr, eb, color='#16a34a', lw=0.5, alpha=0.8)
        tw.set_ylabel('Raw 8-60 Hz\npower, 1 s (dB)', fontsize=6, color='#16a34a'); tw.tick_params(labelsize=6, colors='#16a34a')
        for k, (col, lab) in enumerate((('p_d0', 'Band energy'), ('p_cimp', 'Impact-pattern\ncorrelation'), ('p_F', 'Combined'))):
            for rec, g in s.groupby('rec'): axs[k + 1].plot(g.t_s, -np.log10(g[col]), color=['#6b7280', '#ea580c', '#111827'][k], lw=1, zorder=3)
            axs[k + 1].set_ylabel(lab + '\n(−log10 p)', fontsize=7)
        axs[1].set_zorder(tw.get_zorder() + 1); axs[1].patch.set_visible(False)
        evv = [r for r in FT[(FT.site == s_) & (FT.speeds == 'physical bounds')].itertuples() if tmin <= ts_(r.event_utc) <= tmax]
        for a_ in [ax0] + axs:
            a_.set_xlim(tmin, tmax); a_.axvspan(w['a0'], w['b0'], color='#d1d5db', alpha=0.45, zorder=0)
            [a_.axvline(w[q], color='#1d4ed8', ls='--', lw=0.9) for q in ('ac', 'bc')]
            for r in evv: a_.axvline(ts_(r.event_utc), color='#ea580c', lw=0.8, ls=':')
        for r in evv: ax0.text(ts_(r.event_utc), ax0.get_ylim()[1], r.event_utc[:8], fontsize=5.5, color='#9a3412', ha='center', va='bottom')
        for a_ in axs[1:]: a_.axhline(-np.log10(0.05), color='#9ca3af', ls='--', lw=0.6); a_.set_ylim(bottom=0)
        span = tmax - tmin; step = 60 if span < 1200 else 300; tk = np.arange(np.ceil(tmin / step) * step, tmax, step)
        for a_ in [ax0] + axs: a_.set_xticks(tk); a_.set_xticklabels([])
        axs[-1].set_xticklabels([hms(x) for x in tk], fontsize=6); axs[-1].set_xlabel('Time at this site (UTC, 8 March 2014)')
        pw = N.WindowCal(s_, cal=CAL[s_]).p(s.F.max(), len(s)) if len(s) else np.nan
        fig.suptitle(SUPT, x=0.08, ha='left', fontsize=9)
        ev_in = [f"{r.event_utc[:8]} ({r.percentile:.0f} %)" for r in evv]
        ax0.set_title(f"{NAMES[s_]}. Expected arrival: physical bounds {hms(w['a0'])}–{hms(w['b0'])} (grey shading, wide grey bars); Kadri 1.45–1.57 km/s {hms(w['ac'])}–{hms(w['bc'])} (blue dashed lines, thin blue bars).\n"
                      f"Window shown {hms(tmin)}–{hms(tmax)} (20 % margin). Path: {'blocked by seabed in all draws' if blocked else ', '.join(sorted(a.pc.dropna().unique()))}; {len(s)} looks; window p (combined) = {('%.3g' % pw) if np.isfinite(pw) else 'no data'}."
                      + (f" Events noted earlier in view (orange dotted, position in expected range): {', '.join(ev_in)}." if ev_in else ""), loc='left', fontsize=7, pad=12)
        foot(fig, FOOT + " " + CAND); pdf.savefig(fig); plt.close(fig)
pd.DataFrame(rows).to_csv('cv/published_bearing_sites.csv', index=False); FT.to_csv('cv/published_bearing_noted_event_fit.csv', index=False)
