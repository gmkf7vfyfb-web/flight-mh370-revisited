cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/searches_run_j"
cat > common_rows.py <<'EOF'
"""Shared row-building helpers for the run J searches: p-values against a null, labels, window membership, Kadri
labels, and the 'eta_needed' coupling column (preregistration.py sections 5-7)."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np, pandas as pd
import preregistration as R


def p_value(score, null):
    null = np.asarray(null, float); null = null[np.isfinite(null)]
    k = np.sum(null >= score)
    return (k + 1.0) / (len(null) + 1.0), len(null)


class Windows:
    def __init__(self):
        self.W = pd.read_csv(R.RD / "searches_run_j" / "prereg_windows.csv")

    def union(self, rx, branch):
        r = self.W[(self.W.receiver == rx) & (self.W.branch == branch) & (self.W.kind == "union")].iloc[0]
        return float(r.start_unix), float(r.end_unix)

    def membership(self, rx, t_unix, branch):
        g = self.W[(self.W.receiver == rx) & (self.W.branch == branch)]
        opts = [r.option for _, r in g[g.kind == "option99"].iterrows() if r.start_unix <= t_unix <= r.end_unix]
        if opts: return "+".join(opts)
        u = g[g.kind == "union"].iloc[0]
        return "union only" if u.start_unix <= t_unix <= u.end_unix else "outside"


def kadri_label(t_unix, table1=None):
    labs = []
    for name, (a, b) in R.BOXES.items():
        if R.hms_to_unix(a) <= t_unix <= R.hms_to_unix(b): labs.append(name)
    if table1 is not None:
        for _, r in table1.iterrows():
            if abs(t_unix - R.hms_to_unix(r.time_utc)) <= R.TABLE1_TOL_S: labs.append(f"Table 1 {r.time_utc} ({r.bearing_deg} deg)")
    return "; ".join(labs) if labs else "unlabelled"


def band_fraction(fc_lo, fc_hi, tau):
    """Energy fraction in [fc_lo, fc_hi] for an ESD flat to 1/tau and f^-2 above, normalised over 1-500 Hz
    (imos_stageB_map.band_fraction convention, band edges instead of a third octave)."""
    f = np.logspace(0, np.log10(500), 4000); fr = 1.0 / tau
    esd = np.where(f <= fr, 1.0, (f / fr) ** -2.0)
    tot = np.trapezoid(esd, f); m = (f >= fc_lo) & (f <= fc_hi)
    return float(np.trapezoid(esd[m], f[m]) / tot)


class Coupling:
    """eta_needed = observed excess 5-40 Hz band energy (Pa^2 s) / [E_med rho c/(2 pi) S_5-40(tau_med) 10^(-TL/10)]."""

    def __init__(self):
        en = json.loads((R.GEOM / "energy.json").read_text())["D0"]
        self.E = en["E_j_q"]["q50"]; self.tau = en["tau90_s_q"]["q50"]; self.lat_med = en["lat_q"]["q50"]
        self.Sb = band_fraction(*R.BAND_MAIN, self.tau)
        self.tl = {}
        if R.TL_GRID.exists():
            g = pd.read_csv(R.TL_GRID)
            g = g[(g.src_depth_m == 10.0) & (g.fc_hz >= 5.0) & (g.fc_hz <= 40.0)]
            g = g[np.isfinite(g.tl_db)]
            if len(g):
                src = g.drop_duplicates("source_id")[["source_id", "src_lat"]]
                for rx, gr in g.groupby("receiver"):
                    s = src[src.source_id.isin(gr.source_id)]
                    if not len(s): continue
                    sid = s.iloc[(s.src_lat - self.lat_med).abs().argmin()].source_id
                    v = gr[gr.source_id == sid].tl_db.values
                    self.tl[str(rx)] = (float(-10 * np.log10(np.mean(10 ** (-v / 10)))), sid, len(v))
        self.pred1 = self.E * R.RHO_C / (2 * np.pi) * self.Sb   # Pa^2 s at 1 m, eta = 1

    def eta_needed(self, rx, excess_pa2s):
        if rx not in self.tl or not np.isfinite(excess_pa2s) or excess_pa2s <= 0:
            return np.nan, "TL pending (grid)" if rx not in self.tl else "no excess"
        tl, sid, n = self.tl[rx]
        return float(excess_pa2s / (self.pred1 * 10 ** (-tl / 10))), f"TL {tl:.1f} dB ({sid}, {n} bands, pass A)"
EOF
cat > imos_search.py <<'EOF'
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
EOF
tail -n1 /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/null/*.log
grep -n "sens_db" ../imos_preregistration.py | head -3