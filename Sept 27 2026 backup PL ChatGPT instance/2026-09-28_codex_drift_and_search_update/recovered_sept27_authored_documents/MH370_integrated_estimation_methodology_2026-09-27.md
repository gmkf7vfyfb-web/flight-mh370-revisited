# Integrated Bayesian/Sequential Monte Carlo Estimation Framework for MH370 Impact and Wreckage Location

**Technical proposal / methodology specification — 2026-09-27**

## 1. Objective

The objective is to estimate a converged, model-averaged probability density for (i) first water contact, (ii) the effective impact/acoustic source region, and (iii) the principal wreckage resting location by propagating uncertainty from the last radar-constrained state through the satellite-observed flight, end-of-flight (EOF) dynamics, impact process, hydroacoustic propagation, ocean drift, satellite imagery, and underwater-search non-detections.

The governing principle is:

> **Sample the physically feasible manifold first; let the observations supply likelihood, rather than selecting a preferred narrative in advance.**

The compact target expression is

```text
p(impact/wreckage location |
  radar + SATCOM + aircraft dynamics + fuel + EOF
  + hydroacoustics + debris/ocean drift + satellite imagery
  + underwater-search results)
```

A fuller joint expression is

```text
p(r_contact, r_source, r_wreck | Y) ∝ Σ_h ∫ p(Θ) p(H=h|Θ) p(X_0|Θ)
[Π_{k=1}^{K} p(X_k|X_{k-1},Θ) L_pre(Y_pre|X_{0:K},Θ)]
p(E_{K:I},Ψ|X_K,H=h,Θ) L_19(Y_19|E_{K:I},H=h,Θ)
L_A(Y_A|Ψ,Θ_A) L_D(Y_D|Ψ,Θ_D) L_P(Y_P|Ψ,Θ_P) L_S(Y_S|Ψ,Θ_S)
dX dE dΨ dΘ
```

The final geographic products are marginals of this joint posterior, especially

```text
p(r_contact | Y),  p(r_source | Y),  and  p(r_wreck | Y).
```

## 2. Evidence classes

Let the total evidence be

```text
Y = {Y_pre, Y_19, Y_A, Y_D, Y_P, Y_S}
```

where:

- **Y_pre**: radar, Burst Timing Offset (BTO), routine Burst Frequency Offset (BFO), received-signal-level/antenna-gain information, fuel/performance evidence, and other observations up to 00:11 UTC.
- **Y_19**: the anomalous 00:19 UTC terminal SATCOM log-on sequence, including BTO, both terminal BFO measurements, reboot timing, and evidence bearing on the SDU power interruption and OCXO warm-up.
- **Y_A**: hydroacoustic/seismic recordings, station metadata, noise state, duty cycle and calibration information.
- **Y_D**: recovered debris identity, type, discovery location/date, biological/weathering information where justified, and negative discovery/search information.
- **Y_P**: satellite imagery and associated acquisition/geometry metadata.
- **Y_S**: underwater search coverage and spatially varying probability of detection.

The 00:19 observations are assimilated only in the EOF stage, so that they are not used twice.

## 3. State representation

The continuous aircraft state is represented as

```text
X_t = [φ, λ, h, v_N, v_E, v_D, m_f, m, ψ, θ, ϕ, b]_t
```

with latitude φ, longitude λ, altitude h, north/east/down velocity components, fuel mass m_f, gross mass m, heading/yaw ψ, pitch θ, roll ϕ, and measurement/system bias terms b.

A parallel discrete state is

```text
Q_t = {flight-control mode, engine state, electrical state, configuration}.
```

The complete EOF/impact latent state Ψ contains at least:

```text
Ψ = {
  t_contact, r_contact,
  mass and 3-D velocity at contact,
  attitude and angular rates,
  engine/electrical/control state,
  energy-deposition time history,
  breakup/debris class,
  effective acoustic source state,
  initial sinking and floating-debris states,
  principal-wreckage latent state
}.
```

It is important not to equate first water contact, effective acoustic-source location, and the final position of the major wreckage.

## 4. Stage 1: flight-state estimation to 00:11 UTC

A fixed, reproducible initialisation epoch should be chosen from the best-supported radar-derived state. Alternative initialisations may be run as sensitivity analyses rather than making start time itself diffuse.

A large adaptive Sequential Monte Carlo (SMC) ensemble is propagated under Boeing 777 performance constraints, fuel burn, winds, feasible accelerations, bank/turn rates, climb/descent rates, stall/overspeed limits and temporally coherent flight-control modes.

