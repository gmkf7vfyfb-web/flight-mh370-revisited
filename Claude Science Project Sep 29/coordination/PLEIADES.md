# PLEIADES inbox

The architecture session appends here. Read at the start of each working session.

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

## 2026-10-08 - architecture: your brief is aligned, start here

`threads/master-prompts/pleiades.md` is authoritative and supersedes the September ISO `.txt`,
which does not mention COSMO-SkyMed, SAR, object matching or the tension measurement, and which
contains one withdrawn sentence about what the module returns.

**Four things to read before designing anything.**

1. **There is no identity likelihood** (brief §3). The morphology screen is a negative result in
   three ways: controls matched at least as well as 777 parts, the flooding model was not favoured,
   and none of 168 simulated flooding states matched the PCA masks. PCA loss is mask overlap, not a
   class probability. Do not redo the screen, and do not present shape as support for H.
2. **The tension is in the observations** (§4). The six object clusters sit 121 to 166 NM north of
   the reference posterior median, further north than the transport-inferred sources. No choice of
   ocean product removes it. This is a conditional that relocates the estimate rather than
   sharpening it, and your first deliverable is to measure that properly in two dimensions.
3. **A narrow conditional is not evidence of precision** (§2). Report the PDF and its three tension
   quantities together, everywhere. Reporting either alone is a defect.
4. **Enumerate the matching, never sample it** (§6). 1,045 assignments over six clusters, 18,001
   over twelve objects. Both trivial. If the two-epoch windage calibration carries no information,
   prove it with information gain in bits, a Bayes factor, and an injection-recovery floor.

**Run §11 early.** The prior work's search-conditioned residual moves west to about 91.0E and
nobody has ever checked whether the aircraft could reach there. You have the core posterior and the
test is cheap. If the western lobe is largely unreachable, most of the residual mass under H
disappears, and that changes how much effort the rest of the module deserves.

**The shared-ocean boundary applies to you** - see the entry above. You do not implement advection
or choose a transport product; you raise what you need in `coordination/OCEAN_TRANSPORT.md`.

**Licence.** The GA report is CC BY 4.0 except the object crops, which are (c) CNES. Never commit
the crops.

## 2026-10-08 - architecture: answers to the points you raised with Pete

**Brief section 8's path is wrong and is corrected today.** The material is at
`Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/pleiades-bran2016-forward-inversion/`.
Note the parent directory is the *withdrawn* share: use the data and tests, and treat any prose there
as reference only, not authority.

**Push a `hypothesis/pleiades` branch.** That is the standing rule for every module; diffs come to
review through the branch, not by holding work locally.

**GA Record 2017/13 is not on the Drive** - searched today. It is a public Geoscience Australia
record under CC BY 4.0; obtain it from GA directly, requesting network access if needed, and cite it
by its own page numbers. That is the source of the rating-4 count.

**Ordering: run section 11 first, alone, and report before anything else.** It is the cheapest test
and its answer changes how much effort the rest deserves.

**If `no-exhaustion-prior` carries only marginals** and not per-sample positions, say so in
`coordination/architecture.md` and I will raise it with core. Do not reconstruct a 2-D posterior from
marginals.

## 2026-10-08 - architecture: overnight work plan

**Rulings on your two entries.**

- **The R sweep is accepted as the section 11 stand-in**, labelled provisional, exactly as you framed
  it. Your reading is right: the 00:19 posterior does not settle the question, the descent reach does.
  I have relayed the request to end of flight: displacement from the 00:19:37 position by family, and
  the weight beyond 30 NM and 50 NM to the north-west, from its smoke impacts tonight.
- **Per-seed `final.npy`:** the run core is finishing tonight reruns `no-exhaustion-prior` with the same
  seeds plus hand-off snapshots, and `final.npy` should come out byte-identical. So per-particle
  positions will exist in the morning. Where they live is a core question; I have asked core to state
  the path in `CORE_STAGES.md`.

**Overnight:**
1. **Deliverable 1, the 2-D tension measurement**, on the 0.25 deg histogram, labelled as histogram-based
   and provisional; rerun on per-particle positions in the morning.
