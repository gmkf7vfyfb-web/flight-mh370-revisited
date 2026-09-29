# MH370 Bayesian estimator — release v0.1 capsule

This directory is the frozen assessment and reproduction capsule for milestone
release **v0.1**. The capsule was assembled on 2026-09-06 UTC from the project
workspace after the release validator and full workspace test suite passed.

The release is a reproducible, model-conditional scientific checkpoint. It is
not a claim that the crash position has been observed, that probabilities over
structural model families are known, or that previously searched seabed can be
used as a calibrated negative likelihood.

## Begin here

1. Run `python3 tools/verify_capsule.py` from this directory. It verifies the
   capsule file ledger, the exact v0.1 producer binary, the nested release
   manifests, and reports the historical source-lock status.
2. Read `PROVENANCE.md` before claiming byte-for-byte source reproduction.
3. Read `SCIENTIFIC_BOUNDARIES.md` before interpreting any plot.
4. Open `index.html` for the curated MH371, MH370, Davey, arc, impact, and
   searched-area views.
5. A new automated assessor should start with `CHATGPT_HANDOFF.md` and then
   inspect `workspace/AGENTS.md`, `workspace/README.md`, and
   `workspace/runs/mh370/release-v0.1/release-manifest.json`.

## Capsule layout

- `bin/linux-x86_64/mh370-v0.1`: exact executable that produced the central
  v0.1 MH370 artifacts.
- `workspace/`: source, configurations, inputs, supporting source
  recreations, vendored Rust dependencies, and retained run artifacts in their
  original project-relative paths.
- `views/`: curated copies of the requested reports and machine-readable arc
  and search geometry.
- `environment/`: toolchain, Python package, platform, and executable linkage
  records.
- `tools/verify_capsule.py`: standard-library-only verifier.
- `SHA256SUMS`: integrity ledger for every file in this directory except the
  ledger itself.

## What is exact

- Original release manifest SHA-256:
  `b5d89ff95bd26594506674dd51a04b36e23a04946ac0b835f85b5ee1b16db9e1`.
- Original producer executable SHA-256:
  `de28b0adc6de796026e6075da614b5e11c78459d4beafbca42f6e30b10758b4b`.
- Original producer source-lock SHA-256:
  `d43975e6be06a07db8ceebdc48009613ce5701638d4d3511e316e74eca2d952d`.
- The central 00:11, R600 continuation, impact-family, optional-evidence, and
  planning artifacts retain their nested checksums.
- The capsule includes all inputs used by the central estimator and the
  complete retained output particle tables needed for independent analysis.

## Important source qualification

The exact producer executable was recovered and is included. Of the 80 files
in the historical producer source lock, 64 remain byte-identical and 16 were
subsequently changed during post-release development. No Git metadata or
complete historical source archive was present in this environment. The
capsule therefore supports exact artifact verification and exact execution of
the retained v0.1 binary on compatible Linux, plus inspection and rebuilding
of the complete current source snapshot. It does **not** falsely claim that a
fresh build of the enclosed current source will recreate the producer binary
bit-for-bit.

See `PROVENANCE.md` for the full distinction and `REPRODUCE.md` for commands.
