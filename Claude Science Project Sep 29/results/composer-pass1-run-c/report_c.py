"""Composer pass 1 (run C): mix the four core run C strata, PDF statistics, tension quantities, tables and figures.

Adaptation of results/composer-pass0/report.py (smooth_to_density, stats, overlap, hdr_mask, smoothed_mode, nm_between imported from
it unchanged: transcriptions of summary.rs and patch B). New in pass 1: three 00:19 options x two versions (all rows; contact speed
<= 212 m/s), families by EoF family4_code first, products without hydro, the rho = 0.5 Pléiades sensitivity, mean displacement.
Usage: python report_c.py <work dir> <out dir>
"""
import csv, json, math, pathlib, sys
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent
P0 = HERE.parent / "repo/Claude Science Project Sep 29/results/composer-pass0"
sys.path.insert(0, str(P0))
import matplotlib
matplotlib.use("Agg")
import summarise_stratum as S
import report as R0   # smooth_to_density, stats, overlap, hdr_mask, smoothed_mode, nm_between, LAT_C, LON_C, LAT_EDGES, LON_EDGES, GRID

STRATA = ["next-c-free", "next-c-repro-radar", "next-c-descent-climb", "next-c-routes"]
SNAME = {"next-c-free": "free", "next-c-repro-radar": "Davey dynamics + radar", "next-c-descent-climb": "descent-climb", "next-c-routes": "routes"}
CORE_MIX = json.loads(pathlib.Path("/Users/pete/Downloads/mh370-exchange/core/next-run-c/report/early-families-mixture.json").read_text())
P_CORE_ALL = {"next-c-free": CORE_MIX["P_family"]["free"], "next-c-repro-radar": CORE_MIX["P_family"]["Davey dynamics + radar"],
              "next-c-descent-climb": CORE_MIX["P_family"]["descent-climb"], "next-c-routes": CORE_MIX["P_family"]["routes"]}
SPLIT = {"next-c-free": (0.918, 0.856), "next-c-repro-radar": (0.910, 0.862), "next-c-descent-climb": (0.892, 0.856), "next-c-routes": (0.850, 0.822)}
OPTS = ["r600-bto+unpowered", "heldout+unpowered", "r600-bfo+unpowered", "r600-bto+unpowered-v212", "heldout+unpowered-v212", "r600-bfo+unpowered-v212"]
ONAME = {"r600-bto": "00:19 R600 BTO Only", "heldout": "00:19 Held Out", "r600-bfo": "00:19 R600 BTO + Raw BFO"}
def oname(t):
    return ONAME[t.split("+")[0]] + (" (contact speed <= 212 m/s)" if t.endswith("-v212") else "")
CHAIN = {"P1": "filter", "G": "P1", "Ga": "G", "D": "P1", "Da": "D", "H": "P1", "Ha": "H", "Hn": "P1", "Hna": "Hn", "PE": "P1",
         "Gx": "P1", "Hx": "P1", "PEx": "P1", "Hc": "P1", "PEc": "P1", "Hr0": "P1", "PEr0": "P1", "Hr5": "P1", "PEr5": "P1", "Y": "P1", "S": "P1"}
MAPPED = ["P1", "G", "Ga", "D", "Da", "H", "Ha", "Hn", "Hna", "Gx", "Hx", "Hr0", "Hr5"]
PNAME = {"P1": "flight + EoF", "G": "G (flight + EoF + drift + hydro)", "Ga": "G after searches", "D": "G without hydro", "Da": "G without hydro, after searches",
         "H": "H (G + Pléiades, given H)", "Ha": "H after searches", "Hn": "H without hydro", "Hna": "H without hydro, after searches",
         "Gx": "G, not-computed excluded", "Hx": "H, not-computed excluded", "Hr0": "H with COSMO, rho 0", "Hr5": "H with COSMO, rho 0.5 (correlated errors)"}
FAM4 = {1: "A1", 2: "A2", 3: "B", 6: "outside B (deliberate onset, no intervention)"}
SCHEMES = ["reweighted-0019", "fixed", "all-evidence"]


