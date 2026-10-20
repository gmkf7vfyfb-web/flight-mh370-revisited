# MH370 Rerun — checkpoint 10

Created 2026-09-19 11:43 UTC.

## Outcome

This work unit independently audited the retained-parent 18:39–19:41 transition pool and added the diagnostics needed to separate three distinct phenomena in a physical run:

1. finite live particle-slot diversity at the entrance to the block;
2. distinct original-root diversity already surviving at that entrance; and
3. candidate/root diversity after the jointly scored block.

The source now reports entrance particle ESS and largest particle mass separately from entrance original-root ESS and largest root mass for every scientific stratum. This matters because many live particle slots may already descend from only one or a few initial states. Increasing `K` cannot reconstruct roots lost before the block.

## Independent executable reference

`retained_parent_reference.py` implements the measure without importing the Rust engine. It expands every finite-mass parent with

`W_parent / K × p(path|parent) / q(path|parent) × likelihood(path)`

and independently implements stratum-local output downselection, defensive root mixing, exact output target/proposal correction, evidence, and lineage propagation.

The reference tests cover `K = 1, 2, 4, 8`, unequal scientific-stratum masses and output allocations, a zero-mass parent, repeated prior roots, and defensive root-mixture settings of 0, 0.35, and 0.4.

- With the production default root-mixture epsilon 0, realized output evidence equals candidate-pool evidence for every systematic-resampling offset (checked to `3e-15` absolute tolerance).
- With a defensive root mixture, individual realized evidence is stochastic, but the exact target/proposal correction recovers evidence and root masses in the systematic-offset grid control.
- Every finite-mass parent contributes exactly `K` candidates; `K` augments rather than replaces the incoming parent bank.
- Output lineage is inherited from the selected candidate's parent slot and original root.

All 24 new exact/source tests pass. The unchanged precompiled baseline also passes 73 particle-filter and 15 Satcom tests, for 112 passing checks and no failures.

## What this establishes—and what it does not

This establishes the bookkeeping identities of the proposed transition pool and makes pre-block genealogical loss observable. It does not compile or execute the modified Rust source, and it does not show that the physical K=4 proposal improves MH370 inference.

The exact compiler provenance was recovered from the surviving build fingerprint: Rust 1.98.0, commit `88d9e12ae178fab0fb5cc050a94da85685d449ea`. Its prior installed path has been pruned, and no compiler executable or Drive toolchain archive was found. Therefore base-versus-K=1 binary equality and physical K=4 trials remain blocked.

## Next physical gate

After restoring the compiler:

1. compile the isolated source and run its embedded retained-parent tests;
2. prove base versus K=1 scientific outputs are byte-identical using the same new executable and seed;
3. run K=4 across multiple seeds with the full incoming parent bank;
4. report entrance particle ESS/root ESS, candidate row/root ESS, output root ESS, evidence, support, and marginal CDF differences;
5. separately compare fixed total path-evaluation budgets so K is not funded by silently shrinking initial-parent diversity.

No full-aircraft bridge was run, no posterior probability or location is claimed, and hydroacoustics remains excluded.
