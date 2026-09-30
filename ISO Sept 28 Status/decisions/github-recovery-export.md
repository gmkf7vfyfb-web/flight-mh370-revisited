---
name: github-recovery-export
description: "How the \"ISO Sept 28 Status\" recovery package was built and pushed to Pete's public GitHub repo; what is never published; where the push token lives"
metadata:
  node_type: memory
  type: reference
  originSessionId: b321a56a-4f19-4c04-acbd-d5031b94cf81
  modified: 2026-09-29T14:39:43.089Z
---

On 2026-09-29 the architecture thread pushed "ISO Sept 28 Status" to Pete's public repository gmkf7vfyfb-web/flight-mh370-revisited. It is commit 7fe30c2 on main, 542 files, 69 MB. Pete chose to publish while the repository is public, even though its AGENTS.md says to keep it private until reviewed.

**Rebuild:** `python3 /jackbox/home/MH370-export/build_export.py` builds the mechanical parts into /jackbox/home/MH370-export/ISO Sept 28 Status/. They are:
- an anonymised git bundle of all branches, with commit-map.tsv;
- a copy of main;
- branch diffs and uncommitted work;
- small results, plus NOT_COPIED.csv;
- input manifests;
- prompts, decisions and environment.

README.md and STATUS.json are hand-written, kept in handwritten/ and copied in afterwards. Then run sha256sum to regenerate MANIFEST.sha256.

**Push:** use the sparse, blob-less clone at /jackbox/home/MH370-export/repo. Authenticate with a one-off credential helper that sources /jackbox/home/.mh370-secrets/github.env (GITHUB_TOKEN, fine-grained, Contents RW, from Pete via `iso secret request`). Never print or persist the token. Commit as "MH370 iso agents <mh370-iso@invalid>".

**Second commit 79afc63 (29 Sep, Pete's request):** inputs/ now holds the downloaded third-party inputs as obtained (198 files, 373 MB), via /jackbox/home/MH370-export/add_inputs.py.
- inputs/acars/ is included and marked MH371 truth, off-limits to the MH371 control (the core thread recorded this in status.md, c3d9c67).
- Items with an explicit restrictive notice are linked to their public sources, not copied: Ulich's "confidential source" Boeing FPPM tables, the SIR Appendix 1.6E Boeing copyright, and the EUROCONTROL/MathWorks/Lissys "all rights reserved" documents.
- The Ball compilation is included with its ARINC 741 page removed.
- Items over 95 MB (ocean, IMOS zip, ERA5/MERRA-2 grids, particles) are listed for the Hugging Face companion dataset.

Pete's view is that downloaded items are public. The line I applied is explicit restrictive notices, not "found online".

**Third commit e8fedbf (29 Sep):** "Archive ISO Pre Sept 28", 292 MB, 5,367 files, from /jackbox/home/MH370-export/build_archive.py.
- Covers the 29 older MH370-project threads. Each has scrubbed log.txt, history.json, final-output.txt, meta.json, storage-index.csv (every stored file with sha256 and location) and its small stored files.
- The three 7 Sep old-codebase copies (MH370-v01-share, the withdrawn share, release-v0.1) go in as small files, de-duplicated by sha256, indexed in codebases/INDEX.csv.
- Scrubbing covers emails, credential patterns, the Modal account name and the iso user ID. The identifier list lives in /jackbox/home/.mh370-secrets/personal-ids.json, never in the published script.
- Withheld from GitHub: 4 credential-like files, and PHaRLAP (DST licence forbids redistribution).
- Left off entirely: the personal and other-project threads.
- Drive: /jackbox/home/MH370-export/gdrive-archive/upload-archive.sh uploads the complete thread stores to "MH370 ISO large files/Archive Pre Sept 28/thread-storage". It skips the Astra thread's 61 GB bulk outputs, per Pete, and the venvs.
- It also uploads the codebase archives (the broad-reproducibility tar.zst and reports zip, the withdrawn v01 complete tar.zst, the whole release-v0.1) to .../codebases.
- The first Drive upload (gdrive/upload.sh) covers the ISO Sept 28 Status large files, under "MH370 ISO large files/{MH370-inputs,repo-data,runs}". It uses the rclone config /jackbox/home/.mh370-secrets/rclone.conf (scope drive.file).

**Gotcha:** never `pkill -f` with a pattern that also appears in your own command line; it kills the calling shell (exit 144).

**Originally left out; now superseded by the second commit for downloaded inputs:**
- the Ulich/Boeing fuel tables, the Boeing simulator runs and plots of them;
- the Ball/ARINC spec;
- the OI 2018 outline;
- the raw SITA log;
- the ACARS workbook (MH371 truth);
- papers of mixed copyright;
- correspondence drafts Pete hasn't approved (the Kadri cover letter and requests, the Metz/Royer asks);
- raw transcripts;
- the git author email.

**Why:** Pete wants a recovery point that any agent or system can resume from. The repository is public, and its own AGENTS.md forbids redistributing restricted Boeing/Inmarsat/SITA material.
**How to apply:** for a later status push, rebuild into a new, versioned folder name; don't overwrite a released folder (that repository's rule). Rerun the secret/email/restricted-name scans before pushing. See [[thread-coordination]].
