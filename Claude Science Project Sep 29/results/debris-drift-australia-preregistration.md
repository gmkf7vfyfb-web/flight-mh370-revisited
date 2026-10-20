# Pre-registration: Australian non-recovery term (drift), 12 Oct 2026

Registered before any production or pilot result (a 3-node, 600-particle smoke checked the code path only; not evidence).
Requested by architecture (OCEAN_DRIFT.md 14:15Z, gap G26). Primary chosen by Pete (ask, 12 Oct ~16:10 UTC).

- **Segments:** 10 Australian coastal segments by ABS remoteness class x region (ASGS Ed. 3 RA 2021), boxes from
  `prepare/pilot/make_australia_segments.py` (commit 22530dd7); find coasts S1-S6 unchanged. No finds on any Australian segment.
- **Levels (relative identification probability, prior mean of ln nu, sigma 1, independent by block, 256 common draws):**

| option | city + inner regional | outer regional | remote + very remote | role |
|---|---|---|---|---|
| **B (primary)** | ln 1 | ln 0.3 | ln 0.05 | every period (I1, I2, I3) |
| A | ln 0.1 / ln 0.5 / ln 1 by period | same | same | sensitivity (equal to find coasts) |
| C | ln 0.3 | ln 0.1 | ln 0.02 | sensitivity (low) |
| off | ~0 | ~0 | ~0 | comparison (current result) |
| searcher | as A, plus ln 3 on S3 and S5 in I3 | | | sensitivity (Gibson's searches) |

  Find coasts S1-S6: ln 0.1 / ln 0.5 / ln 1 for I1 / I2 / I3 (unchanged, provisional).
- **Window:** 8 Mar 2014 - 30 Jun 2016 (the existing window end).
- **Domain:** must reach 160 E before the pilot (requested from ocean transport); until then the term is reach-limited and labelled.
- **Pilot:** GLORYS12, every 4th of the 710 run A nodes (178), 10^5 particles, about 4 h under the heavy lock, after run I (Pete).
- **Label until in production:** "Australian non-recovery not modelled" on every drift product.
