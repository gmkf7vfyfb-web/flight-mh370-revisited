"""Run the pre-registered statistics (kadri-preregistration.md, artifact 0e9cad65) on all case x station records,
plus the reproduction match against Kadri's printed panels. Outputs in kadri/out/:
  window_statistics.csv, reproduction_match.csv, panels/<case>_<triad>.npz (arrays for the figures)."""
import sys, os, json
import numpy as np, pandas as pd
from obspy import read, read_inventory, UTCDateTime
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.chdir(os.path.join(HERE, "..", ".."))
from cases import CASES
import measure as M, digitise_panels as dpn

pr = pd.read_csv("kadri/out/predicted_windows.csv"); geo = pd.read_csv("kadri/out/geometry_paths.csv")
C0, SC = 1.482, 0.006; CLO, CHI = C0 - 3 * SC, C0 + 3 * SC
os.makedirs("kadri/out/panels", exist_ok=True)
dig = {k: dpn.digitise(k) for k in dpn.PANELS}
json.dump({k: dict(t0=v["t0"], frame=v["frame"], ticks_px=v["ticks_px"], pa_per_px=v["pa_per_px"], box_min=v["box_min"], ylim_pa=v["ylim_pa"],
                   s_per_px=v["s_per_px"]) for k, v in dig.items()}, open("kadri/out/digitised_panel_calibration.json", "w"), indent=1, default=float)

def load_proc(k, tri, causal=False):
    st = read(f"kadri/data/{k}_{tri}.mseed"); inv = read_inventory(f"kadri/data/resp_{k}_{tri}.xml")
    stm = st.copy(); stm.merge(method=1, fill_value=None)
    trs = M.process_K(st, inv, causal=causal)
    t0, X = M.common_grid(trs)
    n = len(next(iter(X.values()))); gap = np.zeros(n, bool)
    for tr in stm:
        if np.ma.isMaskedArray(tr.data):
            i0 = int(round((tr.stats.starttime - t0) * M.FS)); idx = np.where(np.ma.getmaskarray(tr.data))[0] + i0
            gap[idx[(idx >= 0) & (idx < n)]] = True
    pos, cen = M.enu(inv)
    return dict(t0=t0, X=X, gap=gap, pos=pos, cen=cen)

def parse_win(s):
    a, b = s.split(" - "); A = UTCDateTime(a.replace(" ", "T")); B = UTCDateTime(a[:11].replace(" ", "T") + b)
    return A, (B + 86400 if B < A else B)

def windows_for(k, tri):
    W = {}; row = pr[(pr.case == k) & (pr.station == tri)].iloc[0]; key = f"{k}_{tri}"
    if key in dig:
        d = dig[key]; t0 = UTCDateTime(d["t0"]); W["KB"] = (t0 + d["box_min"][0] * 60, t0 + d["box_min"][1] * 60); W["KP"] = (t0, t0 + 600)
    W["water"] = parse_win(row.water_window)
    if isinstance(row.hybrid_window, str):
        W["hybrid"] = parse_win(row.hybrid_window)
        g = geo[(geo.case == k) & (geo.station == tri) & (geo.position == "off")].iloc[0]; c = CASES[k]
        Ls = g.shallower_1000m_km; Ld = g.range_km - Ls; tt = UTCDateTime(c["off_t"].isoformat())
        W["hybrid_wide"] = (tt + c["off_t_lo"] + Ls / 8.0 + Ld / CHI, tt + c["off_t_hi"] + Ls / 1.5 + Ld / CLO + 60)
    return W

