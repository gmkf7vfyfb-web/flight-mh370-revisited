# Project registry

Date: 25 October 2026. Language: ASD-STE100 for work-specific text. Standard statistical and scientific terms are used as they are.

## 1. What the registry is

The registry is one record of the data, code and results of the project. It tells you what each item is and if you can use it.
It does not move, change or delete files. It does not do a new audit. The status of each item comes from records that already exist.

The registry has these parts:

| File | What it holds |
|---|---|
| `REGISTRY.json` | The merged registry. All module entries, the roots, the status values and the defects. |
| `modules/<module>/REGISTRY.json` | The registry of one module. |
| `modules/<module>/entries.yaml` | The entries of one module before the build. A script makes this file. Do not edit it by hand. |
| `modules/<module>/manifests/<id>.tsv.gz` | For each entry: each file, its size in bytes and its SHA-256. |
| `status_records.yaml` | The status records that a person read: item, status, and the file line or memory row that gives the status. |
| `COVERAGE.md` | Entries for each module and status, and the files that are not registered, with the reason. |
| `../results/INDEX.md` | The index of results. A script makes it from the registry. Do not edit it by hand. |
| `manifest.schema.json` | The JSON Schema for the manifest of a new result folder. |
| `check_project.py` | The check of the rules for new work. |
| `data_homes/` | The inventory of the exchange folder and the record of the module branches. |

The hydroacoustics module has its own registry on branch `hypothesis/hydroacoustics`. Phase 2 merges it into this registry.

## 2. Modules

The modules are: core, end-of-flight, drift (ocean drift, debris drift and ocean transport), settling, searched-areas, pleiades, composer, paper and project.
The module "project" holds items for all modules: archives, data homes, tmp/, coordination notes and the restricted holdings.

## 3. Entries

Each entry has these fields:

