cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/weak_signal"
cat > run_h08s.py <<'EOF'
"""Test set (c) of preregistration.py: H08S airgun suppression on the DIGITISED Kadri Fig. 9 panels d, e (40 Hz):
(c1) shot-train template subtraction (local median template, h08s_shot_template rule, on the 0.25 s envelope),
(c2) cyclostationary gating on the shot cadence (+-1.5 s), (c3) off-cadence residual; residual reduction in dB,
surviving candidates (z >= 3), and recovery of the module's H08S-range template envelope injected before/after.
Usage: python run_h08s.py <templates_raw.npz> <out_dir>"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy import signal
sys.path.insert(0, str(Path(__file__).parent))
import preregistration as R, common as C, bank as B

FS = 40
DAY0 = pd.Timestamp("2014-03-08T00:00:00Z")
KD = Path(__file__).parent.parent.parent / "data" / "kadri_fig9_digitised"


def load(pnl):
    tr = pd.read_csv(KD / f"kadri-2024-figure9-panel-{pnl}-H08S.csv")
    t = (pd.to_datetime(tr.utc) - DAY0).dt.total_seconds().values
    o = np.argsort(t); t, p = t[o], tr.pressure_pa.values[o]
    tg = np.arange(t[0], t[-1], 1 / FS)
    return tg, np.interp(tg, t, p)


def env(p, s=0.25):
    k = int(s * FS); return np.convolve(p ** 2, np.ones(k) / k, "same")


def shots(tg, p):
    e5 = env(p, 0.5)
    pk, _ = signal.find_peaks(e5, distance=int(3 * FS), prominence=2 * np.median(e5))
    t = tg[pk]
    return t[(t - 3 >= tg[0]) & (t + 6 <= tg[-1])]


def subtract(tg, e, ts, pre=3.0, post=6.0, nb=6):
    """(c1): per shot, local median template of neighbours' peak-normalised envelopes, scaled to the shot's peak."""
    w = np.arange(-int(pre * FS), int(post * FS))
    idx = np.searchsorted(tg, ts)
    W = np.array([e[i + w] for i in idx]); pk = W[:, int(pre * FS) - 2: int(pre * FS) + 3].max(1)
    Wn = W / pk[:, None]
    res = e.copy(); tmpl_used = np.zeros_like(W)
    for k, i in enumerate(idx):
        nbh = [j for j in range(max(k - nb, 0), min(k + nb + 1, len(idx))) if j != k]
        tm = np.median(Wn[nbh], axis=0) * pk[k]
        tmpl_used[k] = tm
        res[i + w] = e[i + w] - tm
    return res, W, tmpl_used


def cadence(ts):
    d = np.diff(ts); per = float(np.median(d[(d >= 9) & (d <= 11)]))
    ph = np.angle(np.mean(np.exp(2j * np.pi * ts / per))) * per / (2 * np.pi)
    return per, ph


def gate_mask(tg, per, ph, half=1.5):
    dist = np.abs(((tg - ph) / per - np.round((tg - ph) / per)) * per)
    return dist > half


def zlog(e):
    l = np.log10(np.maximum(e, 1e-12)); med = np.median(l); mad = 1.4826 * np.median(np.abs(l - med))
    return (l - med) / max(mad, 1e-9)


def cand_peaks(tg, e, mask=None, z=3.0):
    ee = e.copy()
    if mask is not None:
        ee[~mask] = np.nan
    zz = zlog(np.nan_to_num(ee, nan=np.nanmedian(ee)))
    pk, _ = signal.find_peaks(np.nan_to_num(zz, nan=-np.inf), distance=int(3 * FS), height=z)
    if mask is not None:
        pk = pk[mask[pk]]
    return tg[pk], zz[pk]


def db(a, b):
    return 10 * np.log10(np.mean(a) / np.mean(b))


def main(tpath, out_dir):
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    T = np.load(tpath)
    # H08S-range template envelope at 40 Hz (p^2, 0.25 s smoothed), peak-normalised
    p100 = B.pulse(T, "h2_3703.5", 1.0, fs=100); p40 = signal.resample_poly(p100, 2, 5)
    tenv = env(p40, 0.25); tenv = tenv / tenv.max(); tpk = int(np.argmax(tenv))
    table1 = pd.read_csv(KD / "kadri-table1-transients.csv")
    lagwin = {}
    for lab, hms in (("text time 00:52:03", "00:52:03"), ("caption time 00:54:30", "00:54:30")):
        t1 = (pd.Timestamp(f"2014-03-08T{hms}Z") - DAY0).total_seconds()
        lagwin[lab] = (t1 + R.H08S_LAG_S[0], t1 + R.H08S_LAG_S[1])
    rows, cands, inj = [], [], []
    series = {}
    rng = np.random.default_rng(R.SEED)
    for pnl in "de":
        tg, p = load(pnl); e = env(p); ts = shots(tg, p)
        res, W, TM = subtract(tg, e, ts)
        per, ph = cadence(ts); gm = gate_mask(tg, per, ph)
        shotfree = np.ones(len(tg), bool)
        for t in ts:
            shotfree &= np.abs(tg - t) > 1.5
        resp = np.maximum(res, 0)
        rows.append(dict(panel=pnl, n_shots=len(ts), cadence_s=per, phase_s=ph, gated_fraction=float(1 - gm.mean()),
                         c1_reduction_db_whole=db(resp, e), c1_reduction_db_shotfree=db(resp[shotfree], e[shotfree]),
                         c2_reduction_db=db(e[gm], e), c1c2_reduction_db=db(resp[gm], e),
                         raw_rms_pa=float(np.sqrt(np.mean(p ** 2)))))
        series[pnl] = dict(tg=tg, p=p, e=e, res=res, gm=gm, ts=ts, per=per, ph=ph)
        # candidates surviving: raw, after c1, after c1+c2; off-cadence (c3) flag
        for stage, ee, mask in (("raw", e, None), ("c1", resp, None), ("c1+c2", resp, gm)):
            tt, zz = cand_peaks(tg, ee, mask)
            for t, z in zip(tt, zz):
                dist = abs(((t - ph) / per - round((t - ph) / per)) * per)
                utc = (DAY0 + pd.Timedelta(seconds=float(t)))
                labs = [lab for lab, (a, b) in lagwin.items() if a <= t <= b]
                cands.append(dict(panel=pnl, stage=stage, utc=utc.strftime("%H:%M:%S"), z=float(z), off_cadence=bool(dist > 2.0), cadence_dist_s=float(dist),
                                  lag_consistent_with=("; ".join(labs) if labs else "none")))
        # injection of the template envelope at 6 levels relative to the median shot peak, 40 onsets each
        shot_pk = float(np.median([e[np.searchsorted(tg, t)] for t in ts]))
        for lev in np.arange(-20, 0.1, 4):
            amp = shot_pk * 10 ** (lev / 10)
            for _ in range(40):
                on = rng.uniform(tg[0] + 10, tg[-1] - 60)
                i0 = int((on - tg[0]) * FS); e2 = e.copy(); e2[i0: i0 + len(tenv)] += amp * tenv[: len(e2) - i0]
                tpeak = on + tpk / FS
                p2 = np.interp(tg, tg, p)  # unchanged waveform; shots found on the raw p
                res2, _, _ = subtract(tg, e2, ts); resp2 = np.maximum(res2, 0)
                hit_raw = any(abs(cand_peaks(tg, e2)[0] - tpeak) <= 2.0)
                hit_c1 = any(abs(cand_peaks(tg, resp2)[0] - tpeak) <= 2.0)
                hit_c12 = any(abs(cand_peaks(tg, resp2, gm)[0] - tpeak) <= 2.0)
                inj.append(dict(panel=pnl, level_db=float(lev), onset_s=on, hit_raw=hit_raw, hit_c1=hit_c1, hit_c1c2=hit_c12, peak_gated=bool(not gm[min(int((tpeak - tg[0]) * FS), len(gm) - 1)])))
    pd.DataFrame(rows).to_csv(out / "suppression.csv", index=False)
    pd.DataFrame(cands).to_csv(out / "surviving_candidates.csv", index=False)
    I = pd.DataFrame(inj); I.to_csv(out / "injection_raw.csv", index=False)
    I.groupby(["panel", "level_db"])[["hit_raw", "hit_c1", "hit_c1c2", "peak_gated"]].mean().reset_index().to_csv(out / "injection_pd.csv", index=False)
    np.savez(out / "series.npz", **{f"{k}/{n}": v for k, d in series.items() for n, v in d.items()}, tenv=tenv)
    json.dump(dict(lag_windows=lagwin, template="KRAKEN h2 3,703.5 km, tau 1 s, p^2 envelope 0.25 s"), open(out / "summary.json", "w"), indent=1, default=str)
    print(pd.DataFrame(rows).round(2).to_string(index=False))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
EOF
echo ok