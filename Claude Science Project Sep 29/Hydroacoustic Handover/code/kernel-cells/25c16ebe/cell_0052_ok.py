ed("""---

## 1. Mission
""",
"""---

## 0. What changed in version 5

Twelve changes. A–C alter what the module is obliged to produce; D–H close places where a prose
requirement in version 4 was silently not honoured; I–L are additions from the audit and the
literature pass. Nothing was removed: §2's original ten rules, §5's fuel-coupling argument and its
case against conditioning on flame-out, §6's log-on treatment, §7's two sweep axes, §9's provenance
discipline and §11's two corrected tests were all honoured and stand as written.

| | change | where |
|---|---|---|
| A | build status rewritten and made a per-sweep obligation | §3 |
| B | the three arms become an acceptance condition, with what a V1a-only sweep may claim | §10.2 |
| C | the onset-boundary diagnostic becomes a gate with a statistic, a place and a threshold | §4 |
| D | level-off altitudes and sustained low-altitude flight become bounds with reported statistics | §4 |
| E | all four control outcomes in every family; weights stated per family; zero weights justified | §4 |
| F | **new rules 11 and 12**: a support change is logged and held-out-revalidated; the silent-exclusion review runs before every sweep | §2 |
| G | **new test 6**: prior recovery under the importance correction, reported per run | §11 |
| H | weight concentration reported beside ESS, per seed and per stratum | §2.6 |
| I | three emission rules: in-sample not sidecar, NaN not placeholder, energy partition declared | §2 interface |
| J | the uncontrolled-arm calibration gate is defined, with what may not be quoted while unpassed | §8 |
| K | four pitfalls added, including the Boeing-against-00:19 contradiction and the fit-failure asymmetry | §12 |
| L | the ordering — simulate, then test, never shape — leads the mission | §1 |

Three measured failures against version 4's own requirements are recorded in place rather than
corrected silently, because each shows a requirement that could not be checked as written: the
onset-boundary condition (§4, 21.6 per cent against a new 5 per cent gate), the two named level-off
altitudes (§4, outside the configured support), and sustained low-altitude flight (§4, 1.75 per cent
against a new 5 per cent floor).

---

## 1. Mission
""", "0 changelog")

ed("""5. Core requests for the missing `ImpactView` fields.
6. The tests of §11.""",
"""5. Core requests for the missing `ImpactView` fields.
6. The tests of §11, including test 6.
7. **The dive-fraction hyper-prior as ruled.** The dive branch was ruled to carry a U[0,1]
   hyper-prior with a marginal of 0.5. As built it is a fixed probability of 0.5 drawn independently
   per descent: measured across 6,232 parents with 20.4 push-over draws each, the across-parent
   standard deviation of the dive share is 0.1140, against 0.1108 predicted for a fixed probability
   and 0.3025 for a per-parent draw from U[0,1]. The fixed form asserts that exactly half of piloted
   push-overs continue to the surface as a known quantity, and so understates the uncertainty on the
   latent that drives the R1200-conditioned result — the 90 per cent impact area moved from 59,000
   to 47,000 km² when the branch was added, and 64 per cent of the southern group are levelled-off
   push-overs. Implement the hyper-prior, re-run the R1200 cells, and report the posterior on the
   fraction as a result: it is directly estimable and currently pinned.
8. **The output of §2 rule 12**, the silent-exclusion review, as a table in each run note.""", "deliverables")
print(EDITS[-3:])
assert v5.count("## 0. What changed") == 1