| Field | Meaning |
|---|---|
| `id` | Registry id, `<module>.<class>.<name>`. Quote this id when you quote a number from the item. |
| `kind` | input, code, product, note, archive, scratch or data_home. |
| `path` | `ROOT:relative path`. The roots are in section 4. |
| `status` | One of the status values in section 5. |
| `status_rank` | The source of the status: ruling, explicit, chain, readme or none. |
| `status_evidence` | The record that gives the status: the file and line, or the memory row id, and the quote. |
| `superseded_by` | The registry id of the newer item, if there is one. |
| `defects` | Defect ids. The defects are in `REGISTRY.json`. |
| `git` | The commit that first added the item and the commit that last changed it. For code on a branch: branch, commit and tree. |
| `n_files`, `bytes`, `manifest`, `manifest_sha256` | The number of files, their total bytes, the manifest file, and the checksum of the manifest content. `manifest_sha256` is the SHA-256 of the manifest rows (relpath, bytes, sha256: three columns, tab between columns), joined by a newline character, without the header row and without a newline at the end. It is not the SHA-256 of the .tsv.gz file. |
| `note` | One line that tells what the item is. |
| `restricted` | true for restricted material (section 7). |
| `uses_recorded_in` | For restricted material: the ledger that records each use. |
| `drive_link` | For a DRIVE entry: `project` (a file on the project Drive) or `third-party` (a link to another person's Drive; not a project file). |
| `memory_notes` | The memory rows that give information about this entry (section 11). |

## 4. Roots

A root is the start of a path. The roots point only to the repository, the exchange folder, the data homes in ~/Downloads, the external drive, git or a Google Drive file id.
A root never points to a session workspace. The platform deletes session workspaces.

| Root | Location |
|---|---|
| `REPO` | The top of the git checkout. |
| `WORK` | `Claude Science Project Sep 29/` in the git checkout. |
| `EX` | `/Users/pete/Downloads/mh370-exchange` |
| `DL` | `/Users/pete/Downloads` (data homes such as `mh370-ocean-data`) |
| `XDRIVE` | `/Volumes/Porsche 1TB Backup/mh370-archive` (external drive) |
| `GIT` | `<branch>@<commit>` on GitHub |
| `DRIVE` | A Google Drive file id |

To use a different location, set the environment variable `PROJECT_ROOT_<NAME>`.

## 5. Status values

| Status | Meaning |
|---|---|
| CURRENT | The records show no defect. We did not verify it again in this run. |
| CURRENT_WITH_CAVEATS | You can use it. Give the limits beside each number that you take from it. |
| KNOWN_DEFECT | A record gives a defect that changes a number or a claim. Do not use the parts that have the defect. |
| SUPERSEDED | A newer item replaces it. `superseded_by` gives the newer item. We keep the old item for history. |
| WITHDRAWN | Pete withdrew it. Do not use it. |
| PENDING_RULING | It waits for a ruling from Pete. |
| UNCHECKED | We found no status record. This means only "not yet used in a result that we quote". It is not a list of work to do. Check the item when you use it. |

The backfill script gives the status in this order:

1. A ruling from Pete.
2. An explicit statement that the item is superseded, withdrawn or has a defect.
3. A newer version with the same name stem (for example `-v2`, or `-DRAFT` and the final file).
4. The status line in the item's own README or note.
5. If there is no record: UNCHECKED.

A later date in the same name does not make an item SUPERSEDED. A later run can continue an earlier run. `COVERAGE.md` lists these pairs.

## 6. Rules for new work

These rules stop the errors from occurring again. `check_project.py` does a check of them before each push.

1. **No manifest, no result.** Put each new result in `results/<module>/<run id>/`. Put `manifest.json` in that folder. The manifest must agree with `manifest.schema.json`. It gives the run id, the commit, the configuration, the inputs by registry id, the SHA-256 of each output, the thread id and the status.
2. **Quote by registry id.** When you quote a number, give the registry id of its source.
3. **Do not use version names.** Do not use `-v2`, `_v3`, `-FINAL` or `-rev2` in a new file name or folder name. Give the new item a new run id. Set `supersedes` in the new manifest and `superseded_by` in the old entry.
4. **Verify before CURRENT.** A new result starts as UNCHECKED. Only an independent verifier sets CURRENT, and the manifest then gives `verified_by`.
5. **Do not use memory as a results store.** Write results, paths and numbers to the registry. Write rulings and tool behaviour to memory.
6. **No session-workspace paths.** Do not put a path in a session workspace into a committed file.
7. **Start each module thread from its registry.** Read the registry, not memory, to find the current inputs and products.

## 7. Restricted material

The tmp/ avionics files and three files in `library_full_audit/MH370/` (two MH371 files and Ulich's fuel workbook) are restricted. Their entries have `restricted: true` and status CURRENT_WITH_CAVEATS.

1. Use them internally only.
2. Record each use in `results/restricted-sources-ledger.md`.
3. Do not cite or publish them before the review.

Source: Pete's decisions of 9 and 10 October 2026 (the ledger and memory records). The files stay where they are.

## 8. How to use the scripts

Do these steps from this folder.

1. Install the pre-push check once in each clone: `make install-hooks`.
2. Do the check before you commit: `make check`. A FAIL stops the push. Correct the FAIL item. Do not use `git push --no-verify`.
3. Make the registry again after records change: `make registry MEMORIES=<memory export JSON>`. This runs `backfill`, `build` and `index`.
4. After a registry rebuild that Pete accepts, record the new baseline: `make baseline`. Then commit the baseline files.
5. To see the violations that existed before the rules: `make report`. This writes `existing_violations.tsv`. We list these violations; we do not correct them.

## 9. What the check does

| Check | What it looks for | Result |
|---|---|---|
| C1 | A new result folder without a valid `manifest.json`; a new loose file at the top of `results/` or in `results/<module>/`. Permitted at the top of `results/`: `INDEX.md`, `README.md`, `restricted-sources-ledger.md` and the module citation ledgers `<module>-references.md` / `.bib` | FAIL |
| C1 | A new file in an old result folder that has no manifest | WARN |
| C2 | A session-workspace path in a new path, in a new text file or in a new line of an old file | FAIL |
| C3 | A version suffix in a new file name or a new folder name | FAIL |
| C4 | A registry id that occurs two times, a `superseded_by` target that does not exist, an unknown status, or a root in a session workspace | FAIL, or KNOWN if it is in the baseline |

"New" means: not in `baseline/tracked_paths.txt.gz`. Thus the check does not fail on the old tree.

## 10. Limits

1. The build does not hash the exchange folder again. It uses `SHA256SUMS` files and the hashes from `exchange_inventory.py` (25 October 2026). That script did not hash a file of 1 GB or more that has no `SHA256SUMS` entry. `COVERAGE.md` gives the number and the names.
2. The external drive was not connected to the session. The entries for the drive come from the item lists in `~/Downloads/archive-tools/`. The `VERIFIED-*.txt` lists are on the drive, so the registry does not confirm the copies.
3. Code on module branches is recorded by branch, commit and tree. The registry does not merge branches.
4. `check_project.py` (working tree, `--commit`, `--pre-push`) and `--make-baseline` work in a blobless sparse clone. They read only new paths and the registry files. `--report-existing` reads every file: use a full clone for it.
5. Platform artifacts are not in this registry yet.

## 11. Memory notes

On 25 October 2026 the memory track moved rows out of project memory. The folder `memory-notes/` holds the rows that moved to the registry. The module citation ledgers (`results/<module>-references.md`, `paper/JON-RULES.md`) hold the rows about external sources.

**These rows are records of what memory said. They are not verified facts.** Before you use a value from a row, check it against its source. Each row gives:

1. `mem_id`: the id of the memory row.
2. `registry_entry`: the registry entry that the row is about. If no entry matched, the row links to the note entry of its topic (`<module>.memnote.<topic>`).
3. `original_text`: the text of the row in the memory export (artifact version ba131e4c-350c-4db5-8b56-a61b3f2772f9).
4. `verification_status`: VERIFIED, PARTIAL or UNVERIFIED, from the memory track. `verified_by` and `verification_evidence` tell how.

The repository is public. Thus we changed the text in these cases, and the row tells you so in `text_flags`:

1. If the text names a restricted source, we do not show the text. The row gives the export row to read instead.
2. We replaced each session-workspace path with `<session workspace path>`.
3. We removed spending amounts.

`import_memory_records.py` makes these files. Do not edit them by hand. Hydroacoustics rows are not here (phase 2).
