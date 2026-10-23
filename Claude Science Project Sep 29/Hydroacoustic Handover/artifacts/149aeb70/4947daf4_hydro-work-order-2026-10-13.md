# WORK ORDER — Hydroacoustic module, run J
Issued 13 Oct 2026 by architecture, from the Hydroacoustic Next Steps review. Self-contained: a
fresh thread needs nothing from the old one except the files named here.

---

## 0. Standing facts this order depends on (all measured 13 Oct, do not re-derive)

**Impact set.** `mh370-exchange/end-of-flight/run-i-dive` — 4 strata x 8 seeds, 127,999,840 impacts.
**It supersedes run I; do not use run I and do not marginalise over the two.** Run I is the p = 0
point of run I dive's push-over prior, so treating them as alternatives double-counts the level-off
case. Run I also used 415.45 kN sea-level static thrust against the certificate's 406.8 kN.

**Energy and duration** are in `tau90_v1.npz` beside each `impacts32.npy` (`tau90_s`, `t05_s`,
`t95_s`, `peak_rate_w`, `energy_transferred_j`, `decel_g`, `l_eff_m`; method 1, note
`results/eof-impact-tau-method-oct11.md`). The matching `latent:` columns inside `impacts32.npy` are
NaN in every row — do not read them.

**Dive probability p is a declared alternative, applied by reweighting, not by re-simulating.**
Multiply each row's weight by `2p` where `latent:pushover_to_surface = 1`, by `2(1-p)` where it is 0,
and by 1 where `latent:pushover_drawn = 0`. Report **p = 0.5 as primary with p = 0 and p = 1 beside
it**, each carrying its own effective sample size: on one stratum the effective sample falls to 0.63x
at p = 0 and 0.61x at p = 1. The share of weight in the detectable 10-45 degree band runs 0.037 at
p = 0, 0.164 at p = 0.5 and 0.291 at p = 1, so **no detectability statement may be made at a single
value of p**.

