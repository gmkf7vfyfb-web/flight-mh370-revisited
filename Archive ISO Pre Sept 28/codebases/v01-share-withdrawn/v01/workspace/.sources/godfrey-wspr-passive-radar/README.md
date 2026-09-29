# Godfrey WSPR passive-radar reproduction

This bundle assesses the publicly specified core of the proposed WSPRnet
aircraft-detection method without selecting an aircraft trajectory first. The
principal source is Richard Godfrey, Hannes Coetzee and Simon Maskell, A
Proposed Global Passive Radar, 1 January 2025. The exact source inventory,
versions, retrieval links and SHA-256 identities are in paper/README.md;
citation-ledger.md maps each scientific claim to a located passage.

## Question recreated

The published method labels a WSPR report anomalous when either its received
signal-to-noise ratio or received-frequency departure is at least 0.75 sample
standard deviations from a same-transmitter, same-receiver, same-band reference
within plus or minus three hours. It then treats great-circle paths of anomalous
links near a known or evolving aircraft position as candidate detections.

We reproduced three distinct questions:

1. Do the authors' 48 selected-flight data distinguish aircraft-present from
   aircraft-absent reports?
2. Without supplying the aircraft position first, do the same anomalies
   preferentially localize the withheld aircraft track or the known BTO epoch?
3. Are the assumed great-circle positions compatible with a physically
   identified ionospheric ray at aircraft altitude?

The answer is no under the primary, reproducible **cell-centre** model.  A
coherent within-cell coordinate stress test can, however, create a
PHaRLAP-screened residual known-flight recovery within the frozen retained-pair
universe.  Exact historical antenna
coordinates are therefore a material unresolved input, not a negligible
rounding detail.  The present work neither establishes a WSPR detection nor
supports a general rejection of the proposed method; it shows that the public
inputs and rules are not yet sufficient to yield a calibrated location
likelihood suitable for the estimator.

## Mathematical and control model

For report i, the reference set is

    H_i = {j : (TX_j,RX_j,b_j)=(TX_i,RX_i,b_i),
                 |t_j-t_i| <= 3 hours},  |H_i| >= 5.

For received SNR s and frequency f,

    z_s,i = |s_i - mean(H_s,i)| / sd(H_s,i)
    z_f,i = |f_i - mean(H_f,i)| / sd(H_f,i)
    A_i   = 1[max(z_s,i,z_f,i) >= 0.75].

Six-character Maidenhead locators were decoded to cell centres. Each station
pair defines the normal to a full great circle,

    n_i = (x_TX,i cross x_RX,i) / |x_TX,i cross x_RX,i|,

and two link circles have antipodal intersections

    p_ij,+/- = +/- (n_i cross n_j) / |n_i cross n_j|.

For the arc controls, same-slot intersections in a symmetric 100 NM band about
the relevant BTO arc were clustered within 25 km. A cluster was retained when
at least three link circles could be selected without sharing any transmitter
or receiver. Identical processing was applied at the actual radio time and at
minus 60 and plus 60 minutes. Spatial residuals remove a cluster when another
panel has a cluster within the declared tolerance; subtraction is symmetric.

The blind 48-flight control replaced the known track by 2,048 equal-area
alternative segments of the same length and scored the percentile rank of the
withheld true segment. The same calculation was applied to the authors'
six-minute aircraft-absent control. The candidate-trajectory control separately
tested 12,000 BTO/BFO/performance-compatible paths at the actual WSPR times and
four symmetric time shifts.

The 20-degree pair-angle screen, 25 km clustering, independent-link rule,
symmetric controls, residualization, blind alternatives and BTO-arc search are
assessment choices. They are not claimed to be unpublished GDTAAA rules.

## Reproduced results

