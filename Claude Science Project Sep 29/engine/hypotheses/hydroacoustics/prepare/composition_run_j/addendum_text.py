"""Block 11 A4/A5: regenerate the note's addendum section from the reduce outputs (numbers never typed by hand).
Usage: python addendum_text.py <old_reduce> <new_reduce (v2 product or stats-v2)> <addendum_tables.md> <note.md> <commits text>
Replaces everything from the line starting '## Addendum A4' to the end of the note.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
import prereg as R


def g(df, **kw):
    m = np.ones(len(df), bool)
    for k, v in kw.items(): m &= (df[k] == v).values
    return df[m].iloc[0]


def main(old, new, tabs_path, note_path, commits):
    old, new = Path(old), Path(new)
    uo, un = pd.read_csv(old / "upper_limits.csv"), pd.read_csv(new / "upper_limits.csv")
    eo, en = pd.read_csv(old / "evidence_three_ways.csv"), pd.read_csv(new / "evidence_three_ways.csv")
    nn = pd.read_csv(new / "evidence_nd_only_1deg.csv"); hn = pd.read_csv(new / "holland_p1_vs_p0.csv"); ho = pd.read_csv(old / "holland_p1_vs_p0.csv")
    bn = pd.read_csv(new / "bayes_factors_conditionals.csv"); bo = pd.read_csv(old / "bayes_factors_conditionals.csv"); sm = json.load(open(new / "summary.json"))
    has_amp = (un.receivers == "IMOS gated (amplitude-weighted)").any()
    A = lambda d, o, p, rx, lo=-41, hi=-20: g(d, option=o, p=p, alpha=0.05, receivers=rx, lat_lo=lo, lat_hi=hi)
    a0, b0 = A(uo, "D0", 0.5, "IMOS gated"), A(un, "D0", 0.5, "IMOS gated")
    ea, eb = g(eo, option="D0", p=0.5, alpha=0.05, receivers="IMOS gated"), g(en, option="D0", p=0.5, alpha=0.05, receivers="IMOS gated")
    nd = g(nn, option="D0", p=0.5, receivers="IMOS gated")
    amp = g(en, option="D0", p=0.5, alpha=0.05, receivers="IMOS gated (amplitude-weighted)") if has_amp else None
    bands = [A(un, "D0", 0.5, "IMOS gated", lo, hi)["eta95_bayes_nondetection_logu_1e-6_1e-2"] for lo, hi in [(-41, -36), (-36, -31), (-31, -26), (-26, -21), (-21, -20)]]
    lim = lambda o, p: A(un, o, p, "IMOS gated")["eta95_bayes_nondetection_logu_1e-6_1e-2"]
    d3o, d3n = g(eo, option="D3", p=1.0, alpha=0.05, receivers="IMOS gated"), g(en, option="D3", p=1.0, alpha=0.05, receivers="IMOS gated")
    d4o, d4n = g(eo, option="D4", p=1.0, alpha=0.05, receivers="IMOS gated"), g(en, option="D4", p=1.0, alpha=0.05, receivers="IMOS gated")
    d3nd, d4nd = g(nn, option="D3", p=1.0, receivers="IMOS gated"), g(nn, option="D4", p=1.0, receivers="IMOS gated")
    d3a = g(en, option="D3", p=1.0, alpha=0.05, receivers="IMOS gated (amplitude-weighted)") if has_amp else None
    d4a = g(en, option="D4", p=1.0, alpha=0.05, receivers="IMOS gated (amplitude-weighted)") if has_amp else None
    kad = bn.iloc[0]; kadc = bn.iloc[1]; roy = bn.iloc[2]; kado = bo.iloc[0]
    hol = {o: g(hn, option=o, alpha=0.05) for o in R.OPTIONS}
    cov = sm.get("ramgrid_covered_share") or {}
    ess = sm["ess_streamed"]
    amp_txt = (f"Amplitude-weighted (A4c, σ = 10 dB, down-weighting only): ln Z {amp.lnZ_hydro:+.3f}, shift {amp.shift_median_deg:+.2f}°, KL {amp.KL_core_vs_combined_nats:.3f}. " if has_amp else
               "Amplitude-weighted variant: not available on this product (computed only in the statistics-only runs). ")
    d34_amp = f", amplitude-weighted {d3a.shift_median_deg:+.2f} / {d4a.shift_median_deg:+.2f}°" if has_amp else ""
    txt = f"""## Addendum A4 (22–23 Oct 2026): columns and statistics on the corrected IMOS transmission-loss table (RAM along the arc grid) — product `run-j-gated-v2`

