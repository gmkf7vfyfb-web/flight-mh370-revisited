# Restricted-source ledger: internal use to be reviewed before publication

Decision (Pete Large, 9 October 2026):
- Material in the repository whose redistribution status is uncertain stays where it is.
- It may be used **internally** where it holds useful information.
- **Every use must be recorded here,** so that each one can be reviewed before publication.
- Nothing listed here is cited in the paper, or reproduced in a figure, table or artifact meant for
  publication, until that review clears it.

## Holdings

| path | what it is | committed | status |
|---|---|---|---|
| `tmp/avionics_training_*.{pdf,bin}`, `tmp/avionics_try_*.bin`, `tmp/avionics_min-1.png` | avionics training document; one file name suggests it came from a document-sharing site | `ed40a72`, 29 Sep 2026 | provenance unverified; internal use only |
| `tmp/slideshare_avionics/slide-*.jpg` and their OCR text | slide deck images from SlideShare | `ed40a72`, 29 Sep 2026 | provenance unverified; internal use only |
| fuel tables: the FPPM-confidential cells in Ulich's workbook (`data/fuel-tables.json`, untracked) | flow values marked confidential | not in git | internal fuel model only (core request 16 C) |

## Uses

Record every use as one row: date, session or module, file used, what was taken from it, and where
the result went.

| date | session | file | what was used | where it went |
|---|---|---|---|---|
