"""Step 5 of prereg.py (7dc315f): source-pulse check. KRAKEN coherent broadband (block 7 templates.py physics, synthesis at 256 Hz to hold 70 Hz: hard
bottom, Francois-Garrison, source 10 m, 15 points per wavelength; here 2-70 Hz, df 1/64 Hz) on the representative
range-independent profile of each F-35A path (WOA23 B5C2 April at the path midpoint node; flat bottom = median
along-track depth), receiver at the triad mean depth, range = the path length. One-pole source (block 7
source_filter) for tau on the 25-point grid; Metz processing (4-64 Hz band-pass, 1 s RMS, 0.02 s hop); comparison
with the DIGITISED observed envelopes. Implementation detail (declared, not in the pre-registration text): the
peak-normalised envelopes are compared in dB with both clipped at -15 dB (the observed peak SNR is 12-16 dB).
Usage: python step5_pulse.py <step2_dir> <at_bin> <out_dir> [nproc]
"""
from __future__ import annotations
import json, os, pathlib, re, shutil, subprocess, sys, time
from multiprocessing import Pool
import numpy as np, pandas as pd
from scipy import signal

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
import prereg as R  # noqa: E402
import kraken_tl as KT  # noqa: E402
import obs as OB  # noqa: E402

BOTTOM = dict(cp=1650.0, rho=1.9, ap=0.5); FG = dict(T=4.0, S=34.7, pH=8.0, z_bar=1000.0)
FREQS = np.arange(2.0, 70.0 + 1e-9, 1.0 / 64.0); C_BULK = 1.482; TWIN = 64.0
TAUS = np.logspace(np.log10(0.05), 1.0, 25); CLIP = -15.0; HOP = 0.02


def profile(step2, st):
    """midpoint node profile, extended below the WOA floor with air9_tl_validation.node_profiles (gsw, SA/CT held),
    truncated at the median along-track depth (flat bottom)."""
    import air9_tl_validation as A
    b = pd.read_csv(step2 / "paths" / f"bathy_f35a-{st}.csv"); s = pd.read_csv(step2 / "paths" / f"ssp_f35a-{st}.csv")
    L = float(b.range_km.iloc[-1]); D = float(np.median(-b.elevation_m.values))
    nodes = A.node_profiles(s); node = min(nodes, key=lambda k: abs(nodes[k][0] - L / 2)); _, z, c = nodes[node]
    ok = np.isfinite(c); z, c = z[ok], c[ok]; m = z < D
    return dict(L_km=L, D_m=D, node=int(node), z=np.concatenate([z[m], [D]]), c=np.concatenate([c[m], [np.interp(D, z, c)]]))


def one(args):
    k, f, wd, at_bin, prof, sd, rd, L = args
    root = f"t{k:05d}"; w = pathlib.Path(wd) / root; w.mkdir(parents=True, exist_ok=True)
    try:
        KT.write_env(w / f"{root}.env", root, f, [(prof["D_m"], prof["z"], prof["c"])], [sd], [rd], BOTTOM, FG, 15)
        KT.write_flp(w / f"{root}.flp", [0.0], [L], [sd], [rd], opt="RAOC")
        env = dict(os.environ)
        subprocess.run([f"{at_bin}/Kraken/kraken.exe", root], cwd=w, capture_output=True, text=True, env=env)
        subprocess.run([f"{at_bin}/KrakenField/field.exe", root], cwd=w, capture_output=True, text=True, env=env)
        s = KT.read_shd(w / f"{root}.shd"); p = complex(s["p"][0, 0, 0, 0])
        shutil.rmtree(w, ignore_errors=True); return k, p
    except Exception:  # noqa: BLE001
        shutil.rmtree(w, ignore_errors=True); return k, complex(np.nan, np.nan)


