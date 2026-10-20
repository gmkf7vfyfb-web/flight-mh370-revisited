# Where the floating debris goes, March 2014 to January 2017 (17 Oct 2026, architecture stand-in)

Answer to Pete's questions of 17 Oct: where the debris that does not reach the six find coasts or Australia ends up, maps after 1-3 years for releases
on the 7th arc at 25/30/35/40 S, and where the Pleiades objects (if aircraft debris) would go.

**Method.** `snapshots_test.rs` is an UNTRACKED ignored test appended to deskstar's copy of drift's `tests.rs` (backup `~/mh370/drift/snap/tests.rs.orig`;
not committed to `hypothesis/debris-drift`). It reuses drift's own `class_responses`, `diffusivity_prior` and `OceanSetup::run_tracks_ep` with the
15-160 E configs (`../australia-160E/aus160-<model>.toml`): the same three object classes, windage draws (GlobCurrent product-relative), four ocean-error
realisations, GSHHG coast, refloat off; no importance splitting, so every particle has weight 1. 100,008 particles per release per model; 10 releases
(4 arc points + 6 Pleiades rating-5 targets from `engine/hypotheses/pleiades/data/targets-3km.csv`, released at their 23 Mar 2014 image times).
Aggregated on deskstar by `aggregate.py` to 0.5-deg cells. Check: beached share by 30 Jun 2016 at the 35 S point 49.7 % (GLORYS12) / 38.6 % (GlobCurrent)
against 50.7 / 40.3 % in the production node tables (+-1 deg band).

Files: `debris-maps-2014-2017.pdf` (page 1 two models, page 2 GLORYS12, page 3 GlobCurrent; PNGs alongside), `debris-fate-by-region.csv`
(share beached by coast region by 30 Jun 2016 and by 30 Jan 2017, per release and model), `fate-budget-by-latitude.csv` (from the node tables).