def reproduction(key, P, causal_P=None):
    d = dig[key]; t0 = UTCDateTime(d["t0"]) - P["t0"]; ncol = len(d["t_min"])
    ku = d["upper_pa"]; kl = d["lower_pa"]
    out = []
    for label, PP in [("zero-phase", P), ("causal", causal_P)]:
        if PP is None: continue
        for e, x in sorted(PP["X"].items()):
            best = None
            for lag_col in range(-115, 116):     # +/- ~90 s
                a = int((t0 + lag_col * d["s_per_px"]) * M.FS); b = a + int(600 * M.FS)
                if a < 0 or b > len(x): continue
                seg = x[a:b]; nb = len(seg) // ncol
                Y = seg[: nb * ncol].reshape(ncol, nb)
                ou = Y.max(1); ok = np.isfinite(ku)
                r = np.corrcoef(ou[ok], ku[ok])[0, 1]
                if best is None or r > best[0]: best = (r, lag_col, ou, Y.min(1))
            r, lag_col, ou, ol = best
            # at zero lag too
            a = int(t0 * M.FS); seg = x[a:a + int(600 * M.FS)]; nb = len(seg) // ncol
            if len(seg) >= nb * ncol and nb > 0:
                Y0 = seg[: nb * ncol].reshape(ncol, nb); ou0 = Y0.max(1); r0 = np.corrcoef(ou0[np.isfinite(ku)], ku[np.isfinite(ku)])[0, 1]
            else:
                ou0 = None; r0 = np.nan
            amp_db = 20 * np.log10(np.nanmedian(ou0 if ou0 is not None else ou) / np.nanmedian(ku))
            bx = d["box_min"]; inbox = (d["t_min"] >= bx[0]) & (d["t_min"] <= bx[1])
            out.append(dict(panel=key, filter=label, element=e, r_best=round(float(r), 3), lag_best_s=round(lag_col * d["s_per_px"], 1),
                            r_zero_lag=round(float(r0), 3), median_upper_ratio_dB=round(float(amp_db), 2),
                            kadri_box_peak_Pa=round(float(np.nanmax(np.maximum(ku[inbox], -kl[inbox]))), 3),
                            ours_box_peak_Pa=round(float(np.nanmax(np.maximum(ou0[inbox], -Y0.min(1)[inbox]))), 3) if ou0 is not None else np.nan,
                            kadri_median_upper_Pa=round(float(np.nanmedian(ku)), 3), ours_median_upper_Pa=round(float(np.nanmedian(ou0)), 3) if ou0 is not None else np.nan))
    return out

