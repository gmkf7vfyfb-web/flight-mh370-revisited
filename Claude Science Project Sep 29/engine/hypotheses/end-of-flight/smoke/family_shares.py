"""Posterior share of each end-to-end hypothesis family, per stratum (core family), per 00:19 option and existence
constraint, with the seed-to-seed standard error; plus per-family weighted median impact latitude, mean cross-track
displacement from the takeover track (NM, + = right) and the left-turn share of the free-flight rows.

Families: compact_impacts.family_labels(..., recovery_attempted) `family4_code` - architecture ruling 6 (16:25 -0600
10 Oct) as amended by end of flight 22:45 UTC: A1, A2 (with sub-label 'lost'), B (incl. control lost en route), outside B.
WARNING carried into every output: from the 00:11 hand-off these shares are mostly the module prior (gaps G1-G4); they are
not an A-vs-B test. The A-vs-B test is the 22:41 hand-off (run C m2241 rows).

Usage: python family_shares.py EXCHANGE_RUN_DIR OUT_JSON [P_core as stratum=value ...]   (no P_core: per stratum only)
"""
import json, sys, pathlib
import numpy as np
from displacement_hist import option_posteriors
from compact_impacts import open_seed, family_labels

OPTIONS = {"none__other": "00:19 Held Out", "r600-bto__other": "00:19 R600 BTO Only",
           "r600_no-offset__other": "00:19 R600 BTO + Raw BFO",
           "both_startup-offset__fuel-exhaustion": "00:19 Holland H1", "both_no-offset__other": "00:19 Holland H2"}
CONSTRAINTS = ("alive", "unpowered", "silent")
FAMS = {1: "A1", 2: "A2", 3: "B", 6: "outside B"}


def wmedian(x, w):
    o = np.argsort(x); c = np.cumsum(w[o]); return float(x[o][np.searchsorted(c, 0.5 * c[-1])]) if c[-1] > 0 else float("nan")


def per_seed(sd):
    meta, g = open_seed(sd, sd)
    f = family_labels(g("latent:onset_mechanism"), g("latent:control_realised"), g("latent:recovery_attempted"))
    f4, lost = f["family4_code"], f["a2_lost"]
    lat, lon = g("latitude_deg"), g("longitude_deg")
    tl, tn = g("takeover_latitude_deg"), g("takeover_longitude_deg")
    ve, vn = g("latent:takeover_ground_velocity_east_mps"), g("latent:takeover_ground_velocity_north_mps")
    dn = (lat - tl) * 60; de = (lon - tn) * 60 * np.cos(np.radians(tl)); sp = np.hypot(ve, vn)
    cross = (de * vn - dn * ve) / sp
    speed = np.sqrt(g("velocity_east_mps") ** 2 + g("velocity_north_mps") ** 2 + g("velocity_up_mps") ** 2); fast = speed > 212.0
    sign = g("latent:residual_bank_sign") if "latent:residual_bank_sign" in meta["impact_columns"] else np.full_like(lat, np.nan)
    out = {}
    for key, p, _ in option_posteriors(sd, sd, constraints=CONSTRAINTS):
        base, _, con = key.partition("+")
        if base not in OPTIONS:
            continue
        name0 = OPTIONS[base] + (f" +{con}" if con else "")
        removed = {"total": float(p[fast].sum())}
        # Architecture ruling 20:35 -0600 (G13): also the version with contact speed <= 212 m/s, re-weighted, and the weight removed.
        for name, q in ((name0, p), (name0 + " ~v212", np.where(fast, 0.0, p) / max(float(p[~fast].sum()), 1e-300))):
            r = {}
            for code, fam in FAMS.items():
                s = f4 == code; m = float(q[s].sum()); ok = s & np.isfinite(cross); free = s & np.isfinite(sign)
                r[fam] = {"share": m,
                          "median_lat": wmedian(lat[s], q[s]) if m > 0 else None,
                          "mean_cross_nm": float((q[ok] * cross[ok]).sum() / q[ok].sum()) if q[ok].sum() > 0 else None,
                          "free_left_share": float(q[free][sign[free] == -1].sum() / q[free].sum()) if q[free].sum() > 0 else None}
                if name == name0:
                    removed[fam] = float(p[s & fast].sum() / m) if m > 0 else None
            r["A2"]["lost_share_of_A2"] = float(q[lost == 1].sum() / r["A2"]["share"]) if r["A2"]["share"] > 0 else None
            r["eff_impacts"] = float(1 / (q ** 2).sum())
            out[name] = r
        out[name0]["removed_by_v212_share_of_family"] = removed
    return out


def main(root, outp, pcore):
    root = pathlib.Path(root)
    strata = sorted(d.name for d in root.iterdir() if d.is_dir() and any(d.glob("seed-*"))) if not pcore else list(pcore)
    res = {"warning": "mostly the module prior from the 00:11 hand-off (coverage gaps G1-G4); not an A-vs-B test",
           "families": "ruling 6 as amended 22:45 UTC 10 Oct (family_shares.py docstring)", "p_core": pcore, "strata": {}}
    for st in strata:
        seeds = sorted(d for d in (root / st).glob("seed-*") if (d / "impacts32.npy").exists() or (d / "impacts.npy").exists())
        rows = [per_seed(d) for d in seeds]; res["strata"][st] = {"seeds": [d.name for d in seeds]}
        for key in rows[0]:
            e = {}
            for fam in FAMS.values():
                sh = np.array([r[key][fam]["share"] for r in rows])
                e[fam] = {"share": float(sh.mean()), "share_se": float(sh.std(ddof=1) / np.sqrt(len(sh))) if len(sh) > 1 else None}
                for k in ("median_lat", "mean_cross_nm", "free_left_share"):
                    v = [r[key][fam][k] for r in rows if r[key][fam][k] is not None]
                    e[fam][k] = float(np.mean(v)) if v else None
            if "removed_by_v212_share_of_family" in rows[0][key]:
                e["removed_by_v212_share_of_family"] = {f: (float(np.mean([r[key]["removed_by_v212_share_of_family"][f] for r in rows if r[key]["removed_by_v212_share_of_family"][f] is not None])) if any(r[key]["removed_by_v212_share_of_family"][f] is not None for r in rows) else None) for f in rows[0][key]["removed_by_v212_share_of_family"]}
            v = [r[key]["A2"]["lost_share_of_A2"] for r in rows if r[key]["A2"]["lost_share_of_A2"] is not None]
            e["A2"]["lost_share_of_A2"] = float(np.mean(v)) if v else None
            e["eff_impacts_per_seed"] = [r[key]["eff_impacts"] for r in rows]
            res["strata"][st][key] = e
    if pcore:
        res["mixture_fixed_p_core"] = {}
        for key in res["strata"][strata[0]]:
            if key == "seeds":
                continue
            res["mixture_fixed_p_core"][key] = {fam: float(sum(pcore[s] * res["strata"][s][key][fam]["share"] for s in strata))
                                                 for fam in FAMS.values()}
    pathlib.Path(outp).write_text(json.dumps(res, indent=1))
    for st in strata:
        for key, e in res["strata"][st].items():
            if key != "seeds":
                print(f"{st:18s} {key:36s}", " ".join(f"{f}:{e[f]['share']:.3f}" for f in FAMS.values()))


if __name__ == "__main__":
    pc = {k: float(v) for k, v in (a.split("=") for a in sys.argv[3:])}
    main(sys.argv[1], sys.argv[2], pc)
