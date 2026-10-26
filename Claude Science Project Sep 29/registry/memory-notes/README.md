# Memory notes

Date: 25 October 2026. Language: ASD-STE100.

**Read this first.** Each row in these files is a record of what project memory said. It is not a verified fact. Check a value against its source before you use it.

## What these files are

The memory track (25 October 2026) moved 1446 rows out of memory with the action "move to registry". This folder holds 1230 of them. The 216 hydroacoustics rows are not here; phase 2 adds them to the hydroacoustics registry.

- 454 rows link to an existing registry entry (the memory track found the match).
- 776 rows matched no entry. They link to the note entry of their topic.

## Files

| File | Module | Note entry | Rows | Rows with no other entry | Verification status |
|---|---|---|---|---|---|
| `coordination.jsonl` | project | `project.memnote.coordination` | 67 | 24 | PARTIAL 25, UNVERIFIED 29, VERIFIED 13 |
| `core-eof.jsonl` | core | `core.memnote.core-eof` | 515 | 330 | PARTIAL 98, UNVERIFIED 319, VERIFIED 98 |
| `debris-drift.jsonl` | drift | `drift.memnote.debris-drift` | 114 | 65 | PARTIAL 22, UNVERIFIED 73, VERIFIED 19 |
| `descent-6dof.jsonl` | end-of-flight | `eof.memnote.descent-6dof` | 76 | 58 | PARTIAL 13, UNVERIFIED 49, VERIFIED 14 |
| `drive.jsonl` | project | `project.memnote.drive` | 15 | 12 | PARTIAL 1, UNVERIFIED 14 |
| `figures-style.jsonl` | project | `project.memnote.figures-style` | 39 | 30 | PARTIAL 9, UNVERIFIED 25, VERIFIED 5 |
| `fuel.jsonl` | core | `core.memnote.fuel` | 56 | 43 | PARTIAL 6, UNVERIFIED 41, VERIFIED 9 |
| `git-repo.jsonl` | project | `project.memnote.git-repo` | 13 | 6 | PARTIAL 1, UNVERIFIED 9, VERIFIED 3 |
| `literature.jsonl` | project | `project.memnote.literature` | 6 | 4 | PARTIAL 2, UNVERIFIED 2, VERIFIED 2 |
| `ocean-data.jsonl` | drift | `drift.memnote.ocean-data` | 17 | 12 | PARTIAL 5, UNVERIFIED 8, VERIFIED 4 |
| `other.jsonl` | project | `project.memnote.other` | 29 | 16 | PARTIAL 5, UNVERIFIED 22, VERIFIED 2 |
| `paper.jsonl` | paper | `paper.memnote.paper` | 23 | 14 | PARTIAL 4, UNVERIFIED 13, VERIFIED 6 |
| `platform.jsonl` | project | `project.memnote.platform` | 13 | 9 | PARTIAL 2, UNVERIFIED 10, VERIFIED 1 |
| `pleiades.jsonl` | pleiades | `pleiades.memnote.pleiades` | 120 | 77 | PARTIAL 19, UNVERIFIED 70, VERIFIED 31 |
| `seabed-search.jsonl` | searched-areas | `searched.memnote.seabed-search` | 127 | 76 | PARTIAL 25, UNVERIFIED 78, VERIFIED 24 |

`index.json` gives, for each registry entry, the mem_ids of its rows, and the SHA-256 of the memory export that we used.

## Fields of a row

`mem_id`, `registry_entry`, `link`, `topic`, `module`, `written_utc`, `memory_evidence_tag` (stated, observed or inferred, as in memory), `marker` (superseded or withdrawn, if the row says so), `original_text`, `text_flags`, `verification_status`, `verified_by`, `verification_evidence`, `nature`.

## Changes to the text

The repository is public. We changed the text in these cases only, and `text_flags` tells you which:

1. `withheld_restricted` (27 rows): the text names a restricted source or states content from one (see results/restricted-sources-ledger.md): the FPPM-confidential fuel cells, Ulich's workbook, the internal fuel model files or the tmp/ avionics material. The row gives the export row that holds the text. On 26 October 2026 Pete ruled the MH371 items not confidential; 3 rows that were withheld only for MH371 content (mem_3a2670828580, mem_e4e5d9d7671f, mem_e4cfd062722e) now show their text.
2. `workspace_path_replaced` (6 rows): a session-workspace path is replaced by `<session workspace path>`.
3. `amounts_removed` (1 row): spending amounts are removed.

Source: memory export artifact version ba131e4c-350c-4db5-8b56-a61b3f2772f9 (SHA-256 starts efbc74bc). Made by `registry/import_memory_records.py`. Do not edit by hand.
