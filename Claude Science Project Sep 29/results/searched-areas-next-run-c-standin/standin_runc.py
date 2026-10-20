#!/usr/bin/env python3
"""Architecture stand-in for searched areas, run C: the rulings applied beside the module's own run_release.sh output.

    python standin_runc.py <engine dir> <out dir>

Nothing here is new physics or a new likelihood. Imported unchanged:
  * this module's `impact_map_options` (search_loglik, density, hpd_areas, weighted_quantile, DEFAULT keys, ESS_FLOOR);
  * end of flight's `option_posteriors` (00:19 option weighting, +alive) and `family_evidence.per_seed` (ln Zhat_00:19 per
    stratum, plain and with the 212 m/s cap, end of flight's own convention: faster rows get zero likelihood).
    `family_evidence.CONSTRAINTS_ALL` is narrowed at run time to ('alive', 'alive ~v212') to skip unused keys (speed only).

Per stratum and 00:19 option (the five ruled core options, +alive), two row sets:
  all   - every impact;
  v212  - contact speed |v| <= 212 m/s (1.25 VMO, ruling 20:35 -0600 10 Oct), weights re-normalised per seed.
Mixtures of the four strata (densities and Z combine linearly; seeds equal weight within a stratum):
  fixed       - core's run C P(family), passed in;  for v212 multiplied by each stratum's kept fraction (conditioning
                 on feasibility), re-normalised;
  reweighted  - P_core x Zhat_00:19(stratum, option) [x kept fraction, via end of flight's ~v212 key], re-normalised.
Ruling (a): rows whose search log-likelihood is not finite are carried at the neutral value 0 and their weight reported.
"""
import json
import pathlib
import sys
import time

import numpy as np

ENGINE = pathlib.Path(sys.argv[1]).resolve()
OUT = pathlib.Path(sys.argv[2]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ENGINE / "hypotheses" / "seabed-search"))
import impact_map_options as imo  # noqa: E402  (also puts end of flight's smoke/ on sys.path)
import family_evidence as fe  # noqa: E402
from compact_impacts import load as load_compact  # noqa: E402

fe.CONSTRAINTS_ALL = ("alive", "alive ~v212")
P_CORE = {"next-c-descent-climb": 0.135, "next-c-free": 0.589, "next-c-repro-radar": 0.252, "next-c-routes": 0.024}
assert abs(sum(P_CORE.values()) - 1.0) < 1e-9
VMAX = 212.0
KEYS = list(imo.DEFAULT)
EOF_NAME = {"none__other+alive": "00:19 Held Out", "r600-bto__other+alive": "00:19 R600 BTO Only",
            "r600_no-offset__other+alive": "00:19 R600 BTO + Raw BFO",
            "both_startup-offset__fuel-exhaustion+alive": "00:19 Holland H1", "both_no-offset__other+alive": "00:19 Holland H2"}
FAM4 = {1: "A1", 2: "A2", 3: "B", 6: "code 6 (deliberate onset, no intervention)"}
REGIONS = {"Phase 2 searched (covered fraction >= 0.5)": lambda c, lat: c >= 0.5,
           "not on Phase 2 ground": lambda c, lat: c < 0.5,
           "north of 33 S": lambda c, lat: lat > -33.0, "33-36 S": lambda c, lat: (lat <= -33.0) & (lat > -36.0),
           "36-39 S": lambda c, lat: (lat <= -36.0) & (lat > -39.0), "south of 39 S": lambda c, lat: lat <= -39.0}
VARS = ("all", "v212")


def ess(p):
    s = p.sum()
    return float(s * s / np.sum(p * p)) if s > 0 else 0.0


