"""Reproduces the synthetic calibration numbers quoted in the methods
specification (sections 5 and 11).  Synthetic data only.  Run: python synthetic_calibration.py"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tests"))
import reverse_detectors as rd
from test_reverse_detectors import noise_env, make_shots
FS = 10.0

def s2_thinning():
    env = noise_env(int(3600 * FS), np.random.default_rng(100), corr_s=1.0)
    y = 20 * np.log10(env)
    out = {}
    for name, lag in [("lag1", 1), ("lag_1e", rd.decorrelation_lag(y, thr=1 / np.e)), ("lag_0.1", rd.decorrelation_lag(y, thr=0.1))]:
        o = rd.persistence(env, FS, win_s=20, lag=lag)
        out[name] = {"lag": int(lag), "false_alarm_at_0.05": float(np.nanmean(o["p_bin"] <= 0.05))}
    out["S1_fraction_z_ge_2"] = float(np.nanmean(rd.energy_excess(env, FS, win_s=10)["z"] >= 2))
    return out

def stats_all(e):
    a = rd.energy_excess(e, FS, win_s=10)
    b = rd.persistence(e, FS, win_s=10, lag=rd.decorrelation_lag(20 * np.log10(e), thr=0.1))
    m, s = rd.robust_loc_scale(20 * np.log10(e))
    g, _ = rd.page_cusum(e, FS, m, s, 1.0)
    return a, b, g

def window_stat(a, b, g, t0):
    sel = (a["t"] >= t0 - 5) & (a["t"] <= t0 + 25)
    return np.nanmax(a["z"][sel]), np.nanmax(b["T2"][sel]), np.nanmax(g[int((t0 - 5) * FS):int((t0 + 25) * FS)])

def sensitivity():
    a, b, g = stats_all(noise_env(int(7200 * FS), np.random.default_rng(101)))
    N = np.array([window_stat(a, b, g, t) for t in np.random.default_rng(5).uniform(200, 7000, 400)])
    emp = lambda v, c: rd.empirical_p(v, N[:, c])
    N3 = np.array([rd.fisher_combine(emp(r[0], 0), emp(r[1], 1)) for r in N])
    sh = rd.impulsive_shape(FS, 1.0, 5.0)
    out = {}
    for snr in [-9, -6, -3, 0, 3]:
        det = np.zeros(4)
        for k in range(40):
            e1 = rd.inject_envelope(noise_env(int(600 * FS), np.random.default_rng(1000 + k)), FS, 300.0, sh, snr_db=snr)
            s1, s2, s4 = window_stat(*stats_all(e1), 300.0)
            p1, p2, p4 = emp(s1, 0), emp(s2, 1), emp(s4, 2)
            p3 = rd.empirical_p(rd.fisher_combine(p1, p2), N3)
            det += np.array([p1, p2, p3, p4]) <= 0.05
        out[str(snr)] = dict(zip(["S1", "S2", "S3", "S4"], (det / 40).round(2).tolist()))
    return out

def s7_calibration():
    nulls = []
    for seed in range(20, 40):
        e0, _ = make_shots(np.random.default_rng(seed)); s0 = rd.segment_shots(e0, FS); f0, M0 = rd.shot_features(e0, FS, s0)
        nulls.append(float(rd.shot_population_test(f0, M0, FS, n_mc=100, rng=seed)["p_global"].min()))
    det = {}
    for snr in [3, 6, 8]:
        hits = 0
        for seed in range(40, 50):
            e1, on = make_shots(np.random.default_rng(seed), contaminate=30, snr_db=snr); s1 = rd.segment_shots(e1, FS); f1, M1 = rd.shot_features(e1, FS, s1)
            r1 = rd.shot_population_test(f1, M1, FS, n_mc=100, rng=seed); i = int(np.argmin(r1["p_global"])); c = f1["cycle_start_s"][i]
            hits += int((c <= on[30] + 1.5 < c + f1["period_s_fit"]) and r1["p_global"][i] < 0.05)
        det[str(snr)] = f"{hits}/10"
    return {"null_min_global_p_20_populations": sorted(round(x, 3) for x in nulls), "detected_right_cycle": det}

if __name__ == "__main__":
    res = {"module_version": rd.__version__, "S2_thinning": s2_thinning(), "S1_S4_sensitivity": sensitivity(), "S7": s7_calibration()}
    json.dump(res, open(os.path.join(HERE, "synthetic_calibration.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))
