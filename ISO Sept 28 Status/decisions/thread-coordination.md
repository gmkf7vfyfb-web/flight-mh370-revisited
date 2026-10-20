---
name: thread-coordination
description: "Which iso thread owns which MH370 topic, where worktrees and inputs live, the heavy-job lock rule, and the near-full disk"
metadata:
  node_type: memory
  type: project
  originSessionId: 3b780e64-3c7b-424a-bbcf-7c3113d9ad9d
  modified: 2026-09-28T23:07:13.708Z
---

Since 2026-09-25, Pete Large runs MH370 as one iso thread per topic in project proj_pm8k5krhiy. Each thread works in its own git worktree under /jackbox/home/MH370-worktrees/<name>. Only the core-estimator thread works in the shared checkout /jackbox/home/MH370. Each worktree symlinks data/*.bin, .venv, runs/davey2016 and data/external from the main checkout; data/external is ignored via .git/info/exclude.

Who owns what:
- **Modular Architecture**, thr_4pbhvf3sxi. Owns the architecture. Reviews every branch before merge, handles core_requests, sets merge order. Writes no module code.
- **Investigate persistent agent issue**, thr_mgewhqvb78. Owns the core estimator: base estimate and shoulder investigation, route-guidance plan hook, and fuel/performance after phase 1 (see [[fuel-performance-plan]]).
- **Implement executable core filter**, thr_dkvnnfnn3b. Owns the local app: describe.rs, ui/.
- **Core stages & composer**, thr_6wkhvpqx8k, branch core/stages. Builds phase 1: hand-off, end-of-flight stage, impact hook, alternatives, composer.
- Module threads, each on hypothesis/<name> unless noted:
  - End of flight: thr_kaycpkjz9k.
  - Ocean drift: thr_faie5jqc7p. Builds the shared crates/ocean component on core/ocean-transport, then hypothesis/debris-drift.
  - Pleiades: thr_ec96wswyz6.
  - Searched areas: thr_uduhvqttbk, on hypothesis/seabed-search.
  - Hydroacoustics: thr_gbqx8u9yfp.
  - Ocean impact to ocean floor: thr_7e786pehut, on hypothesis/settling. Created 2026-09-28 at Pete's request: the settling model (contact point to wreckage resting place), a separate module rather than part of Ocean drift.
  - Antenna gain: thr_vimeq9ezrd, on hypothesis/antenna-gain. Created 2026-09-28: set up from Large (2019) and the v01 antenna crate, then parked, not integrated (see [[pete-deferred-until-stable-impact]]).
- WSPR is a low-priority option, mainly to show whether it works.
- Prior-work reference: the 7 Sep v01 share snapshot at /jackbox/home/MH370-v01-share-withdrawn-one-turn-20260907/v01/workspace is still on disk (read-only), and holds the old antenna crate and .sources.
- All threads run on one Claude account. On 2026-09-28 its weekly limit stopped every thread mid-turn (status "error", processes still attached). Pete switched accounts; each thread then needed a `--mode auto` "continue" message.

Where things live:
- Master prompts: /jackbox/home/.iso/thread-storage/thr_4pbhvf3sxi/prompts/.
- Large, licensed or not-redistributable inputs: /jackbox/home/MH370-inputs/, catalogued in its INDEX.txt, never in git.

**Why:** several agents share one repo and one machine (6 cores, 23 GB RAM). Collisions on core files, CPU, RAM and disk have happened; the MERRA-2 run was killed out of memory. Separate threads also keep the architecture thread's context lean.

**How to apply:**
- Before editing crates/flight, filter.rs, config.rs, main.rs or crates/hypothesis, or before merging, announce to thr_4pbhvf3sxi and thr_6wkhvpqx8k.
- Route module questions to the owning thread with `iso thread tell`.
- Wrap any job expected to take more than ~10 min or ~4 GB in `flock /jackbox/home/.mh370-heavy.lock <cmd>`.
- The disk was 96% full on 2026-09-25, about 23 GB free, and 98% on 2026-09-26. The host btrfs keeps snapshots, so deleting files may not free space until Pete clears them. On 2026-09-28 (8.8 GB free), replacing a file created 26 Sep 00:41 freed nothing. So the last snapshot postdates it, probably taken at the host update and reboot around the 26 Sep outage. Only files created since the reboot can be freed. The container can't reach the snapshots even with sudo (no CAP_SYS_ADMIN, no block device); Jack or Pete must clean them on the host. By 23:00 UTC on 2026-09-28, after a host restart at about 18:51, the disk had 41 GB free, so the snapshots had been cleared. New rule sent to all threads: keep at least 15 GB free and announce any single write over 3 GB. Rules from thr_4pbhvf3sxi, 2026-09-26, until space is recovered:
  - check `df -h /jackbox` before any write over ~1 GB and leave at least 8 GB free;
  - keep runs at smoke or fixture scale, so no full `make hypothesis` (about 5 GB of final.npy);
  - stream or subset large sources rather than download them, and delete your own scratch.
