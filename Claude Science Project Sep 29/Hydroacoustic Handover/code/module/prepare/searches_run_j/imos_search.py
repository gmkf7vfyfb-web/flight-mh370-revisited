"""BLOCK 5 (i): the pre-registered searches on the IMOS 8 March 2014 records that overlap the run J search windows
(preregistration.py sections 1-7). Loggers 3315, 3376, 3274, 3275 and 3250 (declared no-information row, still run).
Usage: python imos_search.py <out_dir>   (needs null/null_<logger>.npz from null_worker.py)
Outputs: imos_windows.csv (every scored window), imos_candidates.csv (p < 0.3 rows), imos_summary.json."""
from __future__ import annotations
import json, re, sys, time
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent)); sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import preregistration as R, detectors as D, common_rows as CR
import imos_noise as N, imos_preregistration as P


def subsec(path):
    t = open(path, "rb").read()[-1000:].decode("latin1")
    return int(re.search(r"First Data-\S+ \S+ - (\d+)", t).group(1)) / 65536


def main(out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True); t0 = time.time()
    T = np.load(R.TEMPLATES); bank, _ = D.bank_env(T, R.IMOS_BANK_RANGES, 100)
    rec = pd.read_csv(R.MODULE / "data" / "imos" / "recordings.csv"); rec["logger"] = rec.logger.astype(str)
    meta = P.parse_meta()
    cal = pd.read_csv(R.RD / "imos1d" / "calibration_gain.csv"); cal["logger"] = cal.logger.astype(str)
    Wn = CR.Windows(); cp = CR.Coupling(); table1 = pd.read_csv(R.MODULE / "data" / "kadri_fig9_digitised" / "kadri-table1-transients.csv")
    nulls = {lg: np.load(out.parent / "null" / f"null_{R.NULL_STANDIN[lg]}.npz") for lg in R.IMOS}
    rows, summ = [], {}
    for lg in R.IMOS:
        s0, s1 = Wn.union(lg, "SOFAR"); a0, a1 = Wn.union(lg, "AGW"); lo, hi = min(s0, a0) - 60, max(s1, a1) + 60
        m = meta[lg]
        g = cal[cal.logger == lg]; G = 10 * np.log10(np.mean([10 ** (g[g.band == b].gain_db.iloc[0] / 10) for b in ("5-10", "10-20", "20-40")]))
        div = 10 ** ((G + m["sens_db"]) / 10)       # V^2 -> uPa^2
        nrec, nwin = 0, 0
        for _, r in rec[rec.logger == lg].iterrows():
            f = R.IMOS_ROOT / r.file
            fs, first, n, _ = P.header(f)
            tstart = first.timestamp() + subsec(f) - P.clock_err(m, first)       # convention A
            tend = tstart + n / fs
            if tend < lo or tstart > hi: continue
            x500 = N.decimate(N.read_volts(f))
            st, lev = D.imos_stats(x500, bank)
            sc = D.scores_all(st, len(x500) / R.FS_D)
            e540 = 10 ** (lev[(5.0, 40.0)] / 10)        # V^2 s per second
            nrec += 1
            for key, (ws, s, tm) in sc.items():
                null = nulls[lg][key]
                for w0, sv, tv in zip(ws, s, tm):
                    p, nn = CR.p_value(sv, null); tu = tstart + tv
                    i0, i1 = int(w0), int(w0 + R.WINDOW_S)
                    seg = e540[i0:i1]; base = np.median(e540[max(i0 - 60, 0):i0]) if i0 >= 10 else np.median(e540)
                    excess_pa2s = float(np.sum(np.maximum(seg - base, 0.0))) / div * 1e-12
                    eta, tlnote = cp.eta_needed(lg, excess_pa2s)
                    band = key.split("_", 1)[1] if key.startswith("BE") else "5-40"
                    rows.append(dict(receiver=lg, file=r.file, record_start_utc=R.unix_to_hms(tstart), window_start_utc=R.unix_to_hms(tstart + w0),
                                     time_utc=R.unix_to_hms(tu), t_unix=tu, detector=key.split("_")[0], band_hz=band, statistic=sv, p=p, n_null=nn,
                                     label=R.label_for_p(p), in_window_sofar=Wn.membership(lg, tu, "SOFAR"), in_window_agw=Wn.membership(lg, tu, "AGW"),
                                     kadri_label=CR.kadri_label(tu, table1 if lg in ("3315", "3376") else None),
                                     excess_5_40_pa2s=excess_pa2s, eta_needed=eta, tl_note=tlnote,
                                     band_note="below hardware corner (8 Hz)" if band == "2-5" else "", null_logger=R.NULL_STANDIN[lg],
                                     caveats=R.CAVEATS, provenance="IMOS raw"))
                    nwin += 1
        summ[lg] = dict(n_records=nrec, n_windows_scored=nwin, window_sofar=[R.unix_to_hms(s0), R.unix_to_hms(s1)], window_agw=[R.unix_to_hms(a0), R.unix_to_hms(a1)],
                        null_logger=R.NULL_STANDIN[lg], n_null_windows=int(len(nulls[lg]["M1b"])), gain_5_40_db=G, sens_db=m["sens_db"])
        print(lg, nrec, nwin, round(time.time() - t0), flush=True)
    W = pd.DataFrame(rows); W.to_csv(out / "imos_windows.csv", index=False)
    C = W[W.p < R.SCREEN_P].sort_values("p"); C.to_csv(out / "imos_candidates.csv", index=False)
    exp = {}
    for (lg, det, band), g in W.groupby(["receiver", "detector", "band_hz"]):
        exp[f"{lg}/{det}/{band}"] = dict(n_windows=int(len(g)), **{f"obs_{nm}": int((g.p < thr).sum()) for thr, nm in R.LEVELS}, **{f"exp_{nm}": float(len(g) * thr) for thr, nm in R.LEVELS})
    summ["expected_by_chance"] = exp
    summ["coupling"] = dict(E_med_j=cp.E, tau_med_s=cp.tau, S_5_40=cp.Sb, tl=cp.tl, lat_med=cp.lat_med)
    summ["wall_s"] = round(time.time() - t0, 1)
    (out / "imos_summary.json").write_text(json.dumps(summ, indent=1, default=str))
    print("done", len(W), len(C), round(time.time() - t0))


if __name__ == "__main__":
    main(sys.argv[1])
