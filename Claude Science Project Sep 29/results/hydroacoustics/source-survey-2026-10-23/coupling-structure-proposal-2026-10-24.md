# A structure for acoustic coupling: evidence-based families, not an anchor value

Hydroacoustics module. Design proposal, 24 October 2026. Companion table: [coupling-evidence-register.csv]({{artifact:8d3b7de3-54c5-44e6-a1e2-0c287a56b3fe}}) (17 evidence items).

## 1. Why the present framing fails

Every coupling number we hold answers a different question. Each folds a different subset of these factors into one ratio:

- the energy transferred;
- the fraction radiated as sound;
- the effective source depth;
- the source spectrum;
- the propagation path.

A single "coupling efficiency" therefore cannot be "ruled". The F-35A figure of 2.26e-3 is not a parameter value. It is one point on a curve: the coupling that reproduces the Wake Island record **if** the source is 10 m deep and has a one-pole f⁻² spectrum. At 2 m the same record needs 5.4e-2; at 30 m, 3.4e-4. Brown's ~1e-4 is the same recording read through a different, path-blind relation (Arons 1954). It is not a second datum.

The registry labels "anchor PENDING_RULING" and "bounds AGENT_CHOICE" come from this framing. The structure below makes them unnecessary.

## 2. The structure in four layers

### Layer 1. One source model with separated parameters (per impact)

For each impact drawn by end of flight, the source is described by:

