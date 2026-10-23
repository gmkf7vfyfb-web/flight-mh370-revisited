"""Rerun of the synthetic composer test's bearing rows with the literature's bearing-error model.

Ruled 2026-10-09 (coordination/HYDROACOUSTICS.md, morning rulings, item 7): the single-site-with-bearing
rows are not quotable as "modest" until rerun with the mixture from
results/hydroacoustics-literature-review.md, implication 6: a core of sigma 0.5-1 deg, a station
bias term, and a heavy tail (a 3-5 deg component) whose weight depends on SNR.

Everything else is unchanged from synthetic_composer_test.py: the same stand-in PDF, the same timing
model and baseline (sigma_x 20 NM, impact time N(300 s, 180 s), pick 10 s), the same 200,000 prior
samples, 300 truths and seed, and the same PRE-REGISTERED thresholds (material >= 1 bit, negligible
< 0.25 bit).

PRE-REGISTERED BEARING MODELS (fixed before the first run; do not edit after looking)
  t3-3.3      the original run's model: Student-t nu=3, sd 3.3 deg (reference row)
  mix-a       core N(0, 0.5 deg), tail weight 0.1, tail N(0, 4 deg)
  mix-b       core N(0, 1.0 deg), tail weight 0.1, tail N(0, 4 deg)
  mix-c       core N(0, 0.5 deg), tail weight 0.3, tail N(0, 4 deg)
  mix-d       core N(0, 1.0 deg), tail weight 0.3, tail N(0, 4 deg)
  For every mixture, a station bias N(0, 0.5 deg) is drawn once per truth and station. The
  likelihood does not know the bias; it carries the bias variance in quadrature in both components.
  The tail weight stands for the low-SNR end; it is a declared fixed value here because a marginal
  detection is by definition low SNR, and SNR-dependence enters once injection-recovery exists.
  Station sets with bearing: H01W, H08S, H08S+H08N, H01W+H08S, H01W+H08S+H08N.

Run: python prepare/bearing_mixture_rerun.py <summary.json> <out_dir>
"""

import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import synthetic_composer_test as sct  # noqa: E402

BIAS_SD = 0.5
MODELS = {
    "t3-3.3": None,
    "mix-a": (0.5, 0.1, 4.0),
    "mix-b": (1.0, 0.1, 4.0),
    "mix-c": (0.5, 0.3, 4.0),
    "mix-d": (1.0, 0.3, 4.0),
}


def log_mix(x, core, w, tail):
    c = np.hypot(core, BIAS_SD)
    t = np.hypot(tail, BIAS_SD)
    a = np.log1p(-w) - np.log(c) - 0.5 * (x / c) ** 2
    b = np.log(w) - np.log(t) - 0.5 * (x / t) ** 2
    m = np.maximum(a, b)
    return m + np.log(np.exp(a - m) + np.exp(b - m))


def draw_mix(rng, core, w, tail):
    sd = tail if rng.random() < w else core
    return sd * rng.normal()


def evaluate(rng, prior, geom, stations, cfg, model):
    s_al = prior[:, 2]
    w0 = np.full(len(prior), 1.0 / len(prior))
    prior_sd = np.sqrt(np.cov(s_al)); prior_mean = s_al.mean()
    m = len(stations)
    bscale = sct.BEARING_SD_DEG / np.sqrt(sct.BEARING_NU / (sct.BEARING_NU - 2))
    res = []
    for ti in rng.choice(len(prior), sct.K_TRUTHS, replace=False):
        sd = np.array([np.hypot(cfg["pick_s"], geom[s][0][ti] * sct.SD_C_KM_S / sct.C_KM_S**2) for s in stations])
        t_imp = cfg["mu_t_s"] + cfg["sigma_t_s"] * rng.normal()
        obs = np.array([t_imp + geom[s][0][ti] / sct.C_KM_S + sd[j] * rng.normal() for j, s in enumerate(stations)])
        r = obs[None, :] - cfg["mu_t_s"] - np.column_stack([geom[s][0] / sct.C_KM_S for s in stations])
        ci = np.linalg.inv(np.diag(sd**2) + cfg["sigma_t_s"] ** 2 * np.ones((m, m)))
        ll = -0.5 * np.einsum("ij,jk,ik->i", r, ci, r)
        for s in stations:
            if model is None:
                bt = geom[s][1][ti] + bscale * rng.standard_t(sct.BEARING_NU)
                ll += sct.log_t(sct.wrap180(bt - geom[s][1]), bscale, sct.BEARING_NU)
            else:
                bt = geom[s][1][ti] + BIAS_SD * rng.normal() + draw_mix(rng, *model)
                ll += log_mix(sct.wrap180(bt - geom[s][1]), *model)
        ll -= ll.max(); w = np.exp(ll); w /= w.sum(); nz = w > 0
        mu = np.sum(w * s_al); post_sd = np.sqrt(np.sum(w * (s_al - mu) ** 2))
        res.append((float(np.sum(w[nz] * np.log2(w[nz] / w0[nz]))), post_sd / prior_sd,
                    abs(mu - prior_mean) / post_sd, abs(mu - s_al[ti]), 1.0 / np.sum(w * w)))
    a = np.array(res)
    return {"info_bits_median": float(np.median(a[:, 0])), "info_bits_q10": float(np.quantile(a[:, 0], 0.1)),
            "info_bits_q90": float(np.quantile(a[:, 0], 0.9)), "sd_ratio_median": float(np.median(a[:, 1])),
            "shift_over_post_sd_median": float(np.median(a[:, 2])), "err_post_km_median": float(np.median(a[:, 3])),
            "ess_median": float(np.median(a[:, 4]))}


def main(summary_path, out_dir):
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(sct.SEED)
    ridge, grid, dens, _ = sct.ridge_and_marginal(summary_path)
    q, _ = sct.fit_small_circle(ridge)
    prior = sct.draw_prior(rng, q, grid, dens, sct.N_PRIOR, sct.BASE["sigma_x_nm"])
    geom = sct.station_geometry(prior)
    sets = [("H01W",), ("H08S",), ("H08S", "H08N"), ("H01W", "H08S"), ("H01W", "H08S", "H08N")]
    rows = []
    for name, model in MODELS.items():
        for st in sets:
            r = evaluate(rng, prior, geom, st, sct.BASE, model)
            rows.append({"bearing_model": name, "stations": "+".join(st), **r, "verdict": sct.verdict(r["info_bits_median"])})
            print(f"{name:7s} {'+'.join(st):16s} I={r['info_bits_median']:.2f} [{r['info_bits_q10']:.2f},{r['info_bits_q90']:.2f}] "
                  f"D={r['shift_over_post_sd_median']:.2f} -> {rows[-1]['verdict']}", flush=True)
    json.dump({"models": {k: v for k, v in MODELS.items()}, "bias_sd_deg": BIAS_SD, "base": sct.BASE, "rows": rows},
              open(out / "bearing-mixture-rerun.json", "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