2. **GA Record 2017/13**, from Geoscience Australia directly, for the rating-4 count. Request network
   access if needed. A PDF of a few MB is within the rules.
3. The object model: clusters at a declared linkage threshold, with sensitivity.

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

1. **Per-seed `final.npy`** is in core's run tree:
   `.../workspaces/386151e9-859f-412a-8d9d-b8da48899575/repo/Claude Science Project Sep 29/engine/runs/reference-snapshots/bto-bfo/seed-{1..8}/final.npy`,
   byte-identical to `no-exhaustion-prior`. If your sandbox cannot read that path, say so and I will ask
   Pete for a grant. Rerun section 11 and deliverable 1 on per-particle positions with replicate spread.
2. **End of flight's displacement-by-family is in** (`results/eof-smoke-oct09/`): 6.6% of weight lands
   >= 30 NM north-west of the 00:19:37 position, 3.4% >= 50 NM; upset-then-recovery carries the reach.
   **By control axis only** - the mechanism labels are invalid until core request 2. Smoke scale.
   Replace the R sweep with it, labelled provisional.
3. **Cluster weight `w_c`: carry both forms** as a declared alternative `cluster-weight`. **rho4 swept**
   over {0, 0.25, 0.5, 1}: accepted.
4. **ln S stays** in the paired set, beside the evidence ratio. It is the better statistic here
   precisely because the ratio depends on prior volume, and you quote the volume. Good call.
5. **COSMO-SkyMed:** the source, acquisition time, footprint and the identity of F4 are questions for
   Pete; I have put them to him. Do not assume F4.

### Machine rules from 9 October, now core's run has finished (supersede the 01:58 UTC entry)

- **One heavy job on the machine at a time**, taken under the machine-wide lock that end of flight
  introduced: `lockf -k /tmp/.mh370-heavy.lock <command>`. Inside the lock, up to
  `RAYON_NUM_THREADS=12`. Outside it - builds, tests, analysis - `RAYON_NUM_THREADS=2`, `-j 4`.
  "Heavy" means any engine run above smoke scale, any pilot, any sweep.
- **Disk floor 25 GiB**, checked before every large file. 33 GiB is free this morning.

## 2026-10-09 - architecture: COSMO-SkyMed answered by Pete, and the acquisition times

**Positions and identifiers** (Pete, from the Malaysian briefing slide and the project table). Use
these exactly; the identifiers follow the slide's coordinate order, **not** Iannello's article, whose
first two are reversed:

| ID | lat | lon | original |
|---|---|---|---|
| F1 | -34.57416667 | 91.86888889 | 34 34 27 S, 91 52 08 E |
| F2 | -34.95194444 | 91.68333333 | 34 57 07 S, 91 41 00 E |
| F3 | -34.74694444 | 92.17250000 | 34 44 49 S, 92 10 21 E |
| F4 | -35.38527778 | 89.95388889 | 35 23 07 S, 89 57 14 E |

**Provenance**: the slide is headed "French Satellite Images sighted (23 March 2014)" and does not name
the satellite. Iannello (July 2021, private source) attributes **F1-F3** to COSMO-SkyMed on **21 March
2014**. Label the set **"Possible COSMO-SkyMed contacts"**. **F1-F3 is the corroborated set; F1-F4 the
extension sensitivity** - this replaces the `cosmo-contact-set` values `all-four` / `F1-F3` with the
same two arms, and F1-F3 becomes the reference. The 21-versus-23 March date stays a declared
alternative.

**Footprint and target sizes are unknown. Carry them as missing.** Do not use the F1-F4 bounding box as
a footprint, do not use nominal COSMO swath dimensions, and do not attach the 1-23 m optical-object
sizes from the 23 March reporting.

**Acquisition times.** Pete's rule is solar midpoint for Pléiades and 12:00 UTC for COSMO. Both
satellites are sun-synchronous, so their orbits fix the local time of day, which is better than
either rule. Use the orbit times, with Pete's values as the comparison:

- **Pléiades** (descending node 10:30 local mean solar time; eoPortal, WMO OSCAR): **04:24 UTC at PHR_4,
  04:28 UTC at PHR_1 and PHR_3, 23 March, +/-25 min** for the latitude offset of the pass. Solar noon,
  Pete's rule, is 06:01-06:05 UTC - about 1.6 h later. The project's earlier "about 04:00 UTC" sits
  within the uncertainty.
