# OCEAN_DRIFT inbox

The architecture session appends here. Read at the start of each working session.

## 2026-10-07 — architecture

1. **`crates/ocean` is not yours.** Part A of the old ISO brief is superseded — shared ocean
   transport has its own owner, and you are a consumer of an API you do not control.
2. **Deliverable order:** the plan, then your critical review of the prior work on this case, then
   the pilot — 99% impact coverage, 10 NM spacing, 10⁴ particles per cell. The pilot exists to
   measure three numbers (field-evaluation throughput, arrival probability per coast segment, and
   how fast relative likelihood changes with source separation) that then set the production
   spacing and particle count. Do not fix the production grid before those are measured.
3. **First pass releases at the impact point** and assumes the recovered objects originated there:
   no family-dependent release, no resurfacing. So you do not wait on settling.
4. **Acceptance is seed-to-seed and grid-refinement stability of the UPDATED IMPACT POSTERIOR**,
   not of the drift map. A frozen seed is reproducibility, not convergence.
5. **Queued, to be raised again once the first pass is stable:** the Western Australia non-recovery
   term, and the absence of buoyant cabin material.

## 2026-10-08 - architecture: the shared-ocean boundary, before you start

`crates/ocean` has a **third owner**. It is not owned by drift, not by settling and not by
Pleiades, because all three consume it and a crate owned by one consumer acquires that consumer's
assumptions. That owner does not exist yet and its brief is not written.

Until it does, three rules bind you.

1. **Do not implement advection, field interpolation, or reanalysis dataset access in your own
   module.** Not as a convenience, not temporarily. The moment two modules each have their own,
   the project has two ocean models and no way to tell which one a result came from.
2. **Do not choose a reanalysis product.** Product choice belongs to the shared owner. The
   measurement already in hand says this is the smaller axis anyway: changing the current product
   moved the drift mode 1.2 deg, while scaling the Stokes contribution by 0.5, 1 and 1.5 moved it
   to 11.9, 18.0 and 34.9 deg S. Object response dominates. Spend your effort there.
3. **If you need something from the ocean crate, raise it as an interface request in
   `coordination/OCEAN_TRANSPORT.md`** - what you need, in what frame, at what resolution, with
   what time coverage, and what you will do with it. Those requests are what the shared brief
   will be written from, so a precise one buys you the interface you want.

You may write a stub to keep working. It goes in **your own directory**, is named so that nobody
mistakes it for the real thing, and every number that passes through it is labelled provisional.
A stub must not become the interface by default: state in the request what the stub assumes, so
the shared owner can reject the assumption rather than inherit it.

## 2026-10-08 - architecture: rulings on your seven questions, and a prior-work correction

**A correction to what the project believed about Davey.** Chapter 11 of the book (printed pp.
101-109, running headers checked) **did** perform a drift update, in section 11.2: a per-particle
likelihood for the Reunion flaperon from Global Drifter Program trajectories, undrogued, 508 +/- 30
days, re-weighting the Inmarsat posterior (their eq. 11.4, p. 103). Their result, p. 109: the updated
distribution "is shifted very slightly to the North, but the effect is negligible". They also set out
a Poisson debris-field likelihood (eq. 11.5) and **declined to quantify the absence of other debris**
because its parameters "cannot be reliably determined" (p. 103). That is your direct predecessor and a
reproduction target: reproduce their negligible shift as a check, then say why this module's result
differs, if it does. PDF in the artifact store as `10.1007_978-981-10-0379-0_11.pdf`.

1. **Pilot extent:** size from `no-exhaustion-prior`, the core-only reference run that produced the
   -37.225 median, 50% [-37.85, -37.00], 90% [-38.35, -35.50]. Cite the run, and its datasheet at
   `results/no-exhaustion-prior-datasheet.md`. Use its 00:19:37 posterior, not 00:11, labelled
   provisional, with extent and spacing as config.
2. **Stub: in,** exactly as you scoped it - closed-form fields only, straight-line coast, no data
   access, no gridded interpolation, labelled provisional, deleted when the shared API lands.
3. **Evidence table:** byte-identical copy with sha256 and source path recorded. Confirmed.
4. **Find episodes:** agreed sequence - you draft, I rule.
5. **Island patch:** labelled sensitivity, not default. Confirmed.
6. **Drifter replay split:** confirmed. Drogued replay is the shared owner's test; undrogued and
   windage stay with you.
7. **The shared owner is my next brief after searched areas.** Three precise requests in an hour is the
   evidence I said I was waiting for, and you are right that it is now the critical path.

## 2026-10-08 - architecture: Davey ch. 11 alignment - read `results/davey-ch11-alignment.md`

Pete asked for this project's drift method to be checked against Davey's. The note does it point by
point. Four things now bind you:

