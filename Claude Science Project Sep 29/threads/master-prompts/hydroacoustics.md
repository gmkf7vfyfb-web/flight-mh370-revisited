# Hydroacoustics — mission and master prompt

Supersedes `ISO Sept 28 Status/threads/master-prompts/hydroacoustics.txt`, which remains correct on
the calibration status, the detection-control protocol, the data inventory and its measured
learnings, and is stale on three things: predictive-only is now a **mode** rather than the
definition of the module, the old thread identifiers and `/jackbox/home` paths are gone, and
`ImpactView` now carries the fields the coupling term needs.

Read `ISO Sept 28 Status/threads/master-prompts/common.txt` first for the four-stage architecture
and the eight composition rules, then `ARCHITECTURE.md` for the decisions already ruled. Both bind.

Split deliberately: **§2 is the contract and must not drift. §5 onward is the line of enquiry and
is expected to.**

**Coordination.** There is no live channel between sessions. Read `coordination/HYDROACOUSTICS.md`
at the start of each working session and after any long gap; write anything the architecture
session must act on to `coordination/architecture.md`.

---

## 1. Mission

Take the impact location **and the nature of the impact** — attitude, velocity, energy, dissipation
duration — and forward-propagate to **simulated arrival signals** at every relevant receiving
location: waveform, spectrum, direction and time of arrival, each with an explicit uncertainty
bound on arrival time and on energy. Propagate by both channels: the deep sound channel, and
acoustic-gravity waves.

Those simulated arrivals are then used three ways: to test against the data we actually hold, to
assess detectability honestly where no detection is claimed, and — once the module is calibrated —
to return a log-likelihood that modifies the impact posterior.

### The expertise this module is expected to bring

Act as an expert in hydroacoustics at the level of the current scientific state of the art, not at
the level of this repository's prior code. That includes: prior cases of aircraft and vessel losses
detected or searched for acoustically; hydroacoustic network calibration and propagation modelling;
the estimation and modelling of acoustic energy coupling from an impacting body into the water
column; and acoustic-gravity wave research, theory and practice.

**Familiarise yourself with the relevant literature well beyond what is in this repository and on
the project Drive** — including, but not limited to, Blackman and Kadri. Weight most heavily the
cases where a subsequent ground truth became available, because those are the only ones that
establish whether a method works. Review the prior work on this case critically and with an eye to
improving the rigour of the statistics, and know Bayesian methods thoroughly rather than applying
them by recipe.

---

## 2. The contract — stable; changes need architecture review

1. **Return a likelihood, never a posterior**, and declare whether it is on an absolute scale. Only
   absolute-scale likelihoods can be mixed across alternatives.
2. **The P_D gate.** You may return a log-likelihood **only once injection-recovery has given
   P_D as a function of received level.** Until then you return zero and contribute nothing to the
   posterior. The reason is Pete's rule — *an absence counts only where a signal should have been
   detectable* — which is unimplementable without P_D. The detection-control protocol of §6 is the
   path to a likelihood, not a gate in front of one. The eventual form is
   `(1 − P_D) + P_D × (match to detections ÷ background rate)`; that is an absolute-scale
   likelihood only if the background rate is a proper density, so say which it is.
3. **The deep sound channel and acoustic-gravity waves are separate branches** with separate
   uncertainty and separate declared alternatives. Never one blended prediction. They are different
   physics at different speeds; Kadri's claims rest on the AGW branch and Duncan's objection is
   about the acoustic path, and blending them would make that disagreement untestable.
4. **Pre-register every search before looking.** Windows per station, bands, the detector and its
   threshold, fixed and written down before the data are examined. Significance comes from time
   slides and burst-preserving surrogates, never from a panel's own percentile. See §5 for why this
   is arithmetic rather than etiquette.
5. **Each observation is used once per run**, with declared IDs.
6. **All impact-level modules score the same impact samples.** Never smooth privately over impact
   location.
7. **Smooth, with explicit model error. No floors.** NaN means "not computed", not "impossible".
   A non-detection where the model says nothing was detectable is *not* evidence against that
   location.
8. **Be accurate where the other evidence has mass** — the core estimate is a median of −37.225°
   with a 50% interval of [−37.85, −37.00] — not only near your own peak. Kadri's main candidate
   crosses the arc near 25.8°S, which is far outside that.