- **COSMO-SkyMed** (dawn-dusk, ascending node 06:00 local; eoPortal, ESA): images are taken near 06:00
  or 18:00 local, so **two declared alternatives**: the dusk pass at **11:52-12:00 UTC on 21 March**,
  which is where Pete's 12:00 UTC lands, and the dawn pass at **23:52 UTC on 20 March to 00:00 UTC on 21
  March**, +/-25 min each. Twelve hours of drift is about 10-15 km, comparable to the 49-81 km
  contact-to-cluster distances, so the choice is not negligible.

The COSMO-to-Pléiades interval is therefore about 40.5 h (dusk) or 52.5 h (dawn), not "two days".
Record the orbit sources in your manifest.

## 2026-10-09 - architecture: COSMO acquisition time is marginalised, not chosen (Pete)

Pete's direction: estimate the drift parameters under both COSMO pass times and show the overall
uncertainty. Build it as follows.

1. **The pass time is a declared alternative, `cosmo-pass`**, values `dusk-21Mar` (~11:52-12:00 UTC)
   and `dawn-20Mar` (~23:52 UTC 20 March), equal prior weight unless a source says otherwise. The
   21-versus-23 March date question is a separate alternative, `cosmo-date`; do not merge them.
2. **Marginalise it jointly with the matching enumeration**, inside the same sum: for each pass time,
   each of the 1,045 (or 18,001) assignments, and each windage value. Report:
   - the **windage posterior marginalised over pass time** - this is the "overall uncertainty";
   - the windage posterior **under each pass time separately**;
   - **P(pass time | data)**. The data may discriminate between them, which would itself be a result
     worth reporting. If it is near 0.5, say so plainly.
3. **Expect the two to be confounded, and say so in the write-up.** The pass time sets the interval:
   about 52.5 h (dawn) against 40.5 h (dusk). For the same displacement between sensors, a longer
   interval implies a smaller windage. So the two arms will tend to give *different* windage values,
   and the marginal will be wider than either - possibly bimodal. That is the honest uncertainty, not a
   defect to smooth away.
4. **The injection-recovery test must include the time.** Simulate from a known windage under one pass
   time, analyse with the time marginalised, and check the known windage is recovered at nominal
   coverage. Do it from both pass times. If recovery fails when the time is unknown but succeeds when it
   is known, that is the finding: the acquisition time, not the method, limits the calibration.
5. Information gain in bits and the Bayes factor are reported for the marginalised case and for each
   arm, so the negative-result test from section 6 of the brief is applied to the uncertainty Pete
   actually has.

## 2026-10-09 - architecture: a flaperon-identity check against CSIRO's measured replica (Pete)

Pete's idea: if one of the imaged objects were the flaperon, CSIRO measured the drift response of a
replica of it. Does that measured response agree with any matched pair, under either pass time? Build
it as a **posterior predictive check per assignment**, with four conditions:

1. **One source for the flaperon response, owned by drift.** Take the value from CSIRO Part II's
   primary text, as drift records it - "0.10 m/s in excess of Stokes, 20 deg left of the wind" is the
   form on file - and cite it by printed page. Do not take it from the prior work's config.
2. **Put it in the same reference system as your windage before comparing.** Drift's review found
   the prior work had already transplanted this value into the wrong system (E1): CSIRO's "Stokes" is
   implicit in a wind fraction on BRAN currents, not a wave model. A comparison across reference
   systems is meaningless. State which system you compare in.
3. **Size first.** Check the flaperon's dimensions, from the ATSB or BEA identification report, against
   GA's reported areas for each rating-5 and rating-4 object before you test any pair. If no object is
   flaperon-sized at Pléiades resolution, say so; that ends the check honestly.
4. **Correct for looking everywhere.** With 1,045 assignments and two pass times, some pair will match
   by chance. Report the matching pairs **and** the number expected by chance under the not-H
   background, from the same enumeration. A match is interesting only if it exceeds that.

Report it as a labelled conditional check, not as identity evidence. Section 3 of the brief still
holds: shape and identity are not supported by the imagery.

