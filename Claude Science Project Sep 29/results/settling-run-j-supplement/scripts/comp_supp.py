"""Run J alone against run J + northern supplement (rule B): seabed latitude quantiles, 90 % areas, band masses (seabed and impact).
    python3 comp_supp.py <out json>
"""
import sys, json, pathlib, numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from comp_a1 import outcome_lat
A = pathlib.Path("/Users/pete/Downloads/mh370-exchange/settling/run-j/run-j-waypoints"); B = pathlib.Path("/Users/pete/Downloads/mh370-exchange/settling/run-j-supplement/ruleB-waypoints")
IA = json.loads((A / "rj_waypoints_info.json").read_text()); IB = json.loads((B / "rjs_info.json").read_text())
EA = np.memmap(A / "rj_waypoints_elements.f64", "<f8", "r").reshape(-1, 8); EB = np.memmap(B / "rjs_elements.f64", "<f8", "r").reshape(-1, 8)
EA = np.asarray(EA); EB = np.asarray(EB)
zA = np.load(A / "rj_waypoints_draws.npz"); zB = np.load(B / "rjs_draws.npz")
FA = {**{k: v for k, v in json.loads((A / "settling-seabed-wreckage-run-j-waypoints-core.json").read_text())["options"].items()}}
FB = json.loads((B / "settling-seabed-wreckage-run-j-supplement-waypoints-core.json").read_text())["options"]
BANDS = [("35-30 S", -35, -30), ("30-25 S", -30, -25), ("25-20 S", -25, -20), ("north of 33 S", -33, 0), ("north of 30 S", -30, 0)]
edges = np.arange(-45.0, -10.0 + 1e-9, 0.1)
def q(l, w): o = np.argsort(l); c = np.cumsum(w[o]) / w.sum(); return [float(l[o][min(np.searchsorted(c, x), len(l) - 1)]) for x in (0.05, 0.5, 0.95)]
res = {"edges": edges.tolist()}
for d in ("D0", "D1", "D2", "D3", "D4", "D5"):
    ja = next(j for j, p in enumerate(IA["products"]) if p["D"] == d and p["cell"] == "total" and p["subset"] == "all")
    jb = next(j for j, p in enumerate(IB["products"]) if p["D"] == d and p["subset"] == "all")
    jn = next(j for j, p in enumerate(IB["products"]) if p["D"] == d and p["subset"] == "north33")
    la, wa, _, _ = outcome_lat(EA, zA[f"rows_{ja}"], zA[f"draws_{ja}"]); lb, wb, _, _ = outcome_lat(EB, zB[f"rows_{jb}"], zB[f"draws_{jb}"])
    ln, wn, _, _ = outcome_lat(EB, zB[f"rows_{jn}"], zB[f"draws_{jn}"]); pn = IB["products"][jn]["share_of_option"]
    name = IA["products"][ja]["option"]
    r = {"name": name, "row_ess_alone_settling": IA["products"][ja]["row_ess_kish"], "row_ess_comb": IB["products"][jb]["row_ess_kish"],
         "area90_alone": FA[name]["area_km2_99_90_50"]["wreckage_field"][1], "area90_comb": FB[name]["area_km2_99_90_50"]["wreckage_field"][1],
         "q_alone": q(la, wa), "q_comb": q(lb, wb), "north33_share_comb": pn,
         "pdf_alone": (np.histogram(la, edges, weights=wa)[0] / wa.sum() / 0.1).tolist(),
         "pdf_comb": (np.histogram(lb, edges, weights=wb)[0] / wb.sum() / 0.1).tolist(),
         "pdf_north_comb": (np.histogram(ln, edges, weights=wn)[0] / wn.sum() / 0.1 * pn).tolist(), "bands": {}}
    imp = IB["impact_level"][d]["bands"]
    for nm, lo, hi in BANDS:
        sa = float(wa[(la > lo) & (la <= hi)].sum() / wa.sum()); sb = float(wb[(lb > lo) & (lb <= hi)].sum() / wb.sum())
        nb = float(pn * wn[(ln > lo) & (ln <= hi)].sum() / wn.sum()) if lo >= -33 else None
        r["bands"][nm] = {"seabed_alone": sa, "seabed_alone_se": float(np.sqrt(sa * (1 - sa) / len(zA[f"rows_{ja}"]))),
                          "seabed_comb_total_product": sb, "seabed_comb_from_north_product": nb,
                          "impact_comb": imp[nm]["comb"]["mass"] if nm in imp else None, "impact_comb_row_ess": imp[nm]["comb"]["row_ess"] if nm in imp else None,
                          "impact_alone": imp[nm]["alone"]["mass"] if nm in imp else None, "impact_alone_row_ess": imp[nm]["alone"]["row_ess"] if nm in imp else None}
    res[d] = r
    print(d, "area", round(r["area90_alone"] / 1e3, 1), "->", round(r["area90_comb"] / 1e3, 1), "q", [round(x, 2) for x in r["q_alone"]], "->", [round(x, 2) for x in r["q_comb"]],
          "N33 seabed", round(r["bands"]["north of 33 S"]["seabed_alone"], 4), "->", round(r["bands"]["north of 33 S"]["seabed_comb_from_north_product"], 4), flush=True)
pathlib.Path(sys.argv[1]).write_text(json.dumps(res, indent=1))
