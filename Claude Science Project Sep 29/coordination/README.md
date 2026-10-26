# Coordination inboxes
> **STANDING RULE ON LABELS (Pete, 22 Oct 2026). Applies to every agent, thread, track and sub-agent.**
> 1. **No label may be added without Pete's explicit approval.** This covers every label that stops, limits or discounts the use of a source, dataset or file: "closed access", "paywalled", "not held", "unobtainable", "restricted", "blocked", "unusable", "GAP" set because of access, and any new one of that kind.
> 2. Pete holds the right to use everything stored in the repo, the Google Drive and the project source folders. A publisher's access status is not a reason to avoid, discount or leave out a source.
> 3. If a source cannot be fetched: search the artifact store (filenames can be raw DOIs, such as `art%3A10.1007%2F...pdf`), the repo papers folders on both branches, ~/Downloads and the Drive; then write exactly **"not retrieved — ask Pete"**, record where you searched in `results/source-access-ledger-2026-10-22.csv`, tell Pete, and carry on. Nothing is left out of an analysis or a note because of it.
> 4. To use any other label of this kind, ask Pete first and wait for his answer. Caveats Pete has already required (for example "PREDICTIVE, NOT CALIBRATED", C1/C2, "digitised", chart footnotes, provenance records) stay as written.


There is no live channel between sessions. A session can read another's transcript after the fact
but cannot write to it, so anything another session must act on goes here.

- `architecture.md` — the architecture session's inbox. Module sessions write here.
- `<MODULE>.md` — one per module. The architecture session writes; that module reads.

**Convention, carried in every module prompt:** read your own inbox at the start of each working
session and after any long gap, and treat it as authoritative over anything you remember. Append
rather than overwrite, date each entry, and sign it with the module name. An entry that has been
acted on is marked done rather than deleted — the inbox is a record, not a queue.

Urgent items still go through Pete. An inbox is asynchronous by construction.

## Files held off the Mac (Porsche drive)

Date: 26 October 2026. Applies to every module, thread, track and sub-agent.

Some project files are not on the Mac. They are on Pete's external drive, folder `/Volumes/Porsche 1TB Backup/mh370-archive/`. The registry lists them (root `XDRIVE`, holder "Porsche drive (available on request from Pete)"); `results/INDEX.md` lists them in the section "Files held on the external drive - ask Pete".

What is on the drive:
1. `artifact-store-npy/`: the archive of the platform artifacts final.npy and evaluate.npy (96 .npy files, 39.0 GB, all 346 versions; README.md, SHA256SUMS and `cited-versions.csv`, which maps each version id to its file). This is the only copy. The platform artifacts were deleted on 26 Oct 2026, with Pete's approval. Verified 96 of 96 by SHA-256 (`~/Downloads/archive-tools/VERIFIED-npy-20261026-1129.txt`). Registry entry: `project.ex.archive-artifact-store-npy`.
2. Batch 3 (17 Oct 2026): the run I downstream products (`mh370-exchange/<module>/run-i` for debris-drift, settling, pleiades, hydroacoustics, searched-areas), `composer/run-i-ruling-oct15`, `pleiades/columns`, and the older run D-he columns (`next-run-d-he` for settling, hydroacoustics, searched-areas).
3. Carry-over items: `debris-drift/run-i-dive`, `core/run-j/run-j-smoke-waypoints`, and the IMOS archives `mh370-inputs/hydroacoustics/imos/MH370.zip` and `Portland_MH370.zip`.
4. Batch 4 (20 Oct 2026): the per-seed outputs of the run J northern supplement (`end-of-flight/run-j-supplement/north-k2`, `north-k2b`, `north-k2-xd256`, `north-k2b-xd256`, `north-k2-a1branch`).
5. Earlier batches (Tier A and Tier B, about 78 GB, 16 Oct 2026, as Pete reported). Their item lists are no longer in `~/Downloads/archive-tools/`, and their VERIFIED lists are on the drive only. Ask Pete for the list.

Items 2-4 come from the item lists in `~/Downloads/archive-tools/archive-to-porsche.sh` and `archive-to-porsche.v3.sh`. Of these, only `Portland_MH370.zip` is still on the Mac (checked 26 Oct 2026). Their VERIFIED lists are on the drive, so the registry does not confirm those copies.

Rules:
1. Sessions cannot read the drive.
2. To use a file from the drive, ask Pete to copy it back to `~/Downloads/mh370-exchange/`. Then check each file against the SHA-256 in the registry manifest before you use it.
3. Do not take a file as lost because it is not on the Mac. Look in the registry first (`registry/REGISTRY.json`, `results/INDEX.md`).

Other access rulings (Pete, 26 Oct 2026): Ulich's fuel workbook and the `tmp/` avionics files are in the repository, and Pete accepts that they are public; record each use in `results/restricted-sources-ledger.md`. The MH371 data (ACARS reports, EHM export, SATCOM data and values derived from them) is not confidential.