def impulse(H, L):
    """templates.py convention ('h2'): bulk delay removed, conj for the toolbox time convention, 64 s at 128 Hz."""
    fs = 256.0; nfft = int(TWIN * fs); df = 1 / TWIN; fg = np.arange(nfft // 2 + 1) * df; X = np.zeros(len(fg), complex); delay = L / C_BULK
    for k, f in enumerate(FREQS):
        if np.isfinite(H[k]):
            X[int(round(f / df))] = H[k] * np.exp(1j * 2 * np.pi * f * (delay - TWIN / 4))
    return np.fft.irfft(np.conj(X) * np.exp(1j * 2 * np.pi * fg * TWIN / 2), nfft), fs


def metz_envelope(x, fs):
    sos = signal.butter(4, [4.0, 64.0], btype="bandpass", fs=fs, output="sos"); y = signal.sosfiltfilt(sos, x)
    e = np.convolve(y ** 2, np.ones(int(fs)) / fs, "same"); step = int(round(HOP * fs)) or 1
    return e[::step], step / fs


def norm_db(e):
    return np.maximum(10 * np.log10(np.maximum(e / e.max(), 1e-12)), CLIP)


def widths(t, e):
    out = {}; L = 10 * np.log10(np.maximum(e / e.max(), 1e-12)); i = int(np.argmax(e)); dt = t[1] - t[0]
    for d in (3, 6, 10):
        a = i; b = i
        while a > 0 and L[a - 1] >= -d: a -= 1
        while b < len(L) - 1 and L[b + 1] >= -d: b += 1
        out[f"w{d}_s"] = float(t[b] - t[a] + dt)
    c = np.cumsum(e) / e.sum(); out["span_5_95_s"] = float(np.interp(0.95, c, t) - np.interp(0.05, c, t))
    return out


def main(step2, at_bin, out_dir, nproc=4):
    step2 = pathlib.Path(step2); out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True); t0 = time.time()
    st_meta = json.load(open(step2 / "step2_tl_meta.json"))["receivers"]
    res = {}; H_all = {}
    for st in ("H11N", "H11S"):
        prof = profile(step2, st); rd = st_meta[st]["rcv_depth_m"]; wd = out / f"work_{st}"
        H = np.full(len(FREQS), np.nan + 0j)
        with Pool(nproc) as pool:
            for k, p in pool.imap_unordered(one, [(k, f, str(wd), at_bin, prof, 10.0, rd, prof["L_km"]) for k, f in enumerate(FREQS)], chunksize=16):
                H[k] = p
        shutil.rmtree(wd, ignore_errors=True); H_all[st] = H
        h, fs = impulse(H, prof["L_km"])
        # observed: three elements averaged in linear excess power, peak-aligned
        obs = []
        for el in (f"{st}1", f"{st}2", f"{st}3"):
            t, L = OB.envelope(el); ipk, Ln, a, b = OB.windows(t, L); ex = np.clip(10 ** (L / 10) - 10 ** (Ln / 10), 0, None)
            obs.append(np.interp(np.arange(-12, 12 + 1e-9, HOP), t - t[ipk], ex))
        tg = np.arange(-12, 12 + 1e-9, HOP); eo = np.mean(obs, 0); ow = widths(tg, eo)
        rows = []
        for tau in TAUS:
            b_, a_ = signal.butter(1, 1.0 / tau, btype="low", fs=fs); x = signal.lfilter(b_, a_, h)
            e, dt = metz_envelope(x, fs); te = np.arange(len(e)) * dt; te = te - te[np.argmax(e)]
            em = np.interp(tg, te, e, left=0, right=0)
            m = np.abs(tg) <= 10.0; rms = float(np.sqrt(np.mean((norm_db(em)[m] - norm_db(eo)[m]) ** 2)))
            rows.append(dict(triad=st, tau_s=float(tau), rms_db=rms, **{f"model_{k}": v for k, v in widths(tg, em).items()}))
        res[st] = dict(profile=dict(L_km=prof["L_km"], D_m=prof["D_m"], node=prof["node"], axis_depth_m=float(prof["z"][np.argmin(prof["c"])]), c_min=float(prof["c"].min())),
                       observed=ow, n_bad=int((~np.isfinite(H)).sum()), table=rows)
        np.savez_compressed(out / f"step5_model_{st}.npz", freqs=FREQS, H=H, h=h, fs=fs, t_obs=tg, e_obs=eo)
        print(st, round(time.time() - t0), flush=True)
    T = pd.DataFrame([r for st in res for r in res[st]["table"]]); T.to_csv(out / "step5_tau_scan.csv", index=False)
    tot = T.groupby("tau_s").rms_db.mean(); tau5 = float(tot.idxmin())
    ok = all(abs(float(T[(T.triad == st) & np.isclose(T.tau_s, tau5)].model_w6_s.iloc[0]) - res[st]["observed"]["w6_s"]) <= 1.5 for st in res)
    summ = dict(prereg="prepare/metz_f35a/prereg.py @7dc315f", tau5_s=tau5, rms_at_tau5_db=float(tot.min()), w6_rule_pass=bool(ok),
                tau_used_for_anchor=tau5 if ok else R.TAU_FALLBACK, verdict=("reproduces the arrival duration within 1.5 s (-6 dB width)" if ok else
                "the module's pulse and modelled path do NOT reproduce the F-35A arrival duration; fallback tau 3.30 s used for the anchor"),
                triads={st: dict(profile=res[st]["profile"], observed=res[st]["observed"], n_bad=res[st]["n_bad"],
                                 model_at_tau5={k: v for k, v in T[(T.triad == st) & np.isclose(T.tau_s, tau5)].iloc[0].items() if k.startswith("model_") or k == "rms_db"},
                                 model_at_fallback={k: v for k, v in T[(T.triad == st)].iloc[(T[T.triad == st].tau_s - R.TAU_FALLBACK).abs().argmin()].items() if k.startswith("model_") or k == "rms_db"},
                                 model_at_tau_min={k: v for k, v in T[(T.triad == st)].iloc[0].items() if k.startswith("model_") or k == "rms_db"}) for st in res},
                seconds=round(time.time() - t0))
    json.dump(summ, open(out / "step5_summary.json", "w"), indent=1, default=float); print(json.dumps(summ, indent=1, default=float))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 4)
