# Archive ISO Pre Sept 28: the older MH370 iso threads (13 Aug – 23 Sep 2026)

This folder is for recovering, reusing, continuing and reviewing the work of the 29 MH370 iso threads that predate the modular rebuild. The rebuild is documented in the sibling folder `ISO Sept 28 Status`, which covers the current threads.

- **Built:** 29 September 2026, by the iso thread "Modular Architecture".
- **Researcher:** Pete Large.

## Read this first

These threads worked on the **previous codebase**: about 100k lines of Rust, 19k of Python, 126 markdown files and about 16 GB of runs, with no version control. It was replaced by a lean rebuild on 23–25 September, and deleted on 26 September at Pete's request. What survives is in this folder and on Google Drive:
1. three copies of that codebase from 7 September, in `codebases/`;
2. each thread's stored files, in `threads/<id>/storage/` and on Drive;
3. archives the "Clarify EDU ChatGPT limits" thread recovered from Google Drive;
4. each thread's conversation log.

**Status of the results.** Results from these threads come from pipelines that were often unconverged or unstable. Some were withdrawn by the threads themselves. Examples:
- a "rigorous 21°S" drift result was later withdrawn;
- a conditional Pleiades run collapsed to an effective sample size of 5.6–9.1 out of 150,000;
- the last MH371 check's two runs disagreed by about 98 NM.

Under this repository's AGENTS.md, treat them as **Reconstructed analysis** or **Diagnostic/sensitivity**, never as findings, unless the current estimator re-derives them.

## Contents

| Path | What it holds |
| --- | --- |
| `threads/<id>-<name>/meta.json` | Title, dates, status, environment, and counts of stored files |
| `threads/<id>-<name>/log.txt` | The conversation timeline: prompts, agent messages, commands and outputs. Emails, account IDs and credential-like strings are scrubbed |
| `threads/<id>-<name>/history.json`, `final-output.txt` | Prompt history and the thread's last message (scrubbed) |
| `threads/<id>-<name>/storage-index.csv` | **Every** file the thread stored, with size, SHA-256, and whether it is on GitHub and on Drive |
| `threads/<id>-<name>/storage/` | The stored files small enough for Git: reports, summaries, figures, scripts, logs |
| `threads/THREADS.json` | All 29 threads' metadata in one file |
| `codebases/v01-share/`, `codebases/v01-share-withdrawn/`, `codebases/release-v0.1/` | The three 7 September copies of the old codebase. Small files only (source, configs, docs, small outputs), each unique file stored once |
| `codebases/INDEX.csv` | Every file in the three copies (2,811), with SHA-256 and where it is |
| `ARCHIVE.json` | Machine-readable index of this folder and the Drive layout |
| `build_archive.py` | The script that assembled this folder |
| `MANIFEST.sha256` | Checksums of every file here |

**On Google Drive**, in Pete's private "MH370 ISO large files/Archive Pre Sept 28":
- `thread-storage/<id>/`: the complete thread stores, with one exception. The 61 GB of bulk particle and continuation outputs of the "Review new Astra thread" analysis were left off at Pete's request; their checksums are still in its `storage-index.csv`.
- `codebases/`: the complete archives, from which every old codebase can be rebuilt:
  - `v01-share/MH370-v01-broad-reproducibility.tar.zst`, 1.3 GB;
  - `v01-share/MH370-v01-broad-reports.zip`;
  - `v01-share-withdrawn/MH370-v01-complete.tar.zst`, 0.5 GB;
  - the whole `release-v0.1/` folder.

## The threads

Dates are created → last updated, UTC. "Stored" is the thread's own storage, apart from the old repository.