def load(work):
    D = {}
    for st in STRATA:
        for t in OPTS:
            pj = work / "rust" / st / t / "products.json"; sj = work / "summary" / st / t / "summary.json"
            if not (pj.exists() and sj.exists()):
                continue
            P = json.loads(pj.read_text())
            D.setdefault(st, {})[t] = {"products": {(p["id"].split("-", 1)[1] if "-" in p["id"] else p["id"]): p for p in P["products"]},
                                       "npz": dict(np.load(work / "summary" / st / t / "hist.npz")), "summary": json.loads(sj.read_text())}
    return D


def cum_inc(D, st, t, key):
    tot = 0.0
    while key != "filter":
        tot += D[st][t]["products"][key]["log_evidence_increment"]; key = CHAIN[key]
    return tot


def strata(D, t):
    return [s for s in STRATA if s in D and t in D[s]]


def weights(D, t, key, scheme):
    ss = strata(D, t); pc = {s: P_CORE_ALL[s] for s in ss}
    if scheme == "fixed":
        w = pc
    elif scheme == "reweighted-0019":
        lw = {s: math.log(pc[s]) + cum_inc(D, s, t, "P1") for s in ss}; m = max(lw.values()); w = {s: math.exp(v - m) for s, v in lw.items()}
    else:
        lw = {s: math.log(pc[s]) + cum_inc(D, s, t, key) for s in ss}; m = max(lw.values()); w = {s: math.exp(v - m) for s, v in lw.items()}
    tot = sum(w.values()); return {s: w[s] / tot for s in ss}


def mixture(D, t, key, scheme, part="lat"):
    w = weights(D, t, key, scheme)
    return sum(w[s] * D[s][t]["npz"][f"o-{key}|{part}"].astype(float) for s in w), w


def mean_pos(cell):
    p = cell.reshape(S.NY, S.NX); m = p.sum()
    la = float((p.sum(axis=1) * R0.LAT_C).sum() / m); lo = float((p.sum(axis=0) * R0.LON_C).sum() / m)
    return la, lo


def mix_lnZ(D, t, key, scheme_w):
    """ln sum_s w_s exp(cum_inc(s, key)): the mixture's log evidence increment against the filter, given stratum weights."""
    v = [math.log(scheme_w[s]) + cum_inc(D, s, t, key) for s in scheme_w]; m = max(v)
    return m + math.log(sum(math.exp(x - m) for x in v))


def entry(D, t, key, sc):
    h, w = mixture(D, t, key, sc); d = R0.smooth_to_density(h)
    h0, _ = mixture(D, t, key, sc, "lat_h0"); h1, _ = mixture(D, t, key, sc, "lat_h1")
    cell, _ = mixture(D, t, key, sc, "cell"); cell = cell / cell.sum()
    f4, _ = mixture(D, t, key, sc, "f4"); fc, _ = mixture(D, t, key, sc, "fc")
    f40, _ = mixture(D, t, key, sc, "f4_h0"); f41, _ = mixture(D, t, key, sc, "f4_h1")
    f4m = {f: sum(w[s] * D[s][t]["summary"]["products"][f"o-{key}"]["family4_mass"][f] for s in w) for f in range(7)}
    fcm = {f: sum(w[s] * D[s][t]["summary"]["products"][f"o-{key}"]["family_code_mass"][f] for s in w) for f in range(7)}
    fast = sum(w[s] * D[s][t]["summary"]["products"][f"o-{key}"]["fast_share"] for s in w)
    fastf = {FAM4[f]: (sum(w[s] * D[s][t]["summary"]["products"][f"o-{key}"]["fast_share_by_family4"][f] * D[s][t]["summary"]["products"][f"o-{key}"]["family4_mass"][f] for s in w) / f4m[f]) if f4m[f] > 0 else None for f in FAM4}
    e = {"stratum_weights": w, **R0.stats(d), "split_half_overlap_one_partition": R0.overlap(R0.smooth_to_density(h0), R0.smooth_to_density(h1)),
         "hdr50_area_km2": float(R0.hdr_mask(cell, 0.5).sum() * S.CELL_KM2), "hdr90_area_km2": float(R0.hdr_mask(cell, 0.9).sum() * S.CELL_KM2),
         "smoothed_map_mode_lat_lon": R0.smoothed_mode(cell), "mean_lat_lon": mean_pos(cell),
         "share_contact_speed_above_212": fast, "share_above_212_by_family": fastf,
         "family_probability": {FAM4[f]: f4m[f] for f in FAM4}, "unlabelled": f4m[0],
         "B_split": {"B, approach to ditching (code 3)": fcm[3], "B, control lost en route (code 5)": fcm[5]},
         "A_split": {"A1 (code 1)": fcm[1], "A, controlled then lost (code 4)": fcm[4], "A2 (code 2)": fcm[2]}}
    e["family_stats"] = {}
    for f, nm in FAM4.items():
        if f4[f].sum() > 0:
            s_ = R0.stats(R0.smooth_to_density(f4[f]))
            s_["split_half_overlap_one_partition"] = R0.overlap(R0.smooth_to_density(f40[f]), R0.smooth_to_density(f41[f])) if f40[f].sum() > 0 and f41[f].sum() > 0 else None
            e["family_stats"][nm] = s_
    for code, nm in ((3, "B, approach to ditching (code 3)"), (5, "B, control lost en route (code 5)"), (4, "A, controlled then lost (code 4)")):
        if fc[code].sum() > 0:
            e["family_stats"][nm] = R0.stats(R0.smooth_to_density(fc[code]))
    return e, cell


