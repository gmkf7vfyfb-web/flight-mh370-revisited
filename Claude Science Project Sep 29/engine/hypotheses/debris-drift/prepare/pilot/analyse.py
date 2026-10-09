"""Analyse the drift pilot (brief section 5): the three numbers that size production.

Reads `<run>/nodes.csv` and `<run>/summary.toml` written by the debris-drift module
(`tests.rs::pilot` with `pilot.toml`) and writes `<out>/pilot-numbers.json` plus figures.

1. Throughput: particle-steps per second from the summary (two fields, two RK2 stages per step).
2. Arrival probability by detection segment and class: the fraction of each node's particles that
   strand in the segment by the window end; median and 5-95% over released nodes.
3. How fast relative likelihood changes with source separation. The semivariogram of ln L between
   node pairs, gamma(d) = 1/2 E[(lnL_i - lnL_j)^2], is corrected for Monte Carlo noise using the
   split-half estimates: each half uses N/2 particles, so var(lnL_A - lnL_B) is about 4 var(lnL),
   and the noise contribution to gamma is var(lnL). The correlation length is the separation at
   which the noise-corrected RMS change in ln L reaches one unit.

Plus a diagnostic only: the reference posterior (no-exhaustion-prior 00:19:37 map) reweighted by
the node surface read at each cell centre, with the latitude median and intervals before and
after. PROVISIONAL and not an impact posterior; never evidence.

Usage: python analyse.py <run-dir> <reference-map.csv> <out-dir>
"""
import json
import sys
import tomllib

import numpy as np
import pandas as pd

NM_PER_DEG = 60.0


def gc_nm(lat1, lon1, lat2, lon2):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dl = np.radians(lon2 - lon1)
    h = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * 3440.065 * np.arcsin(np.sqrt(np.minimum(h, 1)))


def variogram(df, col, bins):
    ok = df[col].notna() & df["ln_l_half_a"].notna() & df["ln_l_half_b"].notna() if col == "ln_l" else df[col].notna()
    d = df[ok]
    lat, lon, v = d.lat_deg.values, d.lon_deg.values, d[col].values
    i, j = np.triu_indices(len(d), 1)
    sep = gc_nm(lat[i], lon[i], lat[j], lon[j])
    g = 0.5 * (v[i] - v[j]) ** 2
    out = []
    for lo, hi in zip(bins[:-1], bins[1:]):
        m = (sep >= lo) & (sep < hi)
        out.append((0.5 * (lo + hi), int(m.sum()), float(np.mean(g[m])) if m.any() else float("nan")))
    return out


def weighted_quantiles(x, w, qs):
    o = np.argsort(x)
    c = np.cumsum(w[o]) / w.sum()
    return [float(x[o][np.searchsorted(c, q)]) for q in qs]


def bilinear_ln(surface, lat0, lon0, dlat, dlon, nlat, nlon, la, lo):
    fi, fj = (la - lat0) / dlat, (lo - lon0) / dlon
    if fi < 0 or fj < 0 or fi > nlat - 1 or fj > nlon - 1:
        return np.nan
    i, j = min(int(fi), nlat - 2), min(int(fj), nlon - 2)
    ti, tj = fi - i, fj - j
    pts = [(i, j, (1 - ti) * (1 - tj)), (i + 1, j, ti * (1 - tj)), (i, j + 1, (1 - ti) * tj), (i + 1, j + 1, ti * tj)]
    vals = [(w, surface.get((a, b), np.nan)) for a, b, w in pts if w > 0]
    if any(np.isnan(v) for _, v in vals):
        return np.nan
    m = max(v for _, v in vals)
    ws = sum(w for w, _ in vals)
    return m + np.log(sum(w / ws * np.exp(v - m) for w, v in vals))


