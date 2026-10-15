# Core work order, 15 October 2026 (b), for a FRESH core thread

Issued by coordination. Pete approved Decisions 1–4 on 15 Oct. Do not use the long core thread 386151e9 for any of this work: it did the handover only. Read `threads/work-orders/core-handover-2026-10-15.md` first.

Standing facts from the handover:
- The constant −96.66146918417472 is stale because of the 289.7° track change of 9 Oct.
- Gate B and gate C references are LOST.
- Core request 9 (d4e67b09, `[terminal] within_parent = "unnormalised"`) was never run.
- The request-18 look-ahead hand-off (`handoff-lookahead-d`) did not raise the effective parents.
- Never delete J7 7ba3b89b.

## Step 1 — Regenerate the gate B and gate C references (do first)
Rebuild both references from committed code and config on the current track. Record the SHA-256 checksums and the ln Z values in `results/gates-bc-2026-10-15.md`. All later steps compare against these, not against −96.661…

## Step 2 — Copy the deskstar scripts into the repository (Decision 2)
Copy `compact_c.py` (deskstar `J/53d0d251-e343-4b9a-8a2c-cafdfacce879/`) and `job-run-i-chain.sh` (deskstar `J/6a2ec01f-…/`) into `engine/scripts/`. Add a header line to each with the source path, the date and the SHA-256. No functional change.

## Step 3 — Fuel feasibility check (Decision 3)
Purpose: test the "one in eight feasible" reading against Davey Assumption 4.
Run: config `davey2016-inmarsat.toml` with fuel tracked but NOT constraining: no `require_power_until`, no hard reject. Smoke scale on deskstar under the heavy lock.
Report:
- the weighted share with FE before 00:10:59;
- the FE time quantiles (5/50/95%);
- the share with FE between arcs 6 and 7.
Compare with the reading 0.12 and with run I (FE median 00:19:12; 51.01% of all mass between arcs 6–7).
Prediction to record before the run: share dry before 00:11 is 0.10–0.20.

## Step 4 — Item 10 Phase 1: design the 00:19 two-burst hand-off proposal (Decision 1). Design only, no run.
What it tells us: whether the 00:19 arms (R1200 and both-BFO treatments) can be made estimable. Today the effective hand-off parents are 38.8 per seed (both raw) and 170 per seed (both with Holland transient bias added), so the D3/D4 results rest on very few parents.
Deliver:
- a design note with the proposal law and how its importance weight is corrected;
- why request 18 did not raise the effective parents;
- a predicted gain in effective parents;
- a smoke size.
Full specification: `threads/work-orders/item10-order-rev2-2026-10-15.md`.

## Step 5 — Run-J list
Add the run-J items 6–8 (see `results/run-j-change-list.md`) to the run-J proposal. **Run J needs Pete's explicit GO.**

Post each step's result to `coordination/CORE_STAGES.md`. No overnight runs on long threads.
