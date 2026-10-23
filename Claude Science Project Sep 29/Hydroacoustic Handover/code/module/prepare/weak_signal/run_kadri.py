"""Test set (b) of preregistration.py: every method on the DIGITISED Kadri (2024) Fig. 9 traces (H01W a, b, c; H08S d, e)
at 20 Hz, band 1-9 Hz, with the null from IMOS 3376 background passed through the plot-decimation emulator.
Usage: python run_kadri.py <templates_raw.npz> <out_dir> [nproc]
Outputs: panel_statistics.npz, candidates.csv, box_maxima.csv, m2_cross_station.csv, null_panel_maxima.npz, summary.json"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
from multiprocessing import Pool
import numpy as np, pandas as pd
from scipy import signal
sys.path.insert(0, str(Path(__file__).parent))
import preregistration as R, common as C, methods as M, bank as B

FS = R.PANEL_FS
SOS20 = signal.butter(4, list(R.PANEL_BAND), btype="bandpass", fs=FS, output="sos")
TABLE1 = Path(__file__).parent.parent.parent / "data" / "kadri_fig9_digitised" / "kadri-table1-transients.csv"
CTX = {}


def panel_ctx(T):
    """Envelope templates at 20 Hz for the H01W (2,200 km) and H08S (3,704 km) ranges, three tau; cepstral band."""
    env, keys = [], []
    for key in ("h2_2200.0", "h2_3703.5"):
        for tau in R.TAUS:
            p = B.pulse(T, key, tau, fs=100)
            p20 = signal.resample_poly(p, 1, 5)
            e = M.envelope(p20, FS)             # 10 Hz
            e = e - e.mean(); env.append(e / np.sqrt(np.sum(e ** 2))); keys.append((key, tau))
    ref = signal.resample_poly(B.pulse(T, "h2_2200.0", 1.0, fs=100), 1, 5)
    ref = signal.sosfiltfilt(SOS20, ref)
    X = np.abs(np.fft.rfft(ref * np.hanning(len(ref)))); c = np.fft.irfft(np.log(X + 1e-12)); q = np.arange(len(c)) / FS
    m = (q >= 0.05) & (q <= len(c) / FS / 2); cc = c ** 2 * m; cs = np.cumsum(cc) / cc.sum()
    return dict(bank_env=env, bank_keys=keys, bank_env_peak_idx=int(B.PEAK_AT * 10), q_band=(float(q[np.searchsorted(cs, 0.1)]), float(q[np.searchsorted(cs, 0.9)])))


PANEL_METHODS = {k: v for k, v in M.METHODS.items() if k != "M1a_mf_waveform"}


def m0b_panel(x, fs, ctx=None):
    return M.m0b_bandenergy(x, fs, ctx, bands=((1, 5), (3, 9)))


PANEL_METHODS["M0b_bandenergy"] = m0b_panel


def stats_all(x):
    xb = signal.sosfiltfilt(SOS20, np.asarray(x, float))
    out = {}
    for name, fn in PANEL_METHODS.items():
        out[name] = fn(xb, FS, CTX)
    return out


def _init(ctx):
    global CTX
    CTX = ctx


def null_one(f):
    import imos_noise as N
    try:
        x500 = N.decimate(N.read_volts(f))
    except Exception:  # noqa: BLE001
        return None
    x20 = C.emulate_plot(x500)
    s = stats_all(x20)
    return {k: M.window_maxima(t, v, R.WARMUP_S, R.WINDOW_S, len(x20) / FS) for k, (t, v) in s.items()}, C.band_level_1s(signal.sosfiltfilt(SOS20, x20.astype(float)), FS, 1, 9)[0]


def label_for(utc, table1):
    labs = []
    for name, (a, b) in R.BOXES.items():
        if pd.Timestamp(f"2014-03-08T{a}Z") <= utc <= pd.Timestamp(f"2014-03-08T{b}Z"):
            labs.append(name)
    for _, r in table1.iterrows():
        t = pd.Timestamp(f"2014-03-08T{r.time_utc}Z")
        if abs((utc - t).total_seconds()) <= 10:
            labs.append(f"Table 1 {r.time_utc} ({r.bearing_deg} deg)")
    return "; ".join(labs) if labs else "unlabelled"


def main(tpath, out_dir, nproc=3):
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True); t0 = time.time()
    T = np.load(tpath); ctx = panel_ctx(T)
    # SR constants: calibrate on the first 20 emulated files (pre-registered rule, same as test set a)
    import imos_noise as N
    files = C.bg_files(3376)
    em = [C.emulate_plot(N.decimate(N.read_volts(f))) for f in files[:20]]
    cal = []
    for k in (0.3, 1.0, 3.0):
        for sig in (0.2, 0.35, 0.5, 0.7):
            rates = []
            for x in em:
                xx = signal.sosfiltfilt(SOS20, x.astype(float))
                rms = pd.Series(xx ** 2).rolling(60 * FS, min_periods=5 * FS).mean().shift(1).bfill().values ** 0.5
                s = xx / np.maximum(rms, 1e-12); rr = np.random.default_rng(1); dt = 1 / FS; u = 1.0; prev = 1.0; cnt = 0
                xi = rr.standard_normal(len(s)) * np.sqrt(dt) * sig
                for n in range(len(s)):
                    u = u + dt * (u - u ** 3 + k * s[n]) + xi[n]; sg = 1.0 if u >= 0 else -1.0; cnt += sg != prev; prev = sg
                rates.append(cnt / (len(s) / FS))
            cal.append(dict(k=k, sigma=sig, rate=float(np.median(rates))))
    cal = pd.DataFrame(cal); srbest = cal.iloc[(cal.rate - 1.0).abs().argmin()]
    ctx["sr_k"], ctx["sr_sigma"] = float(srbest.k), float(srbest.sigma)
    _init(ctx)
    # null
    with Pool(nproc, initializer=_init, initargs=(ctx,)) as pool:
        res = pool.map(null_one, files, chunksize=8)
    res = [r for r in res if r is not None]
    null = {k: np.concatenate([r[0][k] for r in res]) for k in PANEL_METHODS}
    np.savez(out / "null_panel_maxima.npz", **null)
    levs = [r[1] for r in res]
    print("null", len(res), round(time.time() - t0), flush=True)
    # panels
    table1 = pd.read_csv(TABLE1)
    S, cands, boxrows = {}, [], []
    Z = {}
    for pnl in "abcde":
        tg, x, utc0, nv = C.load_panel(pnl)
        s = stats_all(x)
        for name, (t, v) in s.items():
            S[f"{pnl}/{name}/t"], S[f"{pnl}/{name}/v"] = t, v
            nv_ = null[name]; nv_ = nv_[np.isfinite(nv_)]
            pk, _ = signal.find_peaks(np.nan_to_num(v, nan=-np.inf), distance=max(int(10 / max(np.median(np.diff(t)), 1e-6)), 1))
            for i in pk:
                if not np.isfinite(v[i]):
                    continue
                p = float((nv_ >= v[i]).mean())
                if p < 0.3:
                    utc = utc0 + pd.Timedelta(seconds=float(t[i]))
                    lab = next((l for thr, l in R.P_LABELS if p < thr), "below screen")
                    cands.append(dict(panel=pnl, station=C.PANELS[pnl][0], method=name, utc=utc.strftime("%H:%M:%S"), statistic=float(v[i]), p_null=p, n_null=int(len(nv_)), label=lab, box=label_for(utc, table1)))
            for bname, (a, b) in R.BOXES.items():
                ta = (pd.Timestamp(f"2014-03-08T{a}Z") - utc0).total_seconds(); tb = (pd.Timestamp(f"2014-03-08T{b}Z") - utc0).total_seconds()
                if tb < 0 or ta > 600:
                    continue
                mx = M.window_max(t, v, ta, tb)
                boxrows.append(dict(panel=pnl, method=name, box=bname, max_statistic=mx, p_null=float((nv_ >= mx).mean()) if np.isfinite(mx) else np.nan, outside_max=M.window_max(t, np.where((t >= ta) & (t <= tb), np.nan, v), 32, 600)))
        lev = C.band_level_1s(signal.sosfiltfilt(SOS20, x.astype(float)), FS, 1, 9)[0]
        Z[pnl] = (utc0, lev)
    np.savez(out / "panel_statistics.npz", **S)
    cd = pd.DataFrame(cands).sort_values("p_null"); cd.to_csv(out / "candidates.csv", index=False)
    pd.DataFrame(boxrows).to_csv(out / "box_maxima.csv", index=False)
    # M2 cross-station: H01W (b, c) with H08S (d, e) at lags 855.93-1346.50 s
    def zser(lev):
        med, mad = M._roll_med_mad(lev, 60); return (lev - med) / mad
    h01 = {}; h08 = {}
    for pnl in "abc":
        u0, lev = Z[pnl]; z = zser(lev)
        for i, zz in enumerate(z):
            h01[int((u0 - pd.Timestamp("2014-03-08T00:00:00Z")).total_seconds()) + i] = zz
    for pnl in "de":
        u0, lev = Z[pnl]; z = zser(lev)
        for i, zz in enumerate(z):
            h08[int((u0 - pd.Timestamp("2014-03-08T00:00:00Z")).total_seconds()) + i] = zz
    lags = np.arange(int(np.ceil(R.H08S_LAG_S[0])), int(R.H08S_LAG_S[1]) + 1)
    m2 = []
    for t1, z1 in h01.items():
        if not np.isfinite(z1):
            continue
        best, blag = -np.inf, None
        for L in lags:
            z2 = h08.get(t1 + L)
            if z2 is not None and np.isfinite(z2) and z1 + z2 > best:
                best, blag = z1 + z2, int(L)
        if blag is not None:
            m2.append(dict(t1_s=t1, utc_h01w=pd.Timestamp("2014-03-08T00:00:00Z") + pd.Timedelta(seconds=t1), lag_s=blag, utc_h08s=pd.Timestamp("2014-03-08T00:00:00Z") + pd.Timedelta(seconds=t1 + blag), M2=best))
    m2 = pd.DataFrame(m2)
    # null for M2 on emulated pairs: random window pairs from the emulated 3376 levels with random lags, windows of 60 s
    rng = np.random.default_rng(R.SEED); zl = [zser(l) for l in levs]; nullm2 = []
    for _ in range(6000):
        a = zl[rng.integers(len(zl))]; b = np.concatenate([zl[rng.integers(len(zl))], zl[rng.integers(len(zl))]])   # two files give the 491 s lag span
        s0 = int(rng.uniform(R.WARMUP_S + 1, len(a) - 61)); best = -np.inf
        for t in range(s0, s0 + 60):
            if not np.isfinite(a[t]):
                continue
            j = rng.integers(32, len(b) - len(lags) - 1)
            seg = b[j: j + len(lags)]; seg = seg[np.isfinite(seg)]
            if len(seg):
                best = max(best, a[t] + seg.max())
        nullm2.append(best)
    nullm2 = np.array(nullm2); nullm2 = nullm2[np.isfinite(nullm2)]
    if len(m2):
        m2["utc_h01w"] = m2.utc_h01w.dt.strftime("%H:%M:%S"); m2["utc_h08s"] = m2.utc_h08s.dt.strftime("%H:%M:%S")
        m2["p_null"] = [float((nullm2 >= v).mean()) for v in m2.M2]
        m2["label"] = [next((l for thr, l in R.P_LABELS if p < thr), "below screen") for p in m2.p_null]
        m2["box"] = [label_for(pd.Timestamp(f"2014-03-08T{u}Z"), table1) for u in m2.utc_h01w]
        m2.sort_values("p_null").to_csv(out / "m2_cross_station.csv", index=False)
    np.save(out / "null_m2_panel.npy", nullm2)
    json.dump(dict(n_null_files=len(res), n_null_windows={k: int(np.isfinite(v).sum()) for k, v in null.items()}, sr=dict(k=ctx["sr_k"], sigma=ctx["sr_sigma"], rate=float(srbest.rate)), q_band=list(ctx["q_band"]), n_candidates=int(len(cd)), n_m2_null=int(len(nullm2)), seconds=round(time.time() - t0),
              vertices={p: C.load_panel(p)[3] for p in "abcde"}), open(out / "summary.json", "w"), indent=1)
    print("done", round(time.time() - t0))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 3)
