"""Block 11 amendment A4: old (imos_tl_ramcorr_arc) against new (imos_tl_ram_arc) statistics, plus the amplitude-weighted variant,
as markdown tables for the note's addendum. Usage: python addendum_tables.py <old_reduce_dir> <new_reduce_dir>
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
import prereg as R
OPT = {"D0": "00:19 Held Out (D0')", "D2": "R600 BTO + BFO (D2)", "D3": "both BFOs as recorded (D3)", "D4": "both BFOs, shared start-up offset (D4)"}


def e(x):
    return "not reached below 1e-2" if (x is None or (isinstance(x, float) and not np.isfinite(x))) else f"{x:.1e}"


def main(old, new):
    old, new = Path(old), Path(new); L = []
    uo, un = pd.read_csv(old / "upper_limits.csv"), pd.read_csv(new / "upper_limits.csv")
    eo, en = pd.read_csv(old / "evidence_three_ways.csv"), pd.read_csv(new / "evidence_three_ways.csv")
    no, nn = pd.read_csv(old / "evidence_nd_only_1deg.csv"), pd.read_csv(new / "evidence_nd_only_1deg.csv")
    ho, hn = pd.read_csv(old / "holland_p1_vs_p0.csv"), pd.read_csv(new / "holland_p1_vs_p0.csv")
    bo, bn = pd.read_csv(old / "bayes_factors_conditionals.csv"), pd.read_csv(new / "bayes_factors_conditionals.csv")
    co, cn = json.load(open(old / "coincidence_summary.json")), json.load(open(new / "coincidence_summary.json"))
    sel = lambda d, o, p, rx, lo=-41, hi=-20: d[(d.option == o) & (d.p == p) & (d.alpha == 0.05) & (d.receivers == rx) & (d.lat_lo == lo) & (d.lat_hi == hi)].iloc[0]
    L.append("**Table A1. Upper limits and P(no detection | η), OLD IMOS TL (constant rule-2 correction) against NEW (RAM along the grid), all latitudes, α = 0.05, IMOS gated; 'amp' = the amplitude-consistency-weighted match variant (new table).**\n")
    L.append("| Option | p | Bayes ND old → new | Bayes full old → new | full, amp-weighted (new) | P(nd) 1e-2 old → new | P(nd) 1e-3 old → new | P(nd) anchor old → new |")
    L.append("|---|---|---|---|---|---|---|---|")
    for o in R.OPTIONS:
        for p in R.PS:
            a, b = sel(uo, o, p, "IMOS gated"), sel(un, o, p, "IMOS gated"); c = sel(un, o, p, "IMOS gated (amplitude-weighted)") if (un.receivers == "IMOS gated (amplitude-weighted)").any() else None
            L.append(f"| {OPT[o]} | {p:g} | {e(a['eta95_bayes_nondetection_logu_1e-6_1e-2'])} → {e(b['eta95_bayes_nondetection_logu_1e-6_1e-2'])} | {e(a.eta95_bayes_full_likelihood)} → {e(b.eta95_bayes_full_likelihood)} | {e(c.eta95_bayes_full_likelihood) if c is not None else 'n/a'} | {a['pnd_at_1e-2']:.2f} → {b['pnd_at_1e-2']:.2f} | {a['pnd_at_1e-3']:.2f} → {b['pnd_at_1e-3']:.2f} | {a.pnd_at_anchor:.2f} → {b.pnd_at_anchor:.2f} |")
    L.append("\n**Table A2. Per 5° band, p = 0.5, α = 0.05, IMOS gated: Bayes ND limit and P(no detection) at η = 1e-2, old → new.**\n")
    L.append("| Option | Band | share | ESS | Bayes ND old → new | P(nd) 1e-2 old → new | P(nd) anchor old → new | classical (new) |"); L.append("|---|---|---|---|---|---|---|---|")
    for o in R.OPTIONS:
        for lo, hi in [(-41, -36), (-36, -31), (-31, -26), (-26, -21), (-21, -20)]:
            a, b = sel(uo, o, 0.5, "IMOS gated", lo, hi), sel(un, o, 0.5, "IMOS gated", lo, hi)
            if b.share <= 0: continue
            L.append(f"| {OPT[o]} | {-lo}–{-hi}°S | {b.share:.4f} | {b.ess:,.0f} | {e(a['eta95_bayes_nondetection_logu_1e-6_1e-2'])} → {e(b['eta95_bayes_nondetection_logu_1e-6_1e-2'])} | {a['pnd_at_1e-2']:.2f} → {b['pnd_at_1e-2']:.2f} | {a.pnd_at_anchor:.2f} → {b.pnd_at_anchor:.2f} | {e(b.eta_excl95_classical if np.isfinite(b.eta_excl95_classical) else None)} |")
    L.append("\n**Table A3. Evidence three ways, old → new (α = 0.05, η marginal): ln Z, median-latitude shift, mass north of 33°S (core → combined), KL; the amplitude-weighted variant and the non-detection-only control on the new table.**\n")
    L.append("| Option | p | ln Z old → new | shift (°) old → new | north of 33°S combined old → new (core) | KL old → new | amp-weighted: ln Z / shift / KL | ND-only (new): ln Z / shift / KL |"); L.append("|---|---|---|---|---|---|---|---|")
    for o in R.OPTIONS:
        for p in R.PS:
            a = eo[(eo.option == o) & (eo.p == p) & (eo.alpha == 0.05) & (eo.receivers == "IMOS gated")].iloc[0]; b = en[(en.option == o) & (en.p == p) & (en.alpha == 0.05) & (en.receivers == "IMOS gated")].iloc[0]
            ca = en[(en.option == o) & (en.p == p) & (en.alpha == 0.05) & (en.receivers == "IMOS gated (amplitude-weighted)")]; c = ca.iloc[0] if len(ca) else None; d = nn[(nn.option == o) & (nn.p == p) & (nn.receivers == "IMOS gated")].iloc[0]
            L.append(f"| {OPT[o]} | {p:g} | {a.lnZ_hydro:+.3f} → {b.lnZ_hydro:+.3f} | {a.shift_median_deg:+.2f} → {b.shift_median_deg:+.2f} | {a.mass_north_33S_combined:.3f} → {b.mass_north_33S_combined:.3f} ({b.mass_north_33S_core:.3f}) | {a.KL_core_vs_combined_nats:.3f} → {b.KL_core_vs_combined_nats:.3f} | {(f"{c.lnZ_hydro:+.3f} / {c.shift_median_deg:+.2f} / {c.KL_core_vs_combined_nats:.3f}") if c is not None else 'n/a'} | {d.lnZ_nd:+.3f} / {d.shift_median_deg:+.2f} / {d.KL_nats:.3f} |")
    L.append("\n**Table A4. Holland-type descent ln BF (p = 1 : p = 0), α = 0.05, old → new; amplitude-weighted and ND-only on the new table.**\n")
    L.append("| Option | IMOS gated old → new | amp-weighted (new) | ND only old → new | IMS proxy old → new |"); L.append("|---|---|---|---|---|")
    for o in R.OPTIONS:
        a = ho[(ho.option == o) & (ho.alpha == 0.05)].iloc[0]; b = hn[(hn.option == o) & (hn.alpha == 0.05)].iloc[0]
        L.append(f"| {OPT[o]} | {a.lnBF_p1_vs_p0_imos:+.3f} → {b.lnBF_p1_vs_p0_imos:+.3f} | {(f"{b.lnBF_p1_vs_p0_ampweighted:+.3f}") if pd.notna(b.get('lnBF_p1_vs_p0_ampweighted', np.nan)) else 'n/a'} | {a.lnBF_p1_vs_p0_nondetection_only:+.3f} → {b.lnBF_p1_vs_p0_nondetection_only:+.3f} | {a.lnBF_p1_vs_p0_ims_proxy:+.3f} → {b.lnBF_p1_vs_p0_ims_proxy:+.3f} |")
    L.append("\n**Table A5. Conditional hypotheses, ln BF on the gated IMOS term (α = 0.05), old → new, with the amplitude-weighted variant (new) and the IMS-proxy sensitivity (new; Kadri rows circular).**\n")
    L.append("| Hypothesis | P(nd) IMOS old → new | ln BF IMOS old → new | amp-weighted (new) | ln BF IMS proxy (new) |"); L.append("|---|---|---|---|---|")
    for (_, a), (_, b) in zip(bo.iterrows(), bn.iterrows()):
        assert a.hypothesis == b.hypothesis
        L.append(f"| {b.hypothesis} | {a['Pnd_imos_marg_a0.05']:.3f} → {b['Pnd_imos_marg_a0.05']:.3f} | {a['lnBF_imos_a0.05']:+.3f} → {b['lnBF_imos_a0.05']:+.3f} | {(f"{b['lnBF_imos_amp_a0.05']:+.3f}") if 'lnBF_imos_amp_a0.05' in b and pd.notna(b['lnBF_imos_amp_a0.05']) else 'n/a'} | {b['lnBF_ims_proxy_a0.05']:+.3f} |")
    L.append("\n**Table A6. Two-site coincidence locus (unchanged geometry; the η requirement uses the IMS proxy fits and IMS TL, which A4 does not touch).**\n")
    for lc_o, lc_n in zip(co["loci"], cn["loci"]):
        L.append(f"- Locus {-lc_n['locus_lat']:.2f}°S {lc_n['locus_lon']:.2f}°E, implied impact {lc_n['implied_impact_utc'][:8]}: η for P_D(both) = 0.5 / 0.05 at α 0.05: old {lc_o['eta_both_pd_0.5_a0.05']:.3g} / {lc_o['eta_both_pd_0.05_a0.05']:.3g} → new {lc_n['eta_both_pd_0.5_a0.05']:.3g} / {lc_n['eta_both_pd_0.05_a0.05']:.3g}; run J mass within ±1° {lc_n['prior_D0_mass_within_1deg']:.3f}.")
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