acc = {}
seedinfo = {}
scratch = ENGINE / "runs" / "seabed-search-analysis" / "standin-c"
scratch.mkdir(parents=True, exist_ok=True)
t0 = time.time()
for st in P_CORE:
    run = ENGINE / "runs" / f"c-{st}"
    seeds = sorted((run / "bto-bfo").glob("seed-*"))
    assert len(seeds) == 8, (st, len(seeds))
    for sd in seeds:
        ll, cov = imo.search_loglik(run, sd, scratch)
        nc = ~np.isfinite(ll)
        ll = np.where(nc, 0.0, ll)                       # ruling (a): carried at neutral
        like = np.exp(ll)
        meta, g = load_compact(sd)
        spd = np.sqrt(g("velocity_east_mps") ** 2 + g("velocity_north_mps") ** 2 + g("velocity_up_mps") ** 2)
        slow = spd <= VMAX
        f4 = g("family4_code")
        ev = fe.per_seed(sd)
        seedinfo.setdefault(st, {})[sd.name] = {"rows": int(ll.size), "not_computed_rows": int(nc.sum())}
        for key, p, c in imo.option_posteriors(run, sd, constraints=("alive",)):
            if key not in KEYS:
                continue
            lat, lon = c["lat"], c["lon"]
            for var in VARS:
                q = p if var == "all" else p * slow
                kept = float(q.sum())
                q = q / kept
                after = q * like
                z = float(after.sum())
                after = after / z
                a = acc.setdefault((st, key, var), {"n": 0, "z": [], "kept": [], "lnZ0019": [], "eff_par": [],
                                                    "on_p2_b": 0.0, "on_p2_a": 0.0, "ess_b": 0.0, "ess_a": 0.0,
                                                    "dens_b": 0.0, "dens_a": 0.0, "lat_b": 0.0, "lat_a": 0.0,
                                                    "nc_w": 0.0, "fam_b": {}, "fam_a": {}, "fam_removed": {},
                                                    "fam_ess_a": {}, "reg_ess_b": {}, "reg_ess_a": {}, "reg_mass_a": {}})
                a["n"] += 1
                a["z"].append(z)
                a["kept"].append(kept)
                e = ev[(EOF_NAME[key], "alive" if var == "all" else "alive ~v212")]
                a["lnZ0019"].append(e["ln_Z"])
                a["eff_par"].append(e["eff_parents"])
                a["on_p2_b"] += float((q * cov).sum())
                a["on_p2_a"] += float((after * cov).sum())
                a["ess_b"] += ess(q)
                a["ess_a"] += ess(after)
                a["nc_w"] += float(q[nc].sum())
                a["dens_b"] = a["dens_b"] + imo.density(lat, lon, q)
                a["dens_a"] = a["dens_a"] + imo.density(lat, lon, after)
                a["lat_b"] = a["lat_b"] + np.histogram(lat, bins=imo.QN, range=imo.QRANGE, weights=q)[0]
                a["lat_a"] = a["lat_a"] + np.histogram(lat, bins=imo.QN, range=imo.QRANGE, weights=after)[0]
                for code, nm in FAM4.items():
                    m = f4 == code
                    a["fam_b"][nm] = a["fam_b"].get(nm, 0.0) + float(q[m].sum())
                    a["fam_a"][nm] = a["fam_a"].get(nm, 0.0) + float(after[m].sum())
                    a["fam_ess_a"][nm] = a["fam_ess_a"].get(nm, 0.0) + ess(after[m])
                    if var == "all":
                        a["fam_removed"][nm] = a["fam_removed"].get(nm, 0.0) + float(p[m & ~slow].sum())
                if var == "all":
                    a["fam_removed"]["all"] = a["fam_removed"].get("all", 0.0) + float(p[~slow].sum())
                for rn, fn in REGIONS.items():
                    m = fn(cov, lat)
                    a["reg_ess_b"][rn] = a["reg_ess_b"].get(rn, 0.0) + ess(q[m])
                    a["reg_ess_a"][rn] = a["reg_ess_a"].get(rn, 0.0) + ess(after[m])
                    a["reg_mass_a"][rn] = a["reg_mass_a"].get(rn, 0.0) + float(after[m].sum())
        print(f"{st} {sd.name} done {time.time() - t0:.0f}s", flush=True)
        del ll, cov, like, spd, slow, f4, ev, g, meta


def summarise(dens_b, dens_a, lat_b, lat_a):
    lv_b, lv_a = imo.hpd_levels(dens_b, imo.LEVELS), imo.hpd_levels(dens_a, imo.LEVELS)
    return {"median_lat_before": imo.weighted_quantile(imo.QLAT, lat_b, 0.5),
            "median_lat_after": imo.weighted_quantile(imo.QLAT, lat_a, 0.5),
            "hpd_km2_before": dict(zip(["99", "90", "50"], imo.hpd_areas(dens_b, lv_b))),
            "hpd_km2_after": dict(zip(["99", "90", "50"], imo.hpd_areas(dens_a, lv_a)))}