def main(run, refmap, out):
    df = pd.read_csv(f"{run}/nodes.csv")
    with open(f"{run}/summary.toml", "rb") as f:
        s = tomllib.load(f)
    res = {"label": "PILOT, PROVISIONAL: land-mask beaching; one ocean model; one diffusivity; 295.66 deg prior extent. Not evidence."}
    res["throughput"] = {k: s[k] for k in ("particle_steps", "wall_s", "particle_steps_per_s", "threads", "trajectories")}
    res["fates"] = {k: s[k] for k in ("model_error_fraction", "left_domain_fraction")}
    res["nodes"] = {k: int(s[k]) for k in ("nodes_released", "nodes_scored", "nodes_unresolved", "nodes_land")}
    lcols = ["ln_l"] + [c for c in df.columns if c.startswith("ln_l_h")]
    res["resolved_fraction"] = {c: float(df[c].notna().mean()) for c in lcols}
    seg = s["segments"]
    arr = {}
    for cls in s["classes"]:
        arr[cls] = {}
        for k, name in enumerate(seg):
            v = df[f"p_{cls}_{k}"].values
            arr[cls][name] = {"median": float(np.median(v)), "p05": float(np.percentile(v, 5)), "p95": float(np.percentile(v, 95)), "zero_fraction": float(np.mean(v == 0))}
        v = df[f"p_{cls}_any_beach"].values
        arr[cls]["any_beach_incl_outside_segments"] = {"median": float(np.median(v))}
    res["arrival_probability"] = arr
    neff = [c for c in df.columns if c.startswith("n_eff_")]
    res["n_eff_median_by_find"] = {c[6:]: float(df[c].median()) for c in neff}
    both = df.ln_l.notna() & df.ln_l_half_a.notna() & df.ln_l_half_b.notna()
    noise_var = float(np.var(df.ln_l_half_a[both] - df.ln_l_half_b[both]) / 4) if both.sum() > 2 else float("nan")
    res["split_half"] = {"nodes": int(both.sum()), "noise_sd_ln_l_full": float(np.sqrt(noise_var)) if noise_var == noise_var else None,
                         "ln_l_sd_across_nodes": float(df.ln_l[both].std()) if both.sum() > 2 else None}
    bins = np.array([0, 15, 25, 40, 60, 90, 130, 200, 300])
    vg = {}
    for c in lcols:
        rows = variogram(df, c, bins)
        vg[c] = [{"sep_nm": a, "pairs": n, "gamma": g} for a, n, g in rows]
    res["variogram"] = vg
    if noise_var == noise_var:
        corr = [(r["sep_nm"], r["gamma"] - noise_var) for r in vg["ln_l"] if r["pairs"] > 20]
        res["variogram_noise_corrected_ln_l"] = [{"sep_nm": a, "gamma_minus_noise": g} for a, g in corr]
        cross = [a for a, g in corr if g >= 0.5]
        res["correlation_length_nm"] = cross[0] if cross else f"> {corr[-1][0] if corr else 'n/a'} (RMS change < 1 ln unit at all measured separations)"
    # Every bandwidth: Monte Carlo noise and correlation length. Split halves where the run wrote
    # them (`ln_l_h<km>_half_a/_b`, from 9475ae5); otherwise the variogram nugget, i.e. gamma in the
    # smallest separation bin, which over-states noise by the true change over that bin (declared).
    per_bw = {}
    for c in lcols:
        if "half" in c:
            continue
        ha, hb = (f"{c}_half_a", f"{c}_half_b") if c != "ln_l" else ("ln_l_half_a", "ln_l_half_b")
        rows = [r for r in vg[c] if r["pairs"] > 20 and r["gamma"] == r["gamma"]]
        ok = df[c].notna() & df.get(ha, pd.Series(np.nan, index=df.index)).notna() & df.get(hb, pd.Series(np.nan, index=df.index)).notna()
        if ok.sum() > 2:
            nv, how = float(np.var(df[ha][ok] - df[hb][ok]) / 4), "split-half"
        elif rows:
            nv, how = rows[0]["gamma"], f"variogram nugget (first bin, {rows[0]['sep_nm']} NM)"
        else:
            per_bw[c] = {"resolved_fraction": float(df[c].notna().mean()), "noise": "not measurable (no resolved nodes)"}
            continue
        corr = [(r["sep_nm"], r["gamma"] - nv) for r in rows]
        # Sustained crossing: the first separation from which every larger bin has noise-corrected
        # gamma >= 0.5 (RMS change >= 1 ln unit). Single-bin crossings are noise at this depth.
        cross = [corr[i][0] for i in range(len(corr)) if all(g_ >= 0.5 for _, g_ in corr[i:])]
        n_now = int(s["trajectories"]) / max(int(s["nodes_released"]), 1)
        per_bw[c] = {"resolved_fraction": float(df[c].notna().mean()), "noise_method": how, "noise_sd_ln_l": float(np.sqrt(nv)),
                     "signal_gamma_by_sep_nm": [{"sep_nm": a_, "gamma_minus_noise": g_} for a_, g_ in corr],
                     "correlation_length_nm": cross[0] if cross else f"> {corr[-1][0]}",
                     "particles_per_node_now": n_now,
                     "particles_per_node_for_noise_sd_0.5": n_now * nv / 0.25}
    res["per_bandwidth"] = per_bw
    hit_cols = [c for c in df.columns if c.startswith("hits_")]
    if hit_cols:
        res["hits_by_find"] = {c[5:]: {"median": float(df[c].median()), "p05": float(df[c].quantile(0.05)), "zero_fraction": float((df[c] == 0).mean())} for c in hit_cols}
    # Diagnostic reweighting of the reference map.
    g = s["grid"]
    k = df.node.values
    surf = {(int(n) // g["nlon"], int(n) % g["nlon"]): v for n, v in zip(k, df.ln_l.values) if v == v}
    ref = pd.read_csv(refmap, comment="#")
    lnl = np.array([bilinear_ln(surf, g["lat0"], g["lon0"], g["dlat"], g["dlon"], g["nlat"], g["nlon"], a, b) for a, b in zip(ref.lat_deg, ref.lon_deg)])
    m = ref.mass.values
    cov = float(m[np.isfinite(lnl)].sum())
    res["reweighting_diagnostic"] = {"reference_mass_with_scored_surface": cov}
    if cov > 0.5:
        ok = np.isfinite(lnl)
        w = m[ok] * np.exp(lnl[ok] - lnl[ok].max())
        before = weighted_quantiles(ref.lat_deg.values[ok], m[ok], [0.05, 0.25, 0.5, 0.75, 0.95])
        after = weighted_quantiles(ref.lat_deg.values[ok], w, [0.05, 0.25, 0.5, 0.75, 0.95])
        res["reweighting_diagnostic"].update({"before_q05_q25_q50_q75_q95": before, "after_q05_q25_q50_q75_q95": after,
                                             "median_shift_nm": (after[2] - before[2]) * NM_PER_DEG, "ess_fraction": float(w.sum() ** 2 / (w ** 2).sum() / ok.sum())})
    with open(f"{out}/pilot-numbers.json", "w") as f:
        json.dump(res, f, indent=1)
    df.to_csv(f"{out}/pilot-nodes.csv", index=False)
    print(json.dumps({k: res[k] for k in ("throughput", "nodes", "resolved_fraction", "split_half")}, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:4])
