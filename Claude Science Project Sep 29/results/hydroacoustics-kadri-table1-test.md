# Hydroacoustics interim deliverable 2a: Kadri (2024) H01W transients against the impact PDF - PROVISIONAL

**Pre-registered** in `prepare/kadri_table1_test.py` (`hypothesis/hydroacoustics` at `0b14da9`) before the
first run. One implementation defect was fixed after the run (`e0ad490`; see "Correction" below).

**Inputs, and what they are:**
- **Kadri's Table 1:** 19 transients, time and bearing at H01W, 00:38:29–00:55:07. EXTRACTED from the
  published table.
- **Fig. 9 traces:** DIGITISED plot vertices, single channel, already filtered by Kadri (2–40 Hz) and
  decimated for plotting. They are clipped at the plot's ±1 Pa axis.
- **Impact PDF:** the parametric 7th-arc stand-in also used by the composer test. Rerun on end of
  flight's impacts when published.

No Kadri-bundle markdown was opened.

**Why it matters.** The synthetic composer test showed that a single site carries little information.
This test shows what the 19 transients carry once their own background rate is taken into account.

## A. Reproduction from the digitised traces: **0 of 18 Table 1 times reproduced**

- **The detector** (fixed in advance): STA/LTA on squared pressure, STA 1 s, LTA 20 s, ratio ≥ 3. It
  fired once across panels b and c (00:37–00:57), at **00:52:03**.
- **The ratio at Table 1's own times** (exploratory diagnostic): 0.9–2.9.
- **Panel b (00:37–00:47) is flat**, with a maximum ratio of 2.1. That agrees with Kadri's text ("no
  observed signals") but not with the **seven** Table 1 events listed in that span.
- **Panel c's one dominant transient is at 00:52:03.** That agrees with Kadri's text ("recorded at
  00:52 UTC"), but Table 1 has **no event within 13 s of it**, and at Table 1's 00:54:30 the ratio is 2.9.

The digitised traces therefore support the **text's** timing and not Table 1's. Bearings need the triad,
so they cannot be reproduced from one plotted channel; Table 1's bearings are taken as published.

## B. Geometry test at H01W

**Prediction from the core-region stand-in:**

| quantity | 2.5% | median | 97.5% |
|---|---|---|---|
| arrival time | 00:42:03 | 00:49:18 | 00:55:41 |
| back-azimuth | 252.6° | 256.1° | 277.7° |
| range | 1,684 km | 2,216 km | 2,382 km |

**The main candidate is geometrically DISFAVOURED** (pre-registered threshold BF ≤ 0.1):

| candidate | bearing error model | log₁₀ BF |
|---|---|---|
| 00:54:30, 306.18° (Table 1) | demonstrated, t₃ with sd 3.3° | **−3.56** |
| | claimed, Gaussian 0.4° | −4.28 |
| 00:52:03, 306.18° (text and Fig. 9c timing) | demonstrated | −2.81 |
| | claimed | −3.03 |

- **The timing is fine; the bearing is not.** 306° is about 50° from the predicted back-azimuth. The
  bearing line crosses the arc at **25.78°S, 101.43°E**, which agrees with the brief's 25.8°S. The stand-in
  places 0.8% of its mass there.
- **Two transients fall where a signal is predicted:** 00:49:58 at 260.41° and 00:53:31 at 257.58°.
  Their BF is about 9.3 each, just below the "supported" threshold of 10.
- **The look-elsewhere null says that is chance** (exploratory, 20,000 sets of 19 background transients
  in Table 1's own time–bearing box). **The best background transient reaches BF ≥ 9.3 in 49.5% of
  sets.**
- **No single-station (time, bearing) point can do much better:** the maximum attainable BF is 27.
- **If either were accepted,** the information gain on the impact position would be **0.35–0.66 bit**.
  That is consistent with the composer test's 0.4–0.6 bit for one site with bearing.

## What this establishes

1. Kadri's main candidate is **inconsistent in bearing** with an impact in the core region. It needs a
   source near 25.8°S. That is a conditional hypothesis (brief §8), to be scored as one, not a detection
   in the core region.
2. Table 1's times are not reproducible from Kadri's own published traces. The traces and the text agree
   on 00:52; Table 1 says 00:54:30.
3. The transients that are consistent with the core region are **indistinguishable from background** at
   one station. This is the composer test's conclusion again, on real candidates: only two-site
   coincidence can carry information.

**Correction (one defect, fixed after the first run, `e0ad490`).** v1 drew one impact time per stand-in
sample, so its "information gain" counted the impact-time nuisance, against the pre-registered
definition (information on position). The Bayes factors are the same marginal; v1 estimated them by
noisier Monte Carlo, and the verdict is unchanged. v1's output is kept as superseded in
`results-data/kadri2a/v1_superseded/`.

*Hydroacoustics module, 2026-10-09.*
