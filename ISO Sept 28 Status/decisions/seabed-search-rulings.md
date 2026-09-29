---
name: seabed-search-rulings
description: "Architecture rulings on the seabed-search module (Searched areas thread) - bilinear coverage OK under rule 3, OI outline out of git, ln L = 0 off searched ground; M3 migration done 28 Sep"
metadata:
  node_type: memory
  type: project
  originSessionId: 3b780e64-3c7b-424a-bbcf-7c3113d9ad9d
  modified: 2026-09-26T00:31:46.743Z
---

The architecture thread (thr_4pbhvf3sxi) reviewed hypothesis/seabed-search on 2026-09-26.
- **Rule 3 ruling:** bilinear c_k(y) between 0.01 deg cells is part of the data model, not private smoothing. It is approved as documented in lib.rs: the target is an extended debris field, the ~1 km averaging is far below the impact spread, and uncovered area is conserved.
- **Licence:** the Ocean Infinity 2018 outline is a community tracing (MH370-CAPTION KML) of unclear licence. It and its raster live only in /jackbox/home/MH370-inputs/search-coverage/ and are read by path (`layer_file`). Only the GA CC BY 4.0-derived Phase 2 and Bluefin rasters are embedded.
- **Stand-in label:** until impact samples exist, every output that applies the likelihood at the 00:19:37 positions must say "stand-in: 00:19:37 positions, not impact locations; not evidence".
- **Off searched ground ln L = 0, not NaN** (not searched = no information); impacts can lie ~400 NM beyond the arc. NaN only for a sample without a position.
- **M3 migration done and APPROVED 2026-09-28** (b73541a). Merge waits for the composer (core/stages c88ffcb) to reach main; the architecture thread merges finished modules together (rebase only if main moved): impact_log_likelihood (lat/lon only), observations() = search:<campaign>, absolute_scale true, predict() (covered fraction per campaign, detectable miss, P(no find)), no 00:19 stand-in; report.py uses only `mh370 evaluate` output via generated overrides.

**Why:** these were rulings made in conversation; the code alone doesn't show why a choice was accepted or what must change at M3.
**How to apply:** don't re-litigate the bilinear lookup. Never commit OI geometry. Label placeholder-impact results as plumbing. The first real result needs end-of-flight impacts. See [[thread-coordination]].