1. **Reproduce Davey's single-flaperon update first, with their method** - GDP undrogued drifters,
   joined trajectories, the eq. 11.9 density ratio with a 1 deg kernel and eps = 1e-4 - on our
   reference posterior. Then carry it forward as a declared `ocean-model` alternative named
   `gdp-empirical`. Any result that differs from theirs must be traceable to the departures D1-D5, one
   at a time.
2. **The count of finds is handled by conditioning (D5).** Under a scale-invariant prior on the
   expected number of items, lambda drops out exactly and only the *relative* spatial variation of
   identification probability matters. Absence of finds elsewhere - Western Australia included - then
   enters through the denominator Q(x). Model identification probability by coast segment AND time:
   coastal search effort rose sharply after July 2015.
3. **Add the biofouling temperature constraint as a deferred observation channel (A2).** Davey flagged
   the 18 C barnacle threshold; the brief does not use it. Cite the biological literature for the
   threshold, not Davey.
4. **Do not claim Davey's negligible result was wrong.** Their 1 deg kernel is comparable to the width
   of the posterior it updated, which bounds how strongly it could reshape it. That is a statement
   about resolving power; write it as one.

## 2026-10-08 - architecture: overnight work plan

1. The critical review and the section 11 fixtures, as planned.
2. The analytic stub, the source-grid layer and the interpolation-of-relative-likelihood layer, so the
   pilot becomes a field swap.
3. **The conditional recovery likelihood of D5** in `results/davey-ch11-alignment.md`, on the stub -
   lambda cancelled, relative identification probability by coast segment and time, the denominator
   Q(x) explicit.
4. **Plan the Davey reproduction (A1).** You may download the **GDP 6-hourly drifter data, up to 1 GiB**,
   to `/Users/pete/Downloads/mh370-ocean-data/gdp/`, record it in `results/ocean-data-manifest.md`, and
   start the joined-trajectory reproduction. GDP is validation data and yours under the replay split.
5. The find-episode grouping draft for the stringent nine, for my ruling.
6. **Nothing else downloaded.** Reanalysis products belong to the shared owner.

### Overnight rules for every module, 8-9 October (binding until Pete is back, ~08:30 MT)

- **CPU:** core's 16-hour run is live until about 08:30 MT. Build with `cargo ... -j 4` and run nothing
  heavier than 4 threads. If the core run is slowed, everything downstream waits on it.
- **Disk:** 38 GiB free and falling while core writes. **Download nothing** unless your entry below
  says you may, and then only within the stated cap. Never save a multi-GB file as an artifact. Never
  let free space fall below 25 GiB - check `df` before each file.
- **Nobody can answer you tonight.** If you hit a question only Pete or the architect can answer,
  write it in `coordination/architecture.md`, choose the more reversible option, label the work
  provisional, and keep going. Do not stop and wait.
- **Concurrent appends:** if a push conflicts on a coordination file, keep BOTH entries in
  chronological order. Never resolve by taking one side.
- **Finish the night with a dated entry in `coordination/architecture.md`**: what landed, with commit
  hashes; what is provisional and why; what you need in the morning.

## 2026-10-08 - architecture: the shared ocean is being built tonight

A sub-agent run by the architecture session is building `crates/ocean` on `core/ocean-transport`,
starting with the API and the analytic fields you are stubbing. Keep your stub's call shape matched to
what you filed in `OCEAN_TRANSPORT.md`, so the swap is a field change, not a rewrite. Watch that file
for its entries.

## 2026-10-09 01:58 UTC - architecture: URGENT - CPU, read before your next run or build

**Machine load is 112 / 142 / 154 on 18 cores** (1/5/15-minute averages). Core's 16-hour run is on
seed 2 of 8 and every minute of oversubscription moves its 08:30 MT finish later.

**My overnight rule was incomplete.** `cargo -j 4` limits compilation only. Engine binaries and test
suites use every core through Rayon regardless. From now until core posts DELIVERED:

1. **Every engine run and test: `RAYON_NUM_THREADS=2`**, and `cargo test ... -- --test-threads=2`.
2. **No full-scale or pilot runs.** Smoke-scale only. End of flight: the children-per-parent pilot waits
   for the morning. Settling: first-pass runs at smoke scale only.
3. **No more than one heavy process per module at a time**, sub-agents included. If you have spawned a
   sub-agent that runs code, tell it the same.
4. **Disk:** free space fell to about 1.2 GiB around 01:45 UTC and has recovered to 41 GiB; the writer
   is not identified. If your session wrote and deleted large files in that window, say so here. The
   25 GiB floor stands.

Code-reading, writing, review, literature work and small tests are unaffected. Keep going on those.

## 2026-10-09 - architecture: morning rulings

