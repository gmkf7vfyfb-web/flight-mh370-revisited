cat > hydro-smoke-run-plain-english.md <<'EOF'
# The hydroacoustic smoke run, in plain words
13 Oct 2026. Written in simplified technical English. Standard statistical terms are used as they
are. A technical note follows each section.

---

## 1. What we are trying to find out

One question, in three parts:

1. If the aircraft went into the sea in a steep, fast dive, the impact is short and loud. **Would
   that sound have been loud enough to record at the receivers we have?**
2. **Is there anything in the recordings that matches such a sound**, at the time and place the
   flight model predicts, at several levels of confidence including loose ones?
3. **Is there anything that matches at more than one receiver at once**, with the time difference
   between them that the geometry demands? That is the strongest result available, because two
   receivers that agree are very hard to produce by chance.

*Technical: the module likelihood stays gated at zero until the probability of detection against
received level is established. Parts 1 and 3 above are what lift that gate; part 2 on its own cannot.*

---

## 2. What the run will not do

- It will not prove that no sound was there. No statistical test can do that.
- It will not give a result that enters the posterior. This is a smoke run. It tests the pipeline
  and gives a first measurement of power.
- It will not calibrate the propagation model. That needs known sources, and it is a separate item.

---

## 3. The data it uses

| Data | What it is | Already held |
|---|---|---|
| Run I impact set | 102 million possible impacts from the end-of-flight model, with position, time, energy and duration for each | yes, on disk |
| Energy and duration sidecar | tau90_v1.npz, written 13 Oct, gives energy, duration and peak power per impact | yes |
| Five research loggers | IMOS deep-water recorders at Perth Canyon (two), Scott Reef, Portland (two) | yes, about 14 GB |
| Two treaty stations | Cape Leeuwin and Diego Garcia South, as traces digitised from the published figure | yes |
| Background noise levels | Measured for every logger in seven frequency bands | yes, measured already |
| Background null | 98 background realisations built earlier for the coincidence test | yes, measured already |
| Transmission loss | Mode model per logger, frequency, source depth and range | yes |
| Blocked paths | Scott Reef is behind 199 km of land; H08N is behind the Chagos Bank | yes |

**Nothing new has to be downloaded and no new 14-day background read is needed.** The earlier
background work is reused. That was a mistake in the first plan and it is corrected.

*Technical: the 14-day read in item 6 of the module plan builds the null distribution of a test
statistic over new run I windows, which is a different object from the noise level. For a smoke run
the existing n_B = 98 realisations are sufficient; they set the smallest resolvable p at 1/98, which
is 0.0102.*

---

## 4. The procedure, step by step

**Step 1. Choose the impacts.** Keep only the loud, short ones: the top tenth by peak radiated power
and shorter than 2 seconds. That is about 10 in 100 of all impacts. Group them into cells about half
a degree across, so the sound path is computed a few hundred times instead of a million times.

**Step 2. Predict.** For each cell and each receiver, compute when the sound arrives and how loud it
is when it gets there. Loudness needs one more number, the fraction of impact energy that becomes
sound in the sound channel. That fraction is about one in ten thousand in the one measured aircraft
case. It is carried as a range, not as a single value.

**Step 3. Screen before scanning.** Compare the predicted loudness with the measured background
noise at each receiver. Receivers behind land or a shallow bank are marked "tells us nothing" before
any recording is opened. Receivers where the prediction sits far below the noise are marked the same
way. Only the rest are scanned.

**Step 4. Scan all receivers, but only in the predicted windows.** This is the correction to the
first plan. Sparse in **time**, not sparse in **receivers**: a sound heard at two receivers is worth
far more than a sound heard at one, so every receiver that can hear is scanned. The recordings
duty-cycle, so between 11 and 47 in 100 of each predicted window was actually being recorded.

**Step 5. Report graded evidence, not a verdict.** For every candidate, report the p-value, the
signal-to-noise ratio and the likelihood ratio. Mark candidates at 0.3, 0.1 and 0.05. Do not reduce
the result to detected or not detected.

**Step 6. Test for agreement between receivers.** For each candidate at one receiver, ask whether
another receiver has a candidate at the exact time difference the geometry demands. Count how often
the 98 background realisations produce the same agreement by chance.

**Step 7. Measure the power.** Put the predicted sound into the real recorded noise, at the right
time, at each receiver, at three levels. Count how often it is recovered. This gives the probability
of detection, the 95% upper limit on source loudness, and the Bayes factor.

*Technical: steps 2 and 3 are a grid cache of propagation quantities, not a second sample set. Step 7
must span the coupling-efficiency prior, not assume one value, or the gate is not established.*

---

## 5. On the confidence level: use 0.1, not 0.01

Moving the test from 0.05 to 0.01 makes the test **harder** to pass. It lifts the bar away from the
noise, so a weak signal is less likely to be found, and it makes the upper limit weaker.

Moving the other way, to 0.1 or even 0.3, is the right move for finding weak signals, and it is safe
here for one specific reason: **a loose bar at a single receiver is cleaned up by the agreement
test.** A candidate that passes at 0.3 on its own means very little. The same candidate, matched at
a second receiver with the correct time difference, is strong. The false-alarm rate of the pair is
measured against the same 98 background realisations, so looseness at one receiver does not leak
into the joint result.

So: screen at 0.3, mark at 0.1, and report every p-value. The deliverables the paper needs, the
power curve, the upper limit and the Bayes factor, do not use a threshold at all.

*Technical: with n_B = 98 the smallest resolvable p is 0.0102, so 0.01 is at the floor and 0.005
(the "strict" setting used earlier) cannot be resolved. Per-site alpha of 0.1-0.3 with a joint
false-alarm rate estimated from the background realisations is the standard two-stage design.*

---

## 6. What comes out

**Tables.** Predicted arrival time and loudness per cell per receiver. A screen table that says which
receivers can inform and which cannot. A candidate list with p-values at each level. An agreement
table. A power table with 95% upper limits. A coverage table that states plainly what was not tested.

**Graphics.** A map of where the loud short impacts are and how many receivers could hear each one.
A time chart of the predicted windows against the recording windows. A power curve, which is the
probability of detection against source loudness, with the 95% upper limit marked. A chart of any
candidates against the noise.

**What it tells us.** Either that a loud short impact would have been detectable at one or more
receivers, which makes the non-detection informative and is the result the paper needs; or that it
would not have been, which makes the non-detection worth almost nothing and moves the effort to the
detectability statement and the package for Kadri. The earlier estimate puts the information in a
non-detection at 0.0000455 bits if the probability of detection is 0.1, and 0.199 bits if it is 1.0,
so this distinction decides whether the module has anything to contribute at all.

---

## 7. Revised cost

About 1 to 1.5 hours of machine time, none of it needing the heavy lock, because the large background
read is dropped. That is up from the 15 to 25 minutes I first quoted, and the increase is the cost of
your correction: scanning every receiver instead of one, and running injection-recovery at every
receiver instead of one. It is the right trade.
EOF
wc -w hydro-smoke-run-plain-english.md