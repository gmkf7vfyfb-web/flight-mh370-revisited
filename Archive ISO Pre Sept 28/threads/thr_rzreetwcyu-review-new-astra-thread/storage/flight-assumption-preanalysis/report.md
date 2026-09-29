# Flight-assumption pre-analysis

**The one-turn restriction can hide a much wider feasible set.** Verified examples in this bounded probe terminate from approximately 37°S to 15°S at 00:11. The extreme examples are 1652 nautical miles apart by great-circle distance; the along-arc span is longer. These are demonstrated examples under declared models, not outer bounds, a credible interval, a density estimate, or a search recommendation.

[Comparison and trajectory plots](flight-assumption-preanalysis.pdf) · [Machine-readable summary](summary.json) · [Run provenance](run-manifest.json)

| Allowed target changes after 18:25 | Demonstrated endpoint range in this probe |
| --- | --- |
| 1 direction change | 36.2°S to 35.3°S |
| 2 direction changes | 36.9°S to 34.2°S |
| 4 direction changes | 37.2°S to 34.2°S |
| 8 direction changes | 37.2°S to 15.1°S |
| 16 direction changes | 37.5°S to 15.1°S |
| 8 direction + up to 2 speed/altitude | 37.2°S to 15.1°S |
| 8 direction + up to 4 speed/altitude | 37.4°S to 15.1°S |
| 8 direction + up to 8 speed/altitude | 37.4°S to 15.1°S |

Ranges include examples from smaller allowances; a trajectory with fewer commands remains admissible when the allowance increases. They are spans between found examples, not a claim that every intervening point has been established. Decimal degrees document the calculation rather than confidence in a boundary. Counts are commanded settings, not a judgement about pilot intent. Some are small corrections or changes of navigation mode.

The main sweep compared 1/2/4/8/16 direction settings, then allowed 2/4/8 speed and altitude target changes separately from direction. Follow-up searches stepped along the arc, removed commands from successful paths, tried all five fixed navigation modes, and used fixed fuel-flow multipliers 0.9 and 1.1 as separate alternatives. Separate speed-only and altitude-only checks were also run. Six structured holding-command probes did not meet all conditions; this limited result does not exclude holding patterns. The northern examples could be reduced to six direction settings while retaining constant cruise targets.

The first coarse sweep appeared to leave gaps and to stop around 20°S. Following successful paths to nearby endpoints found additional examples towards 15°S, including eight-command paths. This shows that apparent gaps and apparent turn-count advantages can be failures of the search. The modest extra span found with 16 settings does not certify saturation at eight. No maximum possible extent X or model-weighted conditional width Y has yet been established.

## Descriptive simplicity measures

| Example endpoint | Direction settings | Mode switches | Sampled total heading change | Climb / descent (ft) |
| --- | ---: | ---: | ---: | ---: |
| 36°S | 1 | 0 | 130° | 0 / 0 |
| 30°S | 8 | 3 | 581° | 0 / 0 |
| 15°S | 6 | 3 | 529° | 0 / 0 |

These measures have no assigned probability weight. Total heading change includes the effects of winds and navigation geometry; it is not a count of deliberate turns. Cruise adjustments remain separate. The full vector, including Mach variation, is saved in the summary.

## What was assumed

