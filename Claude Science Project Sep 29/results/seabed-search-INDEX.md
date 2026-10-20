# Searched areas: what this module has produced, and what each thing concludes

Index as at 10 October 2026, 07:10 UTC. Written because there are now a dozen notes and no map.
Read top to bottom: the first three are the method, the next four are the results, the last four are
the sensitivities and the record.

**The headline, in one line.** The completed seabed searches remove **27–66 %** of the impact
probability depending on how the 00:19 transmissions are interpreted, and they make the remaining
distribution **wider, not narrower** — a non-detection is not a localisation.

## The method

| note | what it settles |
|---|---|
| `seabed-search-methods-draft.md` | the paper's methods text: the likelihood, its reduction to Davey eq. (11.1), the layers, every parameter's source, the composition contract, the convergence rule, seven limitations and the ordered uncertainty budget |
| `seabed-detectable-target.md` | what a detection *is* — two-part, with recognition at campaign level, not per piece — the per-sensor size response, and how a field partly inside a swath is scored |
| `seabed-search-references.md` | the citation ledger. Davey ch. 11 sets the method out and **does not apply it**; Stone et al. applied it to AF447; Davey's ref. [40] is the 2011 Metron report, not the 2014 paper. Holland's two hypotheses, and what the ATSB actually did with the 00:19 BFOs |

## The results

| note | what it concludes |
|---|---|
| `seabed-search-289-fullscale/` | full scale, plain: **Z = 0.7335**; 29.7 % of impact mass on searched ground; the median moves *north*, and the distribution widens |
| `seabed-search-289-fullscale-alive/` | the same under `+alive`, with the ρ sweep, the variant table and the Davey eq. (11.2) curve. **ρ dominates the budget and has no published value** |
| `seabed-search-0019-options/` | across the 00:19 options the searches remove **27 % to 66 %**; scoring any burst shrinks the impact PDF 1.9–3.9× but the search evidence then widens almost every option |
| `seabed-search-0019-h1h2/` and `-alive/` | Pete's four panels. **Holland H1 and H2 are NOT ESTIMABLE** at 36 and 82 effective impacts of 12.8 × 10⁶; the bottleneck is the 00:11 hand-off, not this module |

## The sensitivities, and the negative results worth keeping

| note | what it concludes |
|---|---|
| `seabed-size-response.md` | `g_k` is implemented and **saturates**: realistic fields give g within 10⁻⁹ of 1. Effort spent on the piece-size distribution cannot move this posterior |
| `seabed-field-coverage-289/` | reading coverage over settling's real settled fields rather than at the impact point is worth **0.0003 in Z**. What counts as a detection is worth **0.023** and has no measurement behind it |
| `seabed-repeat-search-dependence.md` | the Phase 2 union hides **17,390.6 km² of repeat coverage**; 15.0 % of the ground was swept more than once, and the dependence choice is worth 0.002 at full scale |
| `seabed-residual-views-and-oi2025.md` | the residual view is a *view*, with a double-application guard; the Ocean Infinity 2025–26 variant is worth 0.0041, small and measurable |
| `seabed-bluefin21-area.md` | the Bluefin-21 layer is 771.41 km² of display geometry against the ATSB's stated 860 km², and removes 0.0000 at every ρ: that search is 2,473 km from the mass |
| `seabed-search-prior-289-vs-29566.md` | the prior track matters more than convergence did at smoke scale; the 289.7° prior strengthens the search evidence |

## Open, and who owns it

1. **Re-run on the (b) impacts** — mine, pre-approved, waiting on `end-of-flight/next-run/READY`.
   `hypotheses/seabed-search/rerun_next.sh` is verified end to end and runs all three products.
2. **Holland H1 against H2 as posteriors** — end of flight's and core's: needs a hand-off that carries
   the 00:19 data. No terminal-stage proposal can lift it.
3. **The residual view on `crates/compose`** — core's: the approved dev-dependency has not landed, so
   the views run on the `mh370 evaluate` path, which is a disclosed deviation.
4. **ATSB Figure 73's three percentages behind q = 0.945** — blocked, not untried: five failed fetches.
   q is reported as 0.945 with the bound 0.940–0.945.
5. **Which core run supplies the prior** — not yet propagated, and possibly the largest term in the
   budget: (a) and (b) differ by 0.26° in the source 00:19 median.

## Standing cautions for anyone quoting this module

- Ocean Infinity coverage is **inferred, grade C**, and never merged into the ATSB-only estimate;
  `engine/hypotheses/seabed-search/coverage/PROVENANCE.md` has the required footnote.
- Anything below 1,000 effective impacts is reported as **unconverged**, never as a result.
- Bathymetric mapping is not search coverage; planned coverage and contract areas exclude nothing;
  the 2014 surface search belongs to ocean drift.
- Alternative settling draws are alternative **outcomes**: average their non-detection probabilities,
  never multiply.
