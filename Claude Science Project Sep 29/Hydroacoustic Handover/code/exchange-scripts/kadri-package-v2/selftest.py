"""Self-test of reference_measure.py on the synthetic triad set (package v2). Generates the set (synth_triad.py, run J pulse
model) into <set_dir>, runs measure() with the M1b templates, and writes selftest_results.csv + selftest_summary.json.
Grid: back-azimuth {256.8 (run J D0' median to H01W), 306.18 (Kadri's row)} x in-pulse SNR {+10, +3, 0, -3, -6, -10} dB
x seeds {1, 2, 3}; plus 60 noise-only runs for the M1b null (maxima of rho over 60 s windows; the 99th percentile is the
alpha = 0.01 reference used in the module's trials). Windows: signal [90, 150] s, noise [10, 70] s.
This is a property of the CODE on model-matched data (perfect coherence, exact element positions, white-ish noise); it says
nothing about field accuracy. The demonstrated field bearing error is 3.3 deg (Kadri 2024 p. 15, t3-like tails).
Usage: python selftest.py <set_dir> <out_dir>
"""
import csv, json, pathlib, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import synth_triad as S          # noqa: E402
import reference_measure as RM   # noqa: E402

BAZS = [256.8, 306.18]; SNRS = [10, 3, 0, -3, -6, -10]; SEEDS = [1, 2, 3]; W = (90.0, 150.0); N = (10.0, 70.0)


def main(set_dir, out):
    set_dir, out = pathlib.Path(set_dir), pathlib.Path(out); set_dir.mkdir(parents=True, exist_ok=True); out.mkdir(parents=True, exist_ok=True)
    T = RM.load_templates(out / "templates_envelope.npz")
    rows = []
    for baz in BAZS:
        for snr in SNRS:
            for sd in SEEDS:
                d = S.make(baz, snr, sd); fn = set_dir / f"synth_H01W_baz{baz:g}_snr{snr:+d}_seed{sd}.npz"; np.savez(fn, **d)
                for r in RM.measure(d, *W, *N, templates=T):
                    err = (r["backazimuth_deg"] - baz + 180) % 360 - 180
                    rows.append(dict(file=fn.name, baz_true=baz, snr_true_db=snr, seed=sd, **r, baz_err_deg=err))
    # noise-only null for M1b: maxima over 60 s windows of the element-mean rho
    null = []
    for sd in range(1000, 1060):
        d = S.make(256.8, -100.0, sd)                        # pulse amplitude ~0: noise only
        y = RM.bandpass(np.asarray(d["x"], float), float(d["fs"]), 5, 40).mean(0)
        t, r = RM.m1b(y, float(d["fs"]), T)
        for a in np.arange(0, S.DUR - 60 + 1e-9, 60.0):
            m = (t >= a) & (t < a + 60)
            if m.any(): null.append(float(r[m].max()))
    null = np.array(null); thr = float(np.quantile(null, 0.99))
    with open(out / "selftest_results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    summ = {}
    for band in ("5-40",):
        for snr in SNRS:
            e = np.array([abs(r["baz_err_deg"]) for r in rows if r["band"] == band and r["snr_true_db"] == snr])
            rho = np.array([r["m1b_rho_max"] for r in rows if r["band"] == band and r["snr_true_db"] == snr and r["m1b_rho_max"] != ""])
            summ[f"snr{snr:+d}"] = dict(baz_err_p50_deg=float(np.median(e)), baz_err_p90_deg=float(np.quantile(e, 0.9)), baz_err_max_deg=float(e.max()),
                                        m1b_rho_median=float(np.median(rho)) if len(rho) else None,
                                        m1b_detected_frac_alpha0_01=float(np.mean(rho > thr)) if len(rho) else None)
    json.dump(dict(n_runs=len(rows) // len(RM.BANDS), bands=[f"{a}-{b}" for a, b in RM.BANDS], window_s=W, noise_window_s=N,
                   m1b_null_windows=int(len(null)), m1b_rho_threshold_alpha0_01=thr, m1b_null_rho_p50=float(np.median(null)),
                   per_snr_band_5_40=summ,
                   caveat="model-matched synthetic data; code property only; field bearing error 3.3 deg demonstrated (Kadri 2024)"),
              open(out / "selftest_summary.json", "w"), indent=1)
    print(json.dumps(summ, indent=1)); print("threshold", thr, "null windows", len(null))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
