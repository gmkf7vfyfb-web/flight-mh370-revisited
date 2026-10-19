"""Pool score_runj_a1branch.py per-seed sums into the stratified estimate under H (order B2, 19 Oct 2026). Waypoints stratum only.

Seeds pooled with equal weight within a set (as option_table_0019 / score_runj within a stratum). Production variants as run J:
'head' = D3 and D4 from end of flight's both-burst set, other D from production; 'prodonly' = production for every D.
For cell (d, c) and setting s (H surface or none), with m the row mass of score_runj and B the A1 branch:
    Z_B,strat(d,c,s) = Z_prod(D0', c, none, B) x Z_pass(d,c,s) / Z_pass(D0', c, none)            (end of flight's estimator,
                                                                                                   E_D0'[L_d L_H | B] from the pass)
  primary ('replace'):  Z(d,c,s) = Z_prod(d,c,s) - Z_prod(d,c,s,B) + Z_B,strat;   A1 = (Z_B,strat + Z_prod(A1 outside B)) / Z
  beside  ('rescale', a1_branch_combine.py): A1 = Z_B,strat / Z_prod(d,c,s) + share of A1 outside B; A2, B, code 6 rescaled.
Effective impacts of the stratified A1: Kish over the pass rows scaled by alpha = Z_B,strat / Z_pass plus production rows of A1 outside B.
Tension (module measure, rerun_reference.tension) on the stratified flight-only map of the total q = 1/3 cell, against production's.
Conditional on H; no identity likelihood; no Bayes factor or P(H | data).

    python aggregate_runj_a1branch.py WORKDIR OUT_JSON
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import score_runj_a1branch as SA  # noqa: E402  (sets SR.SURF)
import score_runj as SR  # noqa: E402
import branch_eof289 as b  # noqa: E402
from rerun_reference import tension  # noqa: E402
from headline_splithalf import rho_L  # noqa: E402

NONE = "none (without H)"
GRIDL = {"gcrel-0.25": (0.25, "mean", "-gcrel"), "g12-0.25": (0.25, 0, "")}
MASKS = ("all", "branch", "A1", "A1_out", "A2", "B", "code 6")


def lse(x):
    x = np.asarray([v for v in x if np.isfinite(v)], float)
    if not len(x):
        return -math.inf
    m = x.max(); return float(m + np.log(np.exp(x - m).sum()))


def load(work):
    R = {}
    for f in sorted(Path(work).glob("*_*.npz")):
        if "partial" in f.name:
            continue
        z = np.load(f); r = json.loads(str(z["res"])); R.setdefault(r["set"], {})[r["seed"]] = (r, f)
    return R


def pooled(R, set_, ck, stg, seeds=None):
    """log-pooled [S, S2, lat, lon, P2] per mask over the set's seeds (equal seed weight)."""
    items = [(k, v) for k, v in R[set_].items() if seeds is None or k in seeds]; c0 = -math.log(len(items))
    out = {}
    for nm in MASKS:
        rows = [(c0, v[0]["cells"][ck][stg]) for k, v in items if v[0]["cells"][ck].get(stg)]
        e = {"lnS": lse([c + x["s"] + math.log(x[nm][0]) if x[nm][0] > 0 else -math.inf for c, x in rows]),
             "lnS2": lse([2 * (c + x["s"]) + math.log(x[nm][1]) if x[nm][1] > 0 else -math.inf for c, x in rows])}
        if len(rows[0][1][nm]) > 4:
            e["lnP2"] = lse([2 * (c + x["s"]) + math.log(x[nm][4]) if x[nm][4] > 0 else -math.inf for c, x in rows])
        if np.isfinite(e["lnS"]):
            M = e["lnS"]
            e["mean_lat"] = sum(math.exp(c + x["s"] - M) * x[nm][2] for c, x in rows)
            e["mean_lon"] = sum(math.exp(c + x["s"] - M) * x[nm][3] for c, x in rows)
        out[nm] = e
    return out


def pooled_arr(R, set_, key, ck, stg, seeds=None, ref=0.0):
    """pooled histogram/map (key of the npz), on the scale exp(ref)."""
    items = [(k, v) for k, v in R[set_].items() if seeds is None or k in seeds]; c0 = -math.log(len(items)); acc = None
    for k, (r, f) in items:
        x = r["cells"][ck].get(stg)
        if not x:
            continue
        a = np.load(f)[key].astype(np.float64) * math.exp(c0 + x["s"] - ref)
        acc = a if acc is None else acc + a
    return acc


def ess(lnS, lnS2):
    return math.exp(2 * lnS - lnS2) if np.isfinite(lnS2) else 0.0


