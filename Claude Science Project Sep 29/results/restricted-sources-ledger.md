# Restricted-source ledger: internal use to be reviewed before publication

Decision (Pete Large, 9 October 2026):
- Material in the repository whose redistribution status is uncertain stays where it is.
- It may be used **internally** where it holds useful information.
- **Every use must be recorded here,** so that each one can be reviewed before publication.
- Nothing listed here is cited in the paper, or reproduced in a figure, table or artifact meant for
  publication, until that review clears it.

## Authorisation

Pete Large, 10 October 2026 (~01:10 UTC): "we have authorization for all confidential items."
- Pete then clarified: **"that authorization applies to all confidential items in the repo."** That
  includes the FPPM-confidential fuel cells, the `tmp/` avionics material and the MH371 ACARS/EHM data
  in `library_full_audit/MH370/`. As stated by Pete; the architecture session has not seen the
  authorisation document.
- **Internal use is authorised in full.**
- **Publication** of derived values or figures, and **redistribution** of the files in the public repo,
  are settled at the paper's provenance review. Until then the confidential tables stay git-ignored, and uses
  continue to be recorded below.

## Holdings

| path | what it is | committed | status |
|---|---|---|---|
| `tmp/avionics_training_*.{pdf,bin}`, `tmp/avionics_try_*.bin`, `tmp/avionics_min-1.png` | avionics training document; one file name suggests it came from a document-sharing site | `ed40a72`, 29 Sep 2026 | provenance unverified; internal use only |
| `tmp/slideshare_avionics/slide-*.jpg` and their OCR text | slide deck images from SlideShare | `ed40a72`, 29 Sep 2026 | provenance unverified; internal use only |
| fuel tables: the FPPM-confidential cells in Ulich's workbook (`data/fuel-tables.json`, untracked) | flow values marked confidential | not in git | internal fuel model only (core request 16 C) |
| `data/external/fuel-model/internal-v1.json` (untracked; git-ignored by `/data/external`) | dense flow grid and test vectors derived from all table classes, including the FPPM-confidential cells | not in git; ALSO held in the local Claude Science artifact store as `fuel-model-internal-v1-LOCAL-ONLY.json` (version `2ee08c24…`), saved 10 Oct by the fuel session; deletion was offered and Pete declined it, so it stays (as the engine-data artifact holding `fuel-tables.json` does) | internal fuel model only; never commit to git, never upload to a third-party service |
| `library_full_audit/MH370/mh371-acars.xlsx`, `MH371_EHM_Export.xls` | 9M-MRO's MH371 ACARS position reports and EHM engine reports, 7 Mar 2014 (the export also holds the MH370 climb report) | in git (library) | provenance unverified; internal use only |

## Uses

Record every use as one row: date, session or module, file used, what was taken from it, and where
the result went.

| date | session | file | what was used | where it went |
|---|---|---|---|---|
| 2026-10-10 | fuel model | `data/fuel-tables.json` (all classes, incl. the FPPM-confidential cells — about 22 % of flow corners used, audit F14 — and the INOP tables) | the internal-v1 table lookup and dense grid | `data/external/fuel-model/internal-v1.json` (local only); committed results are model outputs only (integrated burns, endurances, exhaustion times, implied factors); no cell is reproduced |
| 2026-10-10 | fuel model | `library_full_audit/MH370/9M-MRO Fuel Model V5.X.xlsm` (Ulich), *Fuel Flow Model* and *Endurance Model* sheets | text notes on the temperature physics (θ^0.68, Reynolds term); tank estimate L 21.973 / R 21.827 t at 17:06:43; R/L cruise flow ratio 1.021; flight-plan climb/descent coefficients | `results/fuel-model/internal-model.md` §§1, 4, 5 and `engine-imbalance-180149.csv` |
| 2026-10-10 | fuel model | `library_full_audit/MH370/mh371-acars.xlsx` | 5-min ACARS states of MH371 (pressure altitude, Mach, SAT, GWT, FQIS fuel): measured cruise burn at measured temperature | calibration group "MH371" in `results/fuel-model/internal-calibration*.{csv,json}`, Fig. 1 |
| 2026-10-10 | fuel model | `library_full_audit/MH370/MH371_EHM_Export.xls` | per-engine fuel flow WF-L/WF-R: MH371 05:06:41 (6,607 / 6,839 lb/h), MH370 climb 16:52:21 (15,583 / 15,786) | R/L flow ratio in `results/fuel-model/internal-model.md` §4 and `engine-imbalance-180149.csv` |
| 2026-10-10 | fuel model | (status note) FPPM-confidential cells, `tmp/` material, MH371 ACARS/EHM data | Pete (via Modular Architecture, 10 Oct): the project holds authorisation for these items; **internal use authorised in full**. Publication and redistribution scope **not yet confirmed**: the tables stay git-ignored, no cell is committed, every use is still recorded here. internal-v1 already uses every cell of every class with no penalty or down-weighting (filler cells, which are Ulich's non-Boeing placeholders, are excluded as `extract.py` directs); MH371 enters the calibration at full weight | no change to the model |