- The likelihood uses the ten existing observation epochs from 18:25 through 00:11, including the existing C-channel averages. The first 18:25 BFO is absent. BTO deviations are 29 microseconds, except 43 microseconds for the anomalous 18:25 observation. BFO deviation is 7 Hz, with one shared uncertain bias (existing prior mean 150 Hz and standard deviation 25 Hz).
- The optimizer uses endpoint-target and nominal fuel-time residuals to guide its search (0.2 degrees and 90 seconds as numerical scales). These guidance choices affect search efficiency and which examples are found; they are not additional observations or probability weights in a reported PDF.
- A diagnostic fit screen requires every BTO residual and every BFO residual after the shared-bias fit to be within three declared standard deviations, and the joint standardized squared error to be at most 38. This is a declared screening convention, not a calibrated confidence level. No independent offset is fitted to each BFO.
- Trajectories start from the existing 18:01:49 radar prior. Its position and direction vary within three prior standard deviations. Before 18:25, each trial retains its initial navigation mode and cruise targets; that earlier flying behaviour has not been broadly searched here. Initial Mach is 0.73–0.84 and altitude 25,000–43,000 ft; initial vertical speed is zero.
- After 18:25, command times are continuous. All five existing navigation modes are available in tested schedules. Speed targets may range from Mach 0.3 to 0.87 and altitude targets from 500 to 43,000 ft, subject to the canonical lift, speed, bank, roll, acceleration, climb, thrust and drag checks. The finite mode schedules are not an exhaustive mode-sequence enumeration.
- ERA5 and IGRF inputs are fixed at the configured reconstructions. Public aerodynamic/thrust proxies and the declared fuel extension are conditional models, not a calibrated Boeing performance deck. The main matrix holds the fuel-flow multiplier at 1.0; 0.9 and 1.1 are sensitivity alternatives.
- Fuel uses the existing calculated 18:28 anchor of about 33.5 tonnes and symmetric engine feed/flow. This anchor is calculated, not a direct onboard measurement. Direction changes, climbs, speed and declining mass feed into the actual trajectory calculation.
- The later restart is conditioned through positive exhaustion-to-logon delay windows of 60–180 seconds and 30–300 seconds, relative to 00:19:29.416. Both windows are analyst sensitivity choices. They are not empirical timing confidence intervals. The nominal 00:17:30 comes from the approximate APU/SDU sequence in [ATSB's 2015 report](https://www.atsb.gov.au/sites/default/files/2022-12/AE-2014-054_MH370-Definition%20of%20Underwater%20Search%20Areas_3Dec2015.pdf#page=14). Applying this later condition changes what is inferred about 00:11.
- Ocean drift, Pléiades, antenna gain, hydroacoustics and search non-detection are disabled. No end-of-flight or impact location is inferred. Missing search witnesses remain unresolved.

## Verification and time

The searches completed 538 optimization profiles and approximately 202,959 canonical trajectory evaluations. Summed elapsed time for the search batches and verification was 8.4 minutes, with up to four search workers. Recorded child CPU time for the searches was 20.0 CPU-minutes. The largest individual replay process used about 649 MiB; four concurrent replay processes required approximately four times that amount. Build and engineering time are additional.

All 158 candidate witnesses passed replays at the original integration steps, half steps and quarter steps. The largest coarse-to-quarter endpoint shift was 3.71 NM and the largest exhaustion-time shift was 3.9 seconds. Figures use the fine replay. The original run also has a separately implemented SATCOM comparison in `independent-satcom-check.json`; this external audit is additional to the reproducible runner checks. These checks do not validate the unknown behavioural prior or certify aircraft performance outside the source models.

The pre-analysis exposed an existing exact fuel-boundary continuation error on some changing-flight paths. This probe instead uses the canonical ordinary fuel integration with continuation steps of at most 10 seconds, stopping at the first recorded exhaustion event; refinement reaches 2.5 seconds. No post-exhaustion location is used. The exact-boundary routine must be repaired and checked before the terminal estimator is commissioned.

## Implementation recommendation

Use eight direction changes as the initial working representation and retain sixteen as a required sensitivity comparison. Keep cruise adjustment allowances separate: start with four speed and four altitude target changes and test eight of each. These are computational starting points, not assertions about pilot behaviour. Report the number and total amount of turning, speed adjustment and climb/descent separately; an operationally simple step-climb policy must not be penalized as though it were erratic flying. A scalar preference for simplicity remains an explicit behavioural prior.

A stable PDF is still unproved. The next bounded task is to demonstrate recovery and stable probabilities on known-flight and synthetic controls with this representation, while fixing the fuel-boundary defect. Finding trajectories cheaply does not establish their relative probability. The 30-minute pre-analysis allowance was respected; the earlier two-hour estimator feasibility limit remains in force.

## Reproduction

Use Python with NumPy, SciPy and Matplotlib installed; exact versions and input/code hashes are in the manifest. From the project root, this command runs the bounded search and witness verification into an empty directory:

```bash
python crates/controls/flight_assumptions.py --output /absolute/path/to/empty-output
```

The control builds the central runner, calls its `replay-flight-trajectory` command and stops numerical requests after 30 minutes. Generate the plots and this report from its artifacts:

```bash
python crates/reporting/scripts/flight_assumption_report.py /absolute/path/to/output
```

To check saved witnesses without repeating optimization, use `--verify-existing` with the control command. The original search used the same replay implementation in an isolated temporary harness; all retained geographic witnesses were subsequently reproduced through the integrated central runner. No product scientific equations were replaced by the optimizer.