def main(work, out):
    work, out = pathlib.Path(work), pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    D = load(work)
    RES = {"label": "run C NOT CONVERGED; EoF physics provisional; no structural limit (G13); hydro predictive, not calibrated; drift GLORYS12 only, current nodes; GlobCurrent excluded (F1)",
           "strata_present": {t: strata(D, t) for t in OPTS}, "options": {}}
    rows_prod, rows_mix, rows_fam, rows_cov, rows_ev = [], [], [], [], []
    for t in OPTS:
        ss = strata(D, t)
        if not ss:
            continue
        O = RES["options"][t] = {"name": oname(t), "strata": [SNAME[s] for s in ss], "products": {}, "tension": {}, "evidence": {}}
        for st in ss:
            prods = D[st][t]["products"]
            for key in CHAIN:
                if key not in prods:
                    continue
                p = prods[key]; sh = p["split_half"] or {}
                row = {"option": oname(t), "product": key, "label": p["label"], "stratum": SNAME[st], "contains": " + ".join(p["contains"]),
                       "conditional_on": json.dumps(p["conditional_on"]), "ln_evidence_increment_vs_base": p["log_evidence_increment"],
                       "ln_evidence_vs_flight": cum_inc(D, st, t, key),
                       "split_half_increment_first_half": (sh.get("log_evidence_increment") or [None, None])[0],
                       "split_half_increment_second_half": (sh.get("log_evidence_increment") or [None, None])[1],
                       "composer_status": p["status"], "composer_status_reasons": " | ".join(p.get("status_reasons", [])),
                       "source_split_half_mean": SPLIT[st][0], "source_split_half_min": SPLIT[st][1],
                       "factor_split_half": "; ".join(f"{c['what'].split(',')[0]}: {c['statistic']:.3f} ({'pass' if c['passed'] else 'FAIL'})" for c in p.get("factor_split_half", []) if c["statistic"] is not None),
                       "min_ess_parents_per_seed": min(e[1] for e in p["ess_rows_parents"]), "sum_ess_rows_8_seeds": sum(e[0] for e in p["ess_rows_parents"])}
                for f in p["factors"]:
                    row[f"not_computed_weight_max[{f['name']}]"] = max(f["not_computed_weight"]) if f["not_computed_weight"] else 0.0
                    row[f"factor_alone_min_ess_parents[{f['name']}]"] = min(e[1] for e in f["ess_rows_parents"]) if f["ess_rows_parents"] else None
                if key in MAPPED:
                    dd = R0.smooth_to_density(D[st][t]["npz"][f"o-{key}|lat"]); row.update({f"lat_{k}": v for k, v in R0.stats(dd).items()})
                    cov = D[st][t]["summary"]["products"][f"o-{key}"]
                    for f, v in cov["ess_rows_per_seed_by_family4"].items():
                        if int(f) in FAM4:
                            rows_cov.append({"option": oname(t), "product": key, "stratum": SNAME[st], "by": "EoF family (family4_code)", "value": FAM4[int(f)], "ess_rows_per_seed": json.dumps([round(x) for x in v]), "min": round(min(v))})
                    for f, v in cov["ess_rows_per_seed_by_family_code"].items():
                        if int(f) in (3, 4, 5):
                            rows_cov.append({"option": oname(t), "product": key, "stratum": SNAME[st], "by": "EoF family_code", "value": f, "ess_rows_per_seed": json.dumps([round(x) for x in v]), "min": round(min(v))})
                    for b, v in cov["ess_rows_per_seed_by_latitude_band"].items():
                        rows_cov.append({"option": oname(t), "product": key, "stratum": SNAME[st], "by": "impact latitude band", "value": b, "ess_rows_per_seed": json.dumps([round(x) for x in v]), "min": round(min(v))})
                    rows_cov.append({"option": oname(t), "product": key, "stratum": SNAME[st], "by": "all rows", "value": "", "ess_rows_per_seed": json.dumps([round(x) for x in cov["ess_rows_per_seed"]]), "min": round(min(cov["ess_rows_per_seed"]))})
                rows_prod.append(row)
                for r in p["replicates"]:
                    for m, v in enumerate(r["log_evidence_increment"]):
                        rows_ev.append({"option": oname(t), "product": key, "stratum": SNAME[st], "seed": r["seed"], "mode": m, "ln_D_vs_base": v})
        cells = {}
        for key in MAPPED:
            if not all(key in D[s][t]["products"] for s in ss):
                continue
            O["products"][key] = {}
            for sc in SCHEMES:
                e, cell = entry(D, t, key, sc); O["products"][key][sc] = e
                if sc == "reweighted-0019":
                    cells[key] = cell
                rows_mix.append({"option": oname(t), "product": key, "name": PNAME[key], "mixture": sc, **{k: e[k] for k in ("q025", "median", "q975", "mode", "split_half_overlap_one_partition", "hdr50_area_km2", "hdr90_area_km2")},
                                 "map_mode_lat": e["smoothed_map_mode_lat_lon"][0], "map_mode_lon": e["smoothed_map_mode_lat_lon"][1], "mean_lat": e["mean_lat_lon"][0], "mean_lon": e["mean_lat_lon"][1],
                                 "share_contact_speed_above_212": e["share_contact_speed_above_212"], "stratum_weights": json.dumps({SNAME[s]: round(v, 4) for s, v in e["stratum_weights"].items()})})
                for fk, fv in e["family_stats"].items():
                    rows_fam.append({"option": oname(t), "product": key, "mixture": sc, "family": fk,
                                     "probability": e["family_probability"].get(fk, e["B_split"].get(fk, e["A_split"].get(fk))),
                                     "share_above_212_in_family": e["share_above_212_by_family"].get(fk), **fv})
        # evidence increments of the mixture, re-weighted strata (ln Z of each product against flight + EoF)
        wre = weights(D, t, "P1", "reweighted-0019"); wfix = weights(D, t, "P1", "fixed")
        z1 = mix_lnZ(D, t, "P1", wfix)
        O["evidence"] = {"ln_Z_P1_vs_filter_fixed_strata": z1}
        for key in CHAIN:
            if all(key in D[s][t]["products"] for s in ss):
                O["evidence"][key] = {"ln_evidence_vs_P1_mixture": mix_lnZ(D, t, key, wfix) - z1,
                                      "per_stratum_vs_P1": {SNAME[s]: cum_inc(D, s, t, key) - cum_inc(D, s, t, "P1") for s in ss},
                                      "split_halves_vs_base_per_stratum": {SNAME[s]: (D[s][t]["products"][key]["split_half"] or {}).get("log_evidence_increment") for s in ss}}
        # tension of H against G
        def lnR(hk, gk, pe, sc="reweighted-0019"):
            wg = weights(D, t, gk, sc); wp = weights(D, t, "P1", sc)
            num = sum(wg[s] * math.exp(cum_inc(D, s, t, hk) - cum_inc(D, s, t, gk) + 9.0) for s in ss)
            den = sum(wp[s] * math.exp(cum_inc(D, s, t, pe) - cum_inc(D, s, t, "P1") + 9.0) for s in ss)
            return math.log(num / den)
        for pair, (gk, hk, pe) in {"before searches": ("G", "H", "PE"), "without hydro": ("D", "Hn", "PE"), "not-computed excluded": ("Gx", "Hx", "PEx"),
                                   "after searches": ("Ga", "Ha", None), "rho 0 (P + COSMO surface)": ("G", "Hr0", "PEr0"), "rho 0.5 (P + COSMO, correlated)": ("G", "Hr5", "PEr5")}.items():
            if gk not in cells or hk not in cells:
                continue
            T = O["tension"][pair] = {"per_stratum": {}}
            for st in ss:
                if pe is None:
                    T["per_stratum"][SNAME[st]] = {"ln_R": None, "note": "not computed: needs flight+EoF+searches+Pléiades as the denominator"}; continue
                lr = (cum_inc(D, st, t, hk) - cum_inc(D, st, t, gk)) - (cum_inc(D, st, t, pe) - cum_inc(D, st, t, "P1"))
                g_r, h_r, pe_r, p1_r = ({r["seed"]: r for r in D[st][t]["products"][k]["replicates"]} for k in (gk, hk, pe, "P1"))
                ps = {k: (h_r[k]["log_evidence"] - g_r[k]["log_evidence"]) - (pe_r[k]["log_evidence"] - p1_r[k]["log_evidence"]) for k in h_r}
                shf = lambda key: D[st][t]["products"][key]["split_half"]["log_evidence_increment"]
                T["per_stratum"][SNAME[st]] = {"ln_R": lr, "ln_R_per_seed": ps, "ln_R_split_halves": [shf(hk)[j] - shf(gk)[j] - shf(pe)[j] for j in (0, 1)] if CHAIN[gk] == "P1" else None}
            cg, ch = cells[gk], cells[hk]; mg, mh = R0.hdr_mask(cg, 0.9), R0.hdr_mask(ch, 0.9)
            T.update({"ln_R": lnR(hk, gk, pe) if pe else None, "ln_R_fixed": lnR(hk, gk, pe, "fixed") if pe else None,
                      "hdr90_jaccard": float((mg & mh).sum() / (mg | mh).sum()), "share_of_H_hdr90_inside_G_hdr90": float((mg & mh).sum() / mh.sum()),
                      "H_mass_inside_G_hdr90": float(ch[mg].sum()), "map_mode_G": R0.smoothed_mode(cg), "map_mode_H": R0.smoothed_mode(ch),
                      "mode_displacement_nm": R0.nm_between(R0.smoothed_mode(cg), R0.smoothed_mode(ch)), "mean_G": mean_pos(cg), "mean_H": mean_pos(ch),
                      "mean_displacement_nm": R0.nm_between(mean_pos(cg), mean_pos(ch))})
        O["stratum_weights"] = {"reweighted-0019": {SNAME[s]: v for s, v in wre.items()}, "fixed": {SNAME[s]: v for s, v in wfix.items()}}
        O["_cells"] = {k: v for k, v in cells.items()}
    cells_all = {t: RES["options"][t].pop("_cells") for t in RES["options"]}
    (out / "pass1-results.json").write_text(json.dumps(RES, indent=1, default=float))
    for name, rows in (("products-per-stratum.csv", rows_prod), ("mixtures.csv", rows_mix), ("evidence-increments-per-seed-mode.csv", rows_ev),
                       ("families.csv", rows_fam), ("coverage-ess.csv", rows_cov)):
        keys = []
        for r in rows:
            keys += [k for k in r if k not in keys]
        with open(out / name, "w", newline="") as f:
            wr = csv.DictWriter(f, fieldnames=keys); wr.writeheader(); wr.writerows(rows)
    np.savez_compressed(work / "cells.npz", **{f"{t}|{k}": v for t, c in cells_all.items() for k, v in c.items()})
    print("ok", {t: len(v["strata"]) for t, v in RES["options"].items()})


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