results, repro = [], []
for k, c in CASES.items():
    for tri in c["own_stations"]:
        P = load_proc(k, tri); X = P["X"]; T0 = P["t0"]; n = len(next(iter(X.values())))
        per_el = {}; RR = []
        for e, x in sorted(X.items()):
            tt, rr = M.rms1s(x); RR.append(rr); per_el[e] = rr
        R = np.mean(RR, 0)
        td, D = M.d1_stalta(np.sqrt(np.mean([x ** 2 for x in X.values()], 0)))
        gap_r = np.interp(tt, np.arange(n) / M.FS, P["gap"].astype(float)) > 0
        valid_r = (tt > 60) & (tt < tt[-1] - 60) & (~gap_r)
        W = windows_for(k, tri)
        excl = [(a - 300, b + 300) for nm, (a, b) in W.items() if nm != "KP"]
        exm = np.zeros(len(tt), bool)
        for ea, eb in excl: exm |= (tt >= ea - T0) & (tt <= eb - T0)
        bg_day = float(np.median(R[valid_r & ~exm]))
        # save arrays for figures
        save = dict(tt=tt.astype(np.float32), R=R.astype(np.float32), T0=str(T0), bg_day=bg_day)
        for e in per_el: save[f"rms_{e}"] = per_el[e].astype(np.float32)
        spans = [W["KP"]] if "KP" in W else []
        lo_ = min(a for nm, (a, b) in W.items()) - 300; hi_ = max(b for nm, (a, b) in W.items()) + 300
        a_ = max(0, int((lo_ - T0) * M.FS)); b_ = min(n, int((hi_ - T0) * M.FS))
        save["span_t0"] = float(a_ / M.FS)
        for e, x in X.items(): save[f"x_{e}"] = x[a_:b_].astype(np.float32)
        save["windows"] = json.dumps({nm: [str(a), str(b)] for nm, (a, b) in W.items()})
        for nm, (a, b) in W.items():
            if nm == "KP": continue
            L = b - a; ra = a - T0; rb = b - T0
            m_all = (tt >= ra) & (tt <= rb); m = m_all & valid_r
            row = dict(case=k, station=tri, window=nm, start=str(a)[:19], end=str(b)[:19], length_s=round(L, 1),
                       data_coverage=round(m.sum() / max(1, int(L / 0.5)), 3))
            if m.sum() < 0.5 * L / 0.5:
                row.update(note="window not covered by open data"); results.append(row); continue
            i = np.where(m)[0][np.argmax(R[m])]; S = R[i]; tpk = T0 + tt[i]
            md = (td >= ra) & (td <= rb); dmax = float(D[md].max())
            nullS, nullD, nullT = [], [], []
            for s0 in np.arange(tt[0] + 60, tt[-1] - 60 - L, L):
                A = T0 + s0; B = A + L
                if any((A < eb) and (B > ea) for ea, eb in excl): continue
                mm = (tt >= s0) & (tt <= s0 + L)
                if (~valid_r[mm]).mean() > 0.01: continue
                j = np.where(mm)[0][np.argmax(R[mm])]; nullS.append(R[j]); nullT.append(tt[j])
                q = (td >= s0) & (td <= s0 + L); nullD.append(D[q].max())
            nullS = np.array(nullS); nullD = np.array(nullD); nn = len(nullS)
            p = (1 + np.sum(nullS >= S)) / (nn + 1); pD = (1 + np.sum(nullD >= dmax)) / (nn + 1)
            if "KP" in W:
                pa, pb = W["KP"]; kb = W["KB"]
                mp = (tt >= pa - T0) & (tt <= pb - T0) & ~((tt >= kb[0] - T0) & (tt <= kb[1] - T0)) & valid_r
                bg_panel = float(np.median(R[mp])) if mp.sum() > 100 else np.nan
            else:
                bg_panel = np.nan
            b1 = M.bearing(X, P["pos"], int(tt[i] * M.FS)); b2 = M.bearing(X, P["pos"], int(tt[i] * M.FS), use_env=True)
            exp = float(pr[(pr.case == k) & (pr.station == tri)].expected_baz_deg.iloc[0])
            pk = {e: float(np.max(np.abs(x[int(ra * M.FS):int(rb * M.FS)]))) for e, x in X.items()}
            o = np.argsort(nullS)[::-1][:20]; bn = [M.bearing(X, P["pos"], int(nullT[j] * M.FS)) for j in o]
            row.update(peak_utc=str(tpk)[:21], S_triad_rms1s_Pa=round(float(S), 4),
                       peak_rms1s_Pa_by_element=";".join(f"{e}:{per_el[e][i]:.3f}" for e in sorted(per_el)),
                       peak_inst_Pa_by_element=";".join(f"{e}:{v:.3f}" for e, v in sorted(pk.items())),
                       bg_panel_Pa=round(bg_panel, 4) if np.isfinite(bg_panel) else np.nan, bg_day_Pa=round(bg_day, 4),
                       SNR_panel_dB=round(20 * np.log10(S / bg_panel), 2) if np.isfinite(bg_panel) else np.nan,
                       SNR_day_dB=round(20 * np.log10(S / bg_day), 2), n_null=nn, p_value=round(float(p), 4), p_floor=round(1 / (nn + 1), 4),
                       rank=int(1 + np.sum(nullS >= S)), D1_max=round(dmax, 2), D1_p=round(float(pD), 4),
                       baz_deg=round(b1["baz_deg"], 2), v_app_km_s=round(b1["v_app_km_s"], 3), closure_s=round(b1["closure_s"], 3), cc_min=round(b1["cc_min"], 2),
                       baz_env_deg=round(b2["baz_deg"], 2), v_app_env_km_s=round(b2["v_app_km_s"], 3),
                       expected_baz_deg=exp, baz_minus_expected_deg=round(M.angdiff(b1["baz_deg"], exp), 2),
                       null_top20_baz_deg=";".join(f"{x['baz_deg']:.0f}" for x in bn),
                       null_top20_vapp_median=round(float(np.median([x["v_app_km_s"] for x in bn])), 3))
            results.append(row)
            print(k, tri, nm, row["peak_utc"], row["S_triad_rms1s_Pa"], "p", row["p_value"], "SNRday", row["SNR_day_dB"], "baz", row["baz_deg"], flush=True)
        if f"{k}_{tri}" in dig:
            Pc = load_proc(k, tri, causal=True)
            repro += reproduction(f"{k}_{tri}", P, Pc)
            del Pc
        np.savez_compressed(f"kadri/out/panels/{k}_{tri}.npz", **save)
        del P, X
pd.DataFrame(results).to_csv("kadri/out/window_statistics.csv", index=False)
pd.DataFrame(repro).to_csv("kadri/out/reproduction_match.csv", index=False)
print("DONE")
