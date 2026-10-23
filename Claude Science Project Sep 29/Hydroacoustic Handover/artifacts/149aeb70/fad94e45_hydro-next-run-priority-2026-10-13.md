# Hydroacoustics: priority review of the 14-item plan
Reviewed 13 Oct 2026, against the module's own plan and estimates posted in the hydroacoustic thread (frame d74bf70e, message 3397).

## 1. What the next run must produce

The module likelihood stays at zero until detectability is shown, and the paper labels hydroacoustics predictive-only. The next run is therefore not trying to find a signal. It is trying to produce three defensible statements about run I:

1. **Prediction.** What each station should have received from the run I impact set: arrival time windows, levels, spectra.
2. **Power.** For each station, whether a predicted signal would have been detectable at all. This converts a non-detection into either a quantified rejection with a 95% upper limit, or an explicit "carries no information" row.
3. **Coverage.** What was tested, what could not be tested, and why.

Every item in the plan is scored below against those three. Items that do not serve them are deferred, whatever their intrinsic interest.

## 2. Changes to the plan

**M1. Merge item 13 into item 3.** The run I search windows for the new 00:19 options come out of the same forward pass as the predicted arrivals. Running them as a separate item pays the setup twice. Saves 10-15 min compute and about 45 min development.

**M2 (revised 13 Oct, after measurement). Carry all nine 00:19 options. The exclusion is lifted.**
My first version of this item said to spend nothing on the two Holland-reading options because they
had been recorded as not estimable. That was read from the earlier core (b) and reference-289 runs
and it is wrong for run I. Measured on run I, `both/no-offset` has 5,304 effective parents and
`both/startup-offset` has 20,749, against a threshold of 1,000. Both are estimable and both get the
full treatment. Two depth limits are declared instead: in the loud decile `both/no-offset` has 746
effective parents, below the 1,000 threshold, so it is not estimable at that depth; and at the top
percentile neither of the two is estimable.
Figures and numbers are in `run-i-loud-tail-estimability.md`.

**M2a. The loud impacts are well sampled, so the detectability work is not starved.** The loud decile
holds 3.0 million effective impacts under the 00:19-held-out baseline, and at least 746 effective
parents under every option. The loudest impacts are not concentrated in the two options that were
being excluded: those two put about 0.029 of their probability in the loud decile against 0.100 for
the baseline, while r600/startup-offset puts 0.133 and the r1200 options 0.121 to 0.123 there.

**M3. Screen before scanning: run a power screen ahead of item 6, not after it.** The order in the plan commits about 14 GB of background reads before anything says which loggers can inform. Predicted level from item 3 against the already-measured detection thresholds is nearly free. Loggers whose predicted level sits below threshold become "no information" rows by the same logic already used for the Chagos Bank blocking to H08N. Only the surviving loggers get the full 14-day background null. On present indications this cuts item 6 materially, and it also tells you how much of item 9 is worth running.

**M4. One multi-panel figure, not nine per-station charts.** Nine charts cost render-and-inspect cycles for output the paper cannot carry. One panel figure covering the stations that survive the screen, plus the coverage table, is the publishable form.

**M5. Defer item 12, the 2003 SUS shots.** It is about an hour under the heavy lock, it is the one estimate with no measured basis, and its outcome cannot lift the gate inside this run. It also stands directly in front of the GLORYS12 drift pilot you approved for after run I.

**M6 (revised). Item 2 is already delivered; no request is needed.** End of flight wrote the
energy-transfer sidecar `tau90_v1.npz` on 13 Oct at 08:36 and it is present in all 32 run I seed
directories, carrying `tau90_s`, `t05_s`, `t95_s`, `peak_rate_w`, `energy_transferred_j`, `decel_g`
and `l_eff_m` (method 1, note `results/eof-impact-tau-method-oct11.md`). The module looked at the
`latent:` columns inside `impacts32.npy`, which are NaN in every row, and concluded the quantity was
missing. It should read the sidecar instead. This removes the only external dependency in the plan.

**M7. Keep item 5, the pre-registration, exactly where it is.** It costs no compute and it is what makes the rest admissible. Commit it before any test touches run I.

