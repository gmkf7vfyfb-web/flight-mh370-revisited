# What the impact simulation does — in plain English

The calculation asks a deliberately limited question: **if a Boeing 777-sized
mass met the sea with a specified downward speed, and a specified small fraction
of that motion became long-range underwater sound, what order of peak pressure
might reach Cape Leeuwin (H01W) or Diego Garcia South (H08S)?** It does not yet
simulate the complete crash, water entry or acoustic waveform.

## Which aircraft mass is used?

The Malaysian investigation records **174,369 kg as 9M-MRO's actual zero-fuel
weight on the final loadsheet**. It is not a measured aircraft mass at 00:19 UTC.
We use it as a fuel-exhaustion impact-mass surrogate. The true impact mass is
unknown and could differ because of residual or unusable fuel and uncertainty
about the aircraft's final condition.

## What is presently simulated?

Each Monte Carlo draw has two uncertain inputs:

1. A downward water-contact speed is drawn from one of four explicitly separate
   families: a controlled-ditching class (0.5–1.5 m/s), the measured vertical
   contact speed of US Airways Flight 1549 (3.81 m/s, used only as a cross-aircraft
   analogue), a deliberately broad partially arrested bridge (3.81–70.104 m/s),
   or Holland's conditional unarrested-descent bounds (70.104–128.524 m/s).
2. A coupling efficiency, \(\eta\), is drawn. This is the fraction of normal
   impact energy assumed to become energy carried in the long-range SOFAR
   acoustic channel. One sensitivity distribution is centred on \(10^{-4}\),
   using an F-35 water-impact observation only as an order-of-magnitude anchor;
   a broad log-uniform alternative from \(10^{-8}\) to \(10^{-2}\) is also run.

The normal kinetic-energy surrogate is

\[
E_n=\tfrac12 m v_z^2.
\]

The coupled energy is \(E_a=\eta E_n\). We express it as an effective TNT mass
and apply a published range-only pressure law to the representative station
distances. Repeating this one million times per family and coupling assumption
shows how strongly the answer changes with the impact family and, especially,
the unknown coupling.

## What is not presently simulated?

Altitude and horizontal speed are not initial conditions in this reduced-order
calculation. Nor does it represent pitch, roll or yaw; an explicit impact angle;
the duration over which energy enters the water; fuselage breakup; planing,
cavitation or ventilation; sea state; path-specific bathymetry; acoustic–gravity
wave dispersion; hydrophone response; or contemporaneous station noise. The
four families are therefore **vertical-contact-speed families**, not four
complete impact attitudes or time histories.

The displayed time series and spectrograms add a generic pulse shape and
0.3 Pa RMS display noise so readers can see the calculated median amplitudes on
a common scale. This is close to the order of pressure variation visible in the
extracted publication traces, but it was not estimated as a raw-station noise
floor. Uniformly resampled, median-centred H01W traces have 0.211–0.226 Pa
mean-removed RMS; H08S panel d has 0.242 Pa and the strongly periodic panel e
has 0.390 Pa. Raw plotted vertices give approximately 0.28–0.31 Pa for panels
a–d but depend on the plot's vertex sampling density. Only the Holland-family
median is conspicuous at both stations
in that particular rendering; the partially arrested median is weaker but
visible at Cape Leeuwin. This is not a finding that only the Holland family is
detectable. The noise is illustrative, matched filtering is not applied, and
the broad coupling distributions make the family pressure ranges overlap.
A defensible detection probability requires raw receiver noise, instrument and
processing metadata, a source spectrum and a declared detector threshold.

## What a fuller physical model would do

The proposed fuller chain is exactly the right conceptual progression:

1. sample the aircraft's altitude, three-dimensional velocity, attitude, mass
   and configuration near the end of flight;
2. propagate that state to water contact;
3. model water entry, breakup and the time-dependent force/pressure field for
   nose-first, oblique, partially arrested and controlled-ditching cases;
4. calculate how each source component couples into ordinary acoustic and
   acoustic–gravity modes;
5. propagate those modes over measured bathymetry and ocean structure to each
   station; and
6. apply station response, the historical processing chain and contemporaneous
   noise before running a pre-declared detector.

That would turn the present energy-and-pressure sensitivity into a forward
model capable of estimating waveform shape and detection probability. Public
data constrain parts of this chain, but water-entry breakup and coupling would
remain the dominant uncertainties unless calibrated against relevant full-scale
impacts or controlled experiments.

Flight 1549 provides much more than its 3.81 m/s descent rate: the NTSB records
the A320's mass, 125-knot contact airspeed, 9.5-degree pitch, approximately
3.4-degree downward flightpath, low roll, and resulting pressure loading and
fuselage damage. Those measurements can test the low-energy hydrodynamic/contact
end of a fuller model. There was no remote hydroacoustic observation, so they do
not calibrate sound coupling. Conversely, the F-35 case supplies an estimated
\(900\pm200\) MJ impact energy, an approximately 3,300 km path and a measured
0.7 Pa peak at H11, from which Brown et al. infer order-\(10^{-4}\)
surface-to-SOFAR coupling. It is a high-energy, long-range acoustic anchor, but
not a transferable 777 waveform or universal efficiency.

## Source boundaries

The mass record and every external numerical anchor are passage-audited in
[`data/impact-simulation-citation-ledger.md`](data/impact-simulation-citation-ledger.md).
The reproducible scenario definitions are in
[`data/impact-simulation-config.json`](data/impact-simulation-config.json), and
the numerical results are in
[`outputs/impact-family-quantiles.csv`](outputs/impact-family-quantiles.csv).
