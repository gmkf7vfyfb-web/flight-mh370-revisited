"""Injection-recovery for the two-epoch windage calibration, with the COSMO pass time (9 Oct ruling).

Simulation-based calibration, so coverage is checkable: for each replicate draw the true windage
from its prior (a node of the export grid), the true K from its prior, offset 0, and a true pass time
(fixed per experiment). The first k of F1-F3 (k = 1, 2, 3; contacts chosen at random) truly drifted
with that windage; their simulated Pleiades positions are the deterministic track plus Gaussian
spread drawn from the same analytic model (independent or shared model error). The six real
rating-5 clusters stay in the scene as distractors, so the enumeration faces the real ambiguity.

The identical analysis then runs twice: with the pass time marginalised, and with it known.
Reported per (true pass, k, error model): coverage of the 68 % and 90 % central credible intervals
(randomised PIT on the discrete grid), mean information gain in bits, median |posterior mean - truth|,
correlation of posterior mean with truth, P(true pass | D).

Usage: python injection.py <cosmo-tracks.csv> <data/targets-3km.csv> <outdir> [n_rep]
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import twoepoch as te  # noqa: E402


def simulate(tr, cfg, rng, true_pass, k, real_targets):
    contacts = ["F1", "F2", "F3"]
    ci = int(rng.integers(len(tr.c)))
    lnk = rng.uniform(np.log(cfg.k_range[0]), np.log(cfg.k_range[1]))
    K = float(np.exp(lnk))
    chosen = list(rng.choice(contacts, size=k, replace=False))
    p = te.PASSES.index(true_pass)
    t_scene = te.PLEIADES_T["PHR_4"]
    tj = int(np.argmin(np.abs(tr.times - t_scene)))
    dt = t_scene - te.PASS_T[true_pass]
    var = 2 * K * dt / 1e6 + te.var_ou_km2(cfg.sigma_e_ms, cfg.T_e_s, dt) + cfg.sd_cosmo_km**2 + cfg.sd_target_km**2
    rows = []
    shared = None
    if cfg.shared_error:
        ou = te.var_ou_km2(cfg.sigma_e_ms, cfg.T_e_s, dt)
        shared = rng.normal(0, np.sqrt(ou), 2)
        var = var - ou
    for cid in chosen:
        x = tr.X[tr.contacts.index(cid), p, 1, ci, tj]
        d = rng.normal(0, np.sqrt(var), 2) + (shared if shared is not None else 0)
        lat = x[1] + d[1] / te.KM_PER_DEG
        lon = x[0] + d[0] / (te.KM_PER_DEG * np.cos(np.radians(lat)))
        rows.append(dict(scene="PHR_4", lon=lon, lat=lat, w=1.0, truth=cid))
    t = pd.concat([pd.DataFrame(rows), real_targets.assign(truth="")[["scene", "lon", "lat", "w", "truth"]]], ignore_index=True)
    t["w"] = 1.0 / len(t)
    return t, ci, K


def pit(post, ci, rng):
    cdf = np.cumsum(post)
    lo = cdf[ci - 1] if ci > 0 else 0.0
    return lo + rng.uniform() * post[ci]


def run(tracks_csv, clusters_csv, out, n_rep=200, seed=20261009, configs=None):
    tr = te.Tracks.load(Path(tracks_csv))
    cl = pd.read_csv(clusters_csv)
    c5 = cl[cl.arm == "rating5"].copy()
    real = pd.DataFrame({"scene": c5.scene, "lon": c5.lon, "lat": c5.lat, "w": 1.0})
    rows = []
    configs = configs or [te.Config(shared_error=False), te.Config(shared_error=True, label="shared-error")]
    for cfg in configs:
        shared = cfg.shared_error
        for true_pass in te.PASSES:
            for k in (1, 2, 3):
                rng = np.random.default_rng([seed, int(shared), te.PASSES.index(true_pass), k])
                for r in range(n_rep):
                    targets, ci, K = simulate(tr, cfg, rng, true_pass, k, real)
                    for mode in ("marginalised", "known"):
                        R = te.analyse(tr, ["F1", "F2", "F3"], targets, cfg, pass_fixed=(true_pass if mode == "known" else None))
                        u = pit(R["post_c"], ci, rng)
                        rows.append(dict(config=cfg.label, error="shared" if shared else "independent", true_pass=true_pass, k=k, rep=r, mode=mode,
                                         c_true=tr.c[ci], K_true=K, c_mean=R["mean_c"], ig_bits=R["ig_bits"],
                                         ln_bf=R["ln_bf_free_vs_fixed"], pit=u, p_true_pass=R["p_pass"][te.PASSES.index(true_pass)],
                                         p_any=R["p_any_match"]))
    d = pd.DataFrame(rows)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    d.to_csv(out / "injection-replicates.csv", index=False)
    g = d.groupby(["config", "error", "true_pass", "k", "mode"])
    s = pd.DataFrame({
        "n": g.size(),
        "cover68": g.pit.apply(lambda u: float(((u > 0.16) & (u < 0.84)).mean())),
        "cover90": g.pit.apply(lambda u: float(((u > 0.05) & (u < 0.95)).mean())),
        "ig_bits_mean": g.ig_bits.mean(),
        "ig_bits_p90": g.ig_bits.quantile(0.9),
        "abs_err_median_pct": g.apply(lambda x: float(100 * np.median(np.abs(x.c_mean - x.c_true))), include_groups=False),
        "corr_mean_truth": g.apply(lambda x: float(np.corrcoef(x.c_mean, x.c_true)[0, 1]), include_groups=False),
        "ln_bf_median": g.ln_bf.median(),
        "p_true_pass_mean": g.p_true_pass.mean(),
        "p_any_mean": g.p_any.mean(),
    }).reset_index()
    s.to_csv(out / "injection-summary.csv", index=False)
    return d, s


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 200)


def floor_scan(tracks_csv, clusters_csv, out, n_rep=30, k=3):
    """Map the information floor: IG and error against a FIXED spread (K, sigma_e) and match prior,
    simulated and analysed under the same model, k true matches, both pass times."""
    cfgs = []
    for K in (30.0, 100.0, 248.0, 1000.0):
        for se in (0.0, 0.05):
            for pm in (0.5, 0.9):
                cfgs.append(te.Config(k_range=(K, K), sigma_e_ms=se, pi_match=pm, label=f"K{K:g}-se{se:g}-pi{pm:g}"))
    tr = te.Tracks.load(Path(tracks_csv))
    cl = pd.read_csv(clusters_csv)
    c5 = cl[cl.arm == "rating5"]
    real = pd.DataFrame({"scene": c5.scene, "lon": c5.lon, "lat": c5.lat, "w": 1.0})
    rows = []
    for cfg in cfgs:
        for true_pass in te.PASSES:
            rng = np.random.default_rng([20261009, te.PASSES.index(true_pass), k])
            dt = te.PLEIADES_T["PHR_4"] - te.PASS_T[true_pass]
            sd = float(np.sqrt(2 * cfg.k_range[0] * dt / 1e6 + te.var_ou_km2(cfg.sigma_e_ms, cfg.T_e_s, dt) + cfg.sd_cosmo_km**2 + cfg.sd_target_km**2))
            for r in range(n_rep):
                targets, ci, K = simulate(tr, cfg, rng, true_pass, k, real)
                for mode in ("marginalised", "known"):
                    R = te.analyse(tr, ["F1", "F2", "F3"], targets, cfg, pass_fixed=(true_pass if mode == "known" else None))
                    rows.append(dict(config=cfg.label, K=cfg.k_range[0], sigma_e=cfg.sigma_e_ms, pi_match=cfg.pi_match, sd_km=sd,
                                     true_pass=true_pass, mode=mode, rep=r, c_true=tr.c[ci], c_mean=R["mean_c"],
                                     ig_bits=R["ig_bits"], pit=pit(R["post_c"], ci, rng), p_any=R["p_any_match"],
                                     p_true_pass=R["p_pass"][te.PASSES.index(true_pass)]))
    d = pd.DataFrame(rows)
    Path(out).mkdir(parents=True, exist_ok=True)
    d.to_csv(Path(out) / "floor-scan-replicates.csv", index=False)
    g = d.groupby(["K", "sigma_e", "pi_match", "true_pass", "mode"])
    s = pd.DataFrame({"sd_km": g.sd_km.first(), "ig_bits_mean": g.ig_bits.mean(),
                      "abs_err_median_pct": g.apply(lambda x: float(100 * np.median(np.abs(x.c_mean - x.c_true))), include_groups=False),
                      "cover68": g.pit.apply(lambda u: float(((u > 0.16) & (u < 0.84)).mean())),
                      "p_any_mean": g.p_any.mean(), "p_true_pass_mean": g.p_true_pass.mean()}).reset_index()
    s.to_csv(Path(out) / "floor-scan-summary.csv", index=False)
    return d, s
