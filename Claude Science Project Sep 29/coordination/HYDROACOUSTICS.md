# HYDROACOUSTICS inbox

The architecture session appends here. Read at the start of each working session.

## 2026-10-07 — architecture

1. **Your brief is `threads/master-prompts/hydroacoustics.md`**, not the ISO `.txt`. Predictive-only
   is now a MODE, not the definition: you may return a log-likelihood, but only after
   injection-recovery gives P_D against received level. Until then you return zero.
2. **Blackman is already extracted machine-readable** in `Blackman_2004_extracted_data` — air1–air9
   shot lines, the 2003 A1–A11 events, source-class characteristics, and a conservative
   receiver-observations table with positive AND negative evidence. Use it as the engine validation,
   with the air8 non-detection at H01 as the negative control. One flagged row (JD144 10:54:57.77,
   labelled A3 with A4-like coordinates) needs checking against the page image before publication.
3. **Do the synthetic composer test second, before building detection methods.** How much would a
   detection at one, two or three sites with an O−C inside the uncertainty actually move the impact
   PDF? It needs no real data and it reorders everything after it.
4. **The correlation search must clear about 5.3σ per trial** at a ±1 h window and 30 Hz band for a
   1% global false alarm; two-station coincidence within ±30 s of the predicted lag brings that to
   about 4.4σ. Pre-register windows, bands, detector and threshold before looking, and take
   significance from time slides and burst-preserving surrogates.
5. **Never copy the Kadri bundle's markdown** — 23 files including a private funding note with staff
   email addresses.

## 2026-10-08 - architecture: the impact source interface is now in your brief

A new section at the end of `threads/master-prompts/hydroacoustics.md`, following Pete' consultant
note on the definition of tau. Four things bind you.

1. **Three durations, kept distinct.** Mechanical energy-transfer duration belongs to end of flight
   and arrives as `energy_transfer_tau90_s`. Acoustic source duration and received signal duration
   are yours, and neither equals the first. Propagation broadening is never read back as impact
   duration.
2. **One direction of inference is forbidden.** Never infer a duration from a received signal and
   return it to end of flight. That calibrates the impact model on the data you are scoring.
3. **Coupling efficiency is a declared alternative with a prior**, not a constant. It will dominate
   your predicted received level, and the injection-recovery study that gates whether this module
   may return a log-likelihood at all must span it - a recovery run at one assumed efficiency does
   not establish the gate.
4. **The AGW and SOFAR branches split on tau against the mode cutoff** `f_c = c/4H` - 0.094 Hz,
   10.7 s period, at 4,000 m. Below that period the impact is impulsive for the AGW band and the
   excitation depends on total impulse and displaced volume, not on tau. Compute `f_c` at the
   candidate depth, state the regime per sample, and do not carry a tau dependence into the AGW
   branch where none can exist.

Expect NaN in several of the incoming columns at first pass. A NaN propagates to "not assessed",
never to a default.

## 2026-10-08 - architecture: rulings on your five questions and four positions

**Q1. The Blackman shot lines and A1-A11 tables are not on the Drive.** Searched: only
`blackman_receiver_observations.csv` exists there. **Re-extract them** from `ucrl-tr-207323.txt`
against the PDF page images, under the conservative rule you stated (detection status never inferred
from silence), record the method, and commit the extracted tables with their provenance.

**Q2. Both, in sequence.** Start the synthetic test now on **(b), the parametric 7th-arc PDF**, because
it depends on nothing. The `runs/handoff-smoke` set you proposed for (a) is a 00:11 *hand-off*, not
impact samples - end of flight is producing the first real smoke impacts now. Switch to those for
geometry when published. Both are labelled provisional.

**Q3. Confirmed.** 0.0 means "module selected, no data used"; NaN means a sample the module could not
compute. Recorded as a composer requirement.

**Q4. Dedicated conda environment, accepted, and it is not a core request** - it touches nothing the
core owns. Name it `mh370-hydro`. KRAKEN and RAM are Fortran builds: once built, tar the result and
save it as an artifact so no later session recompiles.

**Q5. Branch `hypothesis/hydroacoustics` confirmed.**

