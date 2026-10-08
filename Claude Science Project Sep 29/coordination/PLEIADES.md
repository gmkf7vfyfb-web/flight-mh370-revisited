# PLEIADES inbox

The architecture session appends here. Read at the start of each working session.

## 2026-10-08 - architecture: the shared-ocean boundary, before you start

`crates/ocean` has a **third owner**. It is not owned by drift, not by settling and not by
Pleiades, because all three consume it and a crate owned by one consumer acquires that consumer's
assumptions. That owner does not exist yet and its brief is not written.

Until it does, three rules bind you.

1. **Do not implement advection, field interpolation, or reanalysis dataset access in your own
   module.** Not as a convenience, not temporarily. The moment two modules each have their own,
   the project has two ocean models and no way to tell which one a result came from.
2. **Do not choose a reanalysis product.** Product choice belongs to the shared owner. The
   measurement already in hand says this is the smaller axis anyway: changing the current product
   moved the drift mode 1.2 deg, while scaling the Stokes contribution by 0.5, 1 and 1.5 moved it
   to 11.9, 18.0 and 34.9 deg S. Object response dominates. Spend your effort there.
3. **If you need something from the ocean crate, raise it as an interface request in
   `coordination/OCEAN_TRANSPORT.md`** - what you need, in what frame, at what resolution, with
   what time coverage, and what you will do with it. Those requests are what the shared brief
   will be written from, so a precise one buys you the interface you want.

You may write a stub to keep working. It goes in **your own directory**, is named so that nobody
mistakes it for the real thing, and every number that passes through it is labelled provisional.
A stub must not become the interface by default: state in the request what the stub assumes, so
the shared owner can reject the assumption rather than inherit it.

## 2026-10-08 - architecture: your brief is aligned, start here

`threads/master-prompts/pleiades.md` is authoritative and supersedes the September ISO `.txt`,
which does not mention COSMO-SkyMed, SAR, object matching or the tension measurement, and which
contains one withdrawn sentence about what the module returns.

**Four things to read before designing anything.**

1. **There is no identity likelihood** (brief §3). The morphology screen is a negative result in
   three ways: controls matched at least as well as 777 parts, the flooding model was not favoured,
   and none of 168 simulated flooding states matched the PCA masks. PCA loss is mask overlap, not a
   class probability. Do not redo the screen, and do not present shape as support for H.
2. **The tension is in the observations** (§4). The six object clusters sit 121 to 166 NM north of
   the reference posterior median, further north than the transport-inferred sources. No choice of
   ocean product removes it. This is a conditional that relocates the estimate rather than
   sharpening it, and your first deliverable is to measure that properly in two dimensions.
3. **A narrow conditional is not evidence of precision** (§2). Report the PDF and its three tension
   quantities together, everywhere. Reporting either alone is a defect.
4. **Enumerate the matching, never sample it** (§6). 1,045 assignments over six clusters, 18,001
   over twelve objects. Both trivial. If the two-epoch windage calibration carries no information,
   prove it with information gain in bits, a Bayes factor, and an injection-recovery floor.

**Run §11 early.** The prior work's search-conditioned residual moves west to about 91.0E and
nobody has ever checked whether the aircraft could reach there. You have the core posterior and the
test is cheap. If the western lobe is largely unreachable, most of the residual mass under H
disappears, and that changes how much effort the rest of the module deserves.

**The shared-ocean boundary applies to you** - see the entry above. You do not implement advection
or choose a transport product; you raise what you need in `coordination/OCEAN_TRANSPORT.md`.

**Licence.** The GA report is CC BY 4.0 except the object crops, which are (c) CNES. Never commit
the crops.

## 2026-10-08 - architecture: answers to the points you raised with Pete

**Brief section 8's path is wrong and is corrected today.** The material is at
`Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/pleiades-bran2016-forward-inversion/`.
Note the parent directory is the *withdrawn* share: use the data and tests, and treat any prose there
as reference only, not authority.

**Push a `hypothesis/pleiades` branch.** That is the standing rule for every module; diffs come to
review through the branch, not by holding work locally.

**GA Record 2017/13 is not on the Drive** - searched today. It is a public Geoscience Australia
record under CC BY 4.0; obtain it from GA directly, requesting network access if needed, and cite it
by its own page numbers. That is the source of the rating-4 count.

**Ordering: run section 11 first, alone, and report before anything else.** It is the cheapest test
and its answer changes how much effort the rest deserves.

**If `no-exhaustion-prior` carries only marginals** and not per-sample positions, say so in
`coordination/architecture.md` and I will raise it with core. Do not reconstruct a 2-D posterior from
marginals.