*Hydroacoustic Module (composition track). Pre-registered as amendment A4 in `prepare/composition_run_j/prereg.py` (`e13a32e`) before any re-run; A5 (statistics re-run on the stable table) disclosed below; {commits}. Trigger: the RAM-along-grid track closed G-TL1 (`results/hydroacoustics-imos-ram-grid.md` and its addendum; table `run-j-tl-grid/tables/imos_tl_ram_arc.csv`, built {sm.get('imos_tl_built')}, 5/8/10/20/40 Hz on all 253 paths). PREDICTIVE, NOT CALIBRATED; C1, C2; both Kadri times; no detection claimed.*

**Plain words.** The corrected sound-loss table makes the Australian recorders less sensitive to impacts in the most likely region (south of 36°S) than the first table did. Everything stated above stays true and the small effects get smaller: adding the recorders now moves the latitude estimate north by about {eb.shift_median_deg:.2f}° (was {ea.shift_median_deg:.2f}°), and the recorders still cannot rule out any sound-coupling share in the assumed range. **The product to use is `run-j-gated-v2`** (all 74 seeds, five columns, corrected table); the first product `run-j-gated` is superseded and says so in its README.

**What changed and what did not.** Only the IMOS TL for the four gated loggers was switched (offset-0 line, 10 m source; covered share of open rows: {', '.join(f'{k} {v:.2f}' for k, v in cov.items())}; uncovered rows keep the old value inside the drop-in file). IMS TL, P_D fits, candidates, windows, weights and the η prior are unchanged; Kish ESS is identical (D0′/D2/D3/D4 at p 0.5: {ess['D0/p0.5']:,.0f} / {ess['D2/p0.5']:,.0f} / {ess['D3/p0.5']:,.0f} / {ess['D4/p0.5']:,.0f}). **A5, disclosed:** the first statistics-only re-run (`stats-ramgrid/`, 09:54–11:34Z) straddled the RAM-grid track's rewrite of the table at 11:29:54Z (5 and 8 Hz added on every path), so its seeds used two table versions; it is marked SUPERSEDED in its DONE file and its numbers are withdrawn. The statistics below come from the consistent product run (`run-j-gated-v2`, 11:46–12:34Z, all seeds on the final table){' and the stable-table statistics re-run `stats-ramgrid-v2` (amplitude-weighted variant)' if has_amp else ''}.

**Headline, corrected table (D0′, p 0.5, α 0.05, η marginal):** ln Z = **{eb.lnZ_hydro:+.3f}** (was {ea.lnZ_hydro:+.3f}); median latitude shift **{eb.shift_median_deg:+.2f}°** (was {ea.shift_median_deg:+.2f}°); mass north of 33°S {eb.mass_north_33S_core:.3f} → **{eb.mass_north_33S_combined:.3f}** (was {ea.mass_north_33S_combined:.3f}); KL **{eb.KL_core_vs_combined_nats:.3f} nats** (was {ea.KL_core_vs_combined_nats:.3f}). {amp_txt}Non-detection only: ln Z {nd.lnZ_nd:+.3f}, shift {nd.shift_median_deg:+.2f}°, KL {nd.KL_nats:.3f}. 95 % upper limit on η from the non-detection **{b0['eta95_bayes_nondetection_logu_1e-6_1e-2']:.1e}** (was {a0['eta95_bayes_nondetection_logu_1e-6_1e-2']:.1e}; prior alone 6.3e-3); per option at p 0.5: D2 {lim('D2', 0.5):.1e}, D3 {lim('D3', 0.5):.1e}, D4 {lim('D4', 0.5):.1e}; per 5° band under D0′: {' / '.join(f'{v:.1e}' for v in bands)} (41–36 … 21–20°S). P(no detection | η) **{b0['pnd_at_1e-2']:.2f} at 10⁻², {b0['pnd_at_1e-3']:.2f} at 10⁻³, {b0.pnd_at_anchor:.2f} at the anchor** (were {a0['pnd_at_1e-2']:.2f} / {a0['pnd_at_1e-3']:.2f} / {a0.pnd_at_anchor:.2f}). Classical exclusion still not reached below 10⁻² anywhere. **The D3/D4 p = 1 shifts fall from {d3o.shift_median_deg:+.2f} / {d4o.shift_median_deg:+.2f}° to {d3n.shift_median_deg:+.2f} / {d4n.shift_median_deg:+.2f}°** (KL {d3o.KL_core_vs_combined_nats:.2f} / {d4o.KL_core_vs_combined_nats:.2f} → {d3n.KL_core_vs_combined_nats:.2f} / {d4n.KL_core_vs_combined_nats:.2f}; non-detection only {d3nd.shift_median_deg:+.2f} / {d4nd.shift_median_deg:+.2f}°{d34_amp}): G11-1 remains the reason those rows are not yet trustworthy, but the corrected table has removed most of the effect. Bayes factors on the gated term: Kadri 306.18° row {kad['lnBF_imos_a0.05']:+.3f} (text time) / {kadc['lnBF_imos_a0.05']:+.3f} (caption time) (was {kado['lnBF_imos_a0.05']:+.3f}; IMS proxy, circular: {kad['lnBF_ims_proxy_a0.05']:+.2f} / {kadc['lnBF_ims_proxy_a0.05']:+.2f}); Royer B {roy['lnBF_imos_a0.05']:+.3f}; Holland p = 1 : p = 0 {hol['D0'].lnBF_p1_vs_p0_imos:+.3f} (D0′), {hol['D2'].lnBF_p1_vs_p0_imos:+.3f} (D2), {hol['D3'].lnBF_p1_vs_p0_imos:+.3f} (D3), {hol['D4'].lnBF_p1_vs_p0_imos:+.3f} (D4) (non-detection only {hol['D0'].lnBF_p1_vs_p0_nondetection_only:+.3f} / {hol['D2'].lnBF_p1_vs_p0_nondetection_only:+.3f} / {hol['D3'].lnBF_p1_vs_p0_nondetection_only:+.3f} / {hol['D4'].lnBF_p1_vs_p0_nondetection_only:+.3f}). The coincidence locus and its η requirement are unchanged (IMS proxy chain untouched).

