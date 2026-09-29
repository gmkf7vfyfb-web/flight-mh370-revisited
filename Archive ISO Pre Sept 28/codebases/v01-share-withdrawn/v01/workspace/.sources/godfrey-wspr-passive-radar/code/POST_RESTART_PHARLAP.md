# Post-restart PHaRLAP control batch

This batch extends the trajectory-blind WSPR control to the seven conventional
post-restart BTO epochs. It is source recreation outside the estimator. No
post-radar aircraft position, heading or candidate trajectory is supplied to
anomaly selection, intersection construction, propagation filtering,
clustering or residualization.

## Frozen scope

The epochs are the current canonical estimator observations `m1825`, `m1941`,
`m2041`, `m2141`, `m2241`, `m0011` and `m0019a`. The two additional 18:28 BTO
reports belong to the first restart event, `m0019b` is the second report of the
seventh-arc event, and the 18:39 and 23:15 records have BFO but no BTO; these are
not treated as additional numbered arcs.

This corrects an important difference from the earlier exploratory all-arc
WSPR figure. That figure used 18:25:27 and BTO 17,120 microseconds for its first
curve. The release input uses canonical `m1825`, 18:25:34 and BTO 12,600
microseconds. At approximately 6.75 degrees north the old curve is near 105.3
degrees east, while the canonical curve is near 96.1 degrees east and is
consistent with the final-radar region. The remaining time changes are about
one second.

Every epoch uses ten WSPR transmission midpoints within plus or minus ten
minutes of the BTO time, complete minus-60-minute and plus-60-minute radio-time
controls, the eastern branch in 64--110 degrees east and 45 degrees south--10
degrees north, a symmetric 100 NM arc band, a 20-degree minimum link-circle
angle, 25 km clustering/residual matching and at least three transmitter- and
receiver-independent links. The BTO curves use 10 km aircraft altitude only as
map geometry; PHaRLAP tests aircraft heights from 0.5 to 13 km separately.

## Frozen inputs and workload

The WSPR input was retrieved from WSPR Live at 2026-09-02 09:51:02 UTC with
the twelve predeclared bands `-1,0,1,3,5,7,10,14,18,21,24,28`, ordered by
`time,id`. Its 179,023 rows have SHA-256
`2a2ceb43517b4f5e3e5cd53729ed66c29ae15144849bbdd1a1ca70e7dd7ebf74`.
WSPR Live is mutable, so this hash identifies the retrieval but the checked-in
compact tables are the authoritative PHaRLAP inputs. The exact one-second
Inmarsat workbook has SHA-256
`a1a84be75ebdcf642a77dd110a755b01c6e4be1adb5dbef2cfb42fc5585989d0`.
Each selected workbook state is also required to equal the corresponding
current product ephemeris row.

Materialization produced 38,581 candidate pair locations referencing 9,828
unique WSPR reports. Deterministic PHaRLAP planning produced 20,678 grouped
route jobs. A measured five-worker rate from the same known-flight calculation
is approximately 0.75 jobs per second, implying about 7.6 hours before assembly
and plotting; this is a runtime estimate, not a scientific result.

The frozen inputs are:

- `data/post-restart/post_restart_pair_locations.csv.gz`
- `data/post-restart/post_restart_spot_records.csv.gz`
- `data/post-restart/post_restart_arc_audit.csv`
- `data/post-restart/post_restart_arcs.csv`
- `data/post-restart/post_restart_candidate_manifest.json`

Validate them from the repository root:

```text
/tmp/mh370-acoustic-venv/bin/python \
  .sources/godfrey-wspr-passive-radar/code/test_post_restart_candidates.py
```

Run or resume the complete propagation batch outside the repository:

```text
/tmp/mh370-acoustic-venv/bin/python \
  .sources/godfrey-wspr-passive-radar/code/pharlap_batch_runner.py \
  --candidate-pairs .sources/godfrey-wspr-passive-radar/data/post-restart/post_restart_pair_locations.csv.gz \
  --spot-records .sources/godfrey-wspr-passive-radar/data/post-restart/post_restart_spot_records.csv.gz \
  --dataset-name post-restart \
  --output-directory /tmp/mh370-wspr-post-restart-pharlap-batch \
  --pharlap-home <PHARLAP-4.7.4-directory> \
  --iri-library <libpharlap_iri2020.so> \
  --ray-library <libpharlap_raytrace_2d_sp.so> \
  --processes 5 --manifest-every 25
```

The command is content-addressed and safe to resume. Assembly refuses a
partial, failed or hash-mismatched cache:

```text
/tmp/mh370-acoustic-venv/bin/python \
  .sources/godfrey-wspr-passive-radar/code/assemble_post_restart_pharlap.py \
  --batch-directory /tmp/mh370-wspr-post-restart-pharlap-batch \
  --output-directory .sources/godfrey-wspr-passive-radar/outputs/post-restart-pharlap
```

The assembler writes complete raw/residual counts and exploratory blocked
control diagnostics for the surface-endpoint and common-aircraft-altitude
screens. Propagation feasibility remains a filter, not evidence that any
returned ionospheric mode was the realized mode.

Render the no-truth residual/control panels and their publication table after
assembly:

```text
/tmp/mh370-acoustic-venv/bin/python \
  .sources/godfrey-wspr-passive-radar/code/plot_post_restart_pharlap_residuals.py \
  --clusters .sources/godfrey-wspr-passive-radar/outputs/post-restart-pharlap/post_restart_pharlap_clusters.csv \
  --arcs .sources/godfrey-wspr-passive-radar/data/post-restart/post_restart_arcs.csv \
  --comparison .sources/godfrey-wspr-passive-radar/outputs/post-restart-pharlap/post_restart_pharlap_comparison.csv \
  --run-metadata .sources/godfrey-wspr-passive-radar/outputs/post-restart-pharlap/run_metadata.json \
  --output-directory .sources/godfrey-wspr-passive-radar/outputs/post-restart-pharlap/figures
```

By default each physical screen is paginated over three, three and one epochs,
with columns for minus 60 minutes, actual time and plus 60 minutes. It emits
300-dpi PNG plus vector PDF/SVG, a 14-row raw/residual count table, plot audit,
captions and a hash manifest. No aircraft-truth or trajectory symbol is drawn.