The proposal should be broad but physically structured, not a set of independent uniform draws.

### 4.1 Speed sampling

A global Mach prior such as a narrow M0.73–M0.84 band is unnecessarily restrictive for this purpose. Speed should instead be sampled conditionally on altitude, mass, atmosphere and aircraft configuration, preferably in CAS/IAS/Mach-control terms that map to TAS and groundspeed with winds.

This permits lower feasible speeds — including states capable of reproducing the relatively low inferred first-arc groundspeed — without spending samples in states below stall or above VMO/MMO.

### 4.2 Altitude and the 00:11 state

Altitude at 00:11 must not be restricted to conventional cruise altitude merely because the preceding hours are consistent with a relatively stable southerly path.

Holland reports a measured 00:11 BFO of 252 Hz and states that it is consistent with level flight, but his Figure 4 shows that for a roughly southerly track the level-flight prediction exceeds the measurement by about 4–6 Hz. With BFO vertical sensitivity near the end of flight of about 1.6–1.7 Hz per 100 ft/min, the centre of a simple southern-track interpretation is therefore a modest descent of order 250–350 ft/min; exact level flight is still well within ordinary BFO error. More substantial descent can be compatible when heading/speed/BFO-error uncertainty is admitted, but extreme descent rates at 00:11 would require correspondingly extreme measurement/model residuals.

Thus **vertical speed should be inferred jointly with track, speed and BFO bias/error**; level flight should not be imposed.

Altitude itself is much less directly constrained by BFO than vertical velocity. To preserve low-altitude support at 00:11 without wasting the entire multi-hour particle cloud at implausibly low altitude, use a temporally coherent descent model. Two practical approaches are:

1. a **descent-onset mixture**: most particles remain in cruise-like altitude modes until a sampled descent-onset time, after which altitude evolves under a feasible descent profile; or
2. a **bridge/auxiliary particle proposal** conditioned on broad terminal altitude strata at 00:11, with correct importance weights.

A useful implementation is to stratify 00:11 altitude (for example low, medium and high bands) and guarantee minimum particle representation in each band, then allow BTO/BFO/fuel/performance likelihoods to determine their weights.

## 5. Stage 2: EOF model from 00:11 to the end of the impact event

The full 00:11 posterior becomes the prior for the EOF filter.

The 00:19 reboot being caused by fuel exhaustion is a **conditional model hypothesis, not an axiom**. Competing hypotheses can include:

- fuel exhaustion near 00:17–00:19 followed by uncontrolled descent;
- fuel exhaustion followed by pilot intervention/arrested descent/glide;
- fuel exhaustion followed by phugoid-like or other dynamically feasible unpowered motion;
- continued powered flight through 00:19 with a separate cause for the SDU power interruption/reboot;
- later fuel exhaustion;
- powered impact before fuel exhaustion.

Fuel exhaustion is represented as a hitting-time event,

```text
T_FE = inf{t : m_f(t) ≤ m_unusable(Q_t)}.
```

After a flameout transition, the aircraft dynamics and electrical configuration change. Branching should be achieved with mixture transition kernels and adaptive resampling rather than by giving every particle an enormous fixed set of descendants.

The 00:19 BTO, BFO and reboot/OCXO evidence are applied here. The model should marginalise over power-interruption duration and oscillator warm-up uncertainty rather than choosing one correction deterministically.

## 6. Impact as a finite-duration process

Impact should be modelled as an episode rather than a point.

Total kinetic energy is

```text
E_K = 1/2 m_I ||v_I||²
```

but acoustic and debris outcomes depend strongly on vertical/horizontal velocity decomposition, attitude, angular motion, breakup sequence and the duration over which energy is dissipated.

A controlled water contact can dissipate energy over a much larger time and distance than a steep high-energy impact, even at similar total kinetic energy.

The impact model should therefore produce:

- first water-contact location/time;
- spatial and temporal energy-deposition history;
- breakup class and initial debris field;
- effective acoustic source spectrum/time history;
- initial sinking states for major wreckage components.

## 7. First contact versus wreckage resting location

Use a separate latent wreckage-transport model:

```text
r_wreck =
  r_release
  + ∫ U(z(t),t) dt
  + ∫ v_rel,h(t) dt
  + Δr_seafloor
```