**M8. Carry the calibration caveat on every number.** The propagation model fails the frequency-slope check against the 2001 airguns by +10 dB/octave at Cape Leeuwin and +7 dB/octave at Diego Garcia South, and the detection probability is a proxy: real transients injected into an IMOS logger's noise, shifted by +4.8 dB to stand in for a three-element IMS station. Every rejection, upper limit and Bayes factor is conditional on both. The wording used for the IMOS result should stay as the module corrected it: no transient exceeded the pre-registered false-alarm level, with the smallest attainable p about 0.02-0.04, which is no significant detection with limited power, not an absence of signal.

**M9. Do not tighten the false-alarm level from 0.05 to 0.01.** Tightening it raises the detection
threshold, moves the detectability envelope away from the noise, lowers the power at a given source
level, and makes the upper limit weaker. It is also not attainable with the background now held: the
smallest p the background sample can resolve is about 1/n_B, which is 0.02 to 0.04, so 0.01 cannot be
reached without roughly tripling the background read. The module's deliverables are the power curve,
the 95% upper limit and the Bayes factor, none of which need a threshold at all. Report both the 0.05
and the 0.01 rows in the coverage table, which is free from the same scan, and get sensitivity from
matched filtering and from multi-site coincidence instead, since coincidence lets each site keep a
loose threshold while the joint false-alarm rate stays controlled.

## 3. Options for the next run

Compute time is machine time. Wall-clock includes the module's own development time, with overlap where the plan allows it.

**Option S, a smoke run, 15 to 25 minutes, no heavy lock.** Added at your request. It exercises every
code path end to end and produces no evidential number and no likelihood. Sparse on both sides: the
source side uses the agreed grid-as-cache design, about 0.5 degree cells along the arc crossed with a
few bins of peak radiated power and tau90, so propagation is solved a few hundred times rather than
100 million; within that, a weight-stratified draw of 20,000 to 50,000 impacts from the loud decile,
which holds 3.0 million effective impacts and so loses nothing at smoke depth. The data side uses one
logger and two days of background rather than five loggers and fourteen days, one band, one template,
predicted windows only. Injection-recovery uses three source levels at one station, which is enough
to locate the 50% and 95% crossings. It must be labelled a smoke run in the commit and the note: a
smoke run that writes output through the normal path looks like a result and is not one.

| | Option A: predictive pass and power screen | Option B (recommended): A plus the quantified non-detection | Option C: the full plan |
|---|---|---|---|
| Items | 1, 2, 3+13, 5, 6 (screened), 7, 10 | A plus 8, 9, 11, one figure | B plus 4 (full charts), 12 |
| Compute | 50 min - 1 h 20 | 2 h 20 - 3 h 25 | 3 h 30 - 4 h 30 |
| Of which heavy lock | 10 - 25 min | 1 h 10 - 2 h 25 | 2 h - 3 h 30 |
| Wall-clock | 4 - 5 h | 8 - 10 h | 11 - 14 h |
| Delivers | Run I predicted arrivals, windows and levels for the estimable 00:19 options; digitised Cape Leeuwin and Diego Garcia South traces re-tested on run I; IMOS scan where power exists; coverage table | A plus detection power, 95% upper limits on coupled source level, Bayes factors for signal-as-predicted against noise-only, multi-site coincidence with information gain, updated airgun chart | B plus per-station charts and the SUS calibration check |
| Does not deliver | Any quantified statement about what a non-detection rules out | The SUS calibration check; the 3-D ridge and acoustic-gravity gaps stay declared, not closed | The two declared model-reach gaps still stay open |
| Effect on the drift pilot | None worth noting | Drift's GLORYS12 pilot starts about 2 h later | Drift's pilot slips most of a working day |

**Recommendation: Option B.** Option A alone leaves hydroacoustics where it already is, predictive with an untested gate, and the paper gets no number from it. Option B is the smallest set that produces the module's actual paper content: a prediction, a measured power, and an upper limit, each with its caveat attached. Option C buys one calibration check of uncertain duration that cannot change the verdict this run.

## 4. Holding token use down

Tool calls dominate token spend, so the savings are in run shape, not in writing less.

- One script per stage, invoked once, logging to file and printing a short summary table. No per-station narration.
- Long jobs as a single background run with one completion wake, not periodic checks.
- Re-use the existing scan and injection code paths. The only new code is the forward pass over run I and the screen.
- One pre-registration document and one results note. The coverage table is an artifact, not prose.
- The figure is rendered once and inspected once.

## 5. What needs your decision

1. Option A, B or C.
2. Lock order between hydroacoustics and the GLORYS12 drift pilot.
3. Whether item 12 is deferred to its own slot or dropped for this cycle.