| Assessment | Result |
| --- | --- |
| Authors' 48-flight spreadsheet | 1,078 rows; row-level AUC 0.5560, flight-bootstrap 95% interval 0.5290 to 0.5871; ocean AUC 0.5284. At the 0.75 threshold, sensitivity 71.9%, specificity 35.5%, and false-positive rate 64.5%. |
| Any anomaly by selected case | All 48 aircraft-present cases and 45 of 47 aircraft-absent controls contain at least one anomaly. |
| Blind localization | True-track mean percentile 46.3% versus 47.3% for controls among 2,048 spatial alternatives; true track ranked higher in 23 cases and control in 25; sign p=0.885, Wilcoxon p=0.939. No ocean case was in the best 10%. |
| Candidate trajectories | All 12,000 paths had one or more anomalies at the actual time and every control. Mean actual-minus-four-control anomaly rate was -0.82 percentage points; only 44.0% of paths were positive. |
| Seventh arc, 00:20 to 00:48 | Raw at least three-link clusters were 704 / 576 / 598 and 25 km residual clusters 61 / 24 / 43 for minus 60 / actual / plus 60 minutes. |
| Sixth arc, 00:02 to 00:20 | Raw clusters were 419 / 294 / 238 and 25 km residual clusters 73 / 33 / 18. No one-sided excess test supported the actual window. |
| All seven BTO epochs | No epoch had a significant actual-time cluster excess. The only nominal two-sided result was an actual-time deficit at the sixth arc. |
| Unfiltered six known-flight BTO controls | Pooled raw clusters were 28 / 48 / 72 and residual clusters 19 / 40 / 60. Epoch-block tests gave p=0.688 and p=1.000 respectively. No actual residual lay within 100 km of withheld aircraft truth. |
| PHaRLAP-filtered six known-flight BTO controls, conditional on cell centres | Surface-endpoint raw and residual counts were both 7 / 0 / 6; common-aircraft-altitude raw counts were 14 / 7 / 25 and residual counts 9 / 6 / 22 (minus 60 / actual / plus 60 minutes). Neither screen recovered any of six withheld central-slot aircraft references. The one-sided epoch-block actual-excess p-value was 1.000 for both screens. |
| Seventh-arc route geometry | Across 24,392 pair intersections, neither contributing link used its transmitter-receiver minor segment at the plotted intersection. Every point required the complementary full-circle branch for both links. |
| Station-coordinate sensitivity | The archive latitude/longitude fields reproduce six-character cell centres, not antenna truth. In 131,072 coherent Sobol designs, raw at-least-three-link clusters fell within 25 km of withheld truth in 31 MH370 16:42 designs and 22 MH370 16:54 designs. PHaRLAP reruns of all 53 local witnesses produced one joint horizontal/altitude recovery at 16:42. For that coherent assignment, the nearest strict raw control proposal among all 357 retained epoch pairs was 198.99 km away, so propagation filtering cannot create a control within the 25 km subtraction radius. The cell-centre residual zero-of-six result is therefore coordinate-sensitive within the frozen pair universe. Full rematerialization could admit previously excluded pairs and remains required. |

The 48-aircraft headline is less paradoxical when the selection mechanism is
made explicit. The published data contain 742 anomalous reports out of 1,078
(68.8%), and about 13 selected links per aircraft. As an illustration only, two
independent standard-normal variables under the 0.75 rule would trigger with
probability

    1 - P(|Z| < 0.75)^2 = 0.701.

Using the observed 68.8% rate, 13 independent opportunities would contain at
least one anomaly with probability 0.99999974. Real WSPR observations are
dependent and non-Gaussian, so that is not a formal null model; it shows why
eventual any-hit detection is not a demanding endpoint. The useful question is
whether the true location outranks the many alternatives, and it did not.

## Propagation and altitude audit

The 2023 paper says a three-dimensional aircraft/ray intersection is required,
but its implemented method is described as a PropLab plausibility check for
maximum usable frequency, elevation and a realistic hop count. The 2024 paper
reports 9.7% of a typical path at commercial-aircraft altitudes without a
derivation. No published rule identifies the realized hop mode, landing point,
delay, angle of arrival or the part of the ground-projected great circle that
was at aircraft altitude.

For a transparent straight triangular hop with virtual apex H, the fraction of
path length and propagation time below altitude h is

    F(h;H) = h/H,  0 <= h <= H.

For a 12 km ceiling and H from 100 to 400 km this is 12% to 3%, independent of
the number of identical hops. It is concentrated near the transmitter,
receiver and intermediate ground landing points, not spread uniformly along
the great circle. For a descending straight ray at elevation alpha, the
horizontal offset between altitude h and the ground landing point is

    d = h / tan(alpha).