where U is the 3-D ocean-current field, v_rel,h is horizontal motion relative to the water caused by the object's own sinking/gliding/tumbling hydrodynamics, and Δr_seafloor represents post-contact movement on the seabed.

Required uncertainties include:

- local water depth and bathymetry;
- current velocity and shear versus depth;
- wreckage mass, volume and buoyancy;
- drag coefficient/projected area/orientation;
- terminal sinking velocity;
- breakup altitude/position over the water and release timing;
- possible hydrodynamic glide or tumbling;
- sediment/slope effects and downslope movement after seabed contact.

AF447 is a useful analogy for search detectability, but not a direct measurement of surface-impact-to-seabed drift. The main AF447 wreckage was found about 6.5 NM from the aircraft's last transmitted position, while the mapped seabed debris concentration was only about 600 m × 200 m. The 6.5 NM includes the aircraft's unobserved motion after the last transmitted position and therefore should not be interpreted as sinking drift.

## 8. Hydroacoustic branch

From every impact-state particle generate a posterior-predictive ensemble of possible received signals.

A useful source/propagation formulation is

```text
Y_r(f,t) =
  Σ_m G_r,m(f,t ; r_source, Θ_ocean)
      S_0,m(f,t ; Ψ, Θ_I)
  + N_r(f,t),
```

where:

- S_0 is the impact-source spectrum/time history;
- m indexes propagation modes (direct waterborne/SOFAR, bathymetric T-phase, water-solid-water conversion, elastic/seismic paths, acoustic-gravity-wave modes, and justified multipath modes);
- G is the propagation operator to station r;
- N_r is station/background noise.

The 2001 and 2003 SIO/LLNL controlled-source cruises can calibrate propagation, timing, bearing, attenuation, frequency dependence, blockage and airgun nuisance rejection. Known aircraft crashes constrain the impact-to-acoustic source prior.

For computational efficiency, use a hierarchy: first arrival time, bearing, amplitude band, spectrum, duration and dispersion; then full waveform simulation only for posterior-supported cases. Raw recordings should be compared using pre-specified detection/beamforming procedures and control-period false-event rates.

A non-detection contributes

```text
P(no detection | Ψ) = 1 - P_D(Ψ),
```

with P_D conditioned on uptime, duty cycle, noise, blockage and predicted signal strength.

## 9. Ocean-drift/debris branch

Floating debris is propagated using a stochastic model such as

```text
dr_d =
  [U_current + U_Stokes + U_leeway] dt
  + Σ^(1/2) dW_t.
```

Debris-specific latent variables include buoyancy, area-to-mass ratio, orientation state, windage/leeway, water ingress, marine growth, survival, beach interception and discovery probability.

The observation model is therefore closer to

```text
P(item found at x,t | impact state, debris class)
```

than merely the probability that an object passes through x.

Breakup state is shared between the acoustic and debris branches; otherwise those streams would be incorrectly treated as independent.

## 10. Satellite imagery branch

Satellite imagery should be treated as another observation process rather than a visually selected confirmation layer.

The official MH370 work already included MODIS/NASA imagery review and subsequent re-analysis of four Pléiades 1A images from 23 March 2014 supplied by the French Ministry of Defence. DigitalGlobe/WorldView imagery and imagery from several nations also influenced the 2014 surface search.

A systematic historical *8 March 2014* census appears feasible and should be done separately:

1. obtain historical TLE/GP data from Space-Track, CelesTrak archives or another TLE archive;
2. propagate all satellites with possible line of sight to the evolving impact PDF;
3. classify spacecraft by sensor class: optical EO, SAR, meteorological, scientific, communications, navigation, military/unknown;
4. for EO systems, apply sensor swath, pointing/off-nadir capability, illumination, cloud cover, spatial resolution and acquisition/tasking availability;
5. search operator/catalogue archives for actual acquisitions.

Candidate civilian/scientific systems active in 2014 include Terra/Aqua MODIS, Suomi NPP, Landsat 7/8, Pléiades 1A/1B, SPOT 5/6, WorldView-1/2, GeoEye-1, TerraSAR-X/TanDEM-X, COSMO-SkyMed and RADARSAT-2. Presence above the horizon is not evidence of image acquisition; tasking and swath geometry must be checked.

I have not found an official publication that performs a complete historical orbit/tasking census of every EO-capable satellite over the candidate impact region at the relevant time. Existing official work discusses particular imagery products rather than a comprehensive satellite-opportunity inventory.