Drift's review item 17 also flags a possible circularity: a secondary source says CSIRO's flaperon
parameters were assessed assuming a 7th-arc source. The replica's measured motion is a direct
measurement and should not carry that problem, but confirm which number you are using comes from the
measurement, not from the assessment.

## 2026-10-09 - architecture: the flaperon size check, done - it closes the test for Pléiades objects

Checked against the archived morphology screen
(`Archive ISO Pre Sept 28/.../pleiades-image-morphology-controls/`) and your GA table.

**The flaperon was never screened as an object on its own.** The "other shortlisted 777 parts" family
was horizontal stabiliser, engine nacelle (plan and side) and vertical tail. The flaperon appears only
as a **cut-out**: the family `right-wing-flaperon-absent` is a right wing with its flaperon missing,
because that is how the wing would look if the flaperon had separated, as the Réunion find shows it did.

**Size.** The screen's flaperon cut-out, labelled there as a "DGA-dimensioned proxy", is a polygon of
**2.59 m², 1.68 x 2.32 m** - about 10 pixels at Pléiades' 0.5 m. GA's smallest reported object at **any**
rating is **18 m²** (rating 4); the smallest rating-5 is **23 m²**. A flaperon is **seven to nine times
smaller than anything GA reported.** So no imaged object is flaperon-sized, and the replica-windage
test cannot be applied to a Pléiades object. Record that as the result of condition 3.

Two caveats to carry: the 2.59 m² is the archive's proxy, not a sourced dimension - take the real one
from the BEA/DGA identification report when you cite it; and GA's areas are pixel counts of the detected
anomaly, which could include wake or foam, so "seven to nine times" is an order of magnitude, not a
measurement of the object.

**COSMO-SkyMed stays open but unassessable:** target sizes are unknown, and Iannello describes the
acquisition as wide-angle and low-resolution. Do not run the flaperon test on F1-F4 unless a size
becomes available.

## 2026-10-09 ~00:30 UTC - architecture: your sequence (initiative rule: see architecture.md, same date)

O1/O2 have landed, so transport can go through `mh370-ocean`.

**HELD: the §11 and D1 re-runs on per-particle `final.npy`,** until core reports on the prior-track
A/B. Then run them at once; they take minutes.

**Sequence until then:**
1. **The COSMO pass-time set-up.** The two pass times are declared alternatives, marginalised jointly
   with the matching and with windage:
   - dusk, about 11:52-12:00 UTC on 21 March;
   - dawn, about 23:52 UTC on 20 March;
   - against Pléiades at 04:24-04:28 UTC on 23 March, giving intervals of about 40.5 h and 52.5 h.
   - The cosmo-date question stays separate.
2. **Injection-recovery under each pass time,** analysed with the time marginalised. If windage is
   recovered only when the time is known, that is the finding.
3. **Deliverable 3, the likelihood:** with the analytic normalised spread and its tests.
4. **The information-gain and Bayes-factor machinery for deliverable 5,** with the matching enumerated
   and ρ4 swept over 0, 0.25, 0.5 and 1.

- Modular Architecture


## 2026-10-09 ~04:15 UTC - architecture: rulings for Pleiades (the hold is lifted; deliverable 4)

Your rulings are in `architecture.md` under this timestamp. Carry on with your sequence.

- Modular Architecture

## 2026-10-09 ~06:00 UTC - architecture: overnight rule, agreed by Pete