9. **Measure Monte Carlo adequacy and report unconverged as unconverged.**
10. **Provenance.** Digitised chart data is labelled as digitised, with its extraction method
    recorded, and is never cited as though it were the underlying measurement. The Kadri bundle
    contains 23 markdown files including a private funding note with staff email addresses:
    **never copy it, never quote it, never commit it.**
11. **One synthetic-recovery test plus hand-computed fixtures.**

### What you consume

`ImpactView`: position, **impact time** (the arrival window is a time window), total and vertical
kinetic energy, flight-path angle, and — added because this module needs them — **attitude at
impact and the dissipation duration τ**, which the coupling term η(γ, ż, attitude, breakup, τ)
cannot be evaluated without. Also **seafloor depth at the impact point**, which is a shared-layer
lookup from one bathymetry surface; settling needs the same quantity and it must not be computed
twice from two different grids. TEOS-10 sound-speed profiles come from the transport work rather
than being rebuilt here.

---

## 3. Calibration status — what can and cannot be pinned

**Propagation can be partly calibrated, and this is the module's foundation.** The 2001 airgun site
air9 (27°33.6′S 98°52.6′E, 19 October 2001, 02:10–02:46 UTC) lies about 116 km from the 7th arc and
was recorded at both H01 (1,665 km) and H08S. Blackman et al., UCRL-TR-207323, give measured
transmission loss of about 120–133 dB at H01 over 10–60 Hz and 122–135 dB at H08S over 5–60 Hz.

**That is ground truth at nearly the right geometry, and it is the engine validation.** Predict from
Blackman's own source points and compare against what they measured. **Site air8 was not detected at
H01 and nobody could explain why — treat that as the negative control.** If the model predicts air8
should have been detected, the model is wrong in a way that matters before any MH370 claim rests on
it. The SUS charge site A11 and the 2003 A1–A11 events extend the set.

**The source term cannot be calibrated from public information.** The only aircraft data point is
the F-35A recorded at H11 (Brown et al. 2026, *Icarus*): 900 ± 200 MJ giving 0.7 Pa at 3,300 km,
η of order 10⁻⁴ — and it is an **upper bound**, because that crash site had a shallow sound channel.
So η is swept log-uniform over at least three decades with the F-35 value as the upper anchor, and
is reported as a sweep rather than a value.

**The honest expectation, stated up front.** Duncan and Dall'Osto's 2023 modelling puts MH370's path
to HA01 20–30 dB worse than the F-35 path, which would place predicted levels at or below the noise
in Kadri's traces. The repository holds their figure 3 (relative level against range for both paths)
and figure 5 (the sound-speed section, which shows the channel axis descending from about 1,000 m to
2,200 m over 8,500 km while the seafloor repeatedly rises above it). Figure 3 is digitisable into a
predicted-level prior; figure 5 is the physical reason. **If that holds, the module's first real
result is a detectability statement rather than a detection, and that is a finding worth
publishing**, not a failure.

---

## 4. Data held

**From Kadri's published paper, recovered by a prior session.** `kadri-table1-transients.csv` (the
19 Table 1 transients), `observed-transient-candidates.csv` (the prior session's own table of
interest), and figure-9 vector traces digitised for five panels across H01W and H08S. This is a
genuine test set and it is narrow: no direction, no full spectrum, limited in time. Treat it
accordingly — it can exercise methods and test conditional hypotheses; it cannot by itself support
a likelihood.

**Prior correlation work**, as configuration rather than prose: `two-station-correlation-config.json`,
`aligned-detection-config.json`, and a `raw-triad` input schema with worked H01W and H08S examples.
That is the skeleton of the technique in §5.

**Blackman, already extracted machine-readable** in `Blackman_2004_extracted_data`: air1–air9 shot
lines with Julian day, times, endpoint coordinates, seafloor depth, shot interval and ranges; the
non-airgun cylinder and sphere sources; the 2003 A1–A11 events; source-class characteristics; and a
conservative receiver-observations table carrying positive **and** negative detection evidence, with
detection status never inferred from silence. One row is flagged: the JD144 10:54:57.77 event is
labelled A3 in the indexed text but its coordinates are essentially A4 — **check it against the
original page image before publication.** The full report is at
`ISO Sept 28 Status/inputs/papers/hydroacoustics/ucrl-tr-207323.pdf`.

