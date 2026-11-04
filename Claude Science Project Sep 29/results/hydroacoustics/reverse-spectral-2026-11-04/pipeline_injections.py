"""S10 injection sensitivity (Amendment 2, A2.6). Injections go into null records only.
Usage: python pipeline_injections.py <tasks.json> <out.csv> [n_proc]"""
import json, sys, os
import numpy as np, pandas as pd
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__))
import reverse_spectral as RS

_cache = {}


def work(task):
    path = task["path"]
    x = RS.read_dat_250(path).astype(float)
    gf, gd = np.array(task["gain_f"]), np.array(task["gain_db"])
    out = []
    for j in task["inj"]:
        rng = np.random.default_rng(j["seed"])
        p, rise, decay = RS.random_impact_draw(rng)
        if j["family"] == "metz":
            p = dict(RS.METZ_MEMBERS[0]); rise, decay = 1.0, 4.0
        elif j["family"] == "outside_steep":
            p["a"] = rng.uniform(6, 7)
        elif j["family"] == "outside_slow":
            rise, decay = 8.0, 60.0
        on = rng.uniform(20, 250)
        sig = RS.synth_signal(len(x), on, p, rise, decay, gf, gd, rng)
        xi, _ = RS.inject(x, sig, on, j["snr"])
        f, t, P = RS.spectrogram(xi)
        W = RS.whiten(f, t, P)
        sr = RS.s10_scan(W, gf, gd)
        m = np.abs(sr.t - on) <= 5
        Rm = np.where(m & np.isfinite(sr.R), sr.R, -np.inf)
        k = int(np.argmax(Rm))
        out.append(dict(station=task["station"], seg=task["seg"], family=j["family"], snr_db=j["snr"], onset=on,
                        R_max=float(sr.R[k]) if np.isfinite(Rm[k]) else np.nan, onset_err=float(sr.t[k] - on),
                        a=p["a"], fc=p["fc"], f_lo=p["f_lo"], f_hi=p["f_hi"], rise=rise, decay=decay,
                        best_spec=int(sr.i_spec[k]), best_time=int(sr.i_time[k]), chi2r=float(sr.chi2r[k])))
    return out


if __name__ == "__main__":
    tasks = json.load(open(sys.argv[1]))
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 14
    with Pool(n) as pool:
        res = pool.map(work, tasks, chunksize=1)
    pd.DataFrame([r for rr in res for r in rr]).to_csv(sys.argv[2], index=False)
    print("done", sum(len(r) for r in res))