| Dates | Thread (iso ID) | What it did | Stored |
| --- | --- | --- | --- |
| 13 Aug | Create knowledge repository foundation (`thr_fvvxab6qkf`) | Wide-net evidence audit and ontology. It concluded that the evidence supports a southern-Indian-Ocean, 7th-arc loss family but not a uniquely precise latitude | – |
| 14–25 Aug | OLD MH370 Core Analysis (`thr_h6z2fv56n6`) | The first core filter and its production verifier (cost, segment and hash checks) | 16 MB |
| 14 Aug–15 Sep | Hydroacoustic Waves & OLD Pleiades (`thr_wkiec86jt2`) | Kadri (2024) figure extraction, and 4 million source/timing samples across the end-of-flight alternatives, with noise controls | 12 MB |
| 16 Aug–15 Sep | Passive Radar WSPR / RxGain Testing (`thr_e7vf6bjiyt`) | WSPR passive-radar localisation, with PHaRLAP ray tracing, and received-power gain tests. A truth-separated MH371 rerun did not recover the flight. See the note on blindness below | 159 MB |
| 20–21 Aug | Launch particle filter visualization (`thr_39x6swebwz`) | A particle-filter visualisation app prototype | – |
| 21–25 Aug | OLD Analyze MH370 object list & Ocean Drift (`thr_bsdvixiiae`) | Debris object list and drift; paper-ready methods text | 2 MB |
| 23 Aug | MH370 antenna gain model – continuation (`thr_b6qutrkpmh`) | Reviewed the Ball AES gain-pattern analysis (D-0031) | – |
| 23 Aug–2 Sep | Study end-of-flight aspects (`thr_dvhqyvtdcu`) | End-of-flight modelling and previews | 0.2 MB |
| 23 Aug–18 Sep | Manage publication papers (`thr_2hjfxguxv4`) | Manuscript and review packs for Pete | 3 MB |
| 24–27 Aug | Continue Pleiades development (`thr_ym8fvgh7s3`) | Pleiades conditional analysis; provenance and manifests | 8 MB |
| 24 Aug–7 Sep | Continue MH370 core analysis (`thr_94ecfzphq2`) | Core filter work. The last MH371 experiment's two runs disagreed by about 98 NM, failing the stability requirement | 20 MB |
| 25–26 Aug | Flight Simulation Model (`thr_bk9z5pvb86`) | Design of the post-flameout transition kernel | – |
| 25–28 Aug | Ocean Drift New (`thr_pexmvwn97e`) | Drift runs, and a fix to the memory-bound data loader | – |
| 27 Aug | Audit public B777 EOF aerodynamics (`thr_3m79zaqax3`) | Concluded that no public, redistributable aero model spans the required envelope | – |
| 27 Aug | Audit MH370 fuel and performance inputs (`thr_d6ja5i7xjp`) | Blocked by the host sandbox | – |
| 27 Aug | Implement MH370 fuel performance audit full mode (`thr_mcykbgtinu`) | Ulich fuel-model recreation: ACARS-predicted burn 5,384 kg against 5,400 kg observed | – |
| 27 Aug | Extend MH370 ERA5 atmosphere full mode (`thr_trg49zc5v7`) | The ERA5 grid, 17:00–01:00 UTC, 500–43,000 ft | – |
| 27 Aug | Extend MH370 ERA5 atmosphere coverage (`thr_vxv9jpjdtq`) | Blocked by the host sandbox | – |
| 27 Aug | Rebuild MH370 searched-area evidence full mode (`thr_kwwu6p8qdu`) | Seabed-search coverage package: report, map and evidence register | – |
| 27 Aug | Rebuild MH370 searched-area evidence (`thr_p2ps2usx67`) | Blocked by the host sandbox | – |
| 27 Aug | Recreate and audit redistributable code (`thr_ytrf242vwy`) | Ended in error, with no output | – |
| 27 Aug | Build MH370 Search Evidence Package (`thr_j7d2aaq2c5`) | Ended in error, with no output | – |
| 28 Aug | Audit better-mixed versus conditional (`thr_3qka8sb6tr`) | Hash-checked comparison runs of mixed versus conditional end-of-flight sampling | – |
| 28 Aug | Finish interrupted impact runner (`thr_s83ha6x9tj`) | Impact-runner completion and lint | – |
| 28 Aug | Audit dynamic ERA5 EOF transitions (`thr_wherses95g`) | End-of-flight timing against the ERA5 time span | – |
| 29 Aug | Review transcript for bugfix (`thr_hf6wc3deg2`) | Traced a thread failure to an iso timeline/watchdog bug (15,890 events, 24 MB log) | – |
| 6 Sep | Ocean Drift — Sept 6 sensitivity atlas (`thr_qpqec5d6kr`) | Drift sensitivity atlas; plot conventions | – |
| 7–18 Sep | Review new Astra thread (`thr_rzreetwcyu`) | Review of the branching filter: overnight, forward-backward, flight-assumption and synthetic fuel-recovery analyses, with antenna-conditioned runs. Replays reproduced the saved results exactly; the weight collapse occurs at the 19:41 contact | 62.7 GB (2.6k files on GitHub; bulk off Drive) |
| 19–23 Sep | Clarify EDU ChatGPT limits (`thr_rkyj8pbpxt`) | Recovered earlier work from Google Drive (the igogu and waypoint analyses, a "Rerun" core recovery); an independent-root engine | 11.0 GB (830 files on GitHub) |

