# Core request 20, Phase 1 smoke (Pete GO 15 Oct 2026)
Design: `results/item10-phase1/design-core-request-20.md`. Job: `engine/scripts/job-request20-smoke.sh`.
Analysis: `engine/scripts/r20_smoke.py` (standard library only).

**Filter chain.** Run I repro-radar's chain without `handoff-lookahead-d.toml` and `server-i-repro.toml`, then
`smoke-base.toml` and one pass file:

    davey2016-inmarsat no-exhaustion-prior s1..s6 reference-snapshots radar-full s7 s8-hold-taper
    inop-flow-fix smoke-base passN

**Passes.** They differ only in hand-off output, so the filter is identical; this is checked by the final.npy sha256.
- `pass1`: 500,000 uniform m0011 rows. Their distinct (mode, particle) pairs are piloted with end of flight's
  module, seed + 1000 (streams disjoint from the scoring children).
- `pass0`: 100,000 uniform rows, the "before".
- `pass2`: 100,000 rows drawn with g from the pilots (`g_index = "particle"`), oversample 50, defensive 0.2,
  the "after".

**Scoring.** End of flight's run I recipe (`full/sweep_run_i.sh` EXTRA, 8 children × 4 descents) on pass0 and pass2.
