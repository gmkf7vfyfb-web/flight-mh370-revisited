# Provenance and freeze status

## Release identity

- Release name: `v0.1`
- Release bundle date recorded by the original manifest: 2026-08-31 UTC
- Capsule assembly date: 2026-09-06 UTC
- Release status: releaseable milestone with explicit evidential boundaries
- Original release manifest SHA-256:
  `b5d89ff95bd26594506674dd51a04b36e23a04946ac0b835f85b5ee1b16db9e1`

The original release validator passes all 70 indexed artifacts. The core and
R600 manifests close transitively with zero missing or mismatched input/output
files.

## Exact producer executable

`bin/linux-x86_64/mh370-v0.1` is the recovered executable recorded by the
central, R600, and impact manifests.

- SHA-256:
  `de28b0adc6de796026e6075da614b5e11c78459d4beafbca42f6e30b10758b4b`
- Program version: `mh370 0.1.0`
- Format: stripped, dynamically linked, x86-64 Linux ELF PIE
- Build ID: `ddbdbbfcb984371e9fffa4e9e39eea57f6901030`
- Highest referenced glibc symbol version: `GLIBC_2.35`

The binary is sufficient to execute the original deterministic estimator on a
compatible x86-64 Linux system. Its runtime-library record is in
`environment/producer-binary.txt`.

## Producer source and enclosed source

The impact release locked 80 producer source files under source-tree identity
`d43975e6be06a07db8ceebdc48009613ce5701638d4d3511e316e74eca2d952d`.
At capsule assembly:

- 64 files matched the lock byte-for-byte;
- 16 files differed after post-release work;
- 0 locked files were missing.

The changed paths are listed in `environment/source-lock-differences.tsv`.
This environment contained neither `.git` metadata nor a complete historical
source archive, so the old contents of those 16 paths cannot be claimed.

The `workspace/` directory is a complete checksum-frozen snapshot of the code
available at capsule assembly, after rejected experimental interfaces were
removed. It passes formatting and the full current workspace tests, but a
fresh build has a different binary identity. The historical binary and current
source are therefore intentionally labelled separately.

This distinction matters:

- exact verification of retained v0.1 artifacts: **supported**;
- exact rerun using the original binary: **supported on compatible Linux**;
- complete inspection and rebuild of the current source: **supported**;
- byte-identical rebuild of the original binary from original source:
  **not supported because 16 original source files are absent**.

## Additions captured by this capsule

The posterior/search-context overview was produced on 2026-09-02 and carries
its own closed run manifest, but it postdates and is not one of the original 70
top-level indexed artifacts. It is included as a v0.1 companion view.

The capsule also contains a fresh MH371 medium-BFO known-flight control made on
2026-09-06 with the exact v0.1 producer binary. Its inference JSONs, run
manifest, scoring manifest, score summary, PDF, and PNG are retained at
`workspace/runs/mh371/v0.1-medium-control/`. This replaces any need to rely on
older MH371 PDFs whose temporary inference inputs had been discarded.

## Integrity layers

1. `SHA256SUMS` covers the assembled capsule.
2. The release manifest covers the 70 top-level release artifacts.
3. Core, R600, impact, conditional, source-recreation, and report manifests
   cover their own inputs and outputs.
4. The producer source lock records the historical source identity.
5. `tools/verify_capsule.py` checks these layers without third-party Python
   packages.
