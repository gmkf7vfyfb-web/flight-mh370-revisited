Shared ocean transport paths (ruling H5, 9 Oct 2026). Built with engine/crates/ocean examples/ocean_paths.rs
from request.json (GEBCO_2026 at 250 m with a +/-2 km corridor; WOA23 decade by epoch: 95A4 month 10 for
air8/air9 in October 2001, A5B4 month 3 for 8 March 2014). The exports (about 50 MB) are not committed:
regenerate with
  cargo run -p mh370-ocean --release --example ocean_paths -- data/ocean_paths/request.json <out>
and convert with prepare/shared_paths.py <out> <dir> <names...> to the schema the propagation scripts read.
Impact points: the stand-in's 2.5/25/50/75/97.5 % latitude quantiles at the median longitude of samples
within 0.05 deg (prepare/synthetic_composer_test.py draw, seed 20261008).
imos_path_blockage.csv: shallowest track depth and corridor maximum before the last 100 km, km of track
shallower than 1,000 m. Scott Reef (3250) is blocked from every impact quantile (land or < 100 m over the
North West Shelf for ~900-1,060 km); Perth Canyon is open (>= 1,837 m); Portland is open until its shelf.
