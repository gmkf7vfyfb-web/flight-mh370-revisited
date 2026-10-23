cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/searches_run_j"
python - <<'EOF'
s=open('common_rows.py').read()
s=s.replace('''        if rx not in self.tl or not np.isfinite(excess_pa2s) or excess_pa2s <= 0:
            return np.nan, "TL pending (grid)" if rx not in self.tl else "no excess"
        tl, sid, n = self.tl[rx]''','''        if rx not in self.tl:
            return np.nan, "TL pending (grid)"
        tl, sid, n = self.tl[rx]
        if tl > 300:
            return np.inf, f"blocked path (pass A TL {tl:.0f} dB, {sid})"
        if not np.isfinite(excess_pa2s) or excess_pa2s <= 0:
            return np.nan, "no excess"''')
open('common_rows.py','w').write(s)
EOF
cat > panel_search.py <<'EOF'
"""BLOCK 5 (ii): the pre-registered searches on the DIGITISED Kadri (2024) Fig. 9 panels: H01W a, b, c and H08S d, e
(decimated plots; preregistration.py sections 1-7). Null A = emulated IMOS 3376 background (null/null_3376.npz,
panel_* keys); null B = 200 block-permutation surrogates per panel. H08S: the (c1)+(c2) suppressed residual is
searched with M1b_res and Z_res beside the raw-panel detectors.
Usage: python panel_search.py <out_dir>
Outputs: panel_windows.csv, panel_candidates.csv, panel_series.npz, h08s_suppression.csv, panel_summary.json."""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np, pandas as pd
from scipy import signal
sys.path.insert(0, str(Path(__file__).resolve().parent))
import preregistration as R, detectors as D, common_rows as CR

KD = R.MODULE / "data" / "kadri_fig9_digitised"
FS40 = 40


def load_panel(pnl, fs=R.PANEL_FS):
    st = "H01W" if pnl in "abc" else "H08S"
    tr = pd.read_csv(KD / f"kadri-2024-figure9-panel-{pnl}-{st}.csv")
    t, p = tr.plotted_time_s.values, tr.pressure_pa.values
    tg = np.arange(0, 600, 1 / fs)
    return tg, np.interp(tg, t, p).astype(float), R.hms_to_unix(R.PANEL_T0[pnl] + ".0"), len(t)


# ---- H08S suppression (weak_signal/run_h08s.py rules, copied) ---------------------------------------------------
def env40(p, s=0.25):
    k = int(s * FS40); return np.convolve(p ** 2, np.ones(k) / k, "same")


def shots40(tg, p):
    e5 = env40(p, 0.5)
    pk, _ = signal.find_peaks(e5, distance=int(3 * FS40), prominence=2 * np.median(e5))
    t = tg[pk]
    return t[(t - 3 >= tg[0]) & (t + 6 <= tg[-1])]


def subtract40(tg, e, ts, pre=3.0, post=6.0, nb=6):
    w = np.arange(-int(pre * FS40), int(post * FS40))
    idx = np.searchsorted(tg, ts)
    W = np.array([e[i + w] for i in idx]); pk = W[:, int(pre * FS40) - 2: int(pre * FS40) + 3].max(1)
    Wn = W / pk[:, None]
    res = e.copy()
    for k, i in enumerate(idx):
        nbh = [j for j in range(max(k - nb, 0), min(k + nb + 1, len(idx))) if j != k]
        res[i + w] = e[i + w] - np.median(Wn[nbh], axis=0) * pk[k]
    return res


def cadence(ts):
    d = np.diff(ts); per = float(np.median(d[(d >= 9) & (d <= 11)]))
    ph = np.angle(np.mean(np.exp(2j * np.pi * ts / per))) * per / (2 * np.pi)
    return per, ph


def gate_mask(tg, per, ph, half=1.5):
    dist = np.abs(((tg - ph) / per - np.round((tg - ph) / per)) * per)
    return dist > half


