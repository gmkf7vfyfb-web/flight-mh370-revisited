
# Item 10 work order — REVISION 2, 15 October 2026 (supersedes section 2 of
# `core-handover-and-item10-2026-10-15.md`)

**For a FRESH core thread. Not to be started without Pete's explicit GO.** Read
`core-handover-2026-10-15.md` in this folder first; it is authoritative over anything below where
they differ.

## What changed from revision 1, and why

1. **This is a design task, not a wiring task.** Revision 1 said "wire and validate core request 9,
   already built". The core handover establishes that core request 9 (commit `d4e67b09`) is a
   different device: unnormalised within-parent weights in the terminal stage,
   `[terminal] within_parent = "unnormalised"`. The device this order needs — a core-side hand-off
   proposal that draws 00:11 parents with the 00:19 bursts in hand — **was never specified and never
   built.** Give it a new request number. Do not call it request 9.
2. **The regression gate value in revision 1 is stale.** −96.66146918417472 was seed 1 of
   `davey2016.toml` as it stood on about 1–2 October; the base prior track changed to 289.7° on
   9 October, so the current tree will not reproduce it. The gates in use are B and C, byte
   comparison of output files against references from an unmodified build (handover section 2).
   **The references were lost with the swept workspace and must be regenerated from HEAD before any
   code is touched.**

## The problem, measured

Any arm scoring both 00:19 bursts is below 1,000 effective impacts and Holland's two readings are
below 100. Effective hand-off parents per stratum per seed, over 100,000 parents: 50,966 with no
00:19 data; 3,983 under the 00:19:29 burst; 216 under the 00:19:37 burst; 170 under both with the
transient bias added; 38.8 under both as recorded, where one trajectory carries 12.3% of the weight.
In three arms the effective impacts equal the effective parents, so the limit is the hand-off and no
improvement inside the descent stage can lift it. About ten of 100,000 cruise states can produce the
00:19 pair.

**A look-ahead hand-off already exists and did not solve it.** Run I used `handoff-lookahead-d`
(core request 18): hand-off rows resampled with a look-ahead weight and corrected exactly. End of
flight measured that on run D it gave no more effective parents after 00:11 than run C (205–593
against 877–2,058). Why it failed is the first thing to understand.

## Phase 1 — diagnose and design. No large run.

1. Regenerate the gate B and C references from an unmodified HEAD build. Record the current seed-1
   log evidence of `config/sensitivity/regress-seed1.toml` so the project has a valid byte-identity
   value again.
2. Diagnose the request 18 look-ahead: what quantity did it look ahead on, and why did it not
   concentrate the hand-off on parents able to produce the 00:19 pair? The likely answer is that it
   scored the 00:19 position or range but not the vertical-speed history the BFO pair demands — a
   parent at the right place but the wrong energy state cannot produce −184 Hz in 8 s.
3. Specify the replacement. It must draw 00:11 parents in proportion to their probability of
   producing the 00:19 observations under the descent stage, with the exact prior-to-proposal ratio
   carried so the target is unchanged. One candidate: use the descent stage itself as the look-ahead
   — fly K cheap pilot descents per candidate parent, score them against the 00:19 bursts, and use
   the pilot mean as the proposal weight. Evaluate the cost against the measured 1,179 µs of CPU per
   descent.
4. Smoke the design on deskstar at small scale: effective hand-off parents for `both/no-offset` and
   `both/startup-offset`, before and after, per seed, with the prior recovered under the importance
   correction (aimed latents uniform on their support with the likelihood off; the end-of-flight
   aimed proposals reach a maximum deviation of 0.0030, use that as the standard).

**Phase 1 stop condition:** if the smoke does not raise effective parents, the hand-off constraint is
not addressable by a proposal. That is a finding and should be reported as one.

**Phase 1 cost:** one to two sessions; smoke runs under an hour on deskstar. Nothing on the Mac
heavy lock.

## Phase 2 — the run. Only on Pete's explicit GO, after Phase 1 is posted.

One four-family core run with the new proposal, chained on deskstar by the existing mechanism
(`job-run-i.sh`, about 2.5–3 h), specified together with item 1 of the run J change list (waypoint
and free-flight convergence) so one run serves both. Then an end-of-flight sweep (about 5 h) and
module re-scoring (about a day).

Note from the handover: adding the 18:25:27 R600 epoch renumbers every later step and shifts every
later random stream, so any run including it can never be byte-compared with run I — compare
statistically.

## Acceptance (Phase 2)
1. Gates B and C pass with the feature off.
2. Prior recovery under the importance correction, as above.
3. Effective hand-off parents for both two-burst arms reported before and after, per stratum per
   seed; target 1,000 effective impacts per arm.
4. All-partition split-half for every stratum against the count-dependent floor.
5. A COVERAGE section, and a statement of whether the change altered the prior or only the precision.

## Out of scope
The 00:19 likelihood itself, the family priors, the fuel model, the end-of-flight dynamics. Widening
any prior. Using core request 9 (`within_parent = "unnormalised"`) in a production run without
Pete's GO — it was held for his GO and never given.


**Erratum (15 Oct 2026, late).** The statement above that core request 9 was "held for his GO and never given" came from the core handover and is superseded. The end-of-flight run I recipe already includes `within-parent-unnormalised.toml` (core request 9). Pete then answered core's question on it ("I will go with your recommendation"), which core recorded as approval for end of flight, including its use in the run I sweep. See `results/run-i-downstream-status-2026-10-15.md` §2.4.