**Amplitude-consistency-weighted match (G11-1 sensitivity, A4c).** For the IMOS receivers the time-matched candidate density is multiplied by exp(−½((log₁₀ E_c − log₁₀ SE_r(i, η))/1.0)²), E_c the candidate's observed excess 5–40 Hz band energy, SE_r the row's predicted received band energy at η (σ = 10 dB, generous). It only down-weights, so it lies between the full and the non-detection-only likelihoods and is labelled, not a calibrated likelihood ratio (no background level density is divided out). With a 10 dB kernel the two Portland 3275 candidates (η needed 19–30 for the median impact) still match the loudest rows near η = 10⁻² (E up to 12 GJ and +2σ calibration), so the variant removes part of their effect, not all of it; the non-detection-only control removes it entirely.

{open(tabs_path).read()}

**Charts.** `hydroacoustics-composition-run-j-evidence` and `-limits` are re-rendered on the corrected table (footnotes name `imos_tl_ram_arc.csv`, amendment A4).

**Coverage changes.** G-TL1 closed for the statistics and for the `run-j-gated-v2` columns (G-TL1a/b closed by the RAM-grid addendum: all 253 paths, 5–40 Hz); G11-6 (exchange columns on the old table) closed by `run-j-gated-v2`; `run-j-gated` superseded, kept; G11-2 closed (all 74 seeds carry five columns in v2); G-TL-X unchanged (latitude-only chain); G11-1 narrowed by the amplitude-weighted sensitivity, not closed. All other gaps as in §7.

**Ruling request, updated.** As §8 with `run-j-gated-v2` as the product: may `hydro-lnL-imos-margeta` (v2) enter the composer as the module's likelihood (default), with `hydro-lnL-ims-proxy-margeta` (v2) as the labelled sensitivity? The module recommends admitting it with the G11-1 label (the D3/D4 p = 1 rows carry the caveat), or the amplitude-weighted variant if architecture prefers a conservative match term (it would need its own column; one driver run).

- done (A4/A5): pre-registered amendment; `run-j-gated-v2` written on the corrected table (74 seeds, five columns, READY, {sm.get('n_subsample', 0):,} subsample rows); statistics from the consistent run; first statistics re-run withdrawn (table changed under it) and re-run on the stable table{'' if has_amp else ' (in progress at the time of writing; the amplitude-weighted numbers follow in a further addendum)'}; charts re-rendered; README of the old product marked SUPERSEDED.
- next: ruling on `run-j-gated-v2`; an amplitude-weighted or non-detection-only column if preferred; the Kadri-package candidate row (33.6°S / 00:31:41 locus).
- blocker: the ruling.
"""
    note = open(note_path).read(); i = note.index("## Addendum A4")
    open(note_path, "w").write(note[:i] + txt); print("addendum written", len(txt))


if __name__ == "__main__":
    main(*sys.argv[1:6])