Each thread's `log.txt` is the fullest record. Its `final-output.txt` says where it stopped.

## What the new estimator reused, and what it learned

**Reused, and re-derived in the current code:**
- the seabed-search miss likelihood and its hand fixture;
- the Kadri (2024) Table 1 and Figure 9 extraction, now used in the hydroacoustics tests;
- the Large (2019) antenna work, now in the parked antenna-gain module;
- the Ulich fuel audit, feeding the fuel plan;
- ERA5 extraction;
- the Boeing simulator runs, used for the end-of-flight calibration;
- small recovered files, now in `ISO Sept 28 Status/inputs/recovered-v01/`.

**Lessons carried forward** (see `ISO Sept 28 Status/decisions/`):
- **Version control:** without it, ledgers, copies and "withdrawn" variants multiplied and contradicted each other.
- **Sparse filters:** they can manufacture the published northern shoulder by chance.
- **Published hydroacoustic traces:** these are filtered, decimated and analyst-selected, and cannot support a likelihood.
- **Acoustic coupling:** it is uncertain by orders of magnitude.
- **Drift results:** they were unstable. GDP-based drift flipped between 34°S and 21°S with a pseudocount choice, and HYCOM moved from 30°S to 37°S without converging.
- **Blind controls:** the old MH371 control was not blind, because its window moved after the truth was seen.

## Not in this folder

| Item | Where it is, and why |
| --- | --- |
| The PHaRLAP ray-tracing distribution (the WSPR thread's `Attachments/` and `pharlap-4.7.4-private/`) | Drive only. DST's release terms forbid redistribution to third parties "under any circumstance" |
| Four stored text files that looked like credentials | Drive only; marked "withheld" in their index |
| Bulk outputs: particle arrays, `.npz`, large JSON and CSV, archives | Drive; checksums in the indexes |
| The 61 GB of bulk Astra outputs | Left off Drive at Pete's request; checksums in `storage-index.csv` |
| Python virtual environments, vendored Rust crates, build output | Regenerable |
| The `.zip` twin of the withdrawn v01 archive | Same content as its `.tar.zst` |
| Personal and other-project iso threads | Not MH370 work |

Emails were redacted in 12 copied text files and in the logs.

## MH371 truth: off-limits to the MH371 control

The old codebases contain MH371 truth data and truth-based validation, for example:
- `codebases/v01-share/v01/workspace/inputs/controls/mh371-truth.csv`;
- `.../runs/mh371/broad-flight-truth-control/`;
- `.sources/large-2019-antenna-gain/outputs/mh371_surface_truth_audit.csv`;
- the Ulich `official_acars.json`.

The current MH371 known-flight control is blind: only its scorer may read truth. No agent building, configuring or tuning the estimator may open these files, as with `ISO Sept 28 Status/inputs/acars/`.

## How to use it

- **To follow a thread:** read its `log.txt`, then `final-output.txt`. Find its files in `storage-index.csv`. Small ones are in `storage/`; the rest are on Drive, under the same relative path in `thread-storage/<id>/`.
- **To rebuild an old codebase:** download the matching archive from Drive `codebases/`, then run `zstd -d -c MH370-v01-complete.tar.zst | tar -x`. Check it against its `DOWNLOADS.sha256`.
- **To locate any file by content:** search for its SHA-256 in `codebases/INDEX.csv` or `threads/*/storage-index.csv`.