At 10 km, d is 286 km at 2 degrees, 163 km at 3.5 degrees and 71 km at 8
degrees. Thus a two-dimensional ground crossing within 2 km is not evidence
that the ray crossed the aircraft at that place. PropLab can model endpoint
height, but the exact authors' build, saved settings, historic inputs, mode
acceptance rule and antenna database are not public.

For a representative 15,000 km, five-hop, 250 km-apex path, the 10 km fraction
is 4.0%: about 2.03 ms of a 50.725 ms geometric propagation time. Each sloping
leg is below 10 km for only about 60 km in ground projection on either side of
its landing point. These are path fractions, not aircraft-intersection odds.

The ionospheric model could be numerically material because it may reject
large numbers of long-path or complementary-circle candidates. It would not by
itself turn the WSPR spot into an observed propagation mode: the archive has no
separate transmit/receive epoch, delay, bearing, raw IQ or resolved Doppler
return. A climatological ray that is possible is not proof that it occurred.

A separate loss-free, favorable bistatic benchmark for the published long
distance example predicts -210.0 dBm scattered power, 51.0 dB below an
optimistic WSPR threshold, and a maximum coherent carrier perturbation of only
0.000084 dB against the direct signal. It omits ionospheric focusing and is
therefore a stress test, not a universal impossibility proof.

## Ocean Infinity and official treatment

The ATSB asked Geoscience Australia to re-review earlier sonar data around
Godfrey's 2021 WSPR location, but explicitly said it had not assessed the
validity of the WSPR work. Public University of Liverpool material described
WSPR as research to determine whether it could help define a search area.
Godfrey reported a relationship with an Ocean Infinity adviser. No Ocean
Infinity or Malaysian primary source located in this audit states that WSPR
defined the contracted 2025-2026 search area or operational survey order.

## Result and integration boundary

Not integrated: the WSPR estimator weight remains zero. The public-core
method does not provide a blind, calibrated likelihood ratio of aircraft at a
candidate state versus no aircraft or another state. A zero weight is not a
claim that controlled HF passive radar using raw signals cannot work.

Reconsideration requires the complete source package and antenna database,
the exact versioned PropLab configuration, an explicit aircraft-altitude
intersection rule, frozen thresholds, same-link paired controls, held-out
ocean flights, flight-blocked validation, and enumeration of false spatial
tracks. Raw IQ or another discriminating delay/Doppler/angle signature would
materially strengthen the observable.

The authors offer Matlab source, data and instructions by email. Obtaining
that private package requires external contact authorization; purchasing
PropLab also requires user authorization. PHaRLAP is an available independent
2D/3D ray tracer, but it would test a new implementation rather than reproduce
the undisclosed historic configuration.

## Reproduce the PHaRLAP known-flight control

The frozen known-flight input contains 1,723 trajectory-blind candidate
intersections at six BTO epochs (three MH371 and three pre-diversion MH370),
1,177 referenced WSPR reports, the six corresponding BTO arcs, and withheld
aircraft truth.  Each epoch declares ten physical two-minute slots for all
three panels even when a slot produces no candidate; radio-window dependence
is therefore defined before anomaly selection.

The primary propagation calculation uses the published spherical great-circle
route construction, WSPR transmission midpoint at slot time plus 56.242 s,
IRI-2020 through PHaRLAP 4.7.4, 0.5 to 13.0 km aircraft heights by 0.5 km, up
to ten hops, and a frozen 295-ray nonuniform elevation fan (0.5 to 15 degrees
by 0.1 degree, then 15.5 to 89.5 degrees by 0.5 degree).  Collision frequency
is zero, so this is explicitly a geometry/MUF-feasibility screen rather than
an attenuation model.  PHaRLAP feasible modes are not treated as evidence
that any particular mode occurred.

The canonical input tables are part of this source bundle and the production
commands below depend only on those descriptive paths.  Verify their frozen
counts and manifest hashes from the repository root:

    python3 .sources/godfrey-wspr-passive-radar/code/test_known_flight_candidates.py

`materialize_known_flight_candidates.py` records the one-time migration from
the retained historical analysis files.  It is not a release-time dependency;
those historical paths need not exist to run the frozen control.

