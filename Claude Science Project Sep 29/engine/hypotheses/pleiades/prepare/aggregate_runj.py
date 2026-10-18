"""Pool score_runj.py per-seed reductions into the H-conditional two-factor table on run J (and the joined V2 per-seed set).

Pooling (as end of flight's option_table_0019 / combine_strata_0019 and composer-views-run-j): seeds pooled by evidence within a
stratum (ln(P_s / K_s) + seed scale), strata mixed by core run J's P(family) at equal prior (core summary.json log_evidence).
D3 and D4, waypoints stratum: end of flight's both-burst supplementary set (8 seeds, thinned, normalised by weight_sum_in) - the
headline, as the composer uses it; the production-only version is reported beside it as a check. Every other cell: production.
Tension: the module's measure (rerun_reference.tension) on the wide 0.05 deg grid, flight-only cell mass against the surface.
Western residual (brief 7, 8.2): H-conditional mass at >= 30 / >= 50 NM inside the arc (arc_distance_nm), over the whole grid
and inside the 90 % region under H (the 8-9 Oct definition of the lobe).

    python aggregate_runj.py WORKDIR OUT_DIR
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE))
import score_runj as SR  # noqa: E402
import branch_eof289 as b  # noqa: E402
from rerun_reference import tension  # noqa: E402
from headline_splithalf import rho_L  # noqa: E402
from branch_figure import hdr_level  # noqa: E402

EXPECT = {"run-j-waypoints": 24, "run-j-free": 18, "run-j-descent-climb": 16, "run-j-repro-radar": 16}
GRIDL = {"gcrel-0.25": (0.25, "mean", "-gcrel"), "g12-0.25": (0.25, 0, ""), "gcrel-0": (0.0, "mean", "-gcrel"), "gcrel-0.5": (0.5, "mean", "-gcrel")}


def lse(x):
    x = np.asarray(x, float); m = x.max(); return float(m + np.log(np.exp(x - m).sum()))


def load(work):
    R = {}
    for f in sorted(Path(work).glob("*_*_*.npz")):
        if "partial" in f.name:
            continue
        z = np.load(f); r = json.loads(str(z["res"]))
        R[(r["set"], r["stratum"], r["seed"])] = (r, f)
    return R


def main(work, out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    R = load(work)
    lnZc = {s: json.load(open(SR.CORE / s / "summary.json"))["cases"][0]["log_evidence"] for s in SR.STRATA}
    PF = {s: math.exp(v - lse(list(lnZc.values()))) for s, v in lnZc.items()}
    have = {s: sorted(k for (st_, s_, k) in R if st_ == "prod" and s_ == s) for s in SR.STRATA}
    hb = sorted(k for (st_, s_, k) in R if st_ == "both")
    complete = all(len(have[s]) == EXPECT[s] for s in SR.STRATA) and len(hb) == 8
    gs = (SR.SURF)
    glat = -44.975 + 0.05 * np.arange(SR.NLAT); glon = 78.025 + 0.05 * np.arange(SR.NLON)
    area = b.area_km2(np.meshgrid(glat, glon, indexing="ij")[0]); z = np.zeros_like(area, dtype=bool)
    Lg = {k: rho_L(gs, *v) for k, v in GRIDL.items()}
    res = {"strata_P": PF, "seeds": {**{s: have[s] for s in SR.STRATA}, "both-burst run-j-waypoints": hb}, "complete": complete,
           "settings": list(SR.SETTINGS), "search": "before seabed search", "variants": {}}
    for variant in ("head", "prodonly"):
        V = {}
        for d in SR.DS:
            for c in SR.CAUSES:
                ck = f"{d} x {c}"
                parts = []   # (log scale, entry dict per setting, map info) per seed
                for s in SR.STRATA:
                    use_both = variant == "head" and d in ("D3", "D4") and s == "run-j-waypoints"
                    seeds = hb if use_both else have[s]; K = len(seeds)
                    for k in seeds:
                        r, f = R[("both" if use_both else "prod", s, k)]
                        parts.append((math.log(PF[s] / K), s, k, r["cells"][ck], f))
                e = {}
                for stg in SR.SETTINGS:
                    L = [(c0 + x[stg]["s"], x[stg], s, k) for c0, s, k, x, _ in parts if x and x.get(stg)]
                    M = max(t[0] for t in L); fct = [math.exp(t[0] - M) for t in L]
                    S = sum(fi * t[1]["S"] for fi, t in zip(fct, L)); S2 = sum(fi * fi * t[1]["S2"] for fi, t in zip(fct, L))
                    g = lambda key: sum(fi * t[1][key] for fi, t in zip(fct, L)) / S
                    fam = {}
                    for nm in SR.FAMS:
                        a1 = sum(fi * t[1]["fam"][nm][0] for fi, t in zip(fct, L)); a2 = sum(fi * fi * t[1]["fam"][nm][1] for fi, t in zip(fct, L))
                        a3 = sum(fi * t[1]["fam"][nm][2] for fi, t in zip(fct, L)); a4 = sum(fi * t[1]["fam"][nm][3] for fi, t in zip(fct, L))
                        fam[nm] = dict(share=a1 / S, eff_impacts=a1 * a1 / a2 if a2 > 0 else 0.0, in30_share_of_family=a3 / a1 if a1 > 0 else float("nan"),
                                       in50_share_of_family=a4 / a1 if a1 > 0 else float("nan"))
                    # waypoints seed scatter of the conditional mean latitude (Monte Carlo check)
                    wp = [(t[1]["lat"] / t[1]["S"], t[0] + math.log(t[1]["S"])) for t in L if t[2] == "run-j-waypoints"]
                    e[stg] = dict(ln_Z=M + math.log(S), eff_impacts=S * S / S2, mean_lat=g("lat"), mean_lon=g("lon"), in30_share=g("in30"),
                                  in50_share=g("in50"), families=fam,
                                  not_computed_core_share=sum(fi * t[1]["S"] * 0 for fi, t in zip(fct, L)),
                                  waypoints_seed_mean_lat_sd=float(np.std([x[0] for x in wp], ddof=1)) if len(wp) > 1 else None,
                                  waypoints_seeds=len(wp))
                    e[stg]["seed_lnZ_waypoints"] = [x[1] for x in wp]
                # not computed under H, as a share of the flight-only mass (setting 'none' scale)
                L0 = [(c0 + x["none (without H)"]["s"], x, s, k) for c0, s, k, x, _ in parts if x]
                M0 = max(t[0] for t in L0)
                for stg in list(SR.SETTINGS)[1:]:
                    num = sum(math.exp(t[0] - M0) * t[1]["none (without H)"]["S"] * t[1][stg]["not_computed_core_share"] for t in L0 if t[1].get(stg))
                    den = sum(math.exp(t[0] - M0) * t[1]["none (without H)"]["S"] for t in L0)
                    e[stg]["not_computed_core_share"] = num / den
                for stg in list(SR.SETTINGS)[1:]:
                    e[stg]["ln_mean_LH"] = e[stg]["ln_Z"] - e["none (without H)"]["ln_Z"]
                    a = np.array(e[stg]["seed_lnZ_waypoints"]); a0 = np.array(e["none (without H)"]["seed_lnZ_waypoints"])
                    if len(a) == len(a0) and len(a) > 1:
                        e[stg]["ln_mean_LH_waypoints_seed_sd"] = float(np.std(a - a0, ddof=1))
                # flight-only grid map pooled, for tension and close-ups
                maps = {"map": None, "map_in30": None, "map_in50": None}
                for nm in maps:
                    acc = None
                    for c0, s, k, x, f in parts:
                        if not x:
                            continue
                        zz = np.load(f); key = f"{ck}|{nm}"
                        if key not in zz.files:
                            acc = None; break
                        h = zz[key].astype(np.float64) * math.exp(c0 + float(zz[f"{ck}|s"]) - M0)
                        acc = h if acc is None else acc + h
                    maps[nm] = acc
                pc = maps["map"].reshape(SR.NLAT, SR.NLON); tot = pc.sum(); pc = pc / tot
                for stg, Lk in Lg.items():
                    t = tension(pc, Lk, area, glat, glon, z, z, z)
                    e[stg]["tension"] = {kk: float(t[kk]) for kk in ("ln_S", "tension_p", "d_shared", "mean_shift_nm", "uncond_in_cond_hdr90",
                                                                       "cond_in_uncond_hdr90", "cond_hdr90_km2", "uncond_hdr90_km2")}
                    if maps["map_in30"] is not None:
                        mh = pc * Lk; mh = mh / mh.sum(); dn = mh / area; hdr = dn >= hdr_level(dn, mh, 0.9)
                        for tag in ("in30", "in50"):
                            mi = maps[f"map_{tag}"].reshape(SR.NLAT, SR.NLON) / tot * Lk / (pc * Lk).sum()
                            e[stg][f"{tag}_share_grid"] = float(mi.sum())
                            e[stg][f"{tag}_share_in_H_hdr90"] = float(mi[hdr].sum())
                            e[stg][f"{tag}_share_in_H_hdr90_west_91p5E"] = float(mi[hdr & (glon[None, :] < 91.5)].sum())
                if variant == "head" and c == "total q=1/3 (C2 silent)":
                    np.savez_compressed(out / f"map-{d}.npz", pre=pc.astype(np.float32), post=pc.astype(np.float32),
                                        in30=(maps["map_in30"].reshape(SR.NLAT, SR.NLON) / tot).astype(np.float32),
                                        in50=(maps["map_in50"].reshape(SR.NLAT, SR.NLON) / tot).astype(np.float32))
                V[ck] = e
                print(variant, ck, flush=True)
        res["variants"][variant] = V
    # gate list (headline variant, headline setting)
    gate = []
    for ck, e in res["variants"]["head"].items():
        for stg in ("gcrel-0.25", "g12-0.25"):
            x = e[stg]
            if x["eff_impacts"] < 1000:
                gate.append(dict(cell=ck, setting=stg, family="all", ess=x["eff_impacts"]))
            for nm in ("A1", "A2", "B"):
                if x["families"][nm]["eff_impacts"] < 1000:
                    gate.append(dict(cell=ck, setting=stg, family=nm, ess=x["families"][nm]["eff_impacts"]))
    res["gate_fail"] = gate
    (out / "pleiades-runj-table.json").write_text(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    main(*sys.argv[1:3])
