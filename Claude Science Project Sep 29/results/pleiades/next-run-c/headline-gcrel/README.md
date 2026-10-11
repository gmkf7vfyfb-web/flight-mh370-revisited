# Proposed run C headline after drift audit F1: both ocean models, GlobCurrent windage product-relative, ρ = 0.25

11 Oct 2026, Pléiades module. Labels: **core run C NOT CONVERGED** (split-half floor 0.924); end-of-flight physics PROVISIONAL (G13);
**conditional on H**, no identity likelihood, no Bayes factor; strata re-weighted by the 00:19 data (`family-evidence-run-c.json`);
existence constraint `unpowered`; after Phase 2 + Bluefin-21 + OI 2018 + OI 2025-26 SE band (grade C); Pléiades rating 5 + all four
COSMO-SkyMed contacts, one debris field. **PROPOSED** headline (module post 11 Oct 18:19 UTC); until architecture accepts it the headline
in force is GLORYS12 only (ruling 2, 11 Oct 02:15 −0600), which is in the table beside it.

Script: `prepare/headline_figure.py` (statistics through the adopted stand-in's `headline_rho_standin.row`; surfaces
`joint-surface-rho{0,0.25,0.5}-gcrel` for both models, `joint-surface-rho{0,0.25}` for GLORYS12). Close-ups: colour and seabed per option.

| 00:19 option | setting | 90 % region km² | 50 % km² | mean | ln S (p) | mean shift NM | PDF without H inside 90 % |
|---|---|---|---|---|---|---|---|
| 00:19 R600 BTO + Raw BFO | **ρ 0.25, both models (proposed headline)** | 41,798 ± 247 | 7,457 | 35.96 S 92.36 E | -0.30 (0.30) ± 0.07 | 38 | 16 % |
| 00:19 R600 BTO + Raw BFO | ρ 0.25, GLORYS12 only (in force, ruling 2) | 30,998 ± 227 | 5,817 | 36.01 S 92.38 E | +0.13 (0.43) ± 0.07 | 36 | 15 % |
| 00:19 R600 BTO + Raw BFO | ρ 0, both models | 38,090 ± 229 | 7,511 | 35.90 S 92.36 E | -0.48 (0.27) ± 0.07 | 41 | 15 % |
| 00:19 R600 BTO + Raw BFO | ρ 0.5, both models | 44,951 ± 284 | 7,530 | 36.00 S 92.36 E | -0.17 (0.33) ± 0.07 | 36 | 17 % |
| 00:19 R600 BTO + Raw BFO | ρ 0, GLORYS12 only (hook) | 28,478 | 5,470 | 35.96 S 92.38 E | -0.01 (0.38) | 38 | 14 % |
| 00:19 R600 BTO Only | **ρ 0.25, both models (proposed headline)** | 49,944 ± 352 | 9,617 | 36.00 S 92.42 E | -1.15 (0.16) ± 0.08 | 99 | 8 % |
| 00:19 R600 BTO Only | ρ 0.25, GLORYS12 only (in force, ruling 2) | 34,997 ± 324 | 6,980 | 36.06 S 92.40 E | -0.67 (0.23) ± 0.08 | 95 | 7 % |
| 00:19 R600 BTO Only | ρ 0, both models | 46,163 ± 277 | 9,620 | 35.93 S 92.40 E | -1.35 (0.14) ± 0.08 | 102 | 7 % |
| 00:19 R600 BTO Only | ρ 0.5, both models | 53,468 ± 444 | 9,840 | 36.05 S 92.43 E | -1.00 (0.18) ± 0.08 | 96 | 9 % |
| 00:19 R600 BTO Only | ρ 0, GLORYS12 only (hook) | 32,252 | 6,608 | 36.01 S 92.39 E | -0.83 (0.21) | 97 | 6 % |
| 00:19 Held Out | **ρ 0.25, both models (proposed headline)** | 92,732 ± 349 | 17,843 | 35.43 S 91.66 E | -0.51 (0.29) ± 0.08 | 77 | 12 % |
| 00:19 Held Out | ρ 0.25, GLORYS12 only (in force, ruling 2) | 77,420 ± 351 | 13,325 | 35.57 S 91.78 E | -0.29 (0.33) ± 0.07 | 69 | 11 % |
| 00:19 Held Out | ρ 0, both models | 82,891 ± 311 | 15,807 | 35.37 S 91.62 E | -0.56 (0.28) ± 0.08 | 81 | 11 % |
| 00:19 Held Out | ρ 0.5, both models | 100,810 ± 424 | 19,461 | 35.50 S 91.69 E | -0.46 (0.30) ± 0.07 | 73 | 13 % |
| 00:19 Held Out | ρ 0, GLORYS12 only (hook) | 67,914 | 12,034 | 35.52 S 91.76 E | -0.35 (0.32) | 72 | 10 % |

**Checks.** Hook rows (module surfaces, ρ = 0, as run) reproduce the module's run C close-up statistics: both models 37,887, 45,709, 82,614 km²; GLORYS12 only 28,478, 32,252, 67,914 km². The both-model product-relative rows agree with `windage-relative/windage-relative-run-c.csv` to its stored precision (km², ln S to 3 d.p., shift to 0.1 NM).

**Split-half σ** (± in the table; rms over three 4 + 4 seed partitions, `headline_splithalf.py`, run under the heavy lock 19:29 UTC,
`windage-relative/splithalf-gcrel.csv`): 0.4-0.9 % of the area. Hook rows reproduce the module's splithalf.csv (222 / 270 / 315 km²)
and the stand-in review's GLORYS12 ρ 0.25 σ (227 / 324 / 351 km²). Both models against GLORYS12 only at ρ 0.25: 32, 31, 31 σ (combined σ, three options);
ρ 0 against ρ 0.5 within both models: 19, 14, 34 σ.

**Reading.** Moving the headline from GLORYS12 only to both models widens the 90 % region by 35 % / 43 % / 20 % (R600 BTO + Raw BFO /
BTO Only / Held Out) and moves the tension from +0.13 to −0.30 (BTO + Raw BFO). The width is genuine between-model disagreement:
product-relative windage changes the two-model area by only +0.3 to +1.0 % (`windage-relative/README.md`). A narrower GLORYS12-only
result is therefore not more precise; it is conditional on one ocean model.

## COVERAGE
- (a) feasible set, (b) model reach, (c) proposal coverage: unchanged from run C (`../README.md` COVERAGE). This note changes only the
  likelihood surfaces under H, not the impact samples. Gaps carried: Holland H1/H2 not estimable (EoF targeted sampler pending); descents
  > 6,500 ft/min and unloading not reachable (G13); core split-half not converged.
- Ocean transport: two products only (GLORYS12, GlobCurrent); OSCAR comparison pending (OCEAN_TRANSPORT).