**Your reproduction corrected me, and the correction is now in the note.** D3 in
`results/davey-ch11-alignment.md` is rewritten: Davey's negligible shift comes from how little the
drifter record says about one find, not from kernel width. D5 now says only a global constant in P_I
cancels; block levels are latent and marginalised. Thank you - that is exactly what a reproduction is for.

Rulings:
1. **Find episodes: G1** (nine object factors with shared detection blocks) is the working default. I
   have not yet read the draft in full; I will, and will say if anything in it changes this.
2. **`gdp-empirical`:** the join rule (150 km, +/-30 days, <=135 days per segment, 4 segments) and
   R = 200 km are **declared reproduction settings**, because Davey never printed theirs. Report R over
   100-400 km as a sensitivity; do not marginalise over a parameter whose only purpose is to match
   an unprinted choice.
3. **`object-response` is module-local** to drift. Pléiades declares its own.
4. **Diffusivity K is an η component owned by the shared ocean**, marginalised jointly. Your
   correction that 5 NM/day is 248 m2/s, not 100, goes to ocean transport.
5. Flaperon response provenance: write it up as review item 17 and I will rule on it.
6-8. **Brief corrections accepted**: section 5 seed-TV attribution, section 9 claim 5, and D3. Recorded
   as amendments at the end of `ocean-drift.md`.
9-11. O1/O2 and DRIFT-1..3 are filed with core; chainage on `Beached` goes to ocean transport.

**The pilot itself waits for O1/O2 and one real product.** Both are in hand today if core lands O1/O2
and Pete approves the Copernicus download.

### Machine rules from 9 October, now core's run has finished (supersede the 01:58 UTC entry)

- **One heavy job on the machine at a time**, taken under the machine-wide lock that end of flight
  introduced: `lockf -k /tmp/.mh370-heavy.lock <command>`. Inside the lock, up to
  `RAYON_NUM_THREADS=12`. Outside it - builds, tests, analysis - `RAYON_NUM_THREADS=2`, `-j 4`.
  "Heavy" means any engine run above smoke scale, any pilot, any sweep.
- **Disk floor 25 GiB**, checked before every large file. 33 GiB is free this morning.

## 2026-10-09 - architecture: the flaperon response has one owner - you

Pléiades will test whether CSIRO's measured flaperon-replica response matches any imaged object pair.
**Drift owns the provenance of that number**, since it is your review item 17 and your E1 finding.
Record it once - CSIRO Part II primary text, printed page, the reference system it is stated in, and
whether it is the at-sea replica measurement or a tuned assessment - in `results/`, and Pléiades will
take it from there. Item 17's circularity check comes first.

## 2026-10-09 ~00:30 UTC - architecture: rulings and your sequence (initiative rule: see architecture.md, same date)

Rulings D-a to D-e are in `architecture.md` under this date. `leeway_speed_mps` is approved and is
ocean transport's first item; use your stub for it until it lands. O1/O2 have landed, so you can
depend on `mh370-ocean` now.

**Sequence:**
1. **Implement G1 and the identification-level marginalisation** (by coast and time).
2. **Swap the stub for `mh370-ocean`,** including the flaperon response as ruled.
3. **The pilot.** It starts from fixed arc nodes, so it does not depend on the prior.
   - Write your prediction (brief §5) before running.
   - Run under the lock when the lock is free (about 0.8 h with waves and wind), or at 2 threads
     beside core if core holds it (about 5 h).
   - Use the GLORYS12 slice that already exists, and WAVERYS and ERA5 as ocean transport delivers them.
   - Do not wait for a perfect product.
4. **Fix the sizing from the pilot,** then build the transport and recovery-observation layers.
5. **The sample-scoring interface:** a smoke test on current hand-off impacts, labelled
   "295.66° prior".
6. **The production run and the 5 NM refinement.** These wait for the final impact samples.

**Data:** ocean transport owns the products and the downloads. The project budget is 300 GB, so ask
for what you need.

- Modular Architecture


## 2026-10-09 ~04:15 UTC - architecture: rulings for ocean drift (D-a amended, D-f)

Your rulings are in `architecture.md` under this timestamp. Carry on with your sequence.

- Modular Architecture

## 2026-10-09 ~06:00 UTC - architecture: overnight rule, agreed by Pete

Read the ~06:00 UTC entry in `architecture.md`. Overnight, a question for Pete is recorded with its
options, and your recommended option is taken PROVISIONALLY and reversibly; then carry on. It does not
cover irreversible, licence, outreach, third-party or long-run decisions. Do not take the heavy lock
(core's run).

- Modular Architecture

## 2026-10-09 ~07:00 UTC - architecture: measured ocean error is far above K = 248; GlobCurrent is the second ocean model

See `architecture.md`, same timestamp. Adopt a measured `OceanErrorModel` before production. The pilot
stands as a sizing run.

- Modular Architecture
