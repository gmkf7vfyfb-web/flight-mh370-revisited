# Known-flight PHaRLAP publication panels

`plot_known_flight_pharlap_residuals.py` is the publication-only consumer of
the blind WSPR/PHaRLAP known-flight control run. It does not form candidate
intersections, run PHaRLAP, cluster points, subtract controls or select against
aircraft truth.

## Required inputs

The command requires seven frozen inputs:

1. A residual-cluster CSV. Its exact required header is the
   `CLUSTER_COLUMNS` constant in the plotter. `epoch_id` is mandatory and the
   upstream run must partition candidates by epoch before clustering; WSPR
   slots shared by overlapping epoch windows must never be pooled. Surface
   clusters have blank altitude fields. A primary common-altitude row is one
   spatial event assembled only after source altitude-slice clusters have been
   matched across control conditions regardless of altitude. Surviving source
   clusters are then collapsed for display and event counting. The row has
   blank `altitude_km` and
   retains `altitude_minimum_km`, `altitude_maximum_km`,
   `feasible_altitude_count`, `feasible_altitudes_km` and
   `source_altitude_clusters`. Exact-altitude residual matching is a separate
   sensitivity, not the primary figure.
2. An arc-polyline CSV. Every `epoch_id` has ordered `arc_point_index` rows and
   fixed flight, sequence and arc-time metadata.
3. A post-selection truth CSV. An `arc_epoch` row supplies the red map star and
   a descriptive whole-window distance. `physical_slot` rows supply aircraft
   truth interpolated to WSPR slot midpoints; exactly one is marked
   `is_nearest_arc_slot=true` for a time-aligned recovery check. Both roles
   retain source, interpolation method and timing offset. The whole-window
   distance is not called recovery because an aircraft can move materially
   over a plus-or-minus-ten-minute panel.
4. An authoritative truth-score CSV produced by the batch assembly. For the
   common-altitude screen it evaluates surviving pre-collapse source centres
   and exact heights, not the displayed collapsed representative or its
   altitude union. It retains parent collapsed-residual IDs for audit.
5. A JSON run record with schema
   `mh370.wspr.pharlap.known-flight-control-run.v1`. It freezes the PHaRLAP and
   route model descriptions, map extent, thresholds, altitude grid, control
   offsets and two essential audit assertions:
   `known_aircraft_truth_used_in_candidate_selection=false` and
   `epoch_partition_applied_before_clustering=true`.
6. A compact reported-position track CSV. It is a descriptive overlay only,
   is never supplied to WSPR selection or scoring and is drawn only in the
   arc-time panels. Reported samples are joined in time order, but the joining
   line is not presented as a continuously observed aircraft trajectory.
7. The track-provenance JSON. It binds the compact table to the audited source
   workbook by file identity, hash, row-selection rule, licence and URL.

## Output

Each screen is separate. For the six original WSPR known-flight epochs the
result is one MH371 and one MH370 figure, each with three epoch rows and the
columns minus 60 minutes, actual time and plus 60 minutes. Longer validation
sets paginate after three epochs without changing scale or semantics. Every
figure is written as a 300-dpi PNG, vector PDF and SVG.

Aircraft references are post-selection overlays in the arc-time panels only.
Interpolated arc-epoch positions are marked by stars. The MH370 17:07 position
is the nearest retained ACARS report, is shown by a distinct diamond and is not
propagated. An independently frozen ACARS report-position table is drawn as a
dashed contextual line in time order; the line is not used by WSPR processing
or scoring and positions between reports are not observed. All three columns'
recovery summaries use the same withheld reference evaluated at the midpoint
of the physical WSPR slot nearest the BTO epoch; the controls do not substitute
aircraft truth at their shifted radio times.

The paired summary CSV reports counts and two distinct proximity measures:

- descriptive distance from every residual in the complete panel to the
  static arc-epoch reference;
- authoritative recovery using surviving source clusters in the physical WSPR
  slot nearest the BTO epoch, compared with aircraft truth interpolated to that
  slot's midpoint. Common-altitude recovery requires both horizontal proximity
  and an exact feasible source height close to truth altitude. The primary
  altitude allowance is 0.5 km
  because retained ACARS altitude is pressure/barometric while PHaRLAP ray
  height is geometric/model height; 0.25 and 1.0 km are reported as frozen
  sensitivities. Surface-endpoint recovery is horizontal-only.

The cluster plot-audit CSV preserves every input cluster and its complete
feasible-altitude set; there is no plot-time spatial or altitude merge. The
manifest hashes all inputs and outputs and records the common support scale.

## Suggested figure caption

**PHaRLAP-filtered WSPR residual controls for the known flights.** Each row is
a BTO epoch and the columns show otherwise identical WSPR windows shifted by
minus 60 minutes, at the arc time, and by plus 60 minutes. Points are spatial
clusters unique to that column after 25 km symmetric residualization; colour
is the number of independent links. The black curve is the epoch's BTO arc.
The orange line, shown only in the central column, joins reported ACARS
positions in time order for post-selection context; it is not a continuously
observed trajectory and was not used to form or select candidates. The star is
the interpolated withheld aircraft reference; the diamond at MH370 17:07 is
the nearest retained report and was not propagated. Control annotations reuse
the withheld central-slot reference and do not represent aircraft position at
the shifted control times. In the common-aircraft-altitude version, marker
size encodes the midpoint of the modeled feasible-height range and is a
geometry attribute, not evidential strength. No central window recovered its
withheld aircraft reference under either propagation screen.

Run from the repository root:

```text
/tmp/mh370-acoustic-venv/bin/python \
  .sources/godfrey-wspr-passive-radar/code/plot_known_flight_pharlap_residuals.py \
  --clusters <residual-clusters.csv> \
  --arcs <arc-polylines.csv> \
  --truth <post-selection-truth.csv> \
  --tracks <post-selection-reported-position-track.csv> \
  --track-metadata <track-provenance.json> \
  --truth-scores <authoritative-truth-scores.csv> \
  --run-metadata <run-metadata.json> \
  --output-directory .sources/godfrey-wspr-passive-radar/outputs/known-flight-pharlap
```

The plotting test uses synthetic data in a temporary directory; it does not
create or check in scientific result figures:

```text
/tmp/mh370-acoustic-venv/bin/python \
  .sources/godfrey-wspr-passive-radar/code/test_plot_known_flight_pharlap_residuals.py -v
```