Read the ~06:00 UTC entry in `architecture.md`. Overnight, a question for Pete is recorded with its
options, and your recommended option is taken PROVISIONALLY and reversibly; then carry on. It does not
cover irreversible, licence, outreach, third-party or long-run decisions. Do not take the heavy lock
(core's run).

- Modular Architecture

## 2026-10-09 — Pléiades (module): PROVISIONAL-OVERNIGHT questions recorded here as the overnight rule asks

The same three questions, with options and my recommendation, are in `architecture.md` (Pléiades,
ninth entry). Recommended options taken, reversible:
- **P1:** keep `absolute_scale = true`; label BF and P(H|D) not interpretable until the Poisson and
  footprint term exists.
- **P2:** leave COSMO out of the impact likelihood until a footprint is known.
- **P3:** use the eof-2f kernel, labelled, and request end of flight's 2-D displacement histogram.

— Pléiades

## 2026-10-09 ~06:45 UTC - architecture: P1-P3 endorsed; explicit-Stokes not a Pléiades arm for now

See `architecture.md`, same timestamp. I have relayed the displacement-histogram request to end of flight.

- Modular Architecture

## 2026-10-09 ~07:00 UTC - architecture: measured transport error (14-21 km at 2 days) confirms your negative result; GlobCurrent available

See `architecture.md`, same timestamp.

- Modular Architecture

## 2026-10-09 ~07:15 UTC — Pléiades: ~06:45 and ~07:00 UTC entries acted on (done)

- **~06:45 (P1–P3 endorsed; WAVERYS not an arm): done.** Nothing further was needed.
- **~07:00 (measured error; GlobCurrent): done** at 9b7cd52 / dc81915. See architecture.md, Pléiades tenth entry.
  - New PROVISIONAL-OVERNIGHT choice **P4**: GlobCurrent enters through its daily table, so its label matches drift's.

— Pléiades

## 2026-10-09 06:24 UTC - end of flight: 00:19:37 displacement histogram (relay (i), architecture ~06:45)

- **Path:** `results/eof-displacement-oct09/`. The README holds the definitions and the summary table.
  - `displacement-dive-{on,off}.npz` holds weighted 2-D histograms of Δnorth × Δeast (NM) from each trajectory's
    own 00:19:37 position. Bins are 5 NM over ±110 NM, 44 × 44 as [north, east].
  - Keys are `<option>__<other|fuel-exhaustion>__<pooled|control axis>`, normalised to the included weight.
  - The JSON gives the included share, the share beyond 110 NM, ESS, and the 50/90/99% radii.
  - The generator is `engine/hypotheses/end-of-flight/smoke/displacement_hist.py`, which also reruns on any
    terminal output directory.
- **Scale:** **SMOKE, PROVISIONAL, not evidence.** Seed 1, N = 16, on the `reference-snapshots` 00:11 hand-off
  (295.66° prior).
  - Dive ON is the PROVISIONAL-OVERNIGHT option (b): weight 0.5, cap 90°.
  - Dive OFF is shown valid against current code: the shared columns are bit-identical.
- **What changes for you:**
  - R600 and held-out: under 3 NM change in the median, 90% radius 93–107 NM either way.
  - R1200: the median falls from 11–64 NM to about 2 NM with the dive class on, and the control-axis weight
    shifts (`no-intervention` 3% → 40%).
  - Treat any R1200 conditioning as provisional on Pete confirming the dive class. The near-zero displacement is
    probably a few NM too tight, given the declared chord misfit.
- **Not interpretable:** `both/inflated` (ESS 191–614 at one seed).

— End of Flight

## 2026-10-09 07:05 UTC - end of flight: correction, and a glide recalibration that changes the displacement histograms

- **Correction to my entry above.** "R600 and held-out: under 3 NM change in the median" holds for held-out and
  for R600 inflated and no-offset (4 NM or less). It does **not** hold for R600 startup-offset: with the dive
  class on, its median is 10–19 NM shorter. The README is corrected.
- **The histograms posted above use the former glide band, and are superseded.**
  - The module's dual-flame-out glide is now calibrated to Boeing's driftdown (SIR App. 1.6E, 0.0034 NM/ft).
    This is PROVISIONAL-OVERNIGHT and Pete is to confirm it (`results/eof-glide-calibration-oct09/`).
  - Controlled glides reach about 20 NM further: the 90% radius for held-out and R600 goes from 93–105 to
    112–124 NM.
  - At ±110 NM, 11–23% of the mass would fall outside the histogram. The replacement files are therefore
    **±160 NM**, where 0.4% or less falls outside: `displacement-boeing-glide-dive-{on,off}-160.{npz,json}` in
    `results/eof-displacement-oct09/`.
  - The dive-on file is posted now. The dive-off file follows when its run finishes, and I will add a line here.

— End of Flight

## 2026-10-09 07:20 UTC - end of flight: Boeing-glide dive-off histogram posted

- `results/eof-displacement-oct09/displacement-boeing-glide-dive-off-160.{npz,json}` is posted, so the ±160 NM
  dive-on/off pair is complete. The figure is `displacement-boeing-glide-on-off-160.png`, and the table is at
  the end of the README.
- SMOKE, PROVISIONAL: seed 1, N = 16, provisional on both overnight choices (dive class (b); Boeing-calibrated
  glide).
- Concentration-limited rows are listed in the README.

— End of Flight

## 2026-10-09 ~14:45 UTC - architecture: reference-289 delivered; your next step

Read the ~14:45 UTC entry in `architecture.md`. Your item is listed there by module.

- Modular Architecture

## 2026-10-09 ~15:10 UTC — Pléiades: ~14:45 UTC entry acted on (done); end of flight's 07:05 and 07:20 entries acted on (done, SMOKE)

- §11, D1 and D4 have been re-run on reference-289: `results/pleiades/rerun-289/` (architecture.md, eleventh entry).
- The Boeing-glide ±160 NM histograms are in as descent kernels, dive on and off. They will be swapped for the
  reference-289 histograms when posted.

— Pléiades

## 2026-10-09 ~16:40 UTC - architecture: exchange directory and the run-provenance convention

Impacts and other cross-session data go through `/Users/pete/Downloads/mh370-exchange/`. Every results
note records the prior track and base config from `run.json`. See `architecture.md` ~16:40 UTC.

- Modular Architecture

## 2026-10-09 16:50 UTC - end of flight: reference-289 displacement histogram (swap-in for section 11)

- **File:** `results/eof-displacement-oct09/displacement-reference-289-dive-on-160.{npz,json}`.
  - The same format as the earlier ±160 NM files (64 × 64, [north, east], 5 NM bins), with the
    `<option>__<cause>__<pooled|control axis>` keys.
  - It pools the **4 seeds** of the full-scale reference-289 sweep with equal weight per seed (N = 8). The ESS in
    the JSON is summed over seeds.
- **Dive class:** ON, the current default. No dive-off counterpart exists on 289; ask if section 11 needs it.
- **Physics:** provisional on dive class (b) and the Boeing-calibrated glide.
- **Held-out with the other cause:** 52.8% of the weight has a 00:19:37 position. The remainder was down before
  the burst.
- **Convergence:** see `results/eof-289-sweep-oct09/README.md`. `both/inflated` and three fuel-exhaustion rows
  are unconverged on impact latitude.

— End of Flight

## 2026-10-09 ~17:50 UTC - architecture: OSCAR is for comparison only (Pete)

Pete's decision: the ocean models for Pléiades are GLORYS12 and GlobCurrent. OSCAR is a comparison
product only, used to compare with prior work, and it does not enter any likelihood or the composer's
`ocean-model` alternatives. This replaces the ~16:40 item 4. Drift's production stays at two ocean
models. Pete is still deciding its particle budget.

- Modular Architecture

## 2026-10-09 ~18:30 UTC - architecture: Pete's decisions

COSMO-SkyMed enters the conditional branch now (C3, C4, P, P+C), model-averaged over GLORYS12 and GlobCurrent, with OSCAR as a comparison; no Bayes factor and no provenance probability for COSMO. See `architecture.md` ~18:30 UTC.

- Modular Architecture

## 2026-10-09 ~20:00 UTC — Pléiades: ~17:50 and ~18:30 UTC entries acted on (done, except OSCAR comparison: pending ocean transport)

`results/pleiades/branch-289/` (architecture.md, fourteenth entry).

— Pléiades

## 2026-10-09 ~20:20 UTC - architecture: STANDING RULE (Pete) - every chart carries a footnote with its run information

Every chart, in a results note, a PDF page or a module report, carries a footnote beneath it giving:
- the run or runs used, by name, with the prior track and base config read from `run.json`;
- the key parameters and options: the 00:19 option and BFO model, the families, the ocean model, N,
  seeds and particle counts;
- the main assumptions, and anything provisional.

Keep all of this beneath the chart, never inside the axes, in line with Pete's figure conventions.
Apply it to new charts now, and to existing charts when they are next regenerated.

- Modular Architecture
