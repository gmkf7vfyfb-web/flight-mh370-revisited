"""Dispersion-aware template bank by KRAKEN broadband synthesis (pre-registration preregistration.py, 'Channel').
Range-independent: one WOA23 March profile at the representative path midpoint (template_profile.npz, built from the
run J seed-1 weighted-median impact towards H01W; template_geometry.json), flat bottom at the path's median depth,
coherent FIELD at each frequency 2-48 Hz step 1/64 Hz; the bulk delay r / 1.482 km/s is removed and the complex
transfer function is inverse-FFT'd to a 64 s window. Source spectra (one-pole, f_r = 1/tau) are applied afterwards.
Usage: python template.py <out_dir> <at_bin> [nproc]   (needs DYLD_LIBRARY_PATH for the toolbox)
"""
from __future__ import annotations
import json, os, sys, time, shutil
from pathlib import Path
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, str(Path(__file__).parent)); sys.path.insert(0, str(Path(__file__).parent.parent))
import preregistration as R
import kraken_tl as KT

PROF = np.load(Path(__file__).parent / "template_profile.npz")
RANGES = sorted(set([float(v) for v in np.arange(R.INJ_RANGE_KM[0], R.INJ_RANGE_KM[1] + 1e-9, 25.0)] + list(R.BANK_RANGES_KM) + list(R.EXTRA_RANGES_KM.values())))   # 25 km grid for injection ranges + bank + IMOS/IMS ranges


def one(args):
    k, f, wd, at_bin = args
    z, c = PROF["z"], PROF["c"]
    m = z <= R.TEMPLATE_DEPTH_M
    zz = np.concatenate([z[m], [R.TEMPLATE_DEPTH_M]]); cc = np.concatenate([c[m], [np.interp(R.TEMPLATE_DEPTH_M, z, c)]])
    root = f"t{k:05d}"
    w = Path(wd) / root; w.mkdir(parents=True, exist_ok=True)
    try:
        KT.write_env(w / f"{root}.env", root, f, [(R.TEMPLATE_DEPTH_M, zz, cc)], [R.TEMPLATE_SD_M], [R.TEMPLATE_RD_M], R.BOTTOM, R.FG, 15)
        KT.write_flp(w / f"{root}.flp", [0.0], RANGES, [R.TEMPLATE_SD_M], [R.TEMPLATE_RD_M], opt="RAOC")
        import subprocess
        subprocess.run([f"{at_bin}/Kraken/kraken.exe", root], cwd=w, capture_output=True, text=True)
        subprocess.run([f"{at_bin}/KrakenField/field.exe", root], cwd=w, capture_output=True, text=True)
        s = KT.read_shd(w / f"{root}.shd")
        p = s["p"][0, 0, 0, :].copy()
        import re
        prt = (w / f"{root}.prt").read_text(errors="replace")
        nm = re.findall(r"Number of modes\s*=\s*(\d+)", prt)
        shutil.rmtree(w, ignore_errors=True)
        return k, p, int(nm[0]) if nm else -1
    except Exception as e:  # noqa: BLE001
        shutil.rmtree(w, ignore_errors=True)
        return k, np.full(len(RANGES), np.nan + 0j), -2


def main(out_dir, at_bin, nproc=3):
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    freqs = np.arange(R.TEMPLATE_FREQS[0], R.TEMPLATE_FREQS[1] + 1e-9, R.TEMPLATE_DF)
    wd = out / "kraken_tmp"
    t0 = time.time()
    H = np.zeros((len(freqs), len(RANGES)), complex); NM = np.zeros(len(freqs), int)
    with Pool(nproc) as pool:
        for n, (k, p, nm) in enumerate(pool.imap_unordered(one, [(k, f, wd, at_bin) for k, f in enumerate(freqs)], chunksize=8)):
            H[k] = p; NM[k] = nm
            if n % 400 == 0:
                print(n, len(freqs), round(time.time() - t0), flush=True)
    shutil.rmtree(wd, ignore_errors=True)
    # time-domain synthesis: remove bulk delay, zero-pad to full spectrum, irfft
    T = R.TEMPLATE_T; fs_syn = 128.0; nfft = int(T * fs_syn); df = 1 / T
    fgrid = np.arange(nfft // 2 + 1) * df
    rr = np.asarray(RANGES)
    bad = ~np.isfinite(H).all(1) | (NM < 0)
    Hc = np.where(np.isfinite(H), H, 0)
    out_t = {}
    for j, r in enumerate(rr):
        delay = r / R.C_BULK_KM_S
        X = np.zeros(len(fgrid), complex)
        for k, f in enumerate(freqs):
            if bad[k]:
                continue
            kk = int(round(f / df))
            # FIELD's pressure exp(-i k r) convention: shift by +omega*delay to centre the arrival in the window at T/4
            X[kk] = Hc[k, j] * np.exp(1j * 2 * np.pi * f * (delay - T / 4))
        h = np.fft.irfft(X, nfft)
        # try the conjugate convention too: choose the one whose energy centroid is causal-compact (ramps up to an abrupt end)
        h2 = np.fft.irfft(np.conj(X) * np.exp(1j * 2 * np.pi * fgrid * T / 2), nfft)
        out_t[f"h_{r:.1f}"] = h
        out_t[f"h2_{r:.1f}"] = h2
    np.savez(out / "templates_raw.npz", freqs=freqs, ranges_km=rr, H=H, n_modes=NM, fs=fs_syn, T=T, **out_t)
    json.dump(dict(n_freq=int(len(freqs)), n_bad=int(bad.sum()), seconds=round(time.time() - t0), n_modes_min=int(NM[NM >= 0].min()), n_modes_max=int(NM.max()), ranges_km=rr.tolist(), profile=json.load(open(Path(__file__).parent / "template_geometry.json"))), open(out / "template_build.json", "w"), indent=1)
    print("done", round(time.time() - t0), "s; bad", int(bad.sum()))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 3)
