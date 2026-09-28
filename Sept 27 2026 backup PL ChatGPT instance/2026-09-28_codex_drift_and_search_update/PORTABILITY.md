# Reuse and paths

`search_conditioned_v1/analyze.py` is self-contained with the included inputs; install its requirements and run it.

`combined_panel_versions/build_panels.py` reads sibling `reverse_drift_v1`. It also copies original search provenance from a local August archive after plotting; the copied provenance is already included, so that final archive-copy section can be skipped on another host.

`reverse_drift_v1/code/run.mjs`, `run_outer.mjs` and `summarize.py` use the included recovered forcing/score files. Plotting uses the saved probability arrays. The report/packaging scripts additionally audit the original archive at /Users/pete/Downloads/MH370-review-research-03.zip; that archival source is not copied, but all recovered computational members are present and hashed. Read the original methods and requirements.

Earlier filter work is a code/result supplement, not a standalone runnable checkpoint bundle; see its BACKUP_SCOPE.md. Do not treat existing absolute-path provenance records as portable file locations.