def wq(h, qs, lat0=-44.975, step=0.05):
    c = np.cumsum(h); c = c / c[-1]
    return [float(lat0 + step * np.searchsorted(c, q)) for q in qs]


def main(work, outp):
    R = load(work)
    nseed = {s: sorted(R[s]) for s in R}
    glat = -44.975 + 0.05 * np.arange(SR.NLAT); glon = 78.025 + 0.05 * np.arange(SR.NLON)
    area = b.area_km2(np.meshgrid(glat, glon, indexing="ij")[0]); z = np.zeros_like(area, dtype=bool)
    Lg = {k: rho_L(SR.SURF, *v) for k, v in GRIDL.items()}
    passinfo = {k: {kk: R["a1"][k][0][kk] for kk in ("rows", "branch_rows", "branch_row_fraction", "distinct_parents")} for k in nseed["a1"]}
    res = {"seeds": nseed, "pass_seeds": passinfo, "settings": list(SR.SETTINGS), "variants": {}}
    halves = {"all": None, "half 1-4": {1, 2, 3, 4}, "half 5-8": {5, 6, 7, 8}}
    for variant in ("head", "prodonly"):
        V = {}
        for d in SR.DS:
            src = "both" if (variant == "head" and d in ("D3", "D4")) else "prod"
            for c in SR.CAUSES:
                ck = f"{d} x {c}"; ref = f"D0 x {c}"
                P0 = pooled(R, "prod", ref, NONE)
                e = {"production_source": src}
                for stg in SR.SETTINGS:
                    Pd = pooled(R, src, ck, stg)
                    ent = {"production": {nm: {"share": math.exp(Pd[nm]["lnS"] - Pd["all"]["lnS"]) if np.isfinite(Pd[nm]["lnS"]) else 0.0,
                                               "eff_impacts": ess(Pd[nm]["lnS"], Pd[nm]["lnS2"])} for nm in MASKS},
                           "production_lnZ": Pd["all"]["lnS"], "production_mean": [Pd["all"].get("mean_lat"), Pd["all"].get("mean_lon")]}
                    for nm in ("all", "branch", "A1"):
                        ent["production"][nm]["eff_parents"] = ess(Pd[nm]["lnS"], Pd[nm].get("lnP2", -math.inf))
                    for hname, hs in halves.items():
                        A = pooled(R, "a1", ck, stg, hs); A0 = pooled(R, "a1", ref, NONE, hs)
                        lnZb = P0["branch"]["lnS"] + A["all"]["lnS"] - A0["all"]["lnS"]
                        lnalpha = lnZb - A["all"]["lnS"]
                        Zo = math.exp(Pd["A1_out"]["lnS"]) if np.isfinite(Pd["A1_out"]["lnS"]) else 0.0
                        Zb = math.exp(lnZb); Zp = math.exp(Pd["all"]["lnS"]); Zpb = math.exp(Pd["branch"]["lnS"]) if np.isfinite(Pd["branch"]["lnS"]) else 0.0
                        Z = Zp - Zpb + Zb
                        sh = {"A1": (Zb + Zo) / Z, "A1_branch": Zb / Z, "A1_outside_branch": Zo / Z}
                        for nm in ("A2", "B", "code 6"):
                            sh[nm] = (math.exp(Pd[nm]["lnS"]) if np.isfinite(Pd[nm]["lnS"]) else 0.0) / Z
                        a1p = ent["production"]["A1"]["share"]; br_r = Zb / Zp; a1r = br_r + Zo / Zp; scale = (1 - a1r) / (1 - a1p)
                        resc = {"A1": a1r, "A2": ent["production"]["A2"]["share"] * scale, "B": ent["production"]["B"]["share"] * scale}
                        S2o = math.exp(Pd["A1_out"]["lnS2"]) if np.isfinite(Pd["A1_out"]["lnS2"]) else 0.0
                        S2b = math.exp(2 * lnalpha + A["all"]["lnS2"])
                        S2all = max(math.exp(Pd["all"]["lnS2"]) - (math.exp(Pd["branch"]["lnS2"]) if np.isfinite(Pd["branch"]["lnS2"]) else 0.0), 0.0) + S2b
                        x = {"lnZ": math.log(Z), "lnZ_branch": lnZb, "shares": sh, "shares_rescale_form": resc,
                             "eff_impacts_all": Z * Z / S2all, "eff_impacts_A1": (Zb + Zo) ** 2 / (S2b + S2o) if (S2b + S2o) > 0 else 0.0,
                             "pass_eff_impacts_rows": ess(A["all"]["lnS"], A["all"]["lnS2"]),
                             "pass_eff_impacts_parents": ess(A["all"]["lnS"], A["all"]["lnP2"]),
                             "pass_ln_E_given_branch": A["all"]["lnS"] - A0["all"]["lnS"],
                             "production_ln_E_given_branch": Pd["branch"]["lnS"] - P0["branch"]["lnS"],
                             "production_branch_eff_impacts": ess(Pd["branch"]["lnS"], Pd["branch"]["lnS2"]),
                             "pass_branch_mean": [A["all"].get("mean_lat"), A["all"].get("mean_lon")],
                             "production_branch_mean": [Pd["branch"].get("mean_lat"), Pd["branch"].get("mean_lon")]}
                        if hname == "all":
                            ent["stratified"] = x
                            # per-seed spread of the pass ratio (Monte Carlo check)
                            per = []
                            for k in nseed["a1"]:
                                a = pooled(R, "a1", ck, stg, {k}); a0 = pooled(R, "a1", ref, NONE, {k})
                                per.append(a["all"]["lnS"] - a0["all"]["lnS"])
                            ent["stratified"]["pass_seed_ln_E_given_branch"] = per
                            ent["stratified"]["pass_seed_sd"] = float(np.std(per, ddof=1))
                            ent["stratified"]["alpha_ln"] = lnalpha
                            # A1 latitude quantiles
                            if stg in SA.HIST_SETTINGS:
                                hp = pooled_arr(R, "a1", f"{ck}|{stg}|all|hist", ck, stg, ref=A["all"]["lnS"])
                                ho = pooled_arr(R, src, f"{ck}|{stg}|A1_out|hist", ck, stg, ref=Pd["all"]["lnS"])
                                h1 = pooled_arr(R, src, f"{ck}|{stg}|A1|hist", ck, stg, ref=Pd["all"]["lnS"])
                                hs_ = hp * math.exp(A["all"]["lnS"] + lnalpha - Pd["all"]["lnS"]) + ho
                                ent["stratified"]["A1_lat_q05_q50_q95"] = wq(hs_, (0.05, 0.5, 0.95))
                                ent["production"]["A1"]["lat_q05_q50_q95"] = wq(h1, (0.05, 0.5, 0.95)) if h1.sum() > 0 else None
                                ent["_hist"] = {"stratified_A1": (hs_ / hs_.sum()).tolist(), "production_A1": (h1 / h1.sum()).tolist() if h1.sum() > 0 else None}
                        else:
                            ent.setdefault("halves", {})[hname] = {"A1": sh["A1"], "eff_impacts_A1": x["eff_impacts_A1"], "lnZ_branch": lnZb}
                    e[stg] = ent
                # tension on the stratified flight-only map, primary cause, D0/D3/D4/D5
                if c == SA.MAP_C and d in SA.MAP_D:
                    Pd = pooled(R, src, ck, NONE); A = pooled(R, "a1", ck, NONE); A0 = pooled(R, "a1", ref, NONE)
                    mall = pooled_arr(R, src, f"{ck}|all|map", ck, NONE, ref=Pd["all"]["lnS"])
                    mbr = pooled_arr(R, src, f"{ck}|branch|map", ck, NONE, ref=Pd["all"]["lnS"])
                    mpa = pooled_arr(R, "a1", f"{ck}|all|map", ck, NONE, ref=A["all"]["lnS"])
                    lnZb = P0["branch"]["lnS"] + A["all"]["lnS"] - A0["all"]["lnS"]
                    mst = mall - mbr + mpa * math.exp(lnZb - Pd["all"]["lnS"])
                    for tag, mp in (("production", mall), ("stratified", mst)):
                        pc = (mp / mp.sum()).reshape(SR.NLAT, SR.NLON)
                        for stg, Lk in Lg.items():
                            t = tension(pc, Lk, area, glat, glon, z, z, z)
                            e.setdefault("tension", {}).setdefault(tag, {})[stg] = {kk: float(t[kk]) for kk in (
                                "ln_S", "tension_p", "d_shared", "mean_shift_nm", "uncond_in_cond_hdr90", "cond_in_uncond_hdr90",
                                "cond_hdr90_km2", "uncond_hdr90_km2")}
                    if variant == "head":
                        np.savez_compressed(Path(outp).parent / f"map-stratified-{d}.npz", stratified=(mst / mst.sum()).reshape(SR.NLAT, SR.NLON).astype(np.float32),
                                            production=(mall / mall.sum()).reshape(SR.NLAT, SR.NLON).astype(np.float32))
                V[ck] = e
                print(variant, ck, flush=True)
        res["variants"][variant] = V
    Path(outp).write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:3])
