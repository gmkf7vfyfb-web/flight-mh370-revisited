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
