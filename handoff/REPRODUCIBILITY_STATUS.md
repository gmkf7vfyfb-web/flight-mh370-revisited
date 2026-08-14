# Reproducibility status

## Classification

| Component | Status | Principal limitation |
|---|---|---|
| Stage-one integrated estimator through 00:11 | Reconstructed, reproducible from retained script and inputs | Original refined-v3 particle checkpoint absent |
| Stage-one report/workbook/CSVs | Preserved release artifacts | Exact historical environment not previously locked |
| Refined fast-BFO estimate | Reproducible from retained short-interval data and script | Depends on cluster definition and estimator choice |
| Drift-smoothed 00:11 posterior | Reconstructed diagnostic | Drift likelihood partly digitized/model-averaged |
| Pleiades/BRAN result | Diagnostic sensitivity | Full two-dimensional BRAN trajectories absent |
| No-precompensation result | Artifact preserved; script currently incomplete | Missing `run_pleiades_bran_fl400_expanded.py` |
| Pulau Perak sensitivity | Reproducible reconstruction | Static workbook tables; original macro/bicubic engine not executed |
| Search-area inventory | Reproducible evidence package | Exact OI AUV swaths unpublished |
| Paper drafts and graphics | Preserved and regenerable in part | Some graphics depend on temporary extracted images |
| Project Library source archive | Preserved as 148 immutable files | Contains duplicates and historical versions requiring provenance review |

## Known missing or external components

1. `run_pleiades_bran_fl400_expanded.py`.
2. Refined-v3 particle checkpoint preserving full state correlations.
3. Full two-dimensional BRAN2015/2016 drift tracks/fields.
4. Exact ACCESS-G wind fields used by prior analyses.
5. Exact Ocean Infinity AUV sonar swaths for several campaigns.
6. A verbatim exported MH370 conversation transcript.

The migration audit recovered several inputs that were previously outside the
workspace, including the full SITA workbooks, Boeing performance references,
the AES antenna specification, Holland's end-of-flight paper, MH371 EHM data,
and the larger Library version of `MH370 calcs.xlsx`. Their preservation removes
an important transfer risk, but does not by itself establish which historical
run used which workbook version.

The previously hard-coded `/workspace` output path in
`build_interactive_search_map.py` was made repository-relative during migration.

## Observed environment at migration

- Python 3.12.13.
- Node.js 24.14.0.
- NumPy 2.3.5.
- pandas 2.2.3.
- SciPy 1.17.0.
- Matplotlib 3.10.8.
- Pillow 12.2.0.
- python-docx 1.2.0.
- ReportLab 4.4.9.
- lxml 6.0.2.
- contourpy 1.3.3.
- openpyxl 3.1.5.

Inspection-only JavaScript files use the harness-specific
`@oai/artifact-tool`; core estimator scripts do not require it.

## Verification standard for the receiving harness

A clean-clone validation should:

1. Verify the file-level SHA-256 manifest.
2. Create a Python 3.12 environment from `environment/requirements-lock.txt`.
3. Run `python scripts/migration/verify_handoff.py`.
4. Run lightweight deterministic checks before expensive particle simulations.
5. For every rerun, compare headline statistics to retained CSV summaries using
   declared Monte Carlo tolerances rather than byte equality of graphics.
6. Record any dependency or numerical-library changes in a new run manifest.