**IMOS/Curtin**, 566 MB. Loggers: Perth Canyon 3315 at 31°52.0′S 115°00.1′E; Perth Canyon 3376 at
31°50.5′S 115°00.8′E, staggered five minutes from 3315; Scott Reef 3250 at 15°29.0′S 121°15.1′E.
Coverage 2014-03-08 00:00 to 03-09 00:49 UTC, one record of about 307 s every 15 minutes at 6 kHz.
Curtin CMST `.DAT` — five ASCII header lines, big-endian int16, a footer — with Curtin's own loader
included. Hydrophone sensitivity about −197.8 dB re V²/Pa², a deliberate roll-off below about 8 Hz,
and clock drift of about 0.25 s per day. **Single hydrophones, so no bearing.** Logger 3376's full
deployment is on AODN for other-night controls.

**IMS data are different**: continuous 250 Hz triads in IDC formats. Write one reader per format,
each producing a **common calibrated-pressure representation**, so the same analysis runs on both
and can be sent to Kadri unchanged.

**Search for further publicly available recordings and use whatever can be found** — this is
explicitly in scope. Record provenance and licence for anything new.

---

## 5. The correlation technique, and what it must clear

The technique Pete wants is the GPS-tracking analogy: use the **predicted** signal as the signal of
interest, place each receiver at its simulated time of arrival, then shift the received signals in
time and look for a correlation peak that also matches the signal of interest, across multiple
sites.

It is the right idea and it is the structure in which the prior work already failed. A matched
filter searching a window of half-width W at bandwidth B has roughly 2·W·B independent trials:

| search | independent trials | per-trial significance for a 1% global false alarm |
|---|---|---|
| ±1 h, 30 Hz | 216,000 | **5.3σ** |
| ±2 h, 30 Hz | 432,000 | 5.5σ |
| ±1 h, 8 Hz | 57,600 | 5.1σ |
| ±15 min, 30 Hz | 54,000 | 5.1σ |

Narrowing the band or the window is a weak lever — a 4× cut in trials buys 0.2σ. **Multi-site
coincidence is the lever that works.** Requiring the second station to be consistent within ±30 s of
the predicted lag cuts the trial space by about 120× and brings the requirement to 4.4σ; within
±10 s, by 360× to 4.1σ. Coincidence is worth about a full sigma, which here is the difference
between a claim and an artefact.

This is why §2 rule 4 is arithmetic rather than etiquette. The recorded prior failures are this
arithmetic in action: a panel's own 99th percentile flags one "detection" per panel **by
construction**; and the null model decided significance, p = 0.0025 under one surrogate against
0.4–0.9 under burst-preserving ones. Bearing errors are heavy-tailed — ±0.4° claimed, 3.3°
demonstrated — so a bearing-consistency cut must use the demonstrated distribution, not the claimed
one.

Set against §3's 20–30 dB, expect that a single-site search cannot clear 5.3σ. State the detection
threshold the search actually requires, and the source energy and coupling at which a signal would
reach it, every time a search returns nothing.

---

## 6. The detection-control protocol

Carried forward from the previous brief unchanged, because it was agreed and it is correct. It is
both the discipline for our own analysis and the specification handed to Kadri.

(a) **Pre-register before looking**: windows per station from the impact posterior (arrival-time and
bearing ranges), bands — e.g. 2–5, 5–10, 10–20, 20–40 Hz — the detector, and its threshold.
(b) **Backgrounds from real data**: the same station outside the window (±60 min to start, ±6 h gives
about 20 windows); the same UTC window on other nights, 1–14 March 2014; off-bearing windows; and
time slides between stations for coincidences.
(c) **Characterise the noise** per station and hydrophone: band-power percentiles at 5/50/95,
burstiness, flagged source classes (seismic airguns including the TGS Huzzas survey at H08S,
earthquake T-phases checked against catalogues, blue and fin whale calls at 15–30 Hz, ships), and
the detector's false-alarm rate against threshold.
(d) **Inject synthetic impact signals into real background and recover them.** This is what yields
P_D against received level, and the timing and bearing errors. **It is the gate in rule 2.**
(e) **Positive controls**: the seismic survey, catalogued earthquakes, and the ~01:34 UTC HA01 event
the ATSB called likely geological.
(f) **Combining near the noise floor**: coherent triad beamforming at one station, about 5 dB of
gain; cross-station association by consistent times and bearings; significance from time slides.
(g) **The likelihood form**, once calibrated, as in rule 2.

---

## 7. Sequence

Pete's sequence, with two changes, and the second is the important one.

