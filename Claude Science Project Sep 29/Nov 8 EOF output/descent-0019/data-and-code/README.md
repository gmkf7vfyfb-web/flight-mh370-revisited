# 00:19 descent-rate comparison: chart data package (9 Nov 2026)

Rebuilds all seven candidate Journal of Navigation figures (A1-A4, B1-B3) without the project code base.

    python descent0019_charts.py <this folder> <output folder>

Requires Python 3 with numpy, pandas, scipy, matplotlib and pillow. Run time is about 50 s.
Outputs: per figure <name>-word.png (600 dpi), <name>.pdf, <name>-proof.png, <name>-caption.txt and <name>-working.png; plus plotted-numbers.csv and band-polygons.csv.

## Files and columns

descent-rate-profiles.csv - descent-rate time series used to build every area and the conditional cut.
  case: flight or 'Boeing 777 simulation N'; group: push-over, roll-off/upset, boeing-alternate, boeing-normal;
  time_s: s from the time origin; descent_rate_fpm: ft/min, positive downward; time_origin: event at t = 0 (Boeing: power loss,
  i.e. the first flame-out in the alternate electrical configuration and the second flame-out in the normal configuration);
  profile_kind: recon (EgyptAir 990 point-mass reconstruction from reported load factor), const (constant acceleration from report
  values: Atlas Air 3591, SilkAir 185, TWA 841 and Lauda Air 004, the last two lower bounds), piecewise/digitised/integrated
  (from report figures), sim (Boeing 2016 end-of-flight simulations, vertical speed by differentiating smoothed altitude).
steady-descent-cases.csv - the 9 steady descents and stalls: case_number, case, rate_source, intent,
  steady_rate_low_fpm, steady_rate_high_fpm (ft/min; equal values = a single mean rate).
boeing-end-of-flight-runs-table.csv - the Boeing simulation table (configuration, flame-out times in s, other run facts as published).
eof-0019-bfo-evidence.csv - final end-of-flight run, 7 Nov 2026. ln Z (natural log evidence) per route model and treatment;
  'ln Z minus as-recorded' and 'ln Z relative to first treatment of the same group' (with 90 % interval over seeds) are ln B against
  the 00:19 BFOs as observed; posterior probabilities under three priors. Codes: D9 BFOs as observed; D10 Holland transient bias added
  to both BFOs (17 Hz floor); D14 the same with zero floor; D11 bias added to the 00:19:37 BFO only (17 Hz floor); D12 the same with
  zero floor. The source file says 'as recorded'; the figures use 'as observed' (same data).
eof-treatments-ess.csv - effective sample size (ess, overall and per family) and the provisional flag (no-pilot ESS < 500)
  for D7 (both BTOs, no BFO), D8 (00:19:29 BFO only), D9, D10, D11, D12, D14, both route models.
bfo-1825-treatment-test.csv - test of each BFO treatment at the 18:25 log-on: ln p for BFO sd 4.32 Hz and 7 Hz, and a reading.
  Residuals are against the settled level from the 18:28 bursts.
posterior-descent-pairs-davey-fuel.npz - final-run descent rates (ft/min, positive downward) at 00:19:29 (rate_001929_fpm) and
  00:19:37 (rate_001937_fpm), family (1 no pilot, 2 piloted) and normalised weights w_D7 ... w_D11 (Davey model with fuel).
  Rows are a thinned subset: rows with negligible weight in every treatment (below 1e-12 of the maximum) are removed. Weighted
  quantiles are unchanged, but the effective sample sizes must be taken from eof-treatments-ess.csv, not from these weights.
descent0019_charts.py - the plotting script (all constants are at the top: implied points, log-on window 67-198 s, line weights).
figures/plotted-numbers.csv - every number drawn: figure, element, series and value columns (rates in ft/min unless the column
  says kfpm = 1000 ft/min; acceleration in g = 32.174 ft/s^2; lnB in nat).
figures/band-polygons.csv - the areas as plotted: plane (rate-rate or rate-acceleration), group (P push-overs, R roll-offs/upsets,
  A Boeing alternate, N Boeing normal, W Boeing build-ups inside the log-on window), segment, first_instant_rate_kfpm (bin centre,
  750 ft/min bins), low, high (rate 8 s later in kfpm, or acceleration in g).

## Method (as in the chosen chart, lineage 1ffdc3eb)
Build-up limbs: rising parts of each profile that gain at least 1,500 ft/min between a local minimum and maximum (0.25 s grid,
9-point running mean, extrema order 12). Pairs: (rate at t, rate at t + 8 s) every 0.25 s with both instants on the limb.
Areas: minimum and maximum of the 8-s-later rate in 750 ft/min bins of the first-instant rate, smoothed over three bins.
Implied points: 00:19 BFOs as observed 4,350 -> 14,860 ft/min; Holland transient bias added (published point) 8,590 -> 18,830 ft/min.
Posterior ranges: weighted 5-95 % quantiles from the npz. Comparison rule: ln Z is compared only among D9, D10, D11 (same data).