res = {"p_core": P_CORE, "vmax_mps": VMAX, "keys": KEYS, "strata": {}, "mixtures": {}, "seeds": seedinfo}
mixdens = {}
for (st, key, var), a in acc.items():
    n = a["n"]
    zhat = float(np.mean(np.exp(a["lnZ0019"])))
    r = {"seeds": n, "evidence_z": float(np.mean(a["z"])), "z_per_seed": a["z"],
         "z_split_half": [float(np.mean(a["z"][: n // 2])), float(np.mean(a["z"][n // 2:]))],
         "kept_fraction": float(np.mean(a["kept"])), "zhat_0019": zhat, "ln_zhat_0019": float(np.log(zhat)),
         "eff_parents_0019": float(np.sum(a["eff_par"])),
         "on_phase2_before": a["on_p2_b"] / n, "on_phase2_after": a["on_p2_a"] / n,
         "ess_before": a["ess_b"], "ess_after": a["ess_a"], "not_computed_weight": a["nc_w"] / n,
         "family_share_before": {k: v / n for k, v in a["fam_b"].items()},
         "family_share_after": {k: v / n for k, v in a["fam_a"].items()},
         "family_ess_after": a["fam_ess_a"],
         "weight_above_212_by_family": {k: v / n for k, v in a["fam_removed"].items()},
         "region_ess_before": a["reg_ess_b"], "region_ess_after": a["reg_ess_a"],
         "region_mass_after": {k: v / n for k, v in a["reg_mass_a"].items()}}
    r.update(summarise(a["dens_b"] / n, a["dens_a"] / n, a["lat_b"] / n, a["lat_a"] / n))
    r["estimable_impact_ess"] = bool(r["ess_after"] >= imo.ESS_FLOOR)
    r["estimable_parents"] = bool(r["eff_parents_0019"] >= imo.ESS_FLOOR)
    res["strata"].setdefault(st, {}).setdefault(key, {})[var] = r

for key in KEYS:
    for var in VARS:
        for mix in ("fixed", "reweighted"):
            S = res["strata"]
            if mix == "fixed":
                raw = {st: P_CORE[st] * (1.0 if var == "all" else S[st][key][var]["kept_fraction"]) for st in P_CORE}
            else:
                raw = {st: P_CORE[st] * S[st][key][var]["zhat_0019"] for st in P_CORE}
            tw = sum(raw.values())
            W = {st: v / tw for st, v in raw.items()}
            A = {st: acc[(st, key, var)] for st in P_CORE}
            nn = {st: A[st]["n"] for st in P_CORE}
            db = sum(W[st] * A[st]["dens_b"] / nn[st] for st in P_CORE)
            da = sum(W[st] * A[st]["dens_a"] / nn[st] for st in P_CORE)
            lb = sum(W[st] * A[st]["lat_b"] / nn[st] for st in P_CORE)
            la = sum(W[st] * A[st]["lat_a"] / nn[st] for st in P_CORE)
            m = {"weights": W, "evidence_z": sum(W[st] * S[st][key][var]["evidence_z"] for st in P_CORE),
                 "z_split_half": [sum(W[st] * S[st][key][var]["z_split_half"][h] for st in P_CORE) for h in (0, 1)],
                 "strata_z_spread": max(S[st][key][var]["evidence_z"] for st in P_CORE)
                 - min(S[st][key][var]["evidence_z"] for st in P_CORE),
                 "on_phase2_before": sum(W[st] * S[st][key][var]["on_phase2_before"] for st in P_CORE),
                 "on_phase2_after": sum(W[st] * S[st][key][var]["on_phase2_after"] for st in P_CORE),
                 "ess_before": sum(S[st][key][var]["ess_before"] for st in P_CORE),
                 "ess_after": sum(S[st][key][var]["ess_after"] for st in P_CORE),
                 "eff_parents_0019": sum(S[st][key][var]["eff_parents_0019"] for st in P_CORE),
                 "family_share_after": {f: sum(W[st] * S[st][key][var]["family_share_after"][f] for st in P_CORE)
                                        for f in FAM4.values()},
                 "family_ess_after": {f: sum(S[st][key][var]["family_ess_after"][f] for st in P_CORE)
                                      for f in FAM4.values()},
                 "region_ess_after": {rn: sum(S[st][key][var]["region_ess_after"][rn] for st in P_CORE) for rn in REGIONS},
                 "not_computed_weight": sum(W[st] * S[st][key][var]["not_computed_weight"] for st in P_CORE)}
            if var == "all":
                m["weight_above_212_by_family"] = {f: sum(W[st] * S[st][key]["all"]["weight_above_212_by_family"].get(f, 0.0)
                                                         for st in P_CORE) for f in list(FAM4.values()) + ["all"]}
            m.update(summarise(db, da, lb, la))
            m["estimable"] = bool(m["ess_after"] >= imo.ESS_FLOOR and m["eff_parents_0019"] >= imo.ESS_FLOOR)
            res["mixtures"].setdefault(key, {}).setdefault(var, {})[mix] = m
            mixdens[f"{key}|{var}|{mix}|before"] = db.astype(np.float32)
            mixdens[f"{key}|{var}|{mix}|after"] = da.astype(np.float32)

(OUT / "standin-runc.json").write_text(json.dumps(res, indent=1) + "\n")
np.savez_compressed(OUT / "standin-runc-mixture-densities.npz", **mixdens)
print("wrote", OUT, f"{time.time() - t0:.0f}s")
