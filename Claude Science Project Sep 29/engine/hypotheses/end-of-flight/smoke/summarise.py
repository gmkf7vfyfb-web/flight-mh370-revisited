"""Pool a multi-seed contract.json (from analyse.py) with EQUAL WEIGHT PER SEED, as core pooled the
snapshots, and report the range across seeds beside every pooled number: that spread is the Monte
Carlo uncertainty at the scale run, and a pooled figure without it is not to be quoted.

    python3 summarise.py <contract.json> <summary.json>
"""
import json, sys
import numpy as np


def stats(values):
    v = np.array([x for x in values if x is not None and np.isfinite(x)], float)
    if not len(v):
        return None
    return {"pooled": float(v.mean()), "min": float(v.min()), "max": float(v.max()), "seeds": int(len(v))}


def main(src, dst):
    C = json.load(open(src))
    reps = C["replicates"]
    fam = C["families"]
    out = {"source": C["source"], "code_revision": C["code_revision"], "runtime_s": C["runtime_s"],
           "children": C["children"], "seeds": [r["seed"] for r in reps],
           "parents_per_seed": [r["parents"] for r in reps], "descents_per_seed": [r["descents"] for r in reps]}

    # Items 2-4.
    out["item2_parents_without_impact_total"] = int(sum(r["item2_parents_without_impact"] for r in reps))
    out["item3"] = {k: stats([r["item3"][k] for r in reps]) for k in
                    ("hand_off_fuel_kg_median", "rows_dry_at_hand_off", "dry_parent_descents_labelled_thrusting",
                     "fuel_fallback_fired", "mass_fallback_fired", "share_flown_powered_after_core_exhaustion")}
    out["item3"]["median_s_flown_powered_after_core_exhaustion"] = stats(
        [(r["item3"]["flown_powered_after_core_exhaustion_s_quantiles_5_50_95_of_those"] or [None, None])[1] for r in reps])
    out["item4"] = {"latent_columns": sorted({r["item4"]["latent_columns"] for r in reps}),
                    "unexpected_nan_any_seed": {k: v for r in reps for k, v in r["item4"]["unexpected_nan_by_latent"].items()},
                    "declared_nan_all_nan_every_seed": all(r["item4"]["declared_nan_all_nan"] for r in reps),
                    "impact_fields_finite_every_seed": all(r["item4"]["impact_fields_finite"] for r in reps)}

    # Item 7: effective parents per data option, per seed.
    cols = [c["column"] for c in reps[0]["terminal_json"]["columns"]]
    ess = {}
    for c in cols:
        per = [next(x for x in r["terminal_json"]["columns"] if x["column"] == c) for r in reps]
        ess[c] = {"ess_parents": stats([p["ess_parents"] for p in per]), "ess_rows": stats([p["ess_rows"] for p in per]),
                  "log_evidence_increment": stats([p["log_evidence_increment"] for p in per]),
                  "resolved_every_seed": all(p["ess_parents"] >= 1000 for p in per)}
    out["item7_ess_by_option"] = ess
    out["proposal_self_check"] = [r["terminal_json"]["proposal_self_check"] for r in reps]

    # Item 5 flags, pooled by family label.
    flags = {}
    for r in reps:
        for s in r["item5_spread_by_family"]:
            if s["flag"]:
                flags.setdefault(s["label"], set()).add(s["flag"])
    out["item5_flagged_families"] = {k: sorted(v) for k, v in flags.items()}

    # Breakup family.
    out["breakup_drawn_share_intact_broken_fragmented"] = [stats([r["breakup"]["drawn_share_intact_broken_fragmented"][k] for r in reps]) for k in range(3)]
    out["breakup_refused_share"] = stats([r["breakup"]["refused_share"] for r in reps])

    # Pleiades section 11 by CONTROL axis (the mechanism label is invalid until core request 2).
    def by_control(r, opt):
        acc = {}
        for f, s in r["pleiades_s11"][opt]["by_family"].items():
            if s is None:
                continue
            c = fam[int(f)].split("/")[2]
            a = acc.setdefault(c, np.zeros(5))
            ws = s["weight_share"]
            a += [ws, ws * s["nw_ge_30nm"], ws * s["nw_ge_50nm"], ws * s["inside_arc_ge_30nm"], ws * s["inside_arc_ge_50nm"]]
        return {c: {"weight": a[0], "nw_ge_30nm": a[1] / a[0], "nw_ge_50nm": a[2] / a[0],
                    "inside_arc_ge_30nm": a[3] / a[0], "inside_arc_ge_50nm": a[4] / a[0]} for c, a in acc.items()}

    pl = {}
    for opt in reps[0]["pleiades_s11"]:
        per_seed = [by_control(r, opt) for r in reps if opt in r["pleiades_s11"]]
        controls = sorted({c for p in per_seed for c in p})
        keys = ["weight", "nw_ge_30nm", "nw_ge_50nm", "inside_arc_ge_30nm", "inside_arc_ge_50nm"]
        pl[opt] = {"all": {k: stats([r["pleiades_s11"][opt]["all"][k] for r in reps]) for k in
                           ["nw_ge_30nm", "nw_ge_50nm", "inside_arc_ge_30nm", "inside_arc_ge_50nm", "any_dir_ge_30nm", "any_dir_ge_50nm"]},
                   "displacement_nm_50": stats([r["pleiades_s11"][opt]["all"]["displacement_nm_50_90_99"][0] for r in reps]),
                   "displacement_nm_90": stats([r["pleiades_s11"][opt]["all"]["displacement_nm_50_90_99"][1] for r in reps]),
                   "by_control": {c: {k: stats([p.get(c, {}).get(k) for p in per_seed]) for k in keys} for c in controls},
                   "position_class_share": {k: stats([r["pleiades_s11"][opt]["position_class_share"][k] for r in reps])
                                            for k in reps[0]["pleiades_s11"][opt]["position_class_share"]}}
    out["pleiades_s11"] = pl
    json.dump(out, open(dst, "w"), indent=1, default=float)
    print("wrote", dst)


if __name__ == "__main__":
    main(*sys.argv[1:3])
