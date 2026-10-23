# Hydroacoustic Handover (23 Oct 2026)

Machine-readable package of all hydroacoustic work in this project (7-23 Oct 2026): code, data products, notes index,
the registry, Pete's rulings, an error register and a report. Prepared at Pete's request for review by another agent and model.
Written in ASD-STE100 for work-specific text.

## Start here

1. `REPORT.md` - what happened, every class of error with its ids, the root causes, what the 23 Oct clean-up did, what holds, what is open.
2. `errors/error_register.json` (and `.csv`) - 119 entries: R- registry defects (19), A- automated reviewer findings (50), P- errors Pete reported (28), S- errors of the 23 Oct session (14),
   V- errors that the independent verifier found in the 23 Oct clean-up (8), each with its status after the fixes.
3. The registry (data of record): branch `hypothesis/hydroacoustics` @ 394707d, `Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/registry/`
   (`REGISTRY.json`: 80 entries with status, defects, sha256 manifests and quoted definitions; `registry.py` loader). A copy is in `code/module/registry/`.
4. `Claude Science Project Sep 29/results/hydroacoustics/` on this branch: `INDEX.md` (generated from the registry), `decisions.md` / `decisions.json`
   (Pete's rulings in his exact words), `proposals.md` (agent proposals; not rules).
5. `verification/VERIFICATION.md` - the independent verifier's two passes on the 23 Oct clean-up (pass 1: 8 errors; pass 2: 6 FIXED, 2 PARTLY),
   and what was changed after pass 2. The raw verifier results are in the same folder.

## Layout

| folder | contents |
|---|---|
| `code/module/` | every tracked file of `engine/hypotheses/hydroacoustics/` at 394707d (git archive) except `results-data/`: `prepare/` (all scripts and tests, 3 small `.npz` templates), `lib.rs`, `physics.rs`, `*.toml`, `registry/`, and `data/` (module input files: digitised paper panels, IMS responses, IMOS and ocean-path tables, stations) |
| `code/kernel-cells/<session>/` | 3,809 code cells run in the 46 sessions' kernels (platform cell log), with `cells_index.json` |
| `code/exchange-scripts/` | `.py`/`.sh` files stored with the exchange products in `~/Downloads/mh370-exchange/hydroacoustics/` |
| `data/results-data/` | text files (csv, json, txt, log, xml) of the module's `results-data/` at c9ac5cc (unchanged at 394707d); files over 200 kB are gzipped. PNG charts are not copied (they are on the module branch). |
| `data/register-2026-10-23/` | the detection register (singles 184, pairs 3,321, triples 12,331) with README, summary and SHA256SUMS of the uncompressed files; files over 200 kB are gzipped |
| `data/kadri-package-v3-draft-predictions/` | Kadri v3 draft predictions (NOT FOR SENDING), meta, README, errata for the v2 text, v2-v3 comparison |
| `artifacts/<session>/<version>_<file>` | 238 text artifacts (csv, md, json, py, txt, bib) produced in the 46 sessions; `artifacts_index.json` lists all 433 artifacts with sha256 |
| `sessions/sessions_index.json` | the 46 sessions: id, parent, profile, recorded model, dates, message counts |
| `errors/` | error register |
| `verification/` | verifier passes 1 and 2 (JSON) and `VERIFICATION.md` |
| `MANIFEST.json` | every file in this folder with size and sha256 |

## Not in this repo (the repo is public)

In `~/Downloads/mh370-exchange/hydroacoustics/handover-2026-10-23/` on Pete's Mac:
- `transcripts/` - full transcripts of the 46 sessions (JSONL, gzip), with tool calls and results;
- `tool-results/` - the platform's stored large tool outputs and images for those sessions;
- `artifacts-all/` - all 433 artifacts, including chart images and purchased or licensed paper PDFs (not for publication);
- `memory/` - the 418 hydro-related project memory rows before the clean-up, and the list of rows changed;
- `pete_messages_hydro.json` - Pete's messages extracted from the transcripts (source of `decisions.md`).
The exchange data products (78.4 GB) stay in `~/Downloads/mh370-exchange/hydroacoustics/`; the registry manifests give their sha256.

## Rules for the next agent (from Pete's rulings; see decisions.md)

Read data only through the registry. Stop when an input is missing; no stand-ins without Pete's approval. Give compute and development
estimates and wait for approval before any run. No statement of absence or certainty without its uncertainty. Do not say or imply that
another researcher's work is wrong without a pre-registered test with checked inputs. A proposal is not a rule.
