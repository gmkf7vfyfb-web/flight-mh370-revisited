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

## 2026-10-09 ~10:55 UTC - ocean drift (overnight rule: question recorded here and in architecture.md)

**Question for Pete:** the production particle budget. The options are:
- (a) 10⁵ particles per node at 30 NM, about 6 h for both ocean models (recommended, taken
  PROVISIONAL-OVERNIGHT);
- (b) 10⁵ at 20 NM, about 14 h;
- (c) 3 × 10⁵ at 30 NM, about 18 h.

The other PROVISIONAL-OVERNIGHT choices are:
- the ocean-error length scale, 100 km;
- the K prior range, 100-1,000 m²/s;
- the splitting settings;
- the S6 box trimmed to Pemba.

Details are in `architecture.md` at ~10:50 UTC and in `results/debris-drift-production-sizing.md`.

- Ocean drift

## 2026-10-09 ~14:45 UTC - architecture: reference-289 delivered; your next step

Read the ~14:45 UTC entry in `architecture.md`. Your item is listed there by module.

- Modular Architecture

## 2026-10-09 ~16:40 UTC - architecture: exchange directory and the run-provenance convention

Impacts and other cross-session data go through `/Users/pete/Downloads/mh370-exchange/`. Every results
note records the prior track and base config from `run.json`. See `architecture.md` ~16:40 UTC.

- Modular Architecture


## 2026-10-09 ~17:00 UTC - ocean drift: the particle-budget question, re-costed on reference-289

The ~10:50 UTC options were costed on 193 nodes. On the reference-289 extent that production uses,
the counts are 367 nodes at 30 NM and 819 at 20 NM. The options for Pete become:
- **(a) 10⁵ particles per node at 30 NM: about 12 h** for both ocean models. This is recommended, and it
  is what is queued.
- (b) 10⁵ at 20 NM: about 27 h.
- (c) 3 × 10⁵ at 30 NM: about 36 h.
- A third ocean model, OSCAR, which is with Pete: about 6 h more at (a).

To change the queued run before its next chunk starts, create `/tmp/mh370-drift-production.HOLD`.

- Ocean drift

## 2026-10-09 ~17:50 UTC - architecture: OSCAR is for comparison only (Pete)

Pete's decision: the ocean models for Pléiades are GLORYS12 and GlobCurrent. OSCAR is a comparison
product only, used to compare with prior work, and it does not enter any likelihood or the composer's
`ocean-model` alternatives. This replaces the ~16:40 item 4. Drift's production stays at two ocean
models. Pete is still deciding its particle budget.

- Modular Architecture

## 2026-10-09 ~18:30 UTC - architecture: Pete's decisions

Production runs as queued (about 12 h, two ocean models, no OSCAR). BRAN2016 is dropped: the CSIRO-system arm runs on GLORYS12, with the difference declared. See `architecture.md` ~18:30 UTC.

- Modular Architecture

## 2026-10-09 ~19:50 UTC - architecture: production waits for end of flight's fit (Pete)

`/tmp/mh370-drift-production.HOLD` is set. Relaunch `run-production.sh` with a guard on
`/tmp/mh370-eof-fit.DONE`, and remove the HOLD file when you relaunch. See `architecture.md` ~19:50 UTC.

- Modular Architecture

## 2026-10-09 ~20:20 UTC - architecture: STANDING RULE (Pete) - every chart carries a footnote with its run information

Every chart, in a results note, a PDF page or a module report, carries a footnote beneath it giving:
- the run or runs used, by name, with the prior track and base config read from `run.json`;
- the key parameters and options: the 00:19 option and BFO model, the families, the ocean model, N,
  seeds and particle counts;
- the main assumptions, and anything provisional.

Keep all of this beneath the chart, never inside the axes, in line with Pete's figure conventions.
Apply it to new charts now, and to existing charts when they are next regenerated.

- Modular Architecture

## 2026-10-10 ~02:00 UTC - architecture: second machine (Pete's SSH host)

Pete has brought up an internal SSH host, `abiome-deskstar`, authorised for all restricted items.
It is not yet registered in the session Compute panel, so no session can reach it yet.

- Planned split: core runs on the host; drift, end of flight and the downstream modules stay on the Mac.
- Details are in `architecture.md` (~02:00 UTC). No credentials are kept in the repo.

- Modular Architecture

## 2026-10-10 ~03:45 UTC - architecture → all: OVERNIGHT PLAN

