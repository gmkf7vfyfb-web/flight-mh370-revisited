"""Run J northern supplement, end of flight: per-seed accumulators for rule B (overnight order A, 19 Oct 2026).

    python supplement_combine.py part SEED_DIR HANDOFF_NPY TECH OUT_NPZ [XD_SEED_DIR]   (TECH = prod | supp)
    python supplement_combine.py rhat-check                                     (prints r_hat lookups)

Row mass under 00:19 treatment d (two-factor total, q = 1/3, C2 silent, survival factor; as option_table_0019.seed_terms):
    m = u_t x beta_t(lat_0011) x exp(surv + D_d + logon total),  u_t = weight / S_t (x K for a K-strided supplement)
where weight = the stored impact weight (= hand-off weight x exp(log_correction) x within-parent weight), S_t = seeds of the
technique, and beta from core's rule B (results/run-j-supplement/README.md section 5): beta1 = n1/(n1 + n2 r),
beta2 = n2 r/(n1 + n2 r), r = r_hat(00:11 latitude) from r_hat.csv (0.1 outside its bins), n1, n2 = hand-off rows flown.
Each part stores, per treatment and for two weightings ("alone": production with beta = 1; "comb": rule B), sums of m and m^2
on 0.1 deg bins of impact latitude and of 00:11 latitude by family (A1, A2, B, other), and per 5 deg band the sums of squared
masses grouped by parent and by distinct 00:11 state (mode, particle) for the Kish ESS over parents and over distinct states.
The global constants (S_t, n_t, K) are passed by environment: SUP_S1 SUP_S2 SUP_N1 SUP_N2 SUP_K.
"""
import csv, json, os, pathlib, sys
import numpy as np
from scipy.special import gammaln
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from compact_impacts import load, family_labels
from displacement_hist import derived_logliks, constraint_log_factor, SATCOM_CSV
from option_table_0019 import d5_loglik, W_S, run_obs

CELLS = ("D0", "D1", "D2", "D3", "D4", "D5")
FINE = np.round(np.arange(-45.0, -14.95, 0.1), 2)        # 300 bins of 0.1 deg
BANDS = np.arange(-45.0, -14.0, 5.0)                       # 6 bands of 5 deg
# D5 is scored with run J's 00:19 BFO error, 4.3177 Hz (config/sensitivity/run-j/obs-bfo432.toml), not the base table's 7 Hz
# (coordination 19 Oct 2026, calibration-smoke fault F1). BTO errors are the same in both tables.
OBS_D5 = pathlib.Path(__file__).resolve().parents[3] / "data" / "variants" / "satcom-observations-bfo432.csv"
RHAT = pathlib.Path(os.environ.get("SUP_RHAT", "/Users/pete/Downloads/mh370-exchange/core/run-j-supplement/r_hat.csv"))


def r_hat(lat):
    rows = [r for r in csv.reader(open(RHAT)) if r and not r[0].startswith("#") and r[0] != "lat_lo_deg"]
    lo = np.array([float(r[0]) for r in rows]); hi = np.array([float(r[1]) for r in rows]); rv = np.array([float(r[2]) for r in rows])
    out = np.full(len(lat), 0.1); i = np.searchsorted(lo, lat, side="right") - 1
    ok = (i >= 0) & (lat < hi[np.clip(i, 0, len(hi) - 1)]); out[ok] = rv[i[ok]]
    return out


def row_terms(sd, handoff):
    meta, g = load(sd); logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
    obs = run_obs(meta)   # the run's own table (run J: 4.3177 Hz), = OBS_D5 for every pass here
    assert abs(float(obs["m0019a"]["bfo_sd_hz"]) - 4.3177) < 1e-9 and abs(float(obs["m0019b"]["bfo_sd_hz"]) - 4.3177) < 1e-9
    w = g("weight"); par = g("parent").astype(np.int64); H = np.load(handoff)
    assert par.max() < len(H), (par.max(), len(H))
    present = [c[len("loglik:"):] for c in meta["impact_columns"] if c.startswith("loglik:")]; der = derived_logliks(meta, g, present)
    V = H[par, 9]
    col = lambda k: np.where(np.isfinite(g("loglik:" + k)), g("loglik:" + k), -np.inf)
    D = {"D0": np.zeros(len(w)), "D1": der["r600-bto"], "D2": col("r600/no-offset"), "D3": col("both/no-offset"),
         "D4": col("both/startup-offset"), "D5": d5_loglik(g, V, obs)}
    lag = logon["logon_unix_s"] - g("latent:realised_flameout_unix_s")
    with np.errstate(divide="ignore", invalid="ignore"):
        lfe = (logon["lag_shape"] - 1) * np.log(lag) - lag / logon["lag_scale_s"] - logon["lag_shape"] * np.log(logon["lag_scale_s"]) - gammaln(logon["lag_shape"])
        surv = np.log1p(-np.clip(g("latent:inflight_p_breakup_to_m0019b"), 0, 1)); lw = np.log(w)
    lfe = np.where(np.isfinite(lag) & (lag > 0), lfe, -np.inf)
    c1 = lfe + constraint_log_factor(g, logon, "fuel-exhaustion", "unpowered"); c2 = -np.log(W_S) + constraint_log_factor(g, logon, "other", "silent")
    p = 0.75; tot = np.logaddexp(np.log(p) + c1, np.log(1 - p) + c2)
    f4 = family_labels(g("latent:onset_mechanism"), g("latent:control_realised"), g("latent:recovery_attempted"))["family4_code"]
    fam = np.select([f4 == 1, f4 == 2, f4 == 3], [0, 1, 2], 3)
    state = H[par, 6].astype(np.int64) * (1 << 40) + H[par, 12].astype(np.int64)
    return {"t": {d: lw + surv + D[d] + tot for d in CELLS}, "lat": g("latitude_deg"), "lat0011": H[par, 1], "par": par,
            "fam": fam, "f4": f4, "state": state, "n_handoff": len(H)}