def residual_stats(tg40, res, gm, shotfree_ref, bank):
    """Residual envelope at 10 Hz (gated samples set to the gap median) -> M1b_res and Z_res."""
    r = np.maximum(res, 0.0)
    med = np.median(shotfree_ref); mad = 1.4826 * np.median(np.abs(shotfree_ref - med))
    r = np.where(gm, r, med)
    r10 = r[: (len(r) // 4) * 4].reshape(-1, 4).mean(1)
    t10 = np.arange(len(r10)) / 10.0 + 0.2
    out = {}
    out["M1b_res"] = D.m1b_env(r10, bank)
    z = (np.convolve(r10, np.ones(30) / 30, "same") - med) / max(mad, 1e-12)
    out["Z_res"] = (t10, z)
    return out


def surrogate_null(x, fs, stat_fn, rng, n=R.N_SURROGATE, block_s=R.SURR_BLOCK_S):
    nb = int(block_s * fs); m = len(x) // nb
    X = x[: m * nb].reshape(m, nb)
    acc = {}
    for _ in range(n):
        xs = X[rng.permutation(m)].ravel()
        st = stat_fn(xs)
        for k, (t, s) in st.items():
            ws, sc, tm = D.window_scores(t, s, len(xs) / fs)
            acc.setdefault(k, []).append(sc)
    return {k: np.concatenate(v) for k, v in acc.items()}


def main(out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True); t0 = time.time()
    T = np.load(R.TEMPLATES)
    bank = {st: D.bank_env(T, (R.PANEL_BANK_RANGE[st],), 100)[0] for st in R.IMS}
    nullA = np.load(out.parent / "null" / "null_3376.npz")
    Wn = CR.Windows(); cp = CR.Coupling(); table1 = pd.read_csv(KD / "kadri-table1-transients.csv")
    rows, series, supp, summ = [], {}, [], {}
    for ip, pnl in enumerate("abcde"):
        st = "H01W" if pnl in "abc" else "H08S"
        tg, x, utc0, nv = load_panel(pnl)
        stats, lev = D.panel_stats(x, bank[st])
        rng = np.random.default_rng(R.SEED + ip)
        nullB = surrogate_null(x, R.PANEL_FS, lambda xs: D.panel_stats(xs, bank[st])[0], rng)
        e_pa2 = 10 ** (lev[(5.0, 9.0)] / 10) + 10 ** (lev[(2.0, 5.0)] / 10)     # Pa^2 s per second, 2-9 Hz (plot band)
        extra = {}
        if st == "H08S":
            tg40, x40, _, _ = load_panel(pnl, FS40)
            e = env40(x40); ts = shots40(tg40, x40); res = subtract40(tg40, e, ts); per, ph = cadence(ts); gm = gate_mask(tg40, per, ph)
            shotfree = np.ones(len(tg40), bool)
            for t in ts: shotfree &= np.abs(tg40 - t) > 1.5
            rs = residual_stats(tg40, res, gm, e[shotfree], bank[st])
            extra = rs
            rp = np.maximum(res, 0)
            supp.append(dict(panel=pnl, n_shots=len(ts), cadence_s=per, gated_fraction=float(1 - gm.mean()),
                             c1_reduction_db=10 * np.log10(rp.mean() / e.mean()), c1c2_reduction_db=10 * np.log10(rp[gm].mean() / e.mean())))
            # surrogate null B for the residual statistics: block permutation of the 40 Hz residual (gated)
            rng2 = np.random.default_rng(R.SEED + 100 + ip)
            nb = int(R.SURR_BLOCK_S * FS40); m = len(res) // nb
            RB = res[: m * nb].reshape(m, nb); GB = gm[: m * nb].reshape(m, nb)
            accB = {}
            for _ in range(R.N_SURROGATE):
                pm = rng2.permutation(m)
                r2 = residual_stats(tg40, RB[pm].ravel(), GB[pm].ravel(), e[shotfree], bank[st])
                for k, (t, s) in r2.items():
                    accB.setdefault(k, []).append(D.window_scores(t, s, m * nb / FS40)[1])
            for k, v in accB.items(): nullB[k] = np.concatenate(v)
            series[f"{pnl}_res40"] = res; series[f"{pnl}_gm40"] = gm; series[f"{pnl}_shots"] = ts
        allst = dict(stats); allst.update(extra)
        for key, (t, s) in allst.items():
            series[f"{pnl}_{key}_t"] = t; series[f"{pnl}_{key}_s"] = s
            ws, sc, tm = D.window_scores(t, s, 600.0)
            nA = nullA[f"panel_{st}_{key}"] if f"panel_{st}_{key}" in nullA else (nullA[f"panel_{st}_M1b"] if key == "M1b_res" else None)
            for w0, sv, tv in zip(ws, sc, tm):
                pA, nnA = CR.p_value(sv, nA) if nA is not None else (np.nan, 0)
                pB, nnB = CR.p_value(sv, nullB[key])
                p_lab = pB if key == "Z_res" else pA
                tu = utc0 + tv
                i0, i1 = int(w0), int(w0 + R.WINDOW_S)
                seg = e_pa2[i0:i1]; base = np.median(e_pa2[max(i0 - 60, 0):i0]) if i0 >= 10 else np.median(e_pa2)
                excess = float(np.sum(np.maximum(seg - base, 0.0)))
                eta, tlnote = cp.eta_needed(st, excess)
                band = key.split("_", 1)[1] if key.startswith("BE") else ("1-9 (plot)" if key in ("D1", "M1b") else "residual env")
                rows.append(dict(receiver=st, panel=pnl, window_start_utc=R.unix_to_hms(utc0 + w0), time_utc=R.unix_to_hms(tu), t_unix=tu,
                                 detector=key if key.endswith("_res") else key.split("_")[0], band_hz=band, statistic=sv, p=p_lab, p_A=pA, p_B=pB, n_null_A=nnA, n_null_B=nnB,
                                 label=R.label_for_p(p_lab), in_window_sofar=Wn.membership(st, tu, "SOFAR"), in_window_agw=Wn.membership(st, tu, "AGW"),
                                 kadri_label=CR.kadri_label(tu, table1 if st == "H01W" else None), excess_2_9_pa2s=excess, eta_needed=eta, tl_note=tlnote,
                                 band_note="plot band 1-9 Hz; 10-20 and 20-40 Hz not computable on the plot", null_A="IMOS 3376 emulated plot",
                                 null_B=f"{R.N_SURROGATE} block-permutation surrogates", caveats=R.CAVEATS, provenance="digitised plot"))
        summ[pnl] = dict(station=st, n_vertices=int(nv), utc0=R.unix_to_hms(utc0), n_null_B=int(len(nullB["M1b"])))
        print(pnl, round(time.time() - t0), flush=True)
    W = pd.DataFrame(rows); W.to_csv(out / "panel_windows.csv", index=False)
    C = W[W.p < R.SCREEN_P].sort_values("p"); C.to_csv(out / "panel_candidates.csv", index=False)
    np.savez_compressed(out / "panel_series.npz", **{k: np.asarray(v) for k, v in series.items()})
    pd.DataFrame(supp).to_csv(out / "h08s_suppression.csv", index=False)
    exp = {}
    for (st, det, band), g in W.groupby(["receiver", "detector", "band_hz"]):
        exp[f"{st}/{det}/{band}"] = dict(n_windows=int(len(g)), **{f"obs_{nm}": int((g.p < thr).sum()) for thr, nm in R.LEVELS}, **{f"exp_{nm}": float(len(g) * thr) for thr, nm in R.LEVELS})
    # box minima (smallest p and the statistic maximum inside each box, per detector)
    box = []
    for name, (a, b) in R.BOXES.items():
        ua, ub = R.hms_to_unix(a), R.hms_to_unix(b)
        for pnl in "abc":
            utc0 = R.hms_to_unix(R.PANEL_T0[pnl] + ".0")
            for key in ("M1b", "D1", "BE_2-5", "BE_5-9"):
                t = series[f"{pnl}_{key}_t"] + utc0; s = series[f"{pnl}_{key}_s"]
                m = (t >= ua) & (t <= ub) & np.isfinite(s)
                if not m.any(): continue
                j = np.argmax(np.where(m, s, -np.inf))
                pA, _ = CR.p_value(s[j], nullA[f"panel_H01W_{key}"])
                g = W[(W.panel == pnl) & (W.detector == key.split("_")[0]) & ((W.band_hz == key.split("_", 1)[1]) if key.startswith("BE") else (W.band_hz == "1-9 (plot)")) & (W.t_unix >= ua - R.WINDOW_S) & (W.t_unix <= ub + R.WINDOW_S)]
                box.append(dict(box=name, panel=pnl, detector=key, stat_max_in_box=float(s[j]), t_max=R.unix_to_hms(t[j]), p_A_of_max=pA, min_window_p=float(g.p.min()) if len(g) else np.nan))
    pd.DataFrame(box).to_csv(out / "box_minima.csv", index=False)
    summ["expected_by_chance"] = exp; summ["wall_s"] = round(time.time() - t0, 1)
    (out / "panel_summary.json").write_text(json.dumps(summ, indent=1, default=str))
    print("done", len(W), len(C), round(time.time() - t0))


if __name__ == "__main__":
    main(sys.argv[1])
EOF
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python panel_search.py /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/panels 2>&1 | tail -8