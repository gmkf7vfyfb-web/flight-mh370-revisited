# IGOGU FIR-intercept and waypoint follow-up

19 September 2026. This package extends the preserved IGOGU work; it does not
replace its posterior, priors or raw samples. Read the four-page report
`output/mh370_IGOGU_FIR_and_waypoints.pdf` and the handoff START_HERE first.

## What this package contains

1. A finite turn begun on N571 before IGOGU, solved to roll out on longitude
   94 degrees 25 minutes east with a true ground course of 180  degrees.
2. Thirty-five early-flight sensitivity/optimization cases. Twenty-seven vary
   nominal unturned IGOGU ETA (18:36,18:38,18:40), altitude (31,35,37kft), and
   initial Mach (.76,.82,.85); eight turn at the 6N FIR corner. All use 22.5 degrees
   commanded-bank parameter under the inherited conservative turn-rate rule.
3. Later continuation and rejection tests, four failed unrestricted Gaussian
   local fits, one gate-passing full-flight example, its refined verification,
   and three unsuccessful smoother-speed local searches. These are examples,
   NOT a Bayesian sample, model evidence calculation, or a new PDF.
4. A 1276-point official published waypoint catalog, a broad weighted screen,
   and exact proximity sums for ten points over all 1,710,701 prior survivors.
5. Source bytes, code, figures, numeric results, failure records and numerical
   QA. No original input or sampler source was modified.

## Model boundary and meaning

- The old conditional model requires actual passage through IGOGU. This new
  model replaces that with an N571 approach and an anticipated FIR interception.
- The old 18:36-18:40 IGOGU arrival interval becomes a NOMINAL UNTURNED arrival
  time. It is not an observed passage time. Approach transit uses frozen initial
  Mach and three-point Gauss quadrature with ERA5 wind; flight-altitude versus
  surface-geodesic length is included approximately. The radar prefix is not
  independently re-fitted here.
- The finite first turn is solved for start distance and commanded turn angle
  so its endpoint is on the meridian with true ground track180 degrees. Ground
  track, not magnetic or air heading, is constrained. Wind crab is allowed.
- The FIR boundary extends south only to 6N, then east. The free later-turn
  example continues south on the MERIDIAN EXTENSION below 6N.
- Early studies are level through 19:41; they use the inherited temperature,
  wind, pressure/altitude proxy, turn-rate ramps, satellite model and aircraft
  performance checks. Early mass starts from midpoint 33524.10488196kg at the
  original 18:28:05.904 fuel anchor and is propagated forward.
- The whole-flight example is FL350 throughout. Fuel exhaustion is fixed to
  the prior mode 00:17:30 and flow scale solved within [.9,1.1], with original
  anchor range [32524.10488196,34524.10488196]kg and no jettison. This is a
  public-data fuel/performance sensitivity, not validated manufacturer data.
- The original BTO ±58 us and every-burst BFO ±8.6 Hz gates remain. Gaussian
  likelihood scales were 29 us and 4.3 Hz. Call likelihoods use their means, not
  independent repetitions; every burst is still a hard check.
- R600 is a separate diagnostic: 00:19:29.416,23000-4600=18400us, sigma 63 us,
  gate ±126 us. Last horizontal velocity is continued kinematically at constant
  altitude. No 00:19 BFO, glide dynamics or impact PDF is introduced.
- The passing example needs Mach jumps of 5-8 original prior standard deviations.
  Its existence is not evidence that it has appreciable integrated probability.
  Failed smoother local searches do not prove that smoother solutions do not exist.

## Dependencies and replay

Extract all five archives specified by the master handoff manifest into one
directory. Keep these siblings:

```
mh370_igogu_conditional/
igogu_followup/
igogu_fir_followup/
```

An original workspace may use `igogu_conditional/` instead of
`mh370_igogu_conditional/`; the loaders support both. The first original archive
contains the real weather bytes. Do not recreate the old ephemeral weather
symlink. Python 3.12, g++ with C++17/OpenMP, numpy, scipy, pandas, pyproj,
matplotlib, reportlab and PyMuPDF are used. Exact environment versions are in
`handoff/environment.json`. C++ libraries compile automatically into`code/`.

From the common extraction directory:

```bash
OPENBLAS_NUM_THREADS=1 python igogu_fir_followup/code/build_waypoint_catalog.py
OPENBLAS_NUM_THREADS=1 python igogu_fir_followup/code/fit_prefix.py
OPENBLAS_NUM_THREADS=1 python igogu_fir_followup/code/full_continuation.py
OPENBLAS_NUM_THREADS=1 python igogu_fir_followup/code/fit_later_example.py
OPENBLAS_NUM_THREADS=1 python igogu_fir_followup/code/fit_later_gates.py
OPENBLAS_NUM_THREADS=1 python igogu_fir_followup/code/validate_fits.py
OPENBLAS_NUM_THREADS=1 python igogu_fir_followup/code/waypoint_audit.py
OPENBLAS_NUM_THREADS=1 python igogu_fir_followup/code/waypoint_exact_shortlist.py
OPENBLAS_NUM_THREADS=1 python igogu_fir_followup/code/validate_waypoints.py
OPENBLAS_NUM_THREADS=1 python igogu_fir_followup/code/make_report.py
```

`fit_smoother_example.py` reproduces the additional unsuccessful local searches;
it is not needed for the principal results. `waypoint_summary.py` regenerates
the broad summary from its saved measure without rerunning dynamics. Exact
shortlist cells are checkpoints: remove or move them to deliberately replay
from scratch. Do not interpret an old checkpoint as a fresh run.

## Machine-readable schemas

- `early_turn_fit_grid.csv/json`: every example, input controls, start/rollout/
  second-turn/arc coordinates and times, residuals and pass/fail flags.
- `early_turn_fits.npz`: physical parameters(N,26), initial state/horizon(N,6),
  observation states(N,85,8). Parameters follow the original model schema.
  `q=[start_lat_rad,start_lon_rad,start_course_rad,first_angle_rad,anchor_fuel_kg,horizon_s]`.
- All clocks ending`_s` are seconds after 2014-03-07T18:22:12UTC(T0=1394216532).
- Observation-state columns: latitude_deg,longitude_deg,height_m,GS_m_s,
  true_course_rad,vertical_speed_m_s,predicted_BTO_us,predicted_BFO_hz.
- Path columns: time_s,latitude_deg,longitude_deg,height_m,GS_m_s,
  true_course_rad,vertical_speed_m_s. Early arrays have zeros for observations
  after the 19:41 horizon; they must not be scored as predictions.
- Full-flight parameter arrays append to the original26 values:
  start_lat_rad,start_lon_rad,start_course_rad,first_command_angle_rad.
- `unturned_later_continuation.csv`: no-further-turn failures, including fuel
  rejection. Missing observation fields indicate a pre-observation model gate.
- `later_gate_fit_fine.npz`: authoritative passing example,5-second integration,
  complete path to exhaustion, parameters, values and all 85 observation states.
- `waypoint_resample_measure.npz`: raw survivor indices, multiplicities for
  original/R600 measures, distances(N,1276), closest times, components and names.
  Distances beyond 100 NM are censored at999. These counts are not independent
  physical-trajectory ESS. Seeds 20260919400/401, 131072 draws per measure.
- `waypoint_exact_cells/*.npz`: exact weighted proximity sums for each original
  replicate/turn-count/altitude cell. Histograms have 0.01 NM bins; exact 5/10/20 NM
  gates and 0.1 NM boundary bands are accumulated before binning.
- `waypoint_exact_shortlist.csv`: final exact fractions and binned medians for
  ten points. Small values printed as0.00% in the report can be nonzero.
- `qa/waypoint_validation.json`: independent WGS84 nearest-segment comparison.
- `qa/fit_numerical_validation.json`: integration-refinement and R600 checks.
- `history/` and`qa/development_failures.json`: superseded and rejected attempts;
  never use them as current results. Rejected optimizer trials stay in`output/`.

## Geographic provenance limits

The baseline retains the historical Malaysian AIP coordinates. New official
India, Indonesia and Australian lists are later editions; publication links,
bytes and source references are supplied. ICAO's August 2010 RASMAG/13 IP/09,
PDF pages 31 and 38, independently documents the BULVA name on M300. It does not
establish the exact March 2014 coordinates. Complete 2014 catalog validity and
chance-association controls remain pending. No waypoint was added as evidence.

## Next scientific work

1. Declare a proper prior over anticipated turn start and nominal ETA; account
   for the induced interception constraint/Jacobian before new Bayesian sampling.
2. Run the entire 0-4-extra-turn,50/50 altitude-class mixture under that new model,
   retaining model-specific evidence denominators and multiple independent runs.
3. Diagnose the strong late-call BFO/speed restriction rather than promoting
   a gate-hugging optimized example to a high-probability route.
4. Verify historical waypoints and assess coincidences with an appropriate
   geographic/control catalog, accounting for correlated route points.
5. Keep original, R600 sensitivity, Pléiades overlay and any terminal/impact
   model distinct until a justified joint likelihood exists.
