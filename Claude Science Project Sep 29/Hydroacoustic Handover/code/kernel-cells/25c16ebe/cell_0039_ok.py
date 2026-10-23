sec = r"""
---

## 9. The published-benchmark check, assembled independently

An independent pass over the retrievable literature was run alongside this audit and is saved as
`eof-published-benchmarks.csv` (91 rows) and `eof-published-benchmarks.md`. Three conclusions from
it change how §5 and §7 should be read.

**a. The module's most downstream-critical outputs have no published calibration target at all.**
No retrievable source publishes an estimate of MH370's impact speed, impact flight-path angle,
impact energy or energy-transfer duration. Per-case impact conditions were withheld from the Boeing
engineering-simulator dataset. So the fields hydroacoustics and settling depend on most cannot be
validated against the literature in principle, only against the dynamics. That raises the weight
that recommendation 2 has to carry: the dive-case trace fit is not one validation among several, it
is the only aircraft-specific validation available for the uncontrolled arm.

**b. There is an unresolved contradiction inside the official material, and the module sits on top
of it.** Ulich and Iannello record that **none of the ten Boeing cases is in a steep descent as the
7th arc is crossed** — so Boeing's own simulations of uncontrolled flight after dual fuel exhaustion
and the descent rate derived from the 00:19 frequency offsets do not agree with each other. This is
directly relevant to the forcing question of the addendum. The module's steep arm is selected by the
00:19 data and is not produced by the published uncontrolled-flight simulations; that tension is a
property of the evidence, not of the sampler, and it should be stated as a result of the study
rather than resolved by either side. The benchmark sheet records it as stated and does not reconcile
it, which is the correct handling.

**c. Holland's descent bounds are published by hypothesis and the separation is usually lost.**
At 00:19:29 the bounds are 3,900 to 14,800 ft/min under the satellite-data-unit-restart hypothesis
against 2,900 to 6,800 ft/min under the no-warm-up hypothesis, and the 8 s mean downward
acceleration is 0.68 g. The module's declared-alternative treatment of the offset model is the right
structure for this, and the sheet's separation of the two bounds should be carried into the methods
so the comparison is made against the matching hypothesis rather than the merged range.

**Provenance warning on the sheet itself.** The Australian safety-bureau reports and the
investigation report's performance appendix could not be retrieved in that pass — the origins
returned nothing or were gated. The Boeing simulator case figures on the sheet are therefore second
hand, reported via Davey et al. and via Ulich and Iannello citing documents the pass could not read,
and 8 of 91 rows are recorded as not retrieved. This matters less than it would otherwise, because
**the project already holds the primary material locally**: the ten engineering-simulator exports at
1 Hz and the performance appendix text are both in the project's own inputs. The sheet should be
reconciled against those local copies before any figure from it reaches the paper, and the local
copies used in preference wherever they overlap.

Six further numbers are flagged on the sheet as untraceable to a primary source, including the
maximum operating speed and Mach number, the 777-200ER maximum lift-to-drag ratio and driftdown
schedule, and a descent-rate pair attributed to Holland that his paper does not contain. The module
currently takes its maximum lift-to-drag ratio of 20.8 to 21.4 from its own Poll–Schumann
construction and the appendix driftdown, which is the defensible route; the methods should say so
explicitly rather than cite a circulating figure.
"""
cur = open("eof-audit-2026-10-13.md").read()
cur = cur.replace("\n---\n\n## 8. Two things to decide", sec + "\n---\n\n## 8. Two things to decide")
# move section 8 after 9 ordering fix: just renumber
cur = cur.replace("## 8. Two things to decide", "## 10. Two things to decide")
open("eof-audit-2026-10-13.md","w").write(cur)
print(cur[cur.find("## 9."):cur.find("## 9.")+200])
print("...\n", cur[cur.find("## 10."):cur.find("## 10.")+120])