## 11. Underwater-search likelihood

Searched seabed should be included explicitly as negative evidence:

```text
L_S = P(no wreckage detection | r_wreck, survey coverage, terrain, sensor, P_D).
```

Search polygons should not be treated as zero-probability masks. Probability of detection is spatially variable because of gaps, terrain shadowing, sensor geometry, resolution and search quality.

## 12. Evidence fusion

Hydroacoustic and debris/drift results branch from the same impact state. They must not be converted independently into posteriors and then multiplied, because that would count the impact prior twice.

For impact particle i,

```text
w_i^final ∝
  w_i^EOF
  L_A^i
  L_D^i
  L_P^i
  L_S^i.
```

Model averaging is

```text
p(r | Y) = Σ_h p(r | Y,H=h) P(H=h | Y).
```

## 13. Formal algorithm

1. **Calibrate component models** using known 9M-MRO flights, aircraft performance/fuel data, 2001/2003 acoustic experiments, known aircraft-water impacts, debris/drifter experiments and survey metadata.
2. **Initialise** N particles at the chosen radar-derived epoch with continuous state X, discrete mode Q and nuisance parameters Θ.
3. **Propagate to 00:11** under feasible aircraft dynamics. At every observation, calculate the appropriate likelihood and update weights:
   ```text
   w~_i = w_i L(y_k | X_k^i, Θ^i)
   w_i = w~_i / Σ_j w~_j.
   ```
4. Monitor effective sample size:
   ```text
   ESS = 1 / Σ_i w_i²
   ```
   and resample/rejuvenate when necessary.
5. **Begin EOF filter at 00:11.** Sample EOF model/hypothesis variables and propagate fuel, engine, electrical and control state.
6. **Assimilate 00:19** BTO/BFO/reboot evidence inside the EOF filter.
7. **Propagate through impact**, producing Ψ and separate contact/source/wreckage latent states.
8. **Evaluate post-impact branches**: hydroacoustic, debris/drift, satellite imagery and underwater-search non-detection likelihoods.
9. **Fuse once at common impact state** using the final weight equation above.
10. **Marginalise** to produce p(r_contact|Y), p(r_source|Y) and p(r_wreck|Y), plus versions conditional on each major EOF hypothesis.
11. **Validate convergence and robustness** using independent random seeds, increased particle count, different resampling thresholds, alternative reasonable priors, leave-one-evidence-stream-out analyses and posterior-predictive checks.

## 14. Computational design

A brute-force Cartesian product of flight particles × EOF descendants × debris particles × acoustic environments is impractical.

Use:

- adaptive SMC and resample-move rejuvenation;
- conditional branching only from material-weight particles;
- SMC² or particle-MCMC for slowly varying/static hyperparameters;
- precomputed or emulated ocean-drift kernels;
- precomputed acoustic transfer-function grids / surrogate models;
- stratified proposals for low-probability but physically important terminal states;
- expensive full-wave or CFD calculations only on posterior-supported subsets.

## 15. Information contribution and sensitivity

For each evidence class j, report how much it changes the geographic posterior. One useful diagnostic is the Kullback-Leibler information gain

```text
ΔI_j =
D_KL[p(r | Y_1:j) || p(r | Y_1:j-1)].
```

The final publication should show both the model-averaged PDF and PDFs conditional on the major EOF hypotheses so that any region dependent on a controversial assumption is immediately visible.

## 16. Principal references and source families

- Davey, S., Gordon, N., Holland, I., Rutten, M. & Williams, J. *Bayesian Methods in the Search for MH370*. Springer/DST Group.
- Holland, I.D. “MH370 Burst Frequency Offset Analysis and Implications on Descent Rate at End-of-Flight.”
- ATSB, *The Operational Search for MH370* and associated search-area, debris, satellite-imagery and First Principles reports.
- Malaysian ICAO Annex 13 Safety Investigation Report MH370/01/2018.
- Geoscience Australia, Pléiades satellite imagery analysis and MH370 bathymetric/search data releases.
- BEA, AF447 final report and sea-search documentation.
- Blackman et al./SIO-LLNL Indian Ocean hydroacoustic calibration reports, 2001 and 2003.
- Kadri et al., published hydroacoustic/AGW analyses relevant to aircraft-water impacts and MH370.
- CSIRO MH370 ocean-drift studies and flaperon drift experiments.
- CelesTrak / Space-Track historical orbital-element archives for systematic satellite-opportunity analysis.
