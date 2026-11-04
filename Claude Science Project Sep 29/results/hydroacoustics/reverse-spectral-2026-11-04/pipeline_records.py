"""Process IMOS records that lie OUTSIDE the arrival windows (N1 same-day, N2 background days):
S10 scan (null), labelling transients (L0) with features, random noise windows, synthetic impact-like
examples, and envelope-form features. Usage: python pipeline_records.py <tasks.json> <out.pkl> [n_proc]
"""
import json, sys, pickle, os
import numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__))
import reverse_spectral as RS


def work(task):
    try:
        x = RS.read_dat_250(task["path"]).astype(float)
        gf, gd = np.array(task["gain_f"]), np.array(task["gain_db"])
        f, t, P = RS.spectrogram(x)
        W = RS.whiten(f, t, P)
        out = dict(task_id=task["task_id"], station=task["station"], seg=task["seg"], pool=task["pool"],
                   t0=task["t0"], n=len(x))
        env = RS.envelope_from_raw(x)
        if task.get("scan", True):
            sr = RS.s10_scan(W, gf, gd)
            out["scan"] = dict(t=sr.t.astype(np.float32), R=sr.R.astype(np.float32), rho=sr.rho.astype(np.float32),
                               chi2r=sr.chi2r.astype(np.float32), i_spec=sr.i_spec.astype(np.int16),
                               i_time=sr.i_time.astype(np.int16))
        rows = []
        if task.get("l0", True):
            for (a, b, tp, z) in RS.l0_transients(W):
                ft = RS.features_raw(x, a, b, gf, gd, W=W)
                fe = RS.features_envelope(env, 10.0, a, b)
                rows.append(dict(kind="l0", t_on=a, t_off=b, t_peak=tp, z=z, **ft,
                                 **{"env_" + k: v for k, v in fe.items()}))
        rng = np.random.default_rng(task["seed"])
        for _ in range(task.get("n_noise", 0)):
            tr = RS.l0_transients(W, z_thr=3.0, min_sep_s=1.0)
            for _try in range(20):
                a = rng.uniform(5, len(x) / RS.FS - 20)
                if all(abs(a + 5 - tp) > 30 for (_, _, tp, _) in tr):
                    break
            else:
                continue
            ft = RS.features_raw(x, a, a + 10, gf, gd, W=W)
            fe = RS.features_envelope(env, 10.0, a, a + 10)
            rows.append(dict(kind="noise", t_on=a, t_off=a + 10, **ft, **{"env_" + k: v for k, v in fe.items()}))
        for _ in range(task.get("n_impact", 0)):
            p, rise, decay = RS.random_impact_draw(rng)
            on = rng.uniform(20, len(x) / RS.FS - 60)
            snr = rng.uniform(0, 12)
            sig = RS.synth_signal(len(x), on, p, rise, decay, gf, gd, rng)
            xi, _ = RS.inject(x, sig, on, snr)
            f2, t2, P2 = RS.spectrogram(xi)
            W2 = RS.whiten(f2, t2, P2)
            sr2 = RS.s10_scan(W2, gf, gd)
            m = np.abs(sr2.t - on) <= 5
            k = np.where(m)[0][np.nanargmax(sr2.R[m])]
            ts, _ = RS.time_shapes()
            g = ts[int(sr2.i_time[k])]
            dur = max(1.0, float(np.where(g >= 0.1)[0].max() + 1) * RS.DT)
            a, b = float(sr2.t[k]) - 1.0, float(sr2.t[k]) + dur + 1.0
            ft = RS.features_raw(xi, a, b, gf, gd, W=W2)
            env2 = RS.envelope_from_raw(xi)
            fe = RS.features_envelope(env2, 10.0, a, b)
            rows.append(dict(kind="impact", t_on=a, t_off=b, snr_db=snr, R=float(sr2.R[k]), rise=rise, decay=decay,
                             **{"p_" + kk: vv for kk, vv in p.items()}, **ft, **{"env_" + k_: v for k_, v in fe.items()}))
        for (a, b, lab) in task.get("windows", []):
            ft = RS.features_raw(x, a, b, gf, gd, W=W)
            fe = RS.features_envelope(env, 10.0, a, b)
            rows.append(dict(kind="window", label=lab, t_on=a, t_off=b, **ft, **{"env_" + k: v for k, v in fe.items()}))
        out["rows"] = rows
        return out
    except Exception as e:  # keep going; report
        return dict(task_id=task["task_id"], error=repr(e))


if __name__ == "__main__":
    tasks = json.load(open(sys.argv[1]))
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 14
    with Pool(n) as pool:
        res = pool.map(work, tasks, chunksize=2)
    pickle.dump(res, open(sys.argv[2], "wb"))
    print("done", len(res), sum("error" in r for r in res))
