---
name: pete-dissertation-spreadsheets-hf
description: "Pete's 2019 dissertation working spreadsheets are public on Hugging Face under CC BY 4.0 (redistributable with attribution); the set also holds the ACARS truth workbook"
metadata:
  node_type: memory
  type: reference
  originSessionId: 0b93e6b9-bf02-4368-9c3b-109418c65a12
  modified: 2026-09-28T23:17:28.571Z
---

huggingface.co/datasets/peteabiome/mh370-dissertation-spreadsheets: Pete Large's working files, uploaded 22 Aug 2026. The dataset card says `license: cc-by-4.0`. 43 files, about 1.75 GB.
- File list: https://huggingface.co/api/datasets/peteabiome/mh370-dissertation-spreadsheets
- Download: .../resolve/main/<url-encoded name>

Useful contents:
- "GAIN IN AC COORDS TO 68 EL 360 AZ.xlsx": AES gain in aircraft coordinates. 118 KB, sha256 1fb1a509. Byte-identical to the v01 copy. A values-only export is committed in hypotheses/antenna-gain.
- "Feb 21 Copy of Angles Test ... (version 1).xlsx" (64 MB): link budget, C/No and BFO. Sheet DATA has 1,044,876 rows by 195 columns of per-burst formulas; received power is in columns DE to EP.
- "BFO and Prx Residuals Values only.xlsx" (22 MB).
- The gain-rotation workbooks (about 120 MB each).
- "ACARS POSITION AND WIND REPORTS.xlsx" (31 MB). This contains MH371 truth.

**Why:** licence questions keep coming up about data derived from Pete's work. Anything in this set is CC BY 4.0, so it can be committed with attribution. Checked 2026-09-28 by the Antenna gain thread.

**How to apply:**
- Cite file name, sha256 and the Hugging Face URL as provenance.
- Many files are large: check disk first and stream only the rows you need (openpyxl read_only).
- Never open the ACARS workbook outside the MH371 scorer. See [[mh371-blind-control]].
