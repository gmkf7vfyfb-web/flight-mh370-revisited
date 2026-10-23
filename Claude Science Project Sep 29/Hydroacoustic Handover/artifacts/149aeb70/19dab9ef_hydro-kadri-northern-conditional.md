# Conditional test: Kadri's bearing-implied northern source
Design, 13 Oct 2026. Nothing has been run against any recording under this hypothesis.

## 1. Why this is a gap, not a repeat

Kadri's strongest signal at Cape Leeuwin carries a bearing of 306.18 degrees. Projected to the arc
that bearing crosses at about **26.2 S, 101.9 E**, which is roughly 1,000 km north of where the
impact distribution puts most of its weight. Working back along the path at 1.48 km/s, the implied
source time is **00:34:55** if the signal is at 00:52:03 as Kadri's text says, or **00:37:22** if it
is at 00:54:30 as his caption says. The 2.5-minute discrepancy is in the publication, not in our
reading of it, and both must be carried.

The pre-registered H01W x H08S pair test searches time differences of 856 to 1,347 s. On this arc
that spans latitudes **45.0 S to 28.9 S**. A source at 26.2 S needs a time difference of **1,493 s**.
**The test as written could not have found Kadri's own preferred source.** The span was set from the
impact distribution, which is concentrated far to the south, so the hypothesis was excluded by
construction rather than by evidence.

## 2. What is already known about this locality

- **Our own impacts do reach it, thinly.** Of the run I dive draw, 0.36 per cent lies within 100 km
  of the crossing, 1.21 per cent within 200 km and 2.31 per cent within 400 km. Run I gives
  0.37, 1.19 and 2.28 per cent for the same three radii.
- **The times agree.** Those impacts have a median impact time of 00:36 to 00:38. The bearing and
  travel time imply 00:34:55 or 00:37:22. These two numbers are arrived at independently, one from
  the flight model and one from an acoustic bearing, and they agree to within a few minutes. That is
  not evidence of a detection, but it is the reason to run the test.
- **Perth Canyon has already been looked at, and found nothing.** Logger 3376 recorded 186.0 s of the
  first predicted window and 154.2 s of the second. The best candidate in each gave p = 0.749 and
  p = 0.709 at a signal-to-noise ratio of 7.7 to 8.7 dB. Logger 3315 had no coverage in either.

## 3. Which receivers can say anything for a source at 26.2 S

| Receiver | Range | Arrival, source 00:34:55 | Status |
|---|---|---|---|
| H01W Cape Leeuwin | 1,520 km | 00:52:02 | the signal itself |
| Perth Canyon 3376 and 3315 | 1,422 km | 00:50:55 | clear, inside the recording window |
| H08S Diego Garcia South | 3,730 km | 01:16:54 | clear, and **untested at this time difference** |
| Scott Reef 3250 | 2,334 km | 01:01:12 | no land on the path, but the shelf blocks it |
| Portland 3274 and 3275 | 3,909 km | 01:18:56 | **land-blocked**; Australia intervenes for any source north of 28.8 S |
| H08N | — | — | Chagos Bank blocks every path |

So the corroboration available is Perth Canyon, which has been looked at, and **Diego Garcia South,
which has not been looked at for this hypothesis**. Everything else is ruled out by geography.

## 4. The test

1. **Pre-register first, and separately.** This is a new conditional with its own look-elsewhere
   correction. Do not fold it into the existing pair test; state the new time-difference span,
   **1,346 to 1,710 s**, which covers arc latitudes 28.9 S to 22 S. The lower bound is set to abut
   the existing test's upper bound of 1,347 s so that the two searches are contiguous: on this arc
   1,346 s is 28.9 S and 1,710 s is 22.0 S. An earlier draft of this note gave the lower bound as
   1,390 s, which is 28.0 S and would have left 28.9 S to 28.0 S searched by neither test.
2. **Fix the locality with its uncertainty.** Use the module's own arc definition rather than a fit
   to the impact cloud, and carry the bearing as a mixture: a core of 0.5 to 1 degree, not the
   pessimistic Student-t with 3.3 degrees. At 1,520 km, 1 degree is 27 km across and 3.3 degrees is
   88 km.
3. **Simulate the whole range of impact types there, whatever our weight says.** Place the full
   mixture of arrival types at the locality at both candidate source times: the shallow arrival with
   its 4-second energy transfer, the steep dive with its 0.13-second transfer, and the intermediate
   band that only run I dive populates. Our own weight at that locality is thin, and the point of a
   conditional is to ask what we would see **if** the aircraft went in there, not how likely that is.
4. **Predict and screen.** Arrival time, level and spectrum at Cape Leeuwin, Perth Canyon and Diego
   Garcia South. Mark Scott Reef, Portland and H08N as carrying no information, with the reason.
5. **Search Diego Garcia South around 01:16:54 and 01:19:21.** This is the one genuinely new look.
   Report the p-value, the signal-to-noise ratio and the likelihood ratio, screening at 0.3 and
   marking at 0.1, never a bare verdict.
6. **Re-examine Perth Canyon with the duty cycle stated.** The earlier look is a non-detection over
   about three minutes of a three-minute-plus window at one logger. State the recovered coverage and
   the power, not just the p-value.
7. **Test agreement.** If Diego Garcia South yields a candidate, test the three-site geometry:
   Cape Leeuwin to Diego Garcia South at 1,493 s and Cape Leeuwin to Perth Canyon at minus 67 s, both
   within their uncertainties. Count how often the 98 background realisations produce the same.
8. **Report the result as a conditional on every figure.** It is a test of Kadri's locality, not of
   the impact distribution, and it stays labelled that way whichever way it comes out.

## 5. What it can and cannot settle

If Diego Garcia South shows nothing with good power, the northern locality is disfavoured at a stated
strength and the matter is closed with a number rather than by omission. If it shows a candidate at
the right time difference, there are two sites in agreement at a locality that our flight model also
reaches at the right time, which is the strongest result available anywhere in this module and would
justify going back to the raw treaty-station data.

It cannot locate the source on its own: two sites give a hyperbola, not a point. It cannot resolve a
p below 0.0101 with the background now held. And it rests on the same uncalibrated propagation and
coupling assumptions as everything else in the module.
