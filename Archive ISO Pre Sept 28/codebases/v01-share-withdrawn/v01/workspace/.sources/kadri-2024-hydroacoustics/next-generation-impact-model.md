# Next-generation impact-to-hydrophone model

## Feasibility

This is feasible as a staged forward model. Python should orchestrate the
uncertainty calculation, data preparation and surrogate evaluation; it should
not replace mature hydrodynamic and underwater-acoustic solvers. The result
could become a scientifically useful sensitivity model and, with raw station
data and relevant calibration evidence, a detection model. Public information
alone is not sufficient to claim a validated forensic likelihood for MH370.

## Proposed chain

1. **Aircraft state at water contact.** Draw mass, centre of gravity,
   three-dimensional velocity, pitch, roll, yaw, flight-control configuration,
   engine state and sea state. Propagate end-of-flight particles to first
   contact rather than assigning only a vertical speed.
2. **Water entry and structural response.** Run a designed set of free-surface
   CFD/fluid–structure simulations for representative nose-first, oblique,
   partially arrested and ditching states. DualSPHysics is a practical first
   open-source candidate: it models free-surface flow and couples fluid forces
   to rigid multi-body dynamics through Project Chrono. Flexible breakup would
   require a declared structural idealisation or another coupled solver.
3. **Reduced source emulator.** Convert each expensive run into a compact
   time-dependent pressure or force source, preserving direction, duration,
   spectrum and uncertainty. Fit a probabilistic emulator over the contact
   state. The main Monte Carlo then evaluates the emulator rather than running
   CFD millions of times.
4. **Acoustic and acoustic–gravity coupling.** Decompose the source into
   ordinary acoustic and coupled acoustic–gravity modes. Treat this as a model
   family because the coupling mechanism and source spectrum are poorly
   calibrated for aircraft water entry.
5. **Path propagation.** Use path-specific bathymetry and March 2014 sound-speed
   structure. GEBCO supplies global 15-arc-second bathymetry. Copernicus
   GLORYS12V1 supplies daily temperature and salinity on a 1/12-degree,
   50-level grid covering 1993 onwards; World Ocean Atlas provides an
   independent climatological control. The open Acoustics Toolbox supplies ray,
   normal-mode, finite-element and time-domain propagation codes including
   BELLHOP, KRAKEN, SCOOTER and SPARC.
6. **Receiver and detector.** Apply hydrophone-array geometry, station response,
   Kadri's processing chain and contemporaneous noise, then run a pre-declared
   detector. Without raw channels and response metadata, this last step remains
   a sensitivity rather than a calibrated detection probability.

## Calibration evidence

US Airways Flight 1549 constrains a low-energy contact/damage case: the report
gives aircraft mass, 125-knot airspeed, 9.5-degree pitch, approximately
3.4-degree downward flightpath, 3.81 m/s descent rate and documented aft-body
damage. It contains no remote hydroacoustic measurement, so it cannot estimate
surface-to-SOFAR coupling.

The 2019 F-35 loss constrains the opposite end: Brown et al. estimate
\(900\pm200\) MJ impact kinetic energy and report a 0.7 Pa peak at H11 over
approximately 3,300 km, implying coupling of order \(10^{-4}\). It anchors an
order of magnitude, not a universal transfer coefficient: the aircraft,
breakup, impact angle, penetration history and source-to-channel environment
differ from MH370.

## Core source representation

For contact state \(\mathbf{x}\), the hydrodynamic model returns a distributed
pressure history \(p_s(\mathbf{r},t\mid\mathbf{x})\). A propagation model with
Green's function \(G_j\) predicts station \(j\):

\[
p_j(t\mid\mathbf{x},\boldsymbol\theta)=
\int\!\!\int G_j(\mathbf{r},t-\tau\mid\boldsymbol\theta)
p_s(\mathbf{r},\tau\mid\mathbf{x})\,d\mathbf{r}\,d\tau,
\]

where \(\boldsymbol\theta\) contains ocean, seabed, coupling and instrument
uncertainties. A detector statistic \(T_j\) is evaluated against measured noise
to obtain \(P(T_j>\gamma_j\mid\mathbf{x},\boldsymbol\theta)\). Model families
must remain explicit; their spread is not ordinary Monte Carlo error.

## Estimator interface and physics-informed acquisition

The canonical estimator should pass the hydroacoustic spoke complete weighted
impact particles, not a two-dimensional crash map. Each particle should retain
source time, latitude, longitude, mass, three-dimensional contact velocity,
attitude, angular rates, engine/control state, impact family and contact-energy
history. The implemented first increment is deliberately predictive only: it
returns station-specific arrival, coupled-energy, pressure-squared-exposure and
RMS-pressure intervals, and it accepts no observed trace. Source coupling,
celerity/dispersion, bathymetry/path transfer and station response are named
model families. This makes a likelihood impossible until a separate,
commissioned observed-signal model is supplied.

For impact particle $z_k$, propagation/source family $m$, environmental
state \(\theta\), coupling state \(\phi\), and station $j$, a
frequency-domain forward model can be written

\[
\mu_j(f\mid z_k,m,\theta,\phi)=
H_{j,m}(f\mid \mathbf{x}_k,\theta)
S_m(f\mid z_k,\phi)
\exp[-2\pi i f\,\tau_{j,m}(\mathbf{x}_k,\theta)] .
\]

