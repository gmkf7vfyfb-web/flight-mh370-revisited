"""Block 11: markdown tables for the results note, generated from reduce.py outputs (no hand transcription).
Usage: python tables.py <reduce_out_dir>   -> prints markdown to stdout
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
import prereg as R

OPT = {"D0": "00:19 Held Out (D0')", "D2": "R600 BTO + BFO (D2)", "D3": "both BFOs as recorded (D3)", "D4": "both BFOs, shared start-up offset (D4)"}


def f(x, d=2):
    if x is None or (isinstance(x, float) and not np.isfinite(x)): return "—"
    return f"{x:.{d}f}"


def e(x):
    if x is None or (isinstance(x, float) and not np.isfinite(x)): return "not reached below 1e-2"
    return f"{x:.1e}"


def main(out):
    out = Path(out); ul = pd.read_csv(out / "upper_limits.csv"); ev = pd.read_csv(out / "evidence_three_ways.csv")
    fam = pd.read_csv(out / "families.csv"); hol = pd.read_csv(out / "holland_p1_vs_p0.csv"); bf = pd.read_csv(out / "bayes_factors_conditionals.csv")
    co = json.load(open(out / "coincidence_summary.json")); summ = json.load(open(out / "summary.json"))
    L = []
    # --- upper limits, all latitudes, per option / p, alpha 0.05, IMOS gated and IMS proxy
    L.append("**Table 1. 95 % upper limits on the coupling efficiency η from the non-detection (all latitudes 41–20°S), per 00:19 option and dive probability p; α = 0.05; IMOS gated (IMS-proxy version in the last two columns).** 'Bayes ND' = 95 % posterior quantile under the log-uniform prior on [1e-6, 1e-2] with the non-detection likelihood (the prior alone gives 6.3e-3); 'Bayes full' = the same with the full likelihood including time-matched candidates; 'classical' = η at which the weighted probability of no detection falls to 0.05; P(nd) = weighted probability of no detection at η = 1e-2 / 1e-3 / anchor 2.1e-4.\n")
    L.append("| Option | p | ESS | Bayes ND | Bayes full | classical | P(nd) 1e-2 | P(nd) 1e-3 | P(nd) anchor | IMS-proxy Bayes ND | IMS-proxy P(nd) 1e-2 |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for o in R.OPTIONS:
        for p in R.PS:
            a = ul[(ul.option == o) & (ul.p == p) & (ul.alpha == 0.05) & (ul.lat_lo == -41) & (ul.lat_hi == -20)]
            g = a[a.receivers == "IMOS gated"].iloc[0]; i = a[a.receivers == "IMS proxy + IMOS"].iloc[0]
            L.append(f"| {OPT[o]} | {p:g} | {g.ess:,.0f} | {e(g['eta95_bayes_nondetection_logu_1e-6_1e-2'])} | {e(g.eta95_bayes_full_likelihood)} | {e(g.eta_excl95_classical if np.isfinite(g.eta_excl95_classical) else None)} | {f(g['pnd_at_1e-2'])} | {f(g['pnd_at_1e-3'])} | {f(g.pnd_at_anchor)} | {e(i['eta95_bayes_nondetection_logu_1e-6_1e-2'])} | {f(i['pnd_at_1e-2'])} |")
    # --- per 5-degree band, D0' p 0.5 (+ other options at p 0.5)
    L.append("\n**Table 2. Upper limits per 5° latitude band, p = 0.5, α = 0.05, IMOS gated (IMS proxy beside).** Share = run J mass in the band under the option; ESS = Kish effective sample size in the band.\n")
    L.append("| Option | Band | share | ESS | Bayes ND | classical | P(nd) 1e-2 | P(nd) 1e-3 | P(nd) anchor | IMS-proxy Bayes ND | IMS-proxy P(nd) 1e-2 |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for o in R.OPTIONS:
        for lo, hi in [(-41, -36), (-36, -31), (-31, -26), (-26, -21), (-21, -20)]:
            a = ul[(ul.option == o) & (ul.p == 0.5) & (ul.alpha == 0.05) & (ul.lat_lo == lo) & (ul.lat_hi == hi)]
            if not len(a): continue
            g = a[a.receivers == "IMOS gated"].iloc[0]; i = a[a.receivers == "IMS proxy + IMOS"].iloc[0]
            if g.share <= 0: L.append(f"| {OPT[o]} | {-lo}–{-hi}°S | 0 | 0 | — | — | — | — | — | — | — |"); continue
            L.append(f"| {OPT[o]} | {-lo}–{-hi}°S | {g.share:.4f} | {g.ess:,.0f} | {e(g['eta95_bayes_nondetection_logu_1e-6_1e-2'])} | {e(g.eta_excl95_classical if np.isfinite(g.eta_excl95_classical) else None)} | {f(g['pnd_at_1e-2'])} | {f(g['pnd_at_1e-3'])} | {f(g.pnd_at_anchor)} | {e(i['eta95_bayes_nondetection_logu_1e-6_1e-2'])} | {f(i['pnd_at_1e-2'])} |")
    # --- alpha sensitivity (D0' p 0.5, all latitudes)
    L.append("\n**Table 3. False-alarm-level sensitivity (D0', p = 0.5, all latitudes, IMOS gated).**\n")
    L.append("| α | Bayes ND | Bayes full | P(nd) 1e-2 | P(nd) anchor | ln Z_hydro (evidence, η marginal) |")
    L.append("|---|---|---|---|---|---|")
    for a_ in R.ALPHAS:
        g = ul[(ul.option == "D0") & (ul.p == 0.5) & (ul.alpha == a_) & (ul.lat_lo == -41) & (ul.lat_hi == -20) & (ul.receivers == "IMOS gated")].iloc[0]
        z = ev[(ev.option == "D0") & (ev.p == 0.5) & (ev.alpha == a_) & (ev.receivers == "IMOS gated")].iloc[0]
        L.append(f"| {a_:g} | {e(g['eta95_bayes_nondetection_logu_1e-6_1e-2'])} | {e(g.eta95_bayes_full_likelihood)} | {f(g['pnd_at_1e-2'])} | {f(g.pnd_at_anchor)} | {z.lnZ_hydro:+.4f} |")
    # --- evidence three ways
    L.append("\n**Table 4. Evidence three ways (α = 0.05, η marginalised): the module's log-evidence against the core, the median impact latitude and the mass north of 33°S for the core alone, combined with the module, and the module alone on a flat prior along the arc; KL(core ‖ combined).**\n")
    L.append("| Option | p | receivers | ln Z_hydro | median lat core | combined | alone | shift (°) | north of 33°S core | combined | alone | KL (nats) |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for o in R.OPTIONS:
        for p in R.PS:
            for rx in ("IMOS gated", "IMS proxy + IMOS"):
                z = ev[(ev.option == o) & (ev.p == p) & (ev.alpha == 0.05) & (ev.receivers == rx)].iloc[0]
                L.append(f"| {OPT[o]} | {p:g} | {rx} | {z.lnZ_hydro:+.4f} | {z.median_lat_core:.2f} | {z.median_lat_combined:.2f} | {z.median_lat_alone:.2f} | {z.shift_median_deg:+.3f} | {z.mass_north_33S_core:.4f} | {z.mass_north_33S_combined:.4f} | {z.mass_north_33S_alone:.3f} | {z.KL_core_vs_combined_nats:.4f} |")
    nd1 = pd.read_csv(out / "evidence_nd_only_1deg.csv")
    L.append("\n**Table 4b. The same with the non-detection likelihood only (amplitude-blind time matches removed; 1° resolution).**\n")
    L.append("| Option | p | receivers | ln Z (ND only) | median lat core | combined | shift (°) | north of 33°S core | combined | KL (nats) |"); L.append("|---|---|---|---|---|---|---|---|---|---|")
    for o in R.OPTIONS:
        for p in R.PS:
            for rx in ("IMOS gated", "IMS proxy + IMOS"):
                z = nd1[(nd1.option == o) & (nd1.p == p) & (nd1.receivers == rx)].iloc[0]
                L.append(f"| {OPT[o]} | {p:g} | {rx} | {z.lnZ_nd:+.4f} | {z.median_lat_core_1deg:.2f} | {z.median_lat_combined_nd:.2f} | {z.shift_median_deg:+.3f} | {z.mass_north_33S_core:.4f} | {z.mass_north_33S_combined_nd:.4f} | {z.KL_nats:.4f} |")
    # --- families
    L.append("\n**Table 5. Families (p = 0.5): share, ESS and the module's log-evidence per family (η marginal, α = 0.05).**\n")
    L.append("| Option | family | share | ESS | ln Z IMOS gated | ln Z IMS proxy |"); L.append("|---|---|---|---|---|---|")
    for o in R.OPTIONS:
        for _, r in fam[(fam.option == o) & (fam.p == 0.5)].iterrows():
            L.append(f"| {OPT[o]} | {r.family} | {r.share:.4f} | {r.ess:,.0f} | {f(r.lnZ_hydro_imos, 4) if pd.notna(r.lnZ_hydro_imos) else '—'} | {f(r.lnZ_hydro_ims_proxy, 4) if pd.notna(r.lnZ_hydro_ims_proxy) else '—'} |")
    # --- Bayes factors
    L.append("\n**Table 6. Bayes factors per conditional hypothesis (ln BF against the run J marginal under D0', p = 0.5; α = 0.05; η marginalised).** Prior column: run J D0' mass within 100 km of the locus. The IMS-proxy column for the Kadri rows is CIRCULAR (the hypothesis was built from the H01W 00:52:04 candidate) and is a sensitivity only.\n")
    L.append("| Hypothesis | implied impact (UTC) | vs 00:19:29 | prior mass < 100 km | receivers scored | P(nd) IMOS | L IMOS | ln BF IMOS gated | ln BF IMS proxy | ln BF IMOS at α 0.3 / 0.01 |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for _, r in bf.iterrows():
        L.append(f"| {r.hypothesis} | {r.t_impact_utc[:8]} | {r.implied_impact_vs_0019} | {r.prior_D0_mass_within_100km:.4f} | {r.scored_receivers if isinstance(r.scored_receivers, str) else 'none (arrivals outside every scored window: no information)'} | {r['Pnd_imos_marg_a0.05']:.3f} | {r['L_imos_a0.05']:.3f} | {r['lnBF_imos_a0.05']:+.3f} | {r['lnBF_ims_proxy_a0.05']:+.3f} | {r['lnBF_imos_a0.3']:+.3f} / {r['lnBF_imos_a0.01']:+.3f} |")
    L.append("\n**Table 7. Holland-type unarrested descent: ln BF (p = 1 against p = 0) from the module's evidence, per option and α (η marginal); 'ND only' uses the non-detection likelihood alone.**\n")
    L.append("| Option | α | ln BF p1:p0 IMOS gated | ND only | IMS proxy | ln BF p0.5:p0 |"); L.append("|---|---|---|---|---|---|")
    for _, r in hol.iterrows():
        L.append(f"| {OPT[r.option]} | {r.alpha:g} | {r.lnBF_p1_vs_p0_imos:+.3f} | {r.lnBF_p1_vs_p0_nondetection_only:+.3f} | {r.lnBF_p1_vs_p0_ims_proxy:+.3f} | {r.lnBF_p05_vs_p0_imos:+.3f} |")
    # --- coincidence
    L.append("\n**Table 8. Two-site coincidence summary.**\n")
    L.append(f"| Item | Value |\n|---|---|\n| Pair | {co['pair']} |\n| Lag | {co['lag_s']:.0f} s (pre-registered interval [809, 1536] s) |\n| Pair count against chance | {co['n_pairs_obs']} against {co['expected_by_chance']:.1f} expected; held-span permutation p = {co['p_perm']:.3f} |\n| Pair tests performed | {co['n_pair_tests']}; probability that at least one reaches p ≤ {co['p_perm']:.3f} by chance ≈ {co['expected_min_p_over_tests']:.2f} |\n| η needed for the rows (searches, median impact) | H01W {co['eta_needed_searches']['H01W']}, H08S {co['eta_needed_searches']['H08S']} (F-35A anchor 2.1e-4) |")
    for lc in co["loci"]:
        L.append(f"| Arc locus with this lag | {-lc['locus_lat']:.2f}°S {lc['locus_lon']:.2f}°E; implied impact {lc['implied_impact_utc'][:8]} ({lc['implied_impact_vs_0019']}); run J D0' mass within ±1° of the latitude {lc['prior_D0_mass_within_1deg']:.3f}; median E {lc['E_median_GJ']:.2f} GJ, τ {lc['tau_median_s']:.1f} s |")
        L.append(f"| η for P_D(H01W)·P_D(H08S) = 0.5 / 0.05 (proxy fits, α 0.05, +4.8 dB) | {lc['eta_both_pd_0.5_a0.05']:.3g} / {lc['eta_both_pd_0.05_a0.05']:.3g} (α 0.3: {lc['eta_both_pd_0.5_a0.3']:.3g} / {lc['eta_both_pd_0.05_a0.3']:.3g}) |")
        L.append(f"| P_D at the anchor, α 0.05 | H01W {lc['pd_H01W_at_anchor_a0.05']:.3f}, H08S {lc['pd_H08S_at_anchor_a0.05']:.3f}, both {lc['pd_both_at_anchor_a0.05']:.4f} |")
    # --- ESS
    L.append("\n**Table 9. Kish ESS per option / p (streamed over all rows + supplement; subsample 1-in-125 beside).**\n")
    L.append("| Option / p | ESS streamed | ESS subsample |"); L.append("|---|---|---|")
    for k in summ["ess_streamed"]:
        L.append(f"| {k} | {summ['ess_streamed'][k]:,.0f} | {summ['ess_subsample'][k]:,.0f} |")
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1])
