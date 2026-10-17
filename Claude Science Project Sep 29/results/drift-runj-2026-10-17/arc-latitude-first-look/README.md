# Arc-latitude first look: debris evidence along the 7th arc (17 Oct 2026)

Post hoc sensitivity from EXISTING drift data only; no new transport. Requested by Pete (arc-latitude scan, first pass).

Inputs: run A finds surfaces (runA-rebuilt, both models, h50); 15-160 E Australian pilot node tables (178 nodes, both models);
run J D0 impact histogram (end-of-flight/run-j/summary/run-j-maps-accumulators.npz, H_D0_all; mean latitude -36.717, equal to aus160-both.json).
Validation: this histogram-level composition reproduces aus160-both.json D0 mean shifts (finds only +0.698 vs +0.696; B +4.828 vs +4.813;
populated only +4.451 vs +4.439; per model within 0.02 deg). Saturating-law fits reproduce k,c = 5.475,0.388 (GLORYS12) and 4.597,0.366 (GlobCurrent).

Pete's proposed detection levels (absolute 0.65/0.5/0.2/0.05/0 for ABS Major Cities/Inner Regional/Outer Regional/Remote/Very Remote),
converted to relative levels with anchor 'find coasts at peak awareness = 0.65' (1/0.77/0.31/0.077/0), and anchors 1.0 and 0.4 as sensitivities.
The pilot segments merge Major Cities+Inner Regional and Remote+Very Remote, so each scheme is bracketed (low end / high end of each merged class).
Pete's levels lie between pre-registered options C and B, so the saturating law is interpolated, not extrapolated.

Files: arc-latitude-profile.csv (log-likelihood at the median impact longitude per 0.5 deg latitude and 50 NM either side, per model and option),
arc-latitude-posterior-summary.csv, arc-latitude-band-shares.csv (1-deg latitude shares, mean of models), arc-latitude-arrivals.csv, figure arc-latitude-first-look.png/pdf.

Caveats: pilot-node Monte Carlo noise about 1.3-1.5 log-likelihood units per node; Australian term is a reconstruction; the northern posterior
rests on run J's thin northern tail (pooled L_eff about 120 north of 33 S; one lineage carries 8.4 per cent of waypoints northern mass),
so northern shape is not reliable. Labelled sensitivity, not headline.

## Addendum: when debris arrives, and the Australian 2014 level (17 Oct 2026)
australia-arrival-timing-by-period.csv: share of recoveries (first beaching + 60-day exponential delay, window to 30 Jun 2016) in each detection period
(I1 to 29 Jul 2015, I2 to 1 Mar 2016, I3 to 30 Jun 2016), from the deskstar snapshot runs (4 arc releases, about 1M particles per model, both models,
point-in-box against the aus160 segment boxes). From 35-40 S, 95-97 per cent of Perth-Augusta recoveries fall in I1 (median beaching about Sep 2014),
while the find-coast ramp factor (0.1/0.5/1 weighted by arrival time) is 0.50-0.59. So only Australia's I1 level matters, and option B (constant 1)
means Perth is about 1.8 times as alert as the find coasts at the time each received debris, not 10 times.
australia-2014-level-shift-curve.csv: posterior shift against the Australian I1 level (Pete's tier shape, merged classes at mid values).