def group_sq(key, b, m, nb):
    """sum over groups (within band b) of (sum m)^2, per band."""
    ok = (b >= 0) & (b < nb) & (m > 0)
    if not ok.any(): return np.zeros(nb)
    kk = b[ok].astype(np.int64) * (int(key.max()) + 1) + key[ok]; u, inv = np.unique(kk, return_inverse=True)
    s = np.bincount(inv, m[ok]); return np.bincount(u // (int(key.max()) + 1), s ** 2, nb)


XD_CELLS = ("D2", "D3", "D4", "D5")   # the treatments the thinned extra-descents files represent (both_burst_thin.py cells)


def pooled(sd, handoff, xd):
    """Per treatment: (t, lat, lat0011, parent, family, state). With XD (a dir of g<k>/ groups from run_j_supplement_xd.sh),
    D2-D5 pool the first pass (64 descents per parent) and the extra pass (n_x per parent) parent by parent with the fixed weights
    64/(64 + n_x) and n_x/(64 + n_x) for the parents in a completed group; exact (the groups are chosen on the 00:11 state only)."""
    R = row_terms(sd, handoff); base = (R["lat"], R["lat0011"], R["par"], R["fam"], R["state"])
    out = {d: (R["t"][d],) + base for d in CELLS}; info = {"xd_groups": 0, "xd_parents": 0}
    if not xd: return out, R["n_handoff"], info
    groups = sorted(pathlib.Path(xd).glob("g[0-9]*/SHA256SUMS"))
    if not groups: return out, R["n_handoff"], info
    n1 = 64.0; sel = np.zeros(R["n_handoff"], bool); ext = {d: [] for d in XD_CELLS}
    for f in groups:
        gd = f.parent; S = json.load(open(gd / "select.json")); idx = np.asarray(S["subset_index"], np.int64)
        meta = json.load(open(gd / "run.json")); nx = float(meta["config"]["terminal"]["children"] * 4)
        Rg = row_terms(gd, gd / "handoff.npy"); pg = idx[Rg["par"]]; sel[idx] = True
        info["xd_groups"] += 1; info["xd_parents"] += len(idx); info["n_x"] = nx
        for d in XD_CELLS:
            ext[d].append((Rg["t"][d] + np.log(nx / (n1 + nx)), Rg["lat"], Rg["lat0011"], pg, Rg["fam"], Rg["state"]))
    a = np.where(sel[R["par"]], np.log(n1 / (n1 + info["n_x"])), 0.0)
    for d in XD_CELLS:
        parts = [(R["t"][d] + a,) + base] + ext[d]
        out[d] = tuple(np.concatenate([q[i] for q in parts]) for i in range(6))
    return out, R["n_handoff"], info


def part(sd, handoff, tech, outp, xd=None):
    S1, S2, N1, N2, K = (float(os.environ[v]) for v in ("SUP_S1", "SUP_S2", "SUP_N1", "SUP_N2", "SUP_K"))
    T, nh, info = pooled(sd, handoff, xd)
    nb = len(BANDS) - 1; nf = len(FINE) - 1
    out = {"n_rows": len(T["D0"][1]), "n_handoff": nh, "xd_groups": info["xd_groups"], "xd_parents": info["xd_parents"]}
    for d, (t, lat, lat0, par, fam, state) in T.items():
        r = r_hat(lat0); beta1 = N1 / (N1 + N2 * r); beta2 = N2 * r / (N1 + N2 * r)
        c = {"alone": np.full(len(lat), 1.0 / S1), "comb": beta1 / S1} if tech == "prod" else {"comb": beta2 * K / S2}
        fi = np.clip(np.floor((lat - FINE[0]) / 0.1 + 1e-9).astype(int), 0, nf - 1)
        f0 = np.clip(np.floor((lat0 - FINE[0]) / 0.1 + 1e-9).astype(int), 0, nf - 1)
        bi = np.digitize(lat, BANDS) - 1; b0 = np.digitize(lat0, BANDS) - 1
        for v, cv in c.items():
            m = np.zeros(len(t)); fin = np.isfinite(t); m[fin] = np.exp(t[fin]) * cv[fin]
            for name, idx in (("imp", fi), ("h11", f0)):
                out[f"{v}/{d}/{name}/m"] = np.stack([np.bincount(idx[fam == j], m[fam == j], nf) for j in range(4)])
                out[f"{v}/{d}/{name}/m2"] = np.stack([np.bincount(idx[fam == j], m[fam == j] ** 2, nf) for j in range(4)])
            for name, bb in (("imp", bi), ("h11", b0)):
                for j, fsel in (("all", None), ("A1", 0), ("A2", 1), ("B", 2)):
                    mm = m if fsel is None else np.where(fam == fsel, m, 0.0)
                    out[f"{v}/{d}/{name}/par2/{j}"] = group_sq(par, bb, mm, nb)
                    out[f"{v}/{d}/{name}/st2/{j}"] = group_sq(state, bb, mm, nb)
    np.savez_compressed(outp, **out); print(f"part {tech} {sd}: {out['n_rows']} rows; extra groups {info['xd_groups']}", flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "part": part(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6] if len(sys.argv) > 6 else None)
    elif sys.argv[1] == "rhat-check": print(r_hat(np.array([-36.0, -34.25, -30.1, -25.2, -21.2, -20.0])))