Run the 2,406 immutable route jobs with local paths to the restricted PHaRLAP
distribution and the independently built IRI/ray libraries.  The cache lives
outside the repository and the command is safe to resume:

    python3 .sources/godfrey-wspr-passive-radar/code/pharlap_batch_runner.py \
      --candidate-pairs .sources/godfrey-wspr-passive-radar/data/known-flight/known_flight_pair_locations.csv.gz \
      --spot-records .sources/godfrey-wspr-passive-radar/data/known-flight/known_flight_spot_records.csv.gz \
      --dataset-name known-flight \
      --output-directory /tmp/mh370-wspr-known-flight-pharlap-batch \
      --pharlap-home <PHARLAP-4.7.4-directory> \
      --iri-library <libpharlap_iri2020.so> \
      --ray-library <libpharlap_raytrace_2d_sp.so> \
      --processes 4 --manifest-every 25

The assembler refuses partial, failed, foreign or hash-mismatched caches.  It
clusters each modeled height first, subtracts source clusters that recur
spatially in another panel while ignoring modeled height, and only then
collapses surviving co-located height slices into display/count events.
Authoritative three-dimensional recovery is evaluated on the surviving source
centres and exact feasible heights, never on the collapsed marker's union:

    python3 .sources/godfrey-wspr-passive-radar/code/assemble_known_flight_pharlap.py \
      --batch-directory /tmp/mh370-wspr-known-flight-pharlap-batch \
      --output-directory .sources/godfrey-wspr-passive-radar/outputs/known-flight-pharlap

    python3 .sources/godfrey-wspr-passive-radar/code/plot_known_flight_pharlap_residuals.py \
      --clusters .sources/godfrey-wspr-passive-radar/outputs/known-flight-pharlap/known_flight_pharlap_clusters.csv \
      --raw-clusters .sources/godfrey-wspr-passive-radar/outputs/known-flight-pharlap/known_flight_pharlap_raw_clusters.csv \
      --arcs .sources/godfrey-wspr-passive-radar/data/known-flight/known_flight_arcs.csv \
      --truth .sources/godfrey-wspr-passive-radar/data/known-flight/known_flight_truth_references.csv \
      --tracks .sources/godfrey-wspr-passive-radar/data/known-flight/known_flight_track_observations.csv \
      --track-metadata .sources/godfrey-wspr-passive-radar/data/known-flight/known_flight_track_provenance.json \
      --truth-scores .sources/godfrey-wspr-passive-radar/outputs/known-flight-pharlap/known_flight_pharlap_truth_scores.csv \
      --run-metadata .sources/godfrey-wspr-passive-radar/outputs/known-flight-pharlap/run_metadata.json \
      --output-directory .sources/godfrey-wspr-passive-radar/outputs/known-flight-pharlap

The assembler exports raw primary clusters separately because common-altitude
source slices are subtracted before surviving slices are collapsed into the
residual display events; the raw event set cannot be reconstructed safely by
inverting the residual table. The plotter produces, for each flight and both
propagation screens, a three-column residual-control figure and a companion
central-window-only raw-cluster figure before control subtraction. Raw
proximity is the descriptive distance to the static arc-time aircraft
reference, not time-aligned recovery. Each epoch row is centered exactly on
that withheld reference and expanded symmetrically until the complete frozen
0--30 degrees north search domain is visible, so no selected cluster is
silently clipped. Pale-grey extensions are explicitly outside that frozen
domain. A 500 km meridional scale ruler appears at the right of every row.

The reported sign-flip probabilities are exploratory.  The six epochs reduce
to only three connected radio-window blocks, so paired epoch effect sizes and
withheld-truth recovery are the primary assessment outputs. The generated
`known-flight-pharlap-publication-results.md` and
`known_flight_pharlap_publication_results.csv` give the pooled and per-epoch
counts directly from the detailed comparison and truth-score artifacts. The
actual-time residual effect was negative at every non-tied surface epoch and
at all six common-altitude epochs; the connected-window sensitivity also gave
one-sided actual-excess p=1.000 for both screens (two-sided p=0.250, only three
dependent blocks).