**Position 14.1 confirmed:** likelihood evaluated per shared impact sample, always; a source-position
grid is admissible only as a cache of propagation quantities interpolated to each sample.

**Position 14.2 accepted:** bathymetry goes to the shared ocean-transport owner, with your along-path
requirement - GEBCO resolution along great-circle paths to H01, H08 and H11, AusSeabed near source -
stated in `OCEAN_TRANSPORT.md`.

**Schedule change accepted:** the synthetic composer test runs alongside Blackman, not after it.

## 2026-10-08 - architecture: overnight work plan

1. Cut `hypothesis/hydroacoustics` and scaffold in predictive mode, returning 0.0.
2. **The synthetic composer test** on the parametric 7th-arc PDF. It needs no propagation engine.
3. **Re-extract the Blackman shot lines and A1-A11 tables** from `ucrl-tr-207323.txt` against the page
   images, with the method recorded.
4. Create the `mh370-hydro` environment. You may download the Acoustics Toolbox source (a few tens of
   MB) and build KRAKEN; tar the build and save it as an artifact.
5. Literature review, Duncan figure 3 digitisation, the JD144 row check.
6. No data downloads beyond those.

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

## 2026-10-09 - architecture: a first answer to your synthetic composer test

The composer's own test 7 already runs the experiment you scheduled, in its simplest form: geometry
only, great-circle ranges at 1.48 km/s, approximate station positions, synthetic detections from a
known truth. The mean of the impact PDF moved by **+18.6 / -36.7 km (N/E) with one station,
+120.1 / -28.6 with two, +119.3 / -29.0 with three**, against a truth displacement of +120 / -30. ESS
52,786 / 8,480 / 4,310. Read it as: **one station constrains almost nothing in the along-arc direction;
two recover it; a third adds little in this geometry.** That is geometry-only and provisional. Your
version with a stated arrival-time uncertainty supersedes it; use this as a check that you reproduce
the same qualitative ordering. Code: `crates/compose/src/tests.rs` on `core/composer` at `5d2a206`.

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

**A strong night. The two-site result reframes the module and is now its headline**: a single site is
nearly worthless (0.08 bit at H01W, 0.01 at H08S); H01W + H08S carries 1.70 bit time-only and survives
600 s of impact-time uncertainty. The value of the module rests on whether a two-site H01 + H08
detection is physically possible from the core region. That question now leads.

1. **Blackman archive:** do not edit the `.b64` in place. That directory is an archived snapshot and the
   project does not edit snapshots. Record the one-character repair, the offset and the checksum match in
   your data manifest; the repaired zip stays an artifact. Your fresh extraction stands.
2. **Brief corrections 1-5 accepted** and recorded as amendments at the end of `hydroacoustics.md`.
   Correction 4 in particular: no number is cited that cannot be traced.
3. **The Drive `blackman_receiver_observations.csv`:** marked superseded in your manifest; I have asked
   Pete whether to remove it from the Drive.
4. **2001 H08S position:** the 2002 FDSN position, labelled provisional, is accepted.
5. **The WOA23 + GEBCO path stub is approved** - those two paths only, tens of MB, in your own
   directory, labelled provisional, sound speed via `gsw`, deleted when the shared API serves profiles
   and bathymetry. State its assumptions in `OCEAN_TRANSPORT.md` so the shared owner can reject them.
6. **Core requests:** latents by name and seafloor depth in `ImpactView` are filed with core, folded
   into request 4. Seafloor depth depends on the shared bathymetry, so it lands after that.
7. Rerun the single-site-with-bearing rows with the literature's mixture before "modest" is quotable.

### Machine rules from 9 October, now core's run has finished (supersede the 01:58 UTC entry)

- **One heavy job on the machine at a time**, taken under the machine-wide lock that end of flight
  introduced: `lockf -k /tmp/.mh370-heavy.lock <command>`. Inside the lock, up to
  `RAYON_NUM_THREADS=12`. Outside it - builds, tests, analysis - `RAYON_NUM_THREADS=2`, `-j 4`.
  "Heavy" means any engine run above smoke scale, any pilot, any sweep.
- **Disk floor 25 GiB**, checked before every large file. 33 GiB is free this morning.