| parameter | meaning | where its prior comes from |
|---|---|---|
| E_t | mechanical energy transferred into the water (J) | end of flight, per row (`impact_energy_transferred_j`, a declared upper bound) |
| η_rad | fraction of E_t radiated as underwater sound, all angles, 1-500 Hz | this structure (Layers 2-3) |
| z_eff | effective acoustic source depth, which sets the surface-image (Lloyd's mirror) loss | water-entry physics: cavity and pinch-off depth for the impact regime |
| S(f) | spectral family: one-pole f⁻² with corner near 1/τ; f⁻⁴-like (Metz near and far records); optional low-frequency cavity resonance (0.5-6 Hz) | Metz spectra (E03); Minnaert arithmetic (E10) |
| τ, n_pulses | source duration and pulse count | end of flight (`energy_transfer_tau90_s`, `energy_transfer_n_pulses`); F-35A bound τ ≤ ~3.3 s (E04) |

The received exposure at a station is E_t × η_rad × ∫ S(f) G(f; z_eff, path) df, where G is the module's propagation chain (KRAKEN + RAM). Only η_rad is "coupling" in this structure, and it is a property of the source alone. Depth, spectrum and path are separate dimensions, each with its own uncertainty.

The definition classes D2 (Arons), D3 (near field) and D4 (in-band) stay in the register. They enter only through their own observation operators (Layer 2); they are never treated as values of η_rad.

### Layer 2. Evidence register: each source enters through its own observation operator

Every source becomes a **likelihood over the Layer-1 parameters**, with its own measurement model and error terms. None is a "value". The register ([coupling-evidence-register.csv]({{artifact:8d3b7de3-54c5-44e6-a1e2-0c287a56b3fe}})) classifies all 17 items by role:

| role | items | what they do |
|---|---|---|
| Likelihood terms | E01 F-35A far field; E03 F-35A spectra | E01 constrains a ridge in (η_rad, z_eff, S), not a point. E03 weights the spectral families. |
| Model-error measures | E02 F-35A near field (4.2× the far-field value on the same KRAKEN-only chain; about 2.0× E01, which uses KRAKEN+RAM); E12 known-yield explosions (site scatter of 3.5 decades in D2; ×13 within one site); E13 Blackman airgun and SUS TL (level passes, slope fails by +7 to +13 dB/octave) | Set σ_model, the uncertainty of the forward model. They do not set η. |
| Consistency check | E05 Brown, Arons-based (same recording as E01) | The forward model must reproduce Brown's D2 ratio on the Misawa→Wake path. Counting it as separate evidence would count the F-35A twice. |
| Scaling points and envelope | E06 bullets ~1e-2; E07 piles 1e-3 to 2e-2; E08 raindrops ~1e-5; E09 iceberg blocks ~8e-7 | Show how η_rad changes with entry speed, bluntness and scale. They set the outer plausible envelope and the direction of transfer from a 20 t jet at 300 m/s to a ~200 t airliner in other attitudes. |
| Prior structure | E10 water-entry physics; E11 surface image | Set the z_eff prior and the low-frequency branch. |
| Separate source | E14 implosions (0.2 % to 18 % of P·V) | Its own branch, with its own depth. |
| Cross-check only | E15 Swissair 111 seismic | Energy-scale check; different physics. |
| Excluded | E16 Kadri's claimed detections; E17 airbursts | Stated reasons in the register. |

Each item carries an **independence group**, so the same recording is never counted twice (E01-E05 are all group G1, the F-35A event).

### Layer 3. Transfer to a Boeing 777: impact-regime families conditional on end of flight

Coupling is not one global number. It depends on how the aircraft meets the water, and end of flight already samples speed, flight-path angle, attitude and energy for every impact. So η_rad, z_eff and S are drawn **per impact row, conditional on its regime**:

| family | regime (from end-of-flight latents) | how its prior is built |
|---|---|---|
| R1 steep high-speed entry | dive, high speed, steep angle (the F-35A regime) | Sample z_eff from its R1 prior. Take η_rad from the F-35A ridge at that depth and spectral family. Add (i) σ_model from E02/E12/E13, (ii) a declared scale-transfer term for 20 t → ~200 t, (iii) event-to-event scatter. The 2.26e-3 is never used alone; the whole ridge is used. |
| R2 shallow uncontrolled entry | moderate speed, shallow angle | No aircraft calibration exists. Bracket the prior between the R1 posterior and the slow-blunt analogs (E08-E09), using the normal velocity component as the scaling variable. The width is deliberately large and stated as such. |
| R3 controlled ditching | low vertical speed, nose-up | Small E_t, shallow z_eff (strong surface-image loss), η_rad toward the slow-blunt regime, plus a break-up term. |
| I implosions (any regime) | trapped volumes collapsing while the wreck sinks | P·V at the implosion depth × η_imp (0.2 % to 18 %), deep source, separate timing. |

Three rules apply to every family:

1. **Joint sampling.** η_rad and z_eff are always sampled together; independent sampling is forbidden. This removes the degeneracy that produced the "anchor".
2. **Envelope.** The outer plausible envelope (about 1e-6 to 2e-2 for impact η_rad) comes from the mechanism analogs E06-E09. It is stated as an assumption with its sources; it is not a chosen constant.
3. **Epistemic switches.** Model choices that cannot be weighted from data are carried as declared alternatives and reported separately, never averaged silently: the spectral family, the scale-transfer form, and KRAKEN-only versus KRAKEN+RAM.

### Layer 4. Testing detection hypotheses across the range

For every candidate signal or non-detection, the module reports three things:

1. **The η-profile.** P_D(η_rad) and the likelihood ratio LR(η_rad) across the whole envelope, at each family's z_eff and S draws. A reader sees the result at every coupling, not at one value.
2. **Family-integrated results.** LR averaged over each family's prior (R1, R2, R3, I), plus the mixture weighted by end of flight's regime shares.
3. **Coupling needed against coupling plausible.** The coupling needed for detection (η_pd50) or for a loudness match (η_level), drawn on the same axis as each family's distribution. This shows where in the plausible range a result sits.

**Robustness rule.** A conclusion is stated as a finding only if its direction holds across the central 90 % of every family that carries material end-of-flight weight. Otherwise it is reported as conditional, naming the family and the parameter that drives it.

The standing caveats travel with every number: the propagation frequency-slope failure, and P_D as a proxy until it is measured on real arrivals.

## 3. What this replaces, and the decisions it needs

- "F-35A anchor 2.26e-3, PENDING_RULING" becomes "E01: derived evidence, a ridge over (η_rad, z_eff, S)". It needs no ruling.
- "Prior bounds 1e-6 to 1e-2, AGENT_CHOICE" becomes family priors derived by stated rules from E01-E14, with the analog envelope as a declared assumption.
- PRIOR-B (Arons, 1e-8 to 2e-4) is kept only for fast screening, labelled as such. Any result that matters is re-run through the full chain.

The decisions needed are about structure, not numbers:

1. Adopt η_rad as the single canonical coupling, with z_eff, S and path as separate dimensions.
2. Make coupling conditional on the end-of-flight impact regime (families R1, R2, R3, plus the implosion branch I).
3. Adopt the evidence roles in the register, including the independence rule (one F-35A event, counted once).
4. Adopt the Layer-4 reporting convention and robustness rule.

## 4. Work to build it

| step | content | compute |
|---|---|---|
| 1 | Re-run the F-35A inversion as a full ridge: z_eff 1-50 m × both spectral families × both propagation options, with the error budget (energy ±22 %, two stations, near-field 4.2× KRAKEN-only, ~2.0× against KRAKEN+RAM) | minutes, local; reuses prepare/metz_f35a |
| 2 | σ_model from E02, E12 (including the pending San Juan level test) and E13 | minutes |
| 3 | z_eff prior per regime from water-entry cavity and pinch-off scaling (Truscott 2014 and the water-entry literature), linked to end-of-flight speed and angle | literature, one session |
| 4 | Scale-transfer term and R2/R3 bracketing from the analog points, as declared alternatives | one session |
| 5 | Per-row sampling in the module; η-profiles and family-integrated LR for the existing candidate tables and non-detections | hours, local |
| 6 | Robustness chart per candidate or claim: coupling needed against each family's plausible range | minutes |

Steps 1-2 and 5-6 reuse existing module code. Step 3 is the only new physics research. With it, z_eff stops being an arbitrary convention and becomes a prior tied to how the aircraft hit the water.