The corresponding seven-epoch, no-truth PHaRLAP batch from the 18:25 restart
through the seventh arc is specified in
`code/POST_RESTART_PHARLAP.md`. Its checked-in trajectory-blind inputs contain
38,581 candidate pairs and deterministically expand to 20,678 resumable route
jobs. The release batch uses the canonical estimator's 18:25 observation and
explicitly records the materially different first curve in the earlier
exploratory WSPR figure.

### Station-coordinate sensitivity

The great circles of several short contributing links are extrapolated about
10,000 to 15,000 km.  A link as short as approximately 40 km therefore has a
large angular lever arm: an antenna displacement of a few kilometres inside a
reported locator cell can move the remote intersection by hundreds or more
than 1,000 km.  The following deterministic audit assigns one surface-uniform
point inside each six-character cell to every `(callsign, locator)` and reuses
that position coherently across all links and epochs:

    python3 .sources/godfrey-wspr-passive-radar/code/audit_known_flight_locator_uncertainty.py \
      --sample-power 17 --seed 370371 --batch-size 2048 \
      --output .sources/godfrey-wspr-passive-radar/outputs/known-flight-locator-uncertainty

The Sobol frequencies are sensitivity-design counts, not a probability model
for antenna location.  The audit also retains only pairs selected under the
cell-centre map/100-NM filter, so it can demonstrate sensitivity but cannot
bound pairs that would enter or leave after complete rematerialization.  The
53 raw witnesses within 25 km of truth were rerun through the unchanged
295-ray PHaRLAP screen:

    python3 .sources/godfrey-wspr-passive-radar/code/run_locator_witness_pharlap.py \
      --audit .sources/godfrey-wspr-passive-radar/outputs/known-flight-locator-uncertainty/known-flight-locator-uncertainty-audit.json \
      --pharlap-home <PHARLAP-4.7.4-directory> \
      --iri-library <libpharlap_iri2020.so> \
      --ray-library <libpharlap_raytrace_2d_sp.so> \
      --witness-set all-primary --processes 5 \
      --output .sources/godfrey-wspr-passive-radar/outputs/known-flight-locator-uncertainty/locator-witness-pharlap-all.json

One truth-selected 16:42 design produced a three-independent-link cluster
10.63 km from the aircraft and included 1.0 km among its feasible heights; the
withheld aircraft height was 0.743 km, a 0.257 km gap under the declared
0.5 km altitude allowance.  All eight contributing endpoint-to-intersection
miss distances were below 25 km.  This is an existence/sensitivity result, not
evidence that those sampled coordinates were the stations' real positions.
For a coherent completion in which all other epoch stations remain at their
cell centres, all 357 retained actual/control pairs were repositioned.  The
nearest strict raw control proposal was 198.99 km from the witness centre.
Because PHaRLAP filtering can remove but not add supporting links, it cannot
create a qualifying control centre inside the 25 km residual radius.  The
witness therefore survives symmetric subtraction within this frozen pair
universe:

    python3 .sources/godfrey-wspr-passive-radar/code/audit_locator_witness_controls.py \
      --audit .sources/godfrey-wspr-passive-radar/outputs/known-flight-locator-uncertainty/known-flight-locator-uncertainty-audit.json \
      --epoch mh370_1642 --sample-index 23526 \
      --actual-center-candidate known-flight:mh370_1642:00000658 \
      --output .sources/godfrey-wspr-passive-radar/outputs/known-flight-locator-uncertainty/locator-witness-control-geometry.json

This still does not rematerialize anomalous pairs excluded by the original
cell-centre map/100-NM filter; newly entering pairs could alter either the
actual or control field.
No defensible public contemporaneous exact coordinates were found for the
critical stations.  The authors describe a private, owner-sourced antenna
database and have offered it on request; a definitive assessment requires its
versioned coordinates, accuracy and date provenance, full candidate
rematerialization, and renewed control/PHaRLAP processing.

## Reproduce the transparent physics check

From the repository root:

    python3 .sources/godfrey-wspr-passive-radar/code/propagation_geometry.py
    python3 .sources/godfrey-wspr-passive-radar/code/test_propagation_geometry.py

The output files are outputs/propagation_geometry.csv and
outputs/physics_summary.json. Frozen numerical results from the retained
large-data reproductions, with their exact output hashes, are summarized in
data/reproduced_results.json. The original large archive remains outside this
lean bundle at the path recorded there; no bundle code is imported by the
estimator.
