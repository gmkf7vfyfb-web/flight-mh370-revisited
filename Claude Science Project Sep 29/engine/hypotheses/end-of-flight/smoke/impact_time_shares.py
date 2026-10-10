"""Impact-time shares against the 00:19:37 burst and the unanswered 01:15:56 handshake, and the effect of the
existence constraints, for one end-of-flight product (hydroacoustics' validation gate; architecture 10 Oct).

Same estimands and JSON keys as results/eof-impact-time-oct10 (reference-289), plus the `unpowered` variant
(airborne at 00:19:37 AND not powered at 01:15:56; architecture ruling ~19:10 UTC 10 Oct, variant (b)).
Reads either layout:
  run layout       RUN/run.json + RUN/bto-bfo/seed-k/impacts.npy   (pass RUN; all seeds)
  exchange layout  STRATUM/seed-k/{run.json, impacts.npy}          (pass STRATUM)
Shares are seed means of option-posterior weight (plain option x cause, no constraint), as before.
Usage: python impact_time_shares.py SRC OUT_PREFIX     -> OUT_PREFIX-impact-time-shares.json, OUT_PREFIX-constraints.json
"""
import json, pathlib, sys, datetime
import numpy as np
from displacement_hist import option_posteriors, constraint_log_factor, T_M0019B, T_LOI_0115

CONS = ("alive", "unpowered", "silent")


def seeds_of(src):
    src = pathlib.Path(src)
    if (src / "run.json").exists() and (src / "bto-bfo").exists():
        return [(src, d) for d in sorted((src / "bto-bfo").glob("seed-*")) if (d / "impacts.npy").exists()]
    return [(d, d) for d in sorted(src.glob("seed-*")) if (d / "impacts.npy").exists()]


def wq(x, w, qs):
    o = np.argsort(x); c = np.cumsum(w[o]); c /= c[-1]
    return [float(x[o][min(np.searchsorted(c, q), len(o) - 1)]) for q in qs]


def utc(t):
    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%H:%M:%S")


def main(src, prefix):
    per = {}
    for run, sd in seeds_of(src):
        meta = json.loads((run / "run.json").read_text()); cols = {c: i for i, c in enumerate(meta["impact_columns"])}
        X = np.load(sd / "impacts.npy", mmap_mode="r")
        t = np.asarray(X[:, cols["unix_s"]], float); fo = np.asarray(X[:, cols["latent:realised_flameout_unix_s"]], float)
        lat = np.asarray(X[:, cols["latitude_deg"]], float)
        powered = (t > T_LOI_0115) & (~np.isfinite(fo) | (fo > T_LOI_0115))
        g = lambda k: np.asarray(X[:, cols[k]], float); logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
        factors = {(cause, c): np.exp(constraint_log_factor(g, logon, cause, c)) for cause in ("other", "fuel-exhaustion") for c in CONS}
        for key, p, _ in option_posteriors(run, sd, constraints=CONS):
            base, _, con = key.partition("+")
            d = per.setdefault(base, {"plain": [], **{c: [] for c in CONS}})
            ok = np.isfinite(lat) & (p > 0)
            row = {"ess": float(p.sum() ** 2 / (p ** 2).sum()), "median_lat": wq(lat[ok], p[ok], (0.5,))[0]}
            if not con:
                row.update(before=float(p[t <= T_M0019B].sum()), after=float(p[t > T_LOI_0115].sum()), powered=float(p[powered].sum()),
                           q=wq(t[p > 0], p[p > 0], (0.05, 0.5, 0.95)),
                           retained={c: float((p * factors[(base.split("__")[1], c)]).sum()) for c in CONS})
            d[con or "plain"].append(row)
    shares, consj = {}, {}
    for base, d in per.items():
        P = d["plain"]
        shares[base] = {"share_before_001937": float(np.mean([r["before"] for r in P])),
                        "share_after_011556": float(np.mean([r["after"] for r in P])),
                        "share_powered_at_011556": float(np.mean([r["powered"] for r in P])),
                        "per_seed": [[r["before"], r["after"], r["powered"]] for r in P],
                        "impact_q05_q50_q95_utc_seed_mean": [utc(np.mean([r["q"][i] for r in P])) for i in range(3)]}
        consj[base] = {"median_lat_plain_" + "_".join(CONS): [float(np.mean([r["median_lat"] for r in d[k]])) if d[k] else None for k in ("plain",) + CONS],
                       "ess_plain_" + "_".join(CONS): [float(np.sum([r["ess"] for r in d[k]])) if d[k] else None for k in ("plain",) + CONS],
                       **{f"retained_{c}": float(np.mean([r["retained"][c] for r in P])) for c in CONS},
                       **{f"ln_retained_{c}": float(np.log(np.mean([r["retained"][c] for r in P]))) for c in CONS},
                       "n_seeds": len(P)}
    pathlib.Path(prefix + "-impact-time-shares.json").write_text(json.dumps(shares, indent=1))
    pathlib.Path(prefix + "-constraints.json").write_text(json.dumps(consj, indent=1))
    return shares, consj


if __name__ == "__main__":
    s, c = main(sys.argv[1], sys.argv[2])
    for k in ("none__other", "none__fuel-exhaustion", "r600-bto__other", "r600_no-offset__other"):
        if k in s: print(k, round(s[k]["share_before_001937"], 4), round(s[k]["share_after_011556"], 4), round(s[k]["share_powered_at_011556"], 4), s[k]["impact_q05_q50_q95_utc_seed_mean"], [round(x, 2) if x else x for x in c[k]["median_lat_plain_alive_unpowered_silent"]])
