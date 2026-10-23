cat > hydro-option-b-plain-english.md <<'EOF'
# Option B, in plain words: what it tests, on what, and what it can and cannot tell us
13 Oct 2026. Simplified technical English. Standard statistical terms are used as they are.
A technical note follows each section.

## 1. The question Option B answers

**If MH370 hit the sea hard and fast, would any of our receivers have heard it, and is there
anything in the recordings that matches?**

It is one question with three parts, and the order matters:

1. **Could it be heard?** For every possible impact, work out the sound that reaches each receiver
   and compare it with the measured background noise there.
2. **Is anything there?** Look in the recordings, in the predicted time windows only, at several
   levels of confidence including loose ones.
3. **How much is a silence worth?** Put the predicted sound into the real recorded noise and count
   how often it is found. Only then does "we heard nothing" mean something.

## 2. The data

| Data | What it is | Status |
|---|---|---|
| Impact set | The end-of-flight run, giving position, time, energy and duration for every possible impact | held; use run I dive, see §6 |
| Five research loggers | Perth Canyon x2, Scott Reef, Portland x2 | held, about 14 GB |
| Two treaty stations | Cape Leeuwin and Diego Garcia South, as traces digitised from the published figure | held |
| Background noise | Measured per logger in seven frequency bands | measured already |
| Background null | 98 realisations of "what the test statistic looks like when nothing is there" | measured already |
| Transmission loss | A mode model per logger, frequency, source depth and range | held |
| Path blocking | Which paths cross land or shallow banks | held |
| Airgun calibration | The 2001 shots at site air9, recorded at both treaty stations | held |

No new data is needed. No new 14-day background read is needed.

## 3. What is actually done

**Step 1. Choose which impacts to carry.** Not the loudest tenth. Carry every impact whose predicted
level at any unblocked receiver comes within about 10 dB of the noise there. Drop only those far
below the noise everywhere. Group what is left into cells about half a degree across, so the sound
path is computed a few hundred times instead of a million times.

**Step 2. Predict.** For each cell and receiver: the arrival time, the level and the spectrum.

**Step 3. Screen.** Mark every receiver that can tell us nothing, and say why: the path is blocked,
or the prediction is far below the noise, or the receiver was not recording at that moment.

**Step 4. Scan.** Every receiver that survives the screen, in the predicted windows only.

**Step 5. Report graded evidence.** For every candidate: the p-value, the signal-to-noise ratio and
the likelihood ratio. Mark at 0.3, 0.1 and 0.05. Never reduce it to "detected" or "not detected".

**Step 6. Test agreement between receivers.** For each candidate at one receiver, ask whether another
receiver has one at the time difference the geometry demands, and count how often the 98 background
realisations do the same by chance.

**Step 7. Measure the power.** Put the predicted sound into the real noise at the predicted time and
level, at every receiver, and count how often it is recovered. This gives the probability of
detection, the 95% upper limit on source loudness and the Bayes factor.

**Step 8. Redraw the airgun chart,** showing measured against predicted loss with the array and
near-field terms and the corridor spread.

## 4. The assumptions you are buying

- **Coupling.** The fraction of impact energy that becomes sound in the sound channel is about one in
  ten thousand in the only measured aircraft case. It is carried as a range with a prior, not as one
  number, and it dominates the predicted level.
- **Propagation.** The model passes a level check against the 2001 airguns but fails a slope check,
  by +10 dB per octave at Cape Leeuwin and +7 at Diego Garcia South. The airgun data cannot separate
  the source spectrum, the array pattern and the propagation itself. Nothing checks Cape Leeuwin
  below 12.5 Hz.
- **Detection probability.** There is no continuous treaty-station noise, so the probability of
  detection is measured in research-logger noise and shifted by +4.8 dB to stand in for a
  three-element treaty station. That is a proxy.
- **Recording gaps.** The loggers duty-cycle. Only 11 to 47 in 100 of each predicted window was
  being recorded.
- **Resolution.** With 98 background realisations the smallest p that can be stated is 1 in 99,
  which is 0.0101.
- **The impact model is provisional.** Every number is conditional on it.

## 5. What it will tell us

- Which receivers could have heard a hard, fast impact, and which could never have, with the reason
  stated for each.
- Whether anything in the recordings matches a predicted arrival, at loose as well as strict levels.
- Whether any two receivers agree, which is the only result strong enough to lift the module from
  prediction-only to contributing evidence.
- What a silence is worth, as a 95% upper limit on source loudness, a Bayes factor and a figure in
  bits. The earlier estimate puts a non-detection at 0.0000455 bits if the probability of detection
  is 0.1, and 0.199 bits if it is 1.0. That spread is the whole question.

## 6. What it will NOT tell us

- **It will not locate the impact.** A single detection gives a travel time, not a position. Two
  receivers give a hyperbola. Three would be needed for a point, and only two unblocked treaty
  stations exist.
- **It cannot prove the aircraft did not hit the sea hard.** Absence of a signal is only ever a
  statement about power.
- **It will not calibrate the source.** No public data gives the sound an aircraft makes hitting
  water. The one measured case is a fighter aircraft about ten times smaller in energy.
- **It will not settle which 00:19 reading is right.** The module's likelihood stays gated at zero
  unless the power work succeeds.
- **It cannot resolve a p below 0.0101** without a larger background sample.
- **It says nothing about acoustic-gravity waves.** The research loggers are high-passed at 8 Hz.
- **Two receivers are already ruled out before it starts.** H08N is behind the Chagos Bank and Scott
  Reef is behind the Australian shelf at every latitude in the impact distribution.
- **It depends on which end-of-flight run is used.** Run I puts only 4 in 100 of its impacts at
  arrival angles between 10 and 45 degrees; run I dive puts 16 in 100 there, because it allows a
  push-over to carry on down to the water. That band is short and loud enough to matter. Option B
  should use run I dive, and the choice must be agreed with end of flight first, because it changes
  the answer.
EOF
wc -w hydro-option-b-plain-english.md