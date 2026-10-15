# Run I through the downstream modules: status, and what must be settled before run J (15 October 2026, late)

Sources: `mh370-exchange/*/run-i*` READMEs and READY files; module inboxes in `coordination/`. Family codes: A1 = cruise to FE then uncontrolled descent; A2 = cruise to FE then controlled or arrested descent; B = planned descent with ditching approach begun before FE.

## 1. Which end-of-flight impact sets exist on run I, and who has scored each

| End-of-flight set | What it is | Drift | Hydro | Pléiades | Searched areas | Settling | Composer |
|---|---|---|---|---|---|---|---|
| `run-i` (12 Oct; now on the SSD only) | original sweep, 4 strata × 8 seeds, 102.4M rows | ✓ | ✓ (predictive: lnL_gated = 0) | ✓ | ✓ (without Ocean Infinity) | ✓ | ✓ pass 2, pass 2b |
| `run-i-dive` (13 Oct) | dive branch, p = 0.5; supersedes run-i for impact conditions | ✓ (all 4 strata READY) | ✗ | ✗ | ✗ | ✗ | ✗ |
| `run-i-joined-v2` (14 Oct) | 22:41 planned-descent arm joined with the 00:11 arm | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ (family shares only) |
| round-3 laws, order b sweeps (15 Oct, running) | sensitivities: round-3 laws; sampled bank limit; fixed 90° | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

So one full pass of run I has been through every module, and the composer, on the 12 Oct impact set. The later end-of-flight improvements have been through drift only, or nowhere.

## 2. Rulings made after that pass, not yet applied to any composed product
1. **Ocean Infinity in the base** (Pete, 13 Oct 00:40Z). The base becomes ATSB Phase 2 + Bluefin-21 + OI 2018 + OI 2025–26 at inferred geometry with its own detection probability. Also wanted: the ρ sweep (0, 0.05, 0.25, 0.5) as columns, and the search likelihood applied to settled-wreckage positions. **Not done on run I**: the run I columns and composer pass 2b exclude Ocean Infinity; OI columns exist only for run D-he.
2. **Australian non-recovery from populated coasts only** (Pete, 15 Oct 07:30). Not in any product (G26). The 160 E re-plan is posted (13 Oct 02:05); not run.
3. **D0′: transmission imposed** (15 Oct). Done by end of flight in its own tables. The composer products still use the raw "held out" weights.
4. **Request 9 (unbiased child weights)**: approved and already in the run I sweep.
5. **Item 4, uniform onset for B: ruling needed from Pete** (end of flight, 20:10Z). The exact version (U1, core posterior held fixed) gives D0 B share 0.108 → 0.098, not 0.225. My binned figure re-weighted the parents' fuel state (82% of the 22:41 deliberate weight has its own predicted exhaustion before 00:11). Options: (i) U1 as the declared sensitivity, which is the module's recommendation; (ii) the binned version as a separate hypothesis about fuel state; (iii) both.

## 3. Corrections to my own figures (from end of flight, full sample)
- **On the sea before 00:19:37: 13.0% of the raw D0 weight, not 32.8%.** The 32.8% counted NaN last-burst rows, which include 21% still in cruise at the burst.
- **Loudest decile on the feasible set, all strata:** D0′ 0.100, D1 0.119, D2 0.154, D3 0.196, D4 0.193, D5 0.237. D4 is 1.93× D0′, not 3.2×, and D3 = D4 within noise. My 0.317 came from one seed of one stratum. The direction holds: every informative 00:19 treatment is louder than D0′.
- **Planned descent under a uniform onset: 0.108 → 0.098 (exact),** not 0.225. "00:11 selects cruise" stands with the core posterior held fixed.

## 4. Requirements to settle BEFORE run J starts

**Core side (they change the run itself):**
1. Northern sampling fix: core's islands check (9dbf93f, running), then the evidence-tilted filter if islands do not give ×4. The mode-allocation arm (`threads/work-orders/mode-allocation-test-2026-10-15.md`) can be added to the same job at no code cost. It tests the mode-probability noise directly, which is about 80% of the northern variance.
2. Core request 21 (fuel extrapolation factor κ_x): built and gated.
3. Output additions: path states at every BTO/BFO epoch on about 20k routes per seed; per-epoch residual and bias state. Code plus gates.
4. Audit F3 time step (running) and the BTO-only reproduction shoulder check.
5. Frozen tag, manifest and final-configuration smoke.

**Downstream side (they do not change run J, but must be ready so that run J's downstream pass is mechanical). Rehearse each on run I first:**
6. Searched areas: OI base columns plus the ρ sweep on `run-i-dive`, and the search applied to settled positions.
7. Drift: Australian populated-coast term (160 E domain), at least as a pre-registered sensitivity.
8. Hydro, Pléiades, settling and searched areas on `run-i-dive`, the current impact set.
9. Composer pass 3 on `run-i-dive`: D0′, OI base, Australian term; **regional ESS output** (sum and sum of squared weights per region, so that northern adequacy is reported routinely); seed-bootstrap intervals.
10. End of flight: the item 4 ruling, the bank-limit sweeps (running), and the both-burst descent-sampling work request (core 23:17Z).

## 5. Approximate downstream cost per impact set (from run I logs)
Drift export about 2 h (2 threads, outside the lock); hydro about 30 min; Pléiades about 6 min; searched areas and settling each about 1 h (from READY times); composer about 1–2 h. In total about one working day, mostly unattended and outside the heavy lock.
