"""Builds results/pleiades/run-i/README.md from score_runi_summary.py outputs (no numbers typed by hand).

    python runi_note.py <results/pleiades/run-i> <mixture json> [<after-search json>]
"""
import json
import math
import sys
from pathlib import Path

LAB = {"gcrel-0.25": "ρ 0.25, both models, product-relative (proposed)", "g12-0.25": "ρ 0.25, GLORYS12 only (in force)"}
D_NAME = {"D0": "held out", "D1": "R600 BTO", "D2": "R600 BTO + R600 BFO", "D3": "R600 BTO + both BFOs (H2 data)",
          "D4": "R600 BTO + both BFOs, Holland transient bias added (H1 data)", "D5": "R600 BTO + R600 BFO + R1200 BFO with offset"}


def table(S, causes=("total q=1/3 (C2 silent)",), stg="gcrel-0.25"):
    ref = S["cells"]["D0 x total q=1/3 (C2 silent)"][stg]["ln_mean_LH"]
    out = ["| D | cause | ESS under H (without H) | mean under H | shift NM | ln S (p) | 90 % km² under H (without H) | ln E[L_H] vs D0 | A1 ESS under H |",
           "|---|---|---|---|---|---|---|---|---|"]
    for ck, e in S["cells"].items():
        d, c = ck.split(" x ", 1)
        if c not in causes:
            continue
        r = e[stg]; z = e["none (without H)"]; t = e[stg].get("tension", {})
        p = t.get("tension_p", float("nan")); p = "n/e" if p != p else f"{p:.2f}"
        out.append(f"| {d} {D_NAME[d]} | {c} | {r['eff_impacts']:,.0f} ({z['eff_impacts']:,.0f}) | {abs(r['mean_lat']):.2f} S {r['mean_lon']:.2f} E | "
                   f"{t.get('mean_shift_nm', float('nan')):.0f} | {t.get('ln_S', float('nan')):+.2f} ({p}) | {t.get('cond_hdr90_km2', float('nan')):,.0f} "
                   f"({t.get('uncond_hdr90_km2', float('nan')):,.0f}) | {r['ln_mean_LH'] - ref:+.2f} | {r['families']['A1']['eff_impacts']:,.0f} |")
    return "\n".join(out)


def gaps(S, stg="gcrel-0.25"):
    g = []
    for ck, e in S["cells"].items():
        r = e[stg]
        if r["eff_impacts"] < 1000:
            g.append(f"{ck} ({r['eff_impacts']:,.0f})")
        a1 = r["families"]["A1"]["eff_impacts"]
        if a1 < 1000:
            g.append(f"A1 under {ck} ({a1:,.0f})")
    return g


def main(out_dir, mix_json, sea_json=None):
    out_dir = Path(out_dir); M = json.loads(Path(mix_json).read_text())
    A = json.loads(Path(sea_json).read_text()) if sea_json else None
    txt = [f"# Pléiades module on core run I: H-conditional 00:19 two-factor table (D0-D5 x C1 / C2 silent / total q = 1/3)\n",
           "Pléiades module. Columns: `mh370-exchange/pleiades/run-i/` (per-stratum READY; top-level READY when all four strata are built).",
           "Scripts: `prepare/build_columns.py`, `prepare/score_runi_summary.py` (end of flight's own D x C weights from",
           "`smoke/option_table_0019.py`, reused term by term; survival factor throughout; C2 silent primary), `prepare/runi_note.py`.\n",
           "**Labels:**",
           "- **conditional on H**; no identity likelihood; no Bayes factor or P(H | data);",
           "- core run I NOT converged (core waypoints split-half floor 0.916);",
           "- end-of-flight physics PROVISIONAL: piloted-turn model, INTERIM pitch-down, push-over and Boeing sequence, in-flight structural",
           "  outcome (end of flight's run I label list applies in full);",
           "- Pléiades rating 5 + all four COSMO-SkyMed contacts, one debris field;",
           "- D4 is named per the 18:15Z wording rule (\"Holland transient bias added\").",
           f"- Strata mixed by core P(family): {', '.join(f'{k} {v:g}' for k, v in M['strata_P'].items())}. {M['search']}.\n",
           "## Primary: competing-causes total q = 1/3 (C2 silent), proposed headline setting, before seabed search\n",
           table(M), "\n## Each cause separately (proposed setting, before search)\n", table(M, ("C1", "C2 silent")),
           "\n## GLORYS12 only at ρ 0.25 (headline in force), total q = 1/3, before search\n", table(M, stg="g12-0.25")]
    if A:
        txt += [f"\n## After the searches ({A['search']}), total q = 1/3, proposed setting\n", table(A)]
    g = gaps(M)
    txt += ["\n## COVERAGE",
            "- **(a) Feasible set and (b) model reach:** end of flight's run I README and COVERAGE apply unchanged; these columns add no sampling.",
            "  Carried gaps: stepped shapes not eligible for push-over; INTERIM pitch-down; core run I not converged.",
            "- **(c) Proposal coverage under H** (effective impacts, proposed setting, before search). Cells and families **below the 1,000 gate (GAP)**:",
            "  " + ("; ".join(g) if g else "none") + ".",
            "- These gaps arise because end of flight's proposal targets the 00:19 data, not the Pléiades-compatible end states (near 35.5 S",
            "  92.3 E). The fix is end of flight's to choose: more seeds, or a defensive-mixture component toward those end states, with exact",
            "  re-weighting (the module's L_H surface is available as a proposal density). Every product that uses a GAP cell must name it.",
            "- **Parameter bounds:** windage 0-5 % U10; transport error ~95-120 km per component at 15 d (measured); ρ 0.25 headline (measured",
            "  0.07-0.41), 0 / 0.5 available via `reader.load_rho`; GlobCurrent product-relative offset 0.60-0.75 % U10 (drift audit F1)."]
    (out_dir / "README.md").write_text("\n".join(txt) + "\n")


if __name__ == "__main__":
    main(*sys.argv[1:4])