The source spectrum $S_m$ comes from the impact emulator;
$H_{j,m}$ is the path, array and instrument response; and
\(\tau_{j,m}\) carries acoustic, SOFAR and acoustic–gravity travel-time
uncertainty. In the current lean spoke, an explicit path-transfer interval maps
coupled source energy to predicted pressure-squared exposure. It is an
uncalibrated sensitivity input until path Green functions or relevant
calibration events are available.

The proposed GPS-acquisition analogy is useful only at the search-architecture
level: source position and propagation state predict station delays, so a bank
can be stepped through delay, dispersion, bearing and source parameters.
Unlike GPS, no known PRN waveform provides a sharp autocorrelation peak or
guaranteed processing gain. A common impact can also be distorted differently
at the two stations. The defensible detector is therefore a whitened,
array-coherent matched-subspace or generalised-likelihood search over a
physically generated template bank, followed by cross-station association.
Simple pressure-waveform correlation should remain a secondary diagnostic.

The present ±100 NM grid is a useful reproduction control, not the final prior.
Production templates should be generated at actual impact particles, or at
adaptively clustered representatives covering declared 95% and 99% weighted
support. Distance beyond the seventh arc must not be converted directly into
impact energy: longer post-00:19 flight favours some lower-energy families, but
a long glide can still terminate in a steep descent. Contact energy and
duration must come from each particle's end-of-flight state.

### Two integration levels

**With the publication traces now available**, retain hydroacoustics as a
zero-weight diagnostic and posterior-predictive product. The figures are
selected, already filtered, single plotted traces. They cannot calibrate array
coherence, bearings, receiver false-alarm rates, processing loss or a
non-detection probability. The filtered and raw-pulse complete-search controls
confirm that visually attractive alignments are expected under the available
publication-trace nulls.

**With calibrated raw channels**, pre-register the spatial/time/template bank;
whiten each channel; model or spatially reject the airgun train; run coherent
triad processing; and evaluate the same detector on large off-source windows,
station time slides and simulated injections into the real noise. Nielsen's IMS
processing account and Tuma, Igel and Prior document bandwise 10 s/150 s STA/LTA
hydroacoustic detection; CTBTO's PMCC work describes coherent detection below
40 Hz from hydrophone triplets. These are useful baselines and controls, not
substitutes for a source-specific likelihood.

A future calibrated particle update could use an injection-derived Bayes factor,

\[
B_{\mathrm{hyd}}(z_k)=
\frac{p(T_{\mathrm{obs}}\mid z_k,H_1)}
     {p(T_{\mathrm{obs}}\mid H_0)},
\qquad
w_k' \propto w_k B_{\mathrm{hyd}}(z_k),
\]

with the same complete-search procedure applied under $H_0$ and $H_1$.
Candidate selection, detector thresholding and source-location scanning are one
experiment and must be trials-corrected together. A hydroacoustic event time,
bearing and amplitude must not be entered as three independent observables if
they come from the same selected detection.

### Recommended execution order

1. Export the canonical full impact-particle hand-off described by the core
   estimator, including end-of-flight family and contact state.
2. Obtain raw H01W/H08S triad channels, timing/response metadata, exact filtering
   and decimation, array geometry, and at least hours of adjacent background.
3. Ask for Kadri's complete transient catalogue—including sub-threshold
   features—and the exact band, channel/beam, pick time, bearing uncertainty,
   range/celerity assumption and selection rule for every entry.
4. Build path-specific acoustic/SOFAR and acoustic–gravity Green-function
   ensembles from March 2014 ocean state and bathymetry.
5. Generate an impact-source bank spanning controlled ditching, partial arrest,
   high-rate descent and breakup/contact-duration alternatives; use CFD only
   to train a reduced probabilistic source emulator.
6. Fit a marked periodic nuisance model and, where raw triads permit, use array
   direction to separate the H08S airgun train rather than relying only on
   single-trace subtraction.
7. Inject the template bank into contemporaneous raw noise and repeat the
   complete position, time, propagation and model-family search. Report
   receiver operating curves, trials-aware false-alarm probabilities,
   localisation coverage and template mismatch.
8. Integrate only likelihood families that recover blinded synthetic sources
   with calibrated coverage. Keep all others as named conditional maps.


## Public inputs and boundaries

- [DualSPHysics SPH and multi-body formulation](https://github.com/DualSPHysics/DualSPHysics/wiki/3.-SPH-formulation)
- [Acoustics Toolbox model overview](https://github.com/oalib-acoustics/Acoustics-Toolbox/blob/main/index.htm)
- [GEBCO gridded bathymetry](https://www.gebco.net/data-products/gridded-bathymetry-data)
- [Copernicus global ocean physics reanalysis](https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030/description)
- [NOAA World Ocean Atlas](https://www.ncei.noaa.gov/products/world-ocean-atlas)
- [Boeing 777 airport planning manuals](https://www.boeing.com/commercial/airports/plan-manuals)

Boeing's public 777 manuals constrain external geometry and operational
dimensions, not certified structural CAD, material failure properties or a
finite-element breakup model. The most valuable additional data would be raw
H01/H08 channels and response metadata, precise 2014 array processing, Boeing
structural/mass-distribution data, and a relevant full-scale impact calibration.
