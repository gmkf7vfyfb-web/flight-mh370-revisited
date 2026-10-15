# Australian non-recovery term: the pre-registered sensitivities (drift, G26)

15 Oct 2026, ocean drift module. Work order: `threads/work-orders/work-order-2026-10-15.md` section 2 (item 9).
Pre-registration: `debris-drift-australia-preregistration.md` (primary B, Pete, 12 Oct 2026). Pilot result:
`debris-drift-australia-pilot.md`. Script: `debris-drift-australia-sensitivities.py`.

> Reach-limited pilot, 15–120 E, GLORYS12 only. Debris that would travel east of 120 E is not tracked, which is
> the population this term is about. Not to be composed until the full pilot runs.

> **Labels:** PILOT; REACH-LIMITED; GLORYS12 + ERA5 only; 175 of 178 pilot nodes scored in all options; beaching on
> entry to the land mask, no refloat; interim, not evidence; run I NOT CONVERGED; the end-of-flight uncontrolled arm
> is NOT CALIBRATED. Impact prior not applied, nothing composed, no Bayes factor.

## No new transport was run, and none was needed

The level options are linear in the stored per-segment arrival coefficients, so the pre-registration required all of
them to be computed in **one** run (`debris-drift-australia-nonrecovery-design.md`, "Options to be computed in ONE
run"). The completed pilot of 12–13 Oct 2026 did that: `ln_l` (B), `ln_l_lev_A`, `ln_l_lev_C`, `ln_l_lev_off` and
`ln_l_lev_searcher`, each with one split-half stream, are columns of the committed node table
`debris-drift-australia-pilot-nodes.csv`. The sensitivities therefore cost no compute; what was missing was the
reporting the work order asks for. Nothing in the pre-registered option definitions was changed.

The base surface for the drift-only latitude is the run A GLORYS12 node log-likelihood with the per-node change
carried by inverse-distance weighting from the pilot nodes, as in the pilot analysis. Only 367 of the 710 run A nodes
are recoverable on disk (`debris-drift-two-model-nodes.csv`); the other 343 are not. The published 710-node figures
are reproduced to within one grid step (0.5 deg) on the 367 nodes: off 30.17 S against 30.67 S, B 27.59 S against
28.17 S, A 28.17 against 28.67, C 28.67 against 29.17. A second cross-check on the 175 pilot nodes alone, with no
carry, is in the last column below.

## Result

Drift alone, GLORYS12, uniform prior over the node grid with a cos(latitude) area weight. "Shift" is the movement of
the mean latitude, which is not quantised by the 0.5 deg grid as the median is; the uncertainty after it is split-half
Monte Carlo noise.

| option | median | 90 per cent interval | shift north of the mean latitude (deg) | change in log evidence (nat) | median, pilot nodes only |
|---|---|---|---|---|---|
| Term off | 30.2 S | 37.2 to 24.2 S | — | — | 30.2 S |
| Option C (low) | 28.7 S | 34.2 to 23.7 S | +1.54 ± 0.35 | -0.57 ± 0.06 | 29.5 S |
| Option A (equal to find coasts) | 28.2 S | 33.2 to 23.7 S | +1.86 ± 0.38 | -0.74 ± 0.07 | 29.2 S |
| Searcher variant | 27.7 S | 32.7 to 23.7 S | +2.26 ± 0.48 | -0.48 ± 0.04 | 28.7 S |
| Option B (pre-registered primary) | 27.6 S | 32.2 to 23.7 S | +2.43 ± 0.49 | -1.08 ± 0.07 | 28.7 S |

Mean change in ln L per node: B −3.02, A −2.07, searcher −1.84, C −1.55 (split-half noise of the change 0.30–0.45).

Share of floating objects that arrive on each coast group, by source latitude, as a mean over the three object
classes. This is the transport, and it is the same under every option; the options differ only in how much a
non-find on each coast counts.

| source latitude band | Australia, all coasts | Western Australia | south coast and Tasmania | north-east | Indian Ocean territories | coasts where debris was found | beached anywhere | left the model domain |
|---|---|---|---|---|---|---|---|---|
| 37–42 S | 18.6 % | 18.4 % | 0.0 % | 0.0 % | 0.24 % | 5.0 % | 35.9 % | 42.0 % |
| 34–37 S | 11.5 % | 11.2 % | 0.0 % | 0.0 % | 0.28 % | 10.1 % | 44.8 % | 18.8 % |
| 31–34 S | 4.7 % | 4.5 % | 0.0 % | 0.0 % | 0.17 % | 12.9 % | 47.2 % | 11.9 % |
| 28–31 S | 2.1 % | 2.0 % | 0.0 % | 0.0 % | 0.10 % | 13.7 % | 51.3 % | 11.4 % |
| 25–28 S | 0.7 % | 0.6 % | 0.0 % | 0.0 % | 0.07 % | 13.5 % | 54.8 % | 13.1 % |
| 20–25 S | 0.3 % | 0.2 % | 0.0 % | 0.0 % | 0.11 % | 10.7 % | 61.9 % | 17.8 % |

Nodes per band: 38, 36, 35, 28, 22, 16 from south to north.

## The question the work order asks, answered

**The northward movement is a property of the non-recovery evidence, not of the remoteness weighting.** Option A
removes the remoteness weighting altogether — every Australian coast is given the same identification level as the
coasts where debris was found, in each period — and the estimate still moves north by 1.86 deg of mean latitude
against B's 2.43 deg, which is 77 per cent of the movement; option C, which makes every Australian coast less
watched than any find coast, keeps 63 per cent of it. The weighting sets the size of the term, not its sign. The
mechanism is in the second table and is pure transport: sources at 37–42 S put 18.6 per cent of floating objects on
Australian coasts against 5.0 per cent on the coasts where debris was found, while sources north of 25 S put 0.3 per
cent there against 10.7 per cent. No weighting of a coast with no finds can turn that into a southward movement.

**The stop condition is not triggered.** The direction does not reverse under any sensitivity: all four options move
the estimate north, in every statistic, and in both split-half streams separately (mean-latitude shift, half a /
half b: B +2.16 / +1.19, A +1.64 / +0.88, C +1.39 / +0.69, searcher +2.11 / +1.15 deg). The searcher variant, which
raises the detection level on southern Mozambique and north-east Madagascar for Gibson's 2016 searches, moves the
estimate furthest north after B.

The change in log evidence is small in every option (−0.49 to −1.08 nat, Monte Carlo noise 0.04–0.07): the term
redistributes support within the arc band rather than arguing against the drift model as a whole.

## What this does not settle

The reach limit bites hardest exactly where the term acts. The domain ends at 120 E, so the Australian south coast,
Victoria and Tasmania are unreachable — their arrival share is 0.0 per cent by construction, not by transport — and
41.9 per cent of the particles released at 37–42 S leave the domain and are counted as never found. The southern
penalty is therefore probably understated, which would move the estimate further north, not back south. Refloat
(none here), GlobCurrent, the level-prior sigma of 1 nat and the early-awareness assumption remain open. G26 stays
OPEN and nothing here is for composition.

## COVERAGE

(a) Feasible set: impacts as in run I (NOT CONVERGED). (b) Model reach: 175 scored nodes of the 178-node pilot, 3
unresolved in the south; Australian coasts west of 120 E only (east of 120 E unreachable, GAP); refloat not modelled
(GAP); breakup origin not modelled (GAP); base surface 367 of 710 run A nodes (the rest not on disk, declared).
(c) Proposal: 1e5 particles per node from the pilot; split-half Monte Carlo noise 0.35–0.49 deg on the mean-latitude
shift and 0.04–0.07 nat on the change in log evidence. Parameter bounds: the pre-registered levels, unchanged;
sigma 1 (no source, declared); window to 30 Jun 2016.