1. **Calibration, noise estimation and controls — with the Blackman engine validation inside this
   step, not after it.** It is the only ground truth available and everything downstream inherits
   its verdict. Include air8 as the negative control.
2. **The composer test, early, on synthetic detections.** Before building detection methods, answer:
   how much would a detection at one, two or three sites, with an O−C inside the stated uncertainty,
   actually move the impact PDF? It needs no real data and it is decisive. If a marginal single-site
   detection moves the posterior by less than its own uncertainty, the module's priorities change —
   effort goes to the detectability statement and the Kadri package rather than to correlation
   methods. If two-site coincidence moves it substantially, that justifies everything after it.
   Days, not months.
3. **Predictive passes and smoke tests** over impact-PDF locations — gridded as ocean drift does it,
   or from source points with the other estimated parameters, whichever the geometry favours.
4. **Trial detections and non-detections** on the data we hold, trying several techniques including
   the correlation method of §5, each pre-registered.
5. **Larger tests and the conditional hypotheses of §8.**
6. **Sample outputs for Kadri** (§9).
7. **Composer integration proper**, now informed by step 2.

---

## 8. Conditional hypotheses

Each is a declared alternative with a prior, reported per alternative, never folded into a base
estimate.

- **An unarrested Holland descent** under cruise-to-flame-out, combined with his descent-rate
  interpretation of the 00:19 BFO values. Note the standing ruling: Holland's bounds are **not** to
  be imported as a constraint on the end-of-flight module, because they are conditional on a
  transient assumption this project declines to treat as established. Here they are the hypothesis
  being tested, which is a different use and is legitimate — state which you are doing.
- **Pleiades**: the impact locations consistent with the imaged-object source region, scored
  acoustically.
- **Kadri's identified candidates** from his paper and tables, including the main one at 00:54:30 on
  a bearing of 306.18°, which crosses the arc near 25.8°S. His 2025 poster reports no plausible
  signal in the expected window at H01W or H08 — that is a result to reproduce and understand, not
  to work around.

---

## 9. The package for Kadri

The collaboration is **active**, and we are flexible on what is sent. But provisional outputs and
results must not depend on it: test the module and show provisional results on what we hold first.

`predictions.csv`, one row per location bin and station: weight, latitude, longitude, seafloor
depth; impact-time range and kinetic energy; range, back-azimuth and arrival window; transmission
loss per band with standard deviation; a blockage flag; predicted peak pressure and exposure for
several values of η. Plus `windows.csv`, and a reference measurement script of about a hundred lines
— Butterworth bands; peak, RMS and exposure; pre-event noise; SNR; a plane-wave bearing fit — with
synthetic triad waveforms. Requests: the historical crashes with the F-35A first; the Blackman shots
if his archive reaches back to 2001 and 2003; same-night controls; noise percentiles 22:00–02:00;
injection-recovery with his detector unchanged; and every detection in the pre-registered windows.
Draft it for Pete's review before anything is sent.

Separately: ask Metz's group for the F-35 paper and waveforms, and Royer (OHASISBIO) for his 2014
data.

---

## 10. Deliverables

1. A short plan, as your first reply.
2. The literature review of §1, and the critical review of the prior work on this case.
3. The calibrated propagation engine, validated against Blackman with air8 as the negative control.
4. The early synthetic composer test of §7 step 2, with its verdict stated plainly.
5. The predictive layer: simulated arrivals with uncertainty bounds on time and energy, per station,
   per branch (deep sound channel and AGW), per η.
6. The detectability statement: the threshold a search must clear and the source energy and coupling
   at which a signal would reach it.
7. Trial detections and non-detections, each pre-registered, with significance from time slides and
   burst-preserving surrogates.
8. The Kadri package, drafted for review.
9. `core_requests` in `hypothesis.toml`, and a note to `coordination/architecture.md` when the
   branch is ready for review.

## 11. Tests

Port the arrival and energy equations and their three tests from the archive: zero range; energy ×4
gives pressure ×2; the H01W/H08S scale. **The rest of the archived physics was placeholder** — a
never-calibrated transfer function and a near-field shock law misapplied at 2,000–3,700 km — and is
not to be ported. Rebuild the station coordinates from one documented source; the values in the old
configs disagree with each other. Add: a hand-computed transmission loss against Blackman; a
synthetic-recovery test that injects a known signal and recovers its time, bearing and energy; and a
null test that the detector's false-alarm rate matches its nominal threshold on real background.

## 12. Scope and reporting

