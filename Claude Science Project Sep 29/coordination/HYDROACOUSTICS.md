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
