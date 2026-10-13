"""Composer pass 2 (run I): seabed PDF products from seabed_pass2.py outputs. Strata mixed with settling's
stratum-mixture-weights.json weights_per_cell (= core share x Z_s(00:19 cell), ruling C) - the module evidence acts within strata,
as in the impact products. Regions as report_pass2.area_stats (0.1 deg, Gaussian 0.1 deg, HPD). Outcome ESS of the mixture =
1 / sum_s (W_s^2 / ESS_s). Split-half: core seeds 1-4 against 5-8 (one partition).
Usage: python seabed_report.py <work dir> <out json> <out maps npz>
"""
import json, pathlib, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from report_pass2 import area_stats, STRATA, NY2, NX2   # noqa: E402

EX = pathlib.Path("/Users/pete/Downloads/mh370-exchange")
LAYERS = ["P1", "Dr", "DrS", "H", "HS"]


def main(work, outj, outm):
    W = json.loads((EX / "settling/run-i/stratum-mixture-weights.json").read_text())["weights_per_cell"]
    A = {st: np.load(pathlib.Path(work) / f"seabed-{st}.npz") for st in STRATA}
    J = {st: json.loads((pathlib.Path(work) / f"seabed-{st}.json").read_text()) for st in STRATA}
    info = {st: json.loads((EX / "settling/run-i" / st / f"ri_{ {'next-i-waypoints': 'waypoints', 'next-i-free': 'free', 'next-i-descent-climb': 'descentclimb', 'next-i-repro-radar': 'reproradar'}[st]}_info.json").read_text())["products"] for st in STRATA}
    res, maps = [], {}
    for j, p in enumerate(info["next-i-waypoints"]):
        cellkey = f"{p['option']} | {p['cell'] if p['subset'] == 'all' else 'total'}"
        ws = W[cellkey]
        for L in LAYERS:
            out = {"j": j, "D": p["D"], "option": p["option"], "cell": p["cell"], "subset": p["subset"], "layer": L, "weights_key": cellkey}
            for kind in ("seabed|all", "impact|all", "seabed|h0", "seabed|h1"):
                h = sum(ws[st] * A[st][f"{j}|{L}|{kind}"].astype(float) for st in STRATA if f"{j}|{L}|{kind}" in A[st])
                a50, a90, sm = area_stats(h)
                out[f"{kind}|A50"] = a50; out[f"{kind}|A90"] = a90
                if kind == "seabed|all":
                    g = sm; out["seabed_in_grid"] = float(h.sum())
                    if p["subset"] == "all" and p["cell"] == "total":
                        maps[f"{p['D']}|{L}"] = sm.astype(np.float32)
                    pr = [J[st]["products"][j] for st in STRATA]
                    assert all(x["D"] == p["D"] and x["subset"] == p["subset"] and x["cell"] == p["cell"] for x in pr)
                    out["ess_outcomes_mix"] = float(1.0 / sum(ws[st] ** 2 / max(J[st]["products"][j]["layers"][L]["ess_outcomes"], 1e-9) for st in STRATA))
                    out["ess_outcomes_waypoints"] = J["next-i-waypoints"]["products"][j]["layers"][L]["ess_outcomes"]
                    out["ess_outcomes_free"] = J["next-i-free"]["products"][j]["layers"][L]["ess_outcomes"]
                    out["N_waypoints"] = J["next-i-waypoints"]["products"][j]["N"]
                    ml = [J[st]["products"][j]["layers"][L].get("seabed_mean_lat_lon", [np.nan, np.nan]) for st in STRATA]
                    out["seabed_mean_lat"] = float(sum(ws[st] * m[0] for st, m in zip(STRATA, ml))); out["seabed_mean_lon"] = float(sum(ws[st] * m[1] for st, m in zip(STRATA, ml)))
                    lat = np.repeat(np.arange(NY2), NX2) * 0.1 - 46.0 + 0.05; c = np.cumsum(np.bincount(np.repeat(np.arange(NY2), NX2), weights=h, minlength=NY2)); c /= c[-1]
                    out["seabed_median_lat"] = float(-46.0 + 0.1 * (np.searchsorted(c, 0.5) + 0.5))
            out["seabed_A90_reldiff_halves"] = abs(out["seabed|h0|A90"] - out["seabed|h1|A90"]) / (0.5 * (out["seabed|h0|A90"] + out["seabed|h1|A90"]))
            out["seabed_A50_reldiff_halves"] = abs(out["seabed|h0|A50"] - out["seabed|h1|A50"]) / (0.5 * (out["seabed|h0|A50"] + out["seabed|h1|A50"]))
            res.append(out)
    pathlib.Path(outj).write_text(json.dumps({"afloat_mass_share": {st: J[st]["afloat_mass_share"] for st in STRATA}, "products": res}, indent=1))
    np.savez_compressed(outm, **maps)


if __name__ == "__main__":
    main(*sys.argv[1:])