**Receiver geometry for the Kadri locality** (source 26.2 S, 101.9 E — re-derive the crossing with
the module's own arc definition, not a fit to the impact cloud): H01W 1,520 km, Perth Canyon
1,422 km, H08S 3,730 km. Blocked and carrying no information: **Portland** (land, for any source
north of 28.765 S), **Scott Reef** (North West Shelf), **H08N** (Chagos Bank).

**Timing uncertainty.** Because the source time is inferred from the H01W reception, the group-speed
error enters only through the range difference: `t_rx = t_H01W + (d_rx - d_H01W)/c`. Terms: bearing
+/-1.0 deg gives +/-9 s at H08S and +/-4 s at Perth Canyon; group speed 1.48 +/- 0.015 km/s gives
+/-15 s and +/-1 s; pick allowance 5 s. Combined 1 sigma: **18 s at H08S, 6 s at Perth Canyon**. With
a pessimistic +/-3.3 deg bearing: 33 s and 14 s.

**p-value floor.** The null holds n_B = 98 background realisations, so the smallest resolvable
p is 1/99 = 0.0101. **Retire the 0.005 "strict" tier** — that null cannot resolve it.

**Kadri cannot share raw IMS data** under his access terms (Pete, 11 Oct;
`kadri-collaboration-package-outline-v0.md`). The analysis goes to the data: we send hypotheses,
predictions and code, he runs them and returns derived products. **Nothing in this order waits on
raw data.**

---

## Task 1 (first, and gating). Smoke-scale test of both Kadri time options on data we hold.

Kadri's main signal carries bearing 306.18 deg from Cape Leeuwin, and his paper gives two times for
it: **00:52:03 in the text and 00:54:30 in the caption**. Implied source times 00:34:55 and 00:37:22.

### 1.1 Pre-register first. Commit before any statistic is computed.
- New pair span **1,346 to 1,710 s**, which covers arc latitudes 28.9 S to 22.0 S and joins the
  existing 856-1,347 s span with no gap. This is a new look-elsewhere family; do not fold it into the
  existing pair test.
- Windows, at 95 per cent, both options:

| | Perth Canyon 3315/3376 | H08S |
|---|---|---|
| text, 00:52:03 | 00:50:44 - 00:51:10 | 01:16:19 - 01:17:33 |
| caption, 00:54:30 | 00:53:11 - 00:53:37 | 01:18:46 - 01:20:00 — **not testable**, the digitised record ends 01:18:29 |

- Statistics: shot energy, inter-shot gap power, shape correlation against a local stacked shot
  template, windowed residuals on the leading and trailing shoulders, and a principal-component
  outlier score. Excess is primary and deficits secondary.
- Tiers: screen 0.3, mark 0.1, report 0.05, floor 0.0101 stated on every table.
- Null: the 98 existing background realisations. No new background read.

### 1.2 Plot the digitised H08S trace.
Across **01:16:20 to 01:17:10** (the predicted window) and **01:11:30 to 01:14:10** (the only four
flagged outliers in the record). Architecture holds per-cycle summaries only; the raw digitised
series is in the module's own checkout.

### 1.3 Run the tests.
Perth Canyon over both windows; H08S over the text window only. Report p, signal-to-noise ratio and
likelihood ratio for every candidate, at p = 0.5, 0 and 1.

### 1.4 Known state — do not re-discover, and do not over-read.
- Perth Canyon has **already been examined for both options** on shot energy: logger 3376 recorded
  186.0 s and 154.2 s of the two windows with best p 0.749 and 0.709 at 7.7-8.7 dB; logger 3315 had
  zero coverage in both. **The new work is the template and shoulder statistics, not another energy
  test.**
- The four flagged outliers in the whole digitised H08S record sit at 01:11:39 (z = -4.17, the only
  one also coincident under the strict condition), 01:12:49 (+4.11), 01:13:09 (-4.91) and
  01:13:59 (-3.16).
- A gap-power excursion of +2.07 sd sits at 01:16:47, 7 s before the text-option prediction. It is
  **not evidence**: 1 of 107 cycles exceeds +2 sd where 2.4 are expected, the module's own gap test
  found zero outliers at strict and loose, and it was found after the fact. Treat it as a
  pre-registered target now, not as a result.

**Acceptance.** A committed pre-registration, the two trace plots, a candidate table with p and
likelihood ratio per statistic per station per option at three values of p, and one paragraph saying
plainly what is and is not testable on the data we hold.
**Compute.** Under one hour. No heavy lock.
**Stop and report if** the template or shoulder statistic cannot be computed on the digitised trace
at the required time resolution. Do not substitute a coarser statistic silently.

---

## Task 2. Option B, the main predictive and power pass, on run I dive.

Steps 1 to 11 of the module's own plan as revised: restore; predicted spectra and arrival times for
all stations by family and 00:19 option; pre-registration; screen before scanning; IMOS scan in the
predicted windows at every unblocked logger; digitised Cape Leeuwin and Diego Garcia South scans;
multi-site coincidence with information gain; injection-recovery for detection probability, 95 per
cent upper limits and Bayes factors; the coverage table; the updated air9 chart; one multi-panel
figure.

**Selection rule, revised.** Select on **predicted signal-to-noise at the best unblocked receiver**,
not on source loudness. Keep everything within about 10 dB of the noise at any receiver; drop only
what is far below the noise everywhere. Do not cut on the loud decile.

**Heavy lock is available — Pete has paused drift and overrides the lock allowance for this run.**

**Acceptance.** The three statements the module exists to make: prediction, power, coverage. Power
reported as a curve with the 95 per cent upper limit marked, and as information in bits, at p = 0.5,
0 and 1. The coverage table must name every receiver that carries no information and why.
**Compute.** Two and a half to three and a half hours.
**Stop and report if** injection-recovery cannot span the coupling-efficiency prior. A recovery run
at one assumed efficiency does not establish the gate.

---

## Task 3. Prepare the Kadri package. Do not send it.

Update `kadri-collaboration-package-outline-v0.md` with the worked results of Tasks 1 and 2, and add
the northern-bearing conditional as its own hypothesis with: the arrival windows at all three
unblocked receivers, the uncertainty budget above, the statistics, and the request that he run the
**caption-time H08S window (01:18:46 - 01:20:00)** which we cannot reach. Ask which of his two times
is correct. Pete approves before anything is sent.

---

## Caveat wording — use verbatim, do not paraphrase

- Peak radiated mechanical power is not an acoustic source level; the coupling is a declared
  alternative with a prior, not a constant.
- The propagation model passes a level check against the 2001 airguns and fails a frequency-slope
  check by +10 dB per octave at Cape Leeuwin and +7 at Diego Garcia South; the airgun data cannot
  separate the source spectrum, the array pattern and the propagation.
- Detection probability is measured in IMOS logger noise and shifted by +4.8 dB to stand in for a
  three-element IMS station. It is a proxy.
- In the predicted windows no transient exceeded the pre-registered false-alarm level; the smallest
  resolvable p is 0.0101. That is no significant detection with limited power, not an absence.
- Module likelihood remains zero until injection-recovery gives detection probability against
  received level.

---

## Out of scope for this thread

Three-dimensional propagation across the ridge; a separate acoustic-gravity forward model; the 2003
SUS absolute-level check; any re-run of end-of-flight; any change to `crates/ocean`.

## Housekeeping

If `threads/run-state/hydroacoustics-RUN-STATE.md` does not exist, writing it is the first
deliverable of this thread, to the template in `thread-and-module-operating-guide.md` Appendix A.
Post results to `coordination/architecture.md` as usual. One thread, one run, one results note, one
commit.
