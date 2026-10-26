# Memory notes (hydroacoustics)

Date: 26 October 2026. Language: ASD-STE100.

**Read this first.** Each row in these files is a record of what project memory said. It is not a verified fact. Check a value against its source before you use it.

## What these files are

On 25 October 2026 the memory track gave 216 hydroacoustics rows the action "move to registry" and 11 rows the action "defer-hydro". Phase 1 did not write them. Phase 2 (26 October 2026) writes them here, in the same format as `Claude Science Project Sep 29/registry/memory-notes/` on `claude-science-sep29`.

| File | Rows | Source of the text |
|---|---|---|
| `hydroacoustics.jsonl` | 216 | memory export, artifact version ba131e4c-350c-4db5-8b56-a61b3f2772f9 (SHA-256 starts efbc74bc) |
| `deferred-hydro.jsonl` | 11 | the memory rows as read on 26 October 2026 (read only). They were written after the export. They were not content-verified (status UNVERIFIED). |

`index.json` gives the counts, the verification status counts, the SHA-256 of the inputs, and for each registry entry the mem_ids of its rows.

## Links to entries

The memory track found no entry for these rows. The registry track linked a row to an entry only when the row text names the path of exactly one entry (the last part of the path, 12 characters or more): `link` = "name match (registry track, 26 Oct 2026)". The other rows link to the topic note entry `note.memnote_hydroacoustics`. A link tells you what the row is about. It does not change the status of the entry.

## Fields of a row

`mem_id`, `registry_entry`, `link`, `topic`, `module`, `written_utc`, `memory_evidence_tag` (stated, observed or inferred, as in memory), `marker`, `original_text`, `text_flags`, `verification_status` (VERIFIED, PARTIAL or UNVERIFIED, from the memory track), `verified_by`, `verification_evidence`, `nature`. Deferred rows also have `text_source` and `action`.

## Changes to the text

The repository is public. The script withholds text that names a restricted source and replaces session-workspace paths. For these 227 rows no text was withheld and no path was replaced (`index.json`, `text_flags`).

The 45 hydroacoustics rows about external sources are in the citation ledger `Claude Science Project Sep 29/results/hydroacoustics-references.md` on `claude-science-sep29` (generated section at the end).

Made by `Claude Science Project Sep 29/registry/import_hydro_memory_records.py` on `claude-science-sep29`. Do not edit by hand.