`make scope H=hydroacoustics` must pass — nothing outside `hypotheses/hydroacoustics/`, plus a
`prepare/` subfolder for analysis scripts. No new `.md` inside `engine/`; assumptions and sources in
the `lib.rs` doc comment, status in `hypothesis.toml`, write-ups in the project-level `results/`.
`make smoke H=hydroacoustics` is the code-path check; **`make hypothesis H=hydroacoustics` runs at
full scale.** Queue anything over ~10 minutes or ~4 GB behind `lockf -k /tmp/.mh370-heavy.lock`.
Python dependencies for the analysis side — scipy for filtering, a parabolic-equation propagation
code — are a core request for the environment, not something to install ad hoc.

## 13. Deferred, and to be raised again

- **An implosion at depth** from a flooding section, which settling may emit as a predicted event
  with a time, depth, position and energy class. **Design the arrival machinery to accommodate a
  second, time-delayed source** — it would arrive tens of minutes after the 7th arc rather than at
  it, which is a timing signature nothing else in the evidence set provides — but do not implement
  it in the first pass.
- **The IMOS analysis.** Wanted, not necessarily first pass.
- **Diego Garcia airgun filtering.** Wanted; note that we cannot beamform on single hydrophones,
  though Kadri may be able to with the raw triad data.
- **The 2014 aerial search** and other surface-search evidence: not this module.

## 14. Open, needing the architecture session

1. Whether the predictive grid follows ocean drift's source-grid design or uses impact samples
   directly — decide after step 3 measures how fast predicted arrivals vary with source position.
2. The shared-layer seafloor-depth lookup, with settling.
3. The composer's treatment of a module that returns zero until calibrated: it must be selectable
   and contribute nothing, not be absent.
4. Environment dependencies for the propagation and signal-processing stack.

---

## The impact source interface — added 8 October 2026

### You receive mechanical quantities. You own the conversion to an acoustic source.

The end-of-flight module emits what happened to the aircraft's energy. It does not emit a sound
source, and it must not be asked to. **Three durations are distinct and this module is the only
place where all three appear, so it is the only place they can be confused:**

1. **Mechanical energy-transfer duration** — `energy_transfer_tau90_s`, the interval containing the
   central 90% of mechanical energy transferred during initial water entry and deceleration,
   defined as `t95 - t05` of the cumulative transfer from first water contact. Owned by end of
   flight. The 90% convention is a declared interface choice, not a standard.
2. **Acoustic source duration** — the duration of the radiated pressure signal at the source.
   **Yours.** It is not equal to (1).
3. **Received signal duration** at a hydrophone — broadened by multipath, modal dispersion and
   bottom interaction along a path of thousands of kilometres. **Yours, and never an estimate of
   either of the others.** The aircraft-crash hydroacoustic literature is explicit that propagation
   broadening must not be read back as impact duration.

**The feedback is forbidden in one direction.** You may not infer a duration from a received signal
and return it to end of flight as `energy_transfer_tau90_s`. That is circular: the impact model
would then be calibrated on the data the module is meant to score.

### What arrives

| latent | meaning |
|---|---|
| `impact_energy_transferred_j` | mechanical energy transferred during the initial event |
| `energy_transfer_t05_s`, `energy_transfer_t95_s` | 5% and 95% times from first water contact |
| `energy_transfer_tau90_s` | `t95 - t05` |
| `energy_transfer_peak_rate_w` | peak rate of transfer |
| `energy_transfer_n_pulses` | distinct peaks above a declared threshold |
| `impact_heading_deg`, `impact_bank_deg` | attitude at contact |

NaN means not computed, and at first pass several of these will be NaN. A NaN propagates into a
"not assessed" rather than into a default.

### Coupling efficiency is a declared alternative, not a constant

Mechanical energy loss is not all converted to sound. It also goes into bulk water motion, surface
waves, structural deformation, fragmentation and heat. The fraction radiated as acoustic energy into
the water column is **one of the most uncertain numbers in the entire chain and it will dominate your
predicted received level.** Carry it as a declared alternative with a stated prior, marginalise it,
and report the received-level prediction's sensitivity to it separately from everything else.

This connects directly to the gate on this module. Hydroacoustics may return a log-likelihood only
after injection-recovery gives P_D against received level. Coupling-efficiency uncertainty enters
that curve; a recovery study run at one assumed efficiency does not establish the gate.

