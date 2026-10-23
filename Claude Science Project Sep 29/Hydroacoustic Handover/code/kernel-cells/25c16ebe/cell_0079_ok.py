wo2 = open("eof-work-order-items-1-2.md").read()
add_sec = r"""
---

## Item 0 — the 22:41 arm, and why it goes first

Run I has `handoff-m2241` hand-offs, so the V1b and V2 arms can be repeated on current physics
without a core re-run. Nothing has been started.

**Sizing confirmed against measured cost.** The 11 October stand-in ran 51.2 M descents in 3 h 11 min
at 8 threads, which is 1,791 µs of CPU per descent against run-i-dive's measured 1,179 µs — a cost
ratio of **1.52×**, not the 6× the flight time alone would suggest. The pre-onset cruise segment is
cheap because it carries no descent machinery. So at 12 threads:

| configuration | descents | CPU-hours | wall-hours |
|---|---|---|---|
| 16 children, as run-i-dive | 128.0 M | 63.7 | **5.3** |
| 8 children, as run I | 102.4 M | 50.9 | **4.2** |
| 4 children × 4 descents, 8 seeds × 4 strata | 51.2 M | 25.5 | **2.1** |

The module thread's own 3–5 h estimate is right.

**Run it before items 1 and 2, not after, and not combined.** Three reasons:

1. **It is the failed gate.** The onset-boundary statistic is 21.6 per cent against the contract's
   new 5 per cent threshold, and it is the only outstanding item that changes what the module can
   *conclude* rather than how precisely it concludes it.
2. **Rule 11 needs a "before".** Adding asymmetric thrust is a change to the model's reach, so the
   contract requires held-out log-evidence and impact median before and after. The 22:41 arm lands
   on exactly the population item 1 touches — 46.2 per cent of the deliberate family begins its
   descent with one engine running, and from a 22:41 start the single-engine phase is longer than
   from 00:11. Without the arm measured on unchanged physics, a later difference cannot be
   attributed between the checkpoint and the asymmetry.
3. **Running it twice is not waste.** The second run, after item 1, answers "how much does
   asymmetric thrust move the impact distribution?" — a question that would otherwise need its own
   experiment.

**Label it** as conditional on symmetric single-engine flight, which is the honest statement until
item 1 lands.

**What the run must emit, or it does not settle the thing it is for:**

- the **onset-boundary statistic per family**, under held-out weighting and under each 00:19 option,
  measured against the 22:41 boundary;
- the **support-truncation fraction** from `takeover_time` — currently a NaN column because the hook
  does not pass its result to `descend` (a core request). If that is still unlanded, say so and
  report the boundary statistic alone;
- the distribution of the per-trajectory onset-window length, since predicted exhaustion is now a
  per-trajectory quantity rather than the removed 00:17:30 anchor.

**The testable prediction.** The earlier 22:41 smoke on core run D gave ln BF (A against B) of about
+0.27, with evidence against deliberate onsets before 23:15 and weak evidence for later ones. If
that holds, the supported onset mass will concentrate at the **late** end of the window rather than
against the 22:41 boundary — which would mean 22:41 is a sufficient checkpoint and 21:41 is
unnecessary. If instead mass piles at 22:41, the run has told you to go to 21:41, and that is a
result rather than a failure.

---

## Smoke gates before any of the three runs

Yes — and the sequence matters, because three of these four cannot be substituted for each other.
Standing rule from `AGENTS.md`: **a smoke run is never evidence.**

1. **`make smoke H=end-of-flight`** — about a minute, code paths only. Catches a parse or API break,
   nothing else. Rebuild first: a stale binary fails immediately on an unknown field.
2. **The unit tests, including the new closed-form ones for item 1** — zero thrust asymmetry
   reproduces the current model to machine precision, one-engine straight flight balances
   `T · y_engine_m`, and the uncorrected yaw rate matches the analytic turn rate. These are the real
   check on item 1 and they are not smoke.
3. **The effective-sample-size measurement at the parent and child counts you intend to use** —
   §7 of the contract requires this *before* any end-of-flight run, and it is the gate that would
   have caught the both-00:19-burst collapse to 38.8 effective parents before a full sweep rather
   than after. For the 22:41 arm, measure it at both the 22:41 hand-off and at 00:11, and compare
   against what the filter achieves at 00:11. Choose the counts from the measurement, not from the
   illustrative values in `config.rs`.
4. **A reduced-scale 22:41 run** that reports the boundary statistic, the support-truncation
   fraction and — for any new aimed proposal component — test 6, the recovery of the uniform prior
   under the sampling weight alone. This gates the full run and is not evidence for any impact
   distribution, log-evidence or family share.

Gate 3 is the one most likely to be skipped and the most expensive to skip.
"""
# insert Item 0 before Item 1
wo2 = wo2.replace("---\n\n## Item 1 — asymmetric thrust", add_sec.strip()+"\n\n---\n\n## Item 1 — asymmetric thrust")
wo2 = wo2.replace("# Work order — end-of-flight dynamics items 1 and 2",
                  "# Work order — end-of-flight: the 22:41 arm, then dynamics items 1 and 2")
wo2 = wo2.replace("""## Sequencing

The two items are **independent and can run in parallel**""",
"""## Sequencing

Item 0 first, on its own, on unchanged physics. Then items 1 and 2, which are
**independent and can run in parallel**""")
open("eof-work-order-items-1-2.md","w").write(wo2)
print(re.findall(r"^## .*$", wo2, re.M))