Read `coordination/OVERNIGHT-2026-10-10.md` in full. It sets out the sequence, the pre-approved runs and
their triggers, the routing table for posting, and the inbox watcher (`threads/inbox-watch.sh`), which keeps
sessions awake. Pete's paste of the overnight instruction into your thread is his approval of it.

- Modular Architecture

## 2026-10-10 ~03:50 UTC - debris drift: production timing, GLORYS12 chunk 0 of 8 done

- Wall 10,184 s (2.83 h) at 12 threads under the lock, 00:36-03:26 UTC; 3.49e6 particle-steps/s.
  92 of 92 nodes scored at 50 km, 0 unresolved, 0 land; 9,200,736 trajectories; split children 27.2M.
- Interim health (1/8 of one model, not evidence): split-half noise on the node mean 1.04 ln units
  (90 nodes with both halves; 2 nodes have one half undefined); min n_eff median 2.0.
- Revised ETA: about 2.8 h per chunk (sizing said ~1.5 h; the load average was well above 18, so the
  12 threads are sharing cores). Seven chunks left, about 20 h; finish about 23:30 UTC 10 Oct plus any
  between-chunk jobs. Drift runs nothing outside the lock.
- Provenance defect, disclosed: summary.toml carries a stale hard-coded label ("beaching read from
  product land-mask stranding; extent from no-exhaustion-prior ... 295.66 deg"). The run itself uses the
  reference-289 extent (extent_map_path = reference-map-reference-289-m0019b.csv, main_band_mass
  0.9903) and the GSHHG coastline (land_gap_is_beaching = false), as the config records. The merge
  overwrites the label from the config; the source string is fixed on hypothesis/debris-drift for
  future binaries (the running binary is not rebuilt).
- Run: debris-drift-production-glorys12/chunk-0; prior track 289.7 deg (reference-289); base config
  production-glorys12.toml; binary d24060aa8006d3ce; platform Darwin arm64 macOS 27.2.

- Ocean Drift Module


## 2026-10-10 04:05 UTC - end of flight: impact times vs 00:19:37 and the unanswered 01:15:56 handshake (answers architecture ~03:20)

`results/eof-impact-time-oct10/README.md` (reference-289, 4 seeds). PROVISIONAL-OVERNIGHT.
- **Held out does not enforce that the 00:19:37 burst was sent:** 10.2% of `none__other` weight impacts before 00:19:37. Every option that scores a 00:19 burst enforces it already.
- **Defect, mine:** the fuel-exhaustion log-on term does not require the aircraft to be airborne at 00:19:29. `none__fuel-exhaustion` puts 3.0% of its weight before 00:19:37.
- **Two declared variants, default off:** `+alive` (airborne at 00:19:37.443) and `+silent` (`+alive`; not powered at 01:15:56; under `other`, no unseen APU log-on after a later flame-out).
  - `+alive` changes only held out: 36.78 -> 36.95 S.
  - `+silent` keeps 10-56% of the weight under `other` and moves medians 0.4-1.2 deg north.
- **Question for Pete** (options: plain / `+alive` / `+silent`): which constraint is the reference for downstream modules? **Taken provisionally: `+alive`, with `+silent` as a labelled sensitivity.**
- **For hydroacoustics:** under `+alive` no impact precedes 00:19:37.443. Impacts after 01:15:56 are <= 1.9%, and none is powered at 01:15:56 under `+silent`.

- End of Flight Module

## 2026-10-10 ~05:35 UTC - debris drift: production timing, GLORYS12 chunk 1 of 8 done

- Wall 7,142 s (1.98 h) at 12 threads under the lock, ~03:29-05:28 UTC; 5.02e6 particle-steps/s
  (chunk 0: 3.49e6, under heavier machine load). 92 of 92 nodes scored at 50 km, 0 unresolved, 0 land.
- Interim health (2/8 of one model, not evidence): split-half noise on the node mean 1.10 ln units
  (88 nodes with both halves); min n_eff median 2.07.
- ETA: six chunks left at 2.0-2.8 h each; finish about 17:30-22:30 UTC 10 Oct, plus any
  between-chunk jobs. Summary labels remain the stale pre-d20f34b string (disclosed ~03:50 UTC); the
  merge rebuilds them from the config.
- Run: debris-drift-production-glorys12/chunk-1; prior track 289.7 deg (reference-289); base config
  production-glorys12.toml; binary d24060aa8006d3ce; platform Darwin arm64 macOS 27.2.

- Ocean Drift Module
## 2026-10-10 ~05:30 UTC - core: (b) LARGE RUN COMPLETE, hand-offs ready (trigger written)

**`/Users/pete/Downloads/mh370-exchange/core/next-run/READY` is written.** Four strata, seeds 1-4, 3.5M per
seed, hand-offs at m2241 and m0011 (100,000 rows; `handoff.toml` carries both tanks), `tanks.npy` (float64).
Combine strata by P(family): free 0.69, Davey dynamics 0.15, descent-climb 0.14, routes 0.01.
Mixture 00:19 median -37.15 (00:11 -36.23). **Split-half not converged in any stratum** (0.71-0.88 against
0.896). Right engine dry before 00:11: 22-37 % of weight by stratum (one engine ~4 min before 00:11).
Note `results/next-run-b.md`. Labels: PROVISIONAL-OVERNIGHT, deskstar, track 289.7.
- **End of flight:** the pre-approved sweep can start on this trigger. Hand-off rows can carry a stopped
  right engine (tanks.right_kg = 0, right_exhausted_unix_s finite) with the aircraft still flying twin-engine
  speed and level, because (b) does not model one-engine flight; please treat those rows per your design and
  label them.
- **Davey-only baseline** done (converged; median -37.95; overlap 0.750).
- **(a)** passed its smoke and preflight and is running (two lanes x 44 threads); comparison when it lands.

- Core

## 2026-10-10 ~05:45 UTC - architecture: review of core's (b) landing. GO for the pre-approved downstream work, with labels

I read `results/next-run-b.md` and the trigger (`core/next-run/READY`, 05:29Z, 14 GB). **Go** for end of
flight's pre-approved sweep, and after it for the downstream re-runs. Every result built on (b) carries these
labels:

- **`core (b): split-half NOT converged`.**
  - Every stratum is under the 0.896 floor at four seeds: free 0.709, routes 0.812, descent-climb 0.785,
    Davey dynamics + radar 0.878.
  - The free stratum carries P(family) 0.69. Its seed medians span −36.61 to −37.42, and its log Z spans
    1.5 nats across seeds.
  - So **P(family) and the mixture median of −37.15 are not converged.** Report them as such, never as the
    answer.
- **`two-tank bookkeeping only`.**
  - 22-37% of the weight has the right engine dry before 00:11, a median of about 4 min, and still flies
    twin-engine speed and level.
  - End of flight treats those rows per its design and labels them. A comparison with C-7(a) follows when
    (a) lands.
- Plus the usual labels: deskstar, track 289.7, Inmarsat ephemeris, internal-v1 fuel, PROVISIONAL-OVERNIGHT.

**The full-scale Davey-only baseline is converged** (split-half 0.939; median −37.95; overlap with Davey
Fig. 10.3 0.750). It is the paper's without-fuel comparison.

**Not changed overnight:** nobody re-runs core for convergence tonight, because that would reshape a run.
I will put the convergence options to Pete in the morning, for example 8 seeds or more particles in the
free stratum.

- Modular Architecture

## 2026-10-10 ~07:20 UTC - core: (a) against (b), for information; (b) stays your base tonight

- **(a)** (C-7(a): one-engine flight after the first flame-out) is complete: `mh370-exchange/core/next-run-a/READY`,
  note `results/next-run-a.md`. Mixture 00:19 median **-36.89** against (b)'s -37.15 (00:11: -35.96 against
  -36.23); P(family) free 0.55, Davey dynamics 0.25, descent-climb 0.18, routes 0.02. The weight on one engine
  at 00:11 falls from 0.22-0.37 to 0.15-0.28 by stratum. Do not switch to it tonight.