**Energy and tau alone do not determine pressure amplitude, spectrum or directivity.** Two events
with the same energy and the same duration can radiate materially different signals. Your source
model needs geometry, source depth, contact sequence and attitude as well — which is why the
attitude latents and the pulse count are in the interface at all.

### Where tau matters, and where it does not — the SOFAR and AGW branches split here

The first acoustic-mode cutoff in a water layer of depth `H` is `f_c = c / 4H`. At the search area:

| H | f_c | period |
|---|---|---|
| 3,000 m | 0.125 Hz | 8.0 s |
| 4,000 m | 0.094 Hz | 10.7 s |
| 5,000 m | 0.075 Hz | 13.3 s |
| 6,000 m | 0.063 Hz | 16.0 s |

A source of duration `tau` rolls off above roughly `1 / tau`. So:

- **SOFAR branch.** For any plausible impact, `tau` between about 0.05 s and 10 s puts the roll-off
  between 20 Hz and 0.1 Hz — squarely inside the band the IMS hydrophones record. **`tau` shapes the
  source spectrum directly and matters a great deal.** A short, steep entry and a long ditching are
  materially different sources here, which is the whole reason the parameter exists.
- **AGW branch.** Below `f_c` the water column does not support a propagating acoustic mode and the
  physics is different. At 4,000 m the cutoff period is 10.7 s, so for `tau` below about 10 s the
  impact is **effectively impulsive for the entire AGW band**, and AGW excitation is governed by the
  total impulse and the displaced volume rather than by `tau`. Only a long event — a well-executed
  ditching with `tau` approaching or exceeding the cutoff period — makes `tau` shape AGW excitation
  as well.

**So whether `tau` matters to AGW is itself a function of `tau`, with the threshold set by depth.**
Compute `f_c` at the candidate impact depth rather than assuming 4,000 m, state which regime each
sample falls in, and do not carry a `tau`-dependence into the AGW branch where the sample is
impulsive — a dependence that cannot be there is a route to a spurious detection.

### How tau enters the look-elsewhere arithmetic

It does not change the number of trials. Those are set by the search window and the bandwidth, by
§5's `2·W·B` with `W` the **half**-width: at ±1 h and 30 Hz, 216,000 independent trials and a 5.3σ
per-trial requirement for a 1% global false alarm, exactly as §5's table records. What `tau` changes
is the **time-bandwidth
product** `tau * B`, which sets the per-trial processing gain: 30 at `tau` 1 s and `B` 30 Hz, 300 at
`tau` 10 s. A longer event is easier to detect at the same radiated energy because more of it is
coherently integrable — but only if the source model says the emission really is that long, which is
(2) above and not (1).

---

## Amendments, 9 October 2026 — accepted from the module's overnight review

1. §3's "20–30 dB worse" refers to Duncan & Dall'Osto's **301.6° HA01 bearing**, crossing the arc near
   24–26°S. It is one comparison case, **not** the core-region path and not a prior.
2. §3's transmission-loss figures are **read off Blackman Fig. 23, approximately ±2 dB**: H01 about
   116–134 dB over 13–60 Hz, H08S about 120–136 dB over 5–60 Hz. Printed range only for air9 (H01
   1,665 km; H08S about 4,825 km).
3. §3: coupling efficiency η is swept over **at least four decades**.
4. §5–§6: "p = 0.0025" and the ATSB "likely geological" wording are **withdrawn**: neither could be traced.
   Cite p ≈ 0.001 under one surrogate against 0.63–0.91 under burst-preserving surrogates, or attribute
   the wording to Curtin or Duncan by page.
5. §4: the Blackman set is at `Sept 27 2026 backup PL ChatGPT instance/Blackman_2004_extracted_data_2026-09-27.zip.b64`
   (one character short; repair recorded in the module manifest). The module's own re-extraction is the
   data of record. JD144 10:54:57.77 is **A4**, not A3 — a typo in the report itself.
6. **Headline from the synthetic composer test:** the module's value rests on **two-site H01 + H08
   detectability from the core region**. One site carries almost no information.


## Side questions (standing rule, Pete, 10 Oct 2026)

Pete, 10 Oct 2026: when he asks a side question, answer it and then go back at once to the work you were doing. If that work is complete, start the next item in your backlog. Do not end your turn after a side answer while you have work in progress or a backlog. End your turn only when the backlog is empty or every item is blocked on something you cannot do yourself. Before you end it, write here which items are blocked and on what. An approved run whose gates you can execute is not blocked: start it.
