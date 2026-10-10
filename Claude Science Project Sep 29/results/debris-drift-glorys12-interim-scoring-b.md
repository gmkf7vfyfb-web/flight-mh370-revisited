# Debris drift, interim: GLORYS12 surface scored on end of flight's core (b) impacts

Ocean Drift Module, 10 Oct 2026 ~12:00 UTC. **INTERIM, single ocean model, NOT EVIDENCE, NOT CONVERGED.**
Labels: PROVISIONAL-OVERNIGHT; core (b) split-half NOT converged; two-tank bookkeeping only; P(family) not
converged; drift surface GLORYS12 only (GlobCurrent running); support gap (unscored mass excluded).

**Inputs.** Drift: `debris-drift-production-glorys12/merged` (367 nodes, 30 NM, reference-289 extent, track 289.7;
GSHHG coastline; binary d24060aa8006d3ce; Darwin arm64 macOS 27.2). Impacts: end of flight's sweep on core (b)
(`mh370-exchange/end-of-flight/next-run`, READY 08:36:15Z, EoF 3c6319f), every option x cause plain and `+alive`,
strata pooled by P(family) (free 0.6948, Davey dynamics + radar 0.1527, descent-climb 0.1376, routes 0.0149),
seeds 1-4 equal. Script `prepare/pilot/score_mixture.py` (502c99d), interpolation exactly as `interpolate.rs`.
What is reported is a DIAGNOSTIC: the impact mixture restricted to the scored mass, before and after multiplying
by the drift likelihood. It is not the composed posterior (the composer owns that).

**Surface health (GLORYS12).** 367/367 nodes resolved at 50 km; split-half noise 1.42 ln units (robust 0.76;
0.90 without the 61 zero-hit nodes at 34.7-40.7 S); node SD 1.98. Figure
`debris-drift-glorys12-interim.png` (artifact 0cfe7a22).

**Result (50 km bandwidth; full table `debris-drift-glorys12-interim-scoring-b.csv`, 48 rows).**

| option x cause | scored | median before | median after drift | shift N |
|---|---|---|---|---|
| none__other (held out) | 0.836 | -36.88 | -35.77 | 1.11 |
| none__other+alive | 0.819 | -37.07 | -35.93 | 1.14 |
| none__fuel-exhaustion+alive | 0.921 | -37.11 | -36.08 | 1.03 |
| r600_inflated__other+alive | 0.885 | -37.70 | -37.00 | 0.70 |
| r600_no-offset__other+alive | 0.967 | -37.39 | -36.76 | 0.63 |
| r600_startup-offset__other+alive | 0.964 | -37.27 | -36.54 | 0.73 |
| r600-bto__other+alive | 0.793 | -37.69 | -37.07 | 0.62 |
| r1200_inflated__other+alive | 0.987 | -36.61 | -35.56 | 1.05 |

- Across the 44 options other than `both_no-offset` / `both_startup-offset`, the drift weighting moves the scored
  median north by 0.40-1.14 deg (median 0.74); ESS ratio of the weighting 0.34-0.66. `both_no-offset__fuel-exhaustion`
  shifts 6.6 deg on a handful of effective parents (end of flight's README): unstable, not to be quoted.
- **Bandwidth sensitivity is large**: at 25 km the after-medians sit ~1-2 deg further north; at 100 and 200 km
  the shift shrinks to roughly 0.2-0.5 deg. 50 km is the declared default (CSIRO practice); this must travel with
  any number.
- **Split-half check** (`...-halves.csv`): both halves shift every main option north, but the magnitudes differ
  by a median 0.9 deg (half B always larger; correlation 0.30). **The direction is consistent; the magnitude is
  not converged.** A plausible mechanism is Monte Carlo zero-hit realisations at southern (Mossel-limited)
  nodes, which push those nodes down and are commoner at half the particles; if so, part of the northward shift
  is a resolution artefact that falls with more particles. To be tested (targeted resolution at the 61 zero-env
  nodes: a new run, so for Pete).
- Scored fractions as in the support note: 79-99.8% by option; unscored mass is excluded, not renormalised.

Footnote: drift GLORYS12V1 + ERA5, 367 nodes, 1e5 particles/node, 4 env realisations, ocean error sigma_eff 0.1146
m/s, K 100-1000 m2/s, splitting Rodrigues 150 km x20 and Mossel 500 km x100, 50 km bandwidth (25/100/200 in CSV),
nine stringent finds; impacts core (b) via end of flight READY 08:36Z, track 289.7, internal-v1 fuel, all 00:19
options plain and +alive, P(family) mixture, 16 seeds.