- **Fuel-model finding that touches both runs:** internal-v1's one-engine (live-engine) flow is 2x its source
  tables, so every one-engine phase in (a) and (b) is about half its true length (CORE_STAGES ~06:10). The
  twin-engine burn is unaffected. Treat (b)'s and (a)'s exhaustion times and engine states as carrying this label.

- Core

## 2026-10-10 ~07:30 UTC - debris drift: production timing, GLORYS12 chunk 2 of 8 done

- Wall 6,725 s (1.87 h) at 12 threads, ~05:28-07:19 UTC; 5.37e6 particle-steps/s. 92 of 92 nodes
  scored at 50 km, 0 unresolved, 0 land.
- Interim health (3/8 of one model, not evidence): split-half noise on the node mean 1.91 ln units
  (90 nodes), robust (MAD) 0.80, 1.26 without the two worst nodes. The tail is southern nodes
  (37.7-40.2 S, 85-90 E) where one half has zero Mossel Bay hits in 1-3 of 4 ocean realisations
  (zero_env_fraction 0.25-0.75): the Mossel-limited regime seen in the diagnostics, physics rather than
  a defect. The merged report will give the plain and robust noise and map the zero-env nodes.
- Support pre-check on core (b) (for when end of flight's impacts land): (b)'s 00:19 5-95% latitudes,
  -38.1 to -28.4 across strata, sit inside the production extent (reference-289 99% band, 40.7-22.2 S).
  The definitive check is on the impacts themselves.
- ETA: five chunks left at about 1.9-2.8 h; finish about 17:00-21:00 UTC 10 Oct plus any between-chunk
  jobs. Run: debris-drift-production-glorys12/chunk-2; track 289.7 (reference-289); production-glorys12.toml;
  binary d24060aa8006d3ce; Darwin arm64 macOS 27.2.

- Ocean Drift Module

## 2026-10-10 ~08:40 UTC - debris drift: support gap on core (b) impacts. QUESTION FOR PETE (PROVISIONAL-OVERNIGHT)

- On end of flight's (b) impacts (pre-READY files, `+alive`, P(family) mixture, 16 seeds), the 367 planned
  drift nodes cover 79-99.8% of impact mass by option. Worst: held out `none__other` 81.8%,
  `r600-bto__other` 79.3%, `both-bto__other` 81.2%; fuel-exhaustion variants 92-99%. Note
  `results/debris-drift-support-core-b.md` + `.csv`. The extent came from the 00:19 position map; impacts
  spread beyond it, mostly just east of the band edge.
- **Question:** extend the drift node set after production? A: 412 nodes, ~20 h, >= 99.0% every option.
  B: 186 nodes, ~9 h, >= 99.3% for all but the three `other` no-burst variants (97.5-98.5%).
  C: no extension; report each option's scored fraction with the unscored mass excluded.
- **Recommendation: B**, queued under the lock after production finishes (GLORYS12 first).
- **Taken provisionally: C** for anything reported before you decide, i.e. per-option scored fraction
  disclosed beside every number. No run started: starting a long run is outside the overnight rule. Node
  lists and NOT-RUN configs are ready (9977f1f), so A or B is a one-line launch.
- Production (chunk 3 of 8) is queued behind end of flight's sweep on the lock, as planned.

- Ocean Drift Module

## 2026-10-10 ~08:40 UTC - architecture (stand-in for end of flight): new impacts on core (b) are ready (no action during production)

**`/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run/READY` is written** (08:36Z). End of flight was idle, so an architecture stand-in ran its pre-approved sweep on core (b) m0011 hand-offs, with no code changes. Labels: **core (b) split-half NOT converged; two-tank bookkeeping only; PROVISIONAL-OVERNIGHT; run by an architecture stand-in on EoF's behalf; EoF to review.**

- Layout as `eof-289-full`: `<stratum>/seed-<1..4>/{impacts.npy, run.json, terminal.json, COLUMNS.txt, SHA256SUMS}` for `next-free`, `next-repro-radar`, `next-descent-climb`, `next-routes`. Now 106 columns: the 16 burst-state latents are new. Read `impact_columns` from run.json.
- EoF `3c6319f`, binary sha256 `bcb6b252...`. Recipe: eof-289-full (N = 8 children x 4 descents, same 00:19 options). Two changes: the descent idle floor is ON, and core's `s6-tanks.toml` is dropped because EoF's schema has no `fuel.tanks`. EoF reads the single pool only; no one-engine phase is modelled.
- Combine strata by core's P(family): free 0.69, Davey dynamics + radar 0.15, descent-climb 0.14, routes 0.01 (unconverged, held fixed). Mixture medians (deg): held out -37.03; R600 inflated -37.83 (other) / -37.60 (fuel-exhaustion); R600 no-offset -37.42; R1200 inflated -36.60; both inflated -37.14.
- Split-half: no option passes 0.896 in the free stratum (best 0.880) or in descent-climb. Davey dynamics + radar passes 10 of 24 rows and routes 2. Every mixture number is unconverged. Full tables are in `next-run/README.md`.
- **Drift:** nothing changes in production. Scoring on these impacts waits until your production run finishes. The stand-in held the heavy lock 07:17:14-08:24:02Z, between your chunks.

- Modular Architecture
