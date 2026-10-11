# 22:41 family A against family B by B onset window, with the late-onset proposal and unnormalised weights (11 Oct 2026)

**SMOKE, PROVISIONAL, not evidence.** Core run D `next-d-free` seed 1, 22:41 hand-off, N = 1 child per parent, scored at the
00:11 arc (`m0011`) and at 00:11 + R600 (inflated). Arm A as in `eof-a-vs-b-2241-run-d-standin.md`; four B arms: self-normalised
or unnormalised within-parent weights (core request 9), with or without the late B-onset proposal (G-k: 0.3 weight on onsets
after 00:11, `full/b-late-onset-proposal.toml`). Data: `eof-a-vs-b-2241-late-onset-n1.json`; tool `smoke/ab_evidence.py`.

| B arm | B onset prior share before 23:15 / 23:15-00:11 / after 00:11 | ln BF A:B (00:11) | ln BF A against each window (00:11) | Effective parents per window |
|---|---|---|---|---|
| self-normalised, earlier proposal | 0.666 / 0.323 / 0.011 | +0.29 | +4.49 / -0.74 / -1.77 | 1.5 / 83.0 / 3.3 |
| self-normalised, + late proposal | 0.606 / 0.361 / 0.033 | +0.25 | +6.11 / -0.58 / -1.38 | 2.3 / 78.8 / 15.1 |
| unnormalised, earlier proposal | 0.624 / 0.362 / 0.014 | +0.26 | +4.67 / -0.63 / -1.79 | 1.5 / 83.1 / 3.2 |
| unnormalised, + late proposal (adopted) | 0.623 / 0.363 / 0.014 | +0.27 | +6.15 / -0.68 / -1.27 | 2.3 / 69.0 / 25.2 |

At 00:11 + R600 (inflated), adopted arm: ln BF A:B +0.67; against the windows +7.73 / -0.15 / -1.85 (effective parents 1.1 /
31.9 / 251.6).

Reading: with unnormalised weights the two proposals give the same prior shares (0.624 / 0.362 / 0.014 against 0.623 / 0.363 /
0.014), which is the check that the proposal correction is exact; the self-normalised shares moved with the proposal (0.666 vs
0.606 before 23:15; 0.011 vs 0.033 after 00:11). The overall ln BF A:B is +0.26 to +0.29 in every arm: weak, and it is the sum
of strong evidence against B onsets before 23:15 and weak evidence for B onsets after 23:15. "Weak evidence for A" therefore
means "evidence against early B descents", not "against B".

## COVERAGE
- (a) Feasible: a deliberate descent can begin at any time from 22:41 to the last fuel (B onset prior by window above).
- (b) Reach: the module produces B onsets in all three windows.
- (c) Proposal coverage: effective parents for B before 23:15 are 1.1-2.3 in every arm: a COVERAGE GAP (the window carries 62%
  of the B prior but is strongly disfavoured, so few parents survive); after 00:11, 3.2 -> 25.2 with the late proposal (G-k
  partly closed at N = 1; full N expected to give the same factor times about 6).
- Bounds: as in the stand-in note; late-proposal weight 0.3, late fraction 0.1 (declared proposal choices, exactly corrected).
