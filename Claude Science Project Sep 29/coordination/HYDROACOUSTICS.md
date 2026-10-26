# HYDROACOUSTICS inbox

Read at the start of each working session and before every commit. Append new entries at the end, dated in UTC.
**This inbox was started again on 26 Oct 2026.** The history from 7 to 26 Oct 2026 is in `coordination/archive/HYDROACOUSTICS-2026-10-07-to-2026-10-26.md`. It is background only. Where it differs from `threads/status/hydroacoustics.md`, the status file is correct.

## 2026-10-26 — REPOSITORY RULE for all modules and all threads (Pete: "please pull everything in and instruct all modules and threads to update the respository going forward"; decisions P62, P66)
From the hydroacoustics overview session (8b907e71), for every module and every thread, on any profile.
1. The repository is the record. A result that exists only as an artifact, in a session workspace or in a kernel is not a result. Commit data, code and results before you report work as done.
2. Commit at the end of every work step, not only at the end of the thread. A thread can stop at any time.
3. Data go into the module's data store only through its build scripts. Hydroacoustics: add a block to `engine/hypotheses/hydroacoustics/registry/data_db/imports.yaml`, rebuild, record the SHA-256. One rebuild at a time; say in the module inbox when you rebuild. Never edit a database by hand.
4. Results go to `results/<module>/<run id>/` with `manifest.json` (schema `registry/manifest.schema.json`). On a module branch: `results-data/<run id>/` with `manifest.json`. No loose files. No `-v2` or `-FINAL` names: give a new run id and set `supersedes`.
5. Registry: add the entry with status UNCHECKED. Only an independent verifier sets CURRENT. Then run the module registry build and the project registry import (`registry/README.md`).
6. Push: install the pre-push hook once per clone (`make -C "Claude Science Project Sep 29/registry" install-hooks`). Never use `--no-verify`. Run `git pull --rebase` before every push. Read branch heads with `git ls-remote`, never from memory.
7. Artifacts are viewing copies for Pete. Put the artifact version id in the manifest (`artifact_version_id`). The file in the repository is the source.
8. A sub-agent may save artifacts and not commit. The parent thread then commits the sub-agent's deliverables before it reports.
9. Read status from the registry and from `threads/status/<module>.md` where that file exists. Memory rows are context, not authority.
10. If you cannot push (no credential, the hook fails), say so at the top of your report and list the files not committed, with their artifact version ids.
-- hydroacoustics overview session 8b907e71, 26 Oct 2026. The same rule is now in every module profile prompt and in the default profile (MH370 project only).

## 2026-10-26 — Two new hydroacoustic threads and their work orders (from the hydroacoustics overview session 8b907e71, at Pete's request)
- **Forward model** (Hydroacoustic Module profile): `threads/work-orders/hydroacoustics-forward-model-order-2026-10-26.md`. It continues the plan of session c764a583 after c764a583 commits its Phase 1 outputs (noise model, airgun level unit audit, bearing check, 777 source physics).
- **Detection model, clean sheet** (Hydroacoustic Module profile): `threads/work-orders/hydroacoustics-detection-order-2026-10-26.md`, with the draft specification `threads/specs/hydro-detection-model-spec-2026-10-26.md`. Step D0 is the specification review with Pete.
- **Ownership:** forward model owns `prepare/forward/`, the transmission-loss grids, source and coupling code and the simulated-arrivals files. Detection owns `detect/`, the interface schema and validator, the injection bench, the known-event association and the Kadri package. The interface schema `interfaces/simulated_arrivals.schema.json` is written by detection (step D1) and agreed by the forward model here in this inbox.
- **Data store:** the repository import of 26 Oct (sub-agent of 8b907e71) adds a declarative import stage (`registry/data_db/imports.yaml`). Rebuild one at a time and announce it here before and after.
- **Overview:** session 8b907e71 keeps the overview for Pete (P72). Post progress, results and questions for the overview here. The overview session reads this inbox and the thread transcripts, and updates `threads/status/hydroacoustics.md`.
-- hydroacoustics overview session 8b907e71

## 2026-10-26 — For session c764a583 (Aircraft Impact Acoustic Source Survey)
- Please commit your Phase 1 outputs under the repository rule above (run folders with manifest.json, UNCHECKED until your verifier passes), and post an entry here that lists them.
- The overview session recommends to Pete that the forward-model thread then takes over your phases 2-5, and that the detection test of your phase 4 moves to the detection thread (clean sheet, P57). Pete decides this; wait for his message.
-- hydroacoustics overview session 8b907e71
