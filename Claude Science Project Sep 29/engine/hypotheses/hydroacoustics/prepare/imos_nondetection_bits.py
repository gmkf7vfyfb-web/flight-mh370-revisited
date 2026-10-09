"""EXPLORATORY (not pre-registered): information gain on the along-arc impact latitude from the 2b
non-detection, as a function of an ASSUMED P_D inside recordings (P_D is uncalibrated until item 3).
Coverage per stand-in sample = arrival (true UTC, convention A clock) inside a recording at a logger,
for the D1-scorable part (from 32 s after recording start). Impact time and celerity are marginalised
within latitude bins (0.25 deg). Optional third argument: loggers to exclude (e.g. 3250, whose geodesic
paths from every impact quantile are blocked by the North West Shelf; shared ocean transport, ruling H5). Posterior weight per bin = mean over its samples of
prod_loggers (1 - P_D * covered). Information gain = KL(posterior || prior) over bins, bits."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).parent))
import imos_preregistration as P  # noqa: E402
import imos_detectors as D  # noqa: E402

def main(summary, out, exclude=()):
    recs = pd.read_csv(Path(__file__).parent.parent / "data/imos/recordings.csv", parse_dates=["start_logger"])
    meta = P.parse_meta()
    rng = np.random.default_rng(P.sct.SEED)
    ridge, grid, dens, _ = P.sct.ridge_and_marginal(summary)
    q, _ = P.sct.fit_small_circle(ridge)
    pr = P.sct.draw_prior(rng, q, grid, dens, P.sct.N_PRIOR, P.sct.BASE["sigma_x_nm"])
    n = len(pr)
    t_imp = P.sct.BASE["mu_t_s"] + rng.normal(0, P.sct.BASE["sigma_t_s"], n)
    c = rng.normal(P.C_G, P.SD_C, n)
    ref = (P.T_IMPACT_REF - D.DAY0).total_seconds()
    cov = {}
    for cid in [c for c in D.LOGGERS if c not in exclude]:
        m = meta[str(cid)]
        _, _, d = P.GEOD.inv(np.full(n, m["lon"]), np.full(n, m["lat"]), pr[:, 1], pr[:, 0])
        ta = ref + t_imp + d / 1000 / c
        r = recs[recs.logger == cid]
        st = np.array([((t + pd.Timedelta(seconds=D.subsec(P.IMOS / f))) - pd.Timedelta(seconds=P.clock_err(m, t)) - D.DAY0).total_seconds()
                       for t, f in zip(r.start_logger, r.file)])
        inside = np.zeros(n, bool)
        for a, b in zip(st + 32, st + r.dur_s.values - 1):
            inside |= (ta >= a) & (ta <= b)
        cov[cid] = inside
    lat = pr[:, 0]
    bins = np.arange(np.floor(lat.min() * 4) / 4, lat.max() + 0.25, 0.25)
    idx = np.digitize(lat, bins)
    prior = np.bincount(idx, minlength=len(bins) + 1).astype(float); prior /= prior.sum()
    res = {"P_any_logger_scorable": float(np.mean(np.any(np.vstack(list(cov.values())), 0))),
           "coverage_scorable": {str(k): float(v.mean()) for k, v in cov.items()}, "bits": {}}
    for pd_ in [0.1, 0.3, 0.5, 1.0]:
        w = np.prod([1 - pd_ * cov[k] for k in cov], axis=0)
        post = np.bincount(idx, weights=w, minlength=len(bins) + 1); post /= post.sum()
        ok = post > 0
        res["bits"][str(pd_)] = float(np.sum(post[ok] * np.log2(post[ok] / prior[ok])))
    Path(out).write_text(json.dumps(res, indent=1)); print(json.dumps(res, indent=1))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], tuple(int(x) for x in sys.argv[3].split(",")) if len(sys.argv) > 3 else ())
