"""Comparison chart: settled seabed latitude of A1 (cruise to fuel exhaustion, then no control) under D2-D5, run J waypoints
production alone against the A1-branch stratified samples; thin lines = pass seeds 1-4 and 5-8 (Monte Carlo spread).
    python3 comp_a1.py <prod folder> <new folder> <out stem>
"""
import sys, json, pathlib, numpy as np

def outcome_lat(el, rows, draws, extra=None):
    st = el[:, 4] == 0
    key = el[st, 0].astype(np.int64) * 1048576 + el[st, 1].astype(np.int64)
    o = np.argsort(key, kind="stable"); key, lat, mass = key[o], el[st, 5][o], el[st, 7][o]
    uk, start = np.unique(key, return_index=True); stop = np.r_[start[1:], len(key)]
    tot = np.add.reduceat(mass, start); share = mass / np.repeat(tot, stop - start)
    want = rows.astype(np.int64) * 1048576 + draws.astype(np.int64)
    pos = np.minimum(np.searchsorted(uk, want), len(uk) - 1); ok = uk[pos] == want
    idx = np.concatenate([np.arange(a, b) for a, b in zip(start[pos[ok]], stop[pos[ok]])])
    w = share[idx] / ok.sum(); grp = None
    if extra is not None: grp = np.repeat(extra[ok], (stop - start)[pos[ok]])
    return lat[idx], w, grp, int((~ok).sum())

def main(prod, new, stem):
    prod, new = pathlib.Path(prod), pathlib.Path(new)
    Ip = json.loads((prod / "rj_waypoints_info.json").read_text()); In = json.loads((new / "rja1_info.json").read_text())
    ELp = np.fromfile(prod / "rj_waypoints_elements.f64", "<f8").reshape(-1, 8); zp = np.load(prod / "rj_waypoints_draws.npz")
    ELn = np.fromfile(new / "rja1_elements.f64", "<f8").reshape(-1, 8); zn = np.load(new / "rja1_draws.npz")
    edges = np.arange(-40.0, -30.0 + 1e-9, 0.1); res = {}
    for d in ("D2", "D3", "D4", "D5"):
        jp = next(j for j, p in enumerate(Ip["products"]) if p["D"] == d and p["cell"] == "total" and p["subset"] == "A1")
        jn = next(j for j, p in enumerate(In["products"]) if p["D"] == d and p["subset"] == "A1")
        lp, wp, _, ncp = outcome_lat(ELp, zp[f"rows_{jp}"], zp[f"draws_{jp}"])
        grp = zn[f"stratum_{jn}"] * 100 + zn[f"seed_{jn}"]
        ln, wn, gn, ncn = outcome_lat(ELn, zn[f"rows_{jn}"], zn[f"draws_{jn}"], grp)
        h = lambda l, w: (np.histogram(l, edges, weights=w)[0] / max(w.sum(), 1e-300) / 0.1)
        halves = []
        for lo, hi in ((101, 104), (105, 108)):
            # half of the pass (its seeds re-weighted to the full pass mass) plus all production rows outside the branch
            pm = gn >= 100; hm = (gn >= lo) & (gn <= hi); ww = np.where(hm, wn * wn[pm].sum() / wn[hm].sum(), 0.0) + np.where(~pm, wn, 0.0)
            halves.append(h(ln, ww).tolist())
        q = lambda l, w: [float(l[np.argsort(l)][np.searchsorted(np.cumsum(w[np.argsort(l)]) / w.sum(), x)]) for x in (0.05, 0.5, 0.95)]
        res[d] = {"production": h(lp, wp).tolist(), "stratified": h(ln, wn).tolist(), "halves": halves,
                  "q_prod": q(lp, wp), "q_new": q(ln, wn), "ess_prod": Ip["products"][jp]["row_ess_kish"], "ess_new": In["products"][jn]["row_ess_kish"],
                  "share_prod": Ip["products"][jp]["share_of_option"], "share_new": In["products"][jn]["share_of_option"],
                  "share_from_production_rows": float(wn[gn < 100].sum() / wn.sum()), "not_computed": [ncp, ncn],
                  "mass_north_of_36S_prod": float(wp[lp > -36].sum() / wp.sum()), "mass_north_of_36S_new": float(wn[ln > -36].sum() / wn.sum())}
    res["edges"] = edges.tolist()
    pathlib.Path(stem + ".json").write_text(json.dumps(res, indent=1))
    for d in ("D2", "D3", "D4", "D5"):
        r = res[d]; print(d, "q prod", [round(x, 2) for x in r["q_prod"]], "q new", [round(x, 2) for x in r["q_new"]], "ESS", round(r["ess_prod"]), round(r["ess_new"]),
                          "N36", round(r["mass_north_of_36S_prod"], 4), round(r["mass_north_of_36S_new"], 4), "from prod rows", round(r["share_from_production_rows"], 5))

if __name__ == "__main__":
    main(*sys.argv[1:4])
