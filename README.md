# Flight MH370 Revisited

Research workspace for **Flight MH370 Revisited: Integrated Bayesian Estimation
without a Prespecified End-of-Flight Scenario**.

This repository combines satellite burst timing offset (BTO), burst frequency
offset (BFO), received signal level/antenna gain, aircraft performance and
trajectory feasibility, ocean drift evidence, Pleiades-imagery sensitivities,
and search non-detection evidence. The principal baseline estimates the
aircraft state through 00:11 UTC; evidence at and after 00:19 UTC is reserved
for a separate end-of-flight stage.

## Start here

1. Read [`handoff/START_HERE.md`](handoff/START_HERE.md).
2. Treat [`AGENTS.md`](AGENTS.md) as binding project instructions.
3. Read [`handoff/PROJECT_STATE.md`](handoff/PROJECT_STATE.md) and
   [`handoff/REPRODUCIBILITY_STATUS.md`](handoff/REPRODUCIBILITY_STATUS.md).
4. Consult the provenance ledger at
   `outputs/mh370_search_evidence/source_register.csv` before adding evidence.

## Current headline baseline

The primary model-averaged impact posterior through 00:11 UTC has a mode near
37.26°S, 89.24°E and a median near 37.03°S, 89.71°E. Its 95% latitude interval
is approximately 33.22°S to 39.15°S. This is a multimodal research posterior,
not a unique crash point or a search recommendation by itself.

The Pleiades analysis is a separate conditional scenario: *if* the selected
objects are assumed to be MH370 debris, a BRAN-anchored diagnostic moves the
impact concentration toward roughly 35.3°S, 92.5°E. No probability is assigned
to the premise that the objects are MH370 debris.

## Status and scope

- Working research repository, published publicly on 14 August 2026.
- Unpublished manuscript material is present.
- Some source files may have redistribution restrictions. The copyright,
  licensing and privacy review described in
  [`handoff/DATA_AND_PROVENANCE.md`](handoff/DATA_AND_PROVENANCE.md) has not
  been completed. Third-party papers, datasets, imagery and technical
  references are included here as collected research material; their presence
  is not a grant of redistribution rights, and rights remain with their
  respective owners. If you hold rights to material here and want it removed,
  please open an issue.
- Seven oversized source files are hosted in a companion Hugging Face dataset,
  [`peteabiome/flight-mh370-revisited-data`](https://huggingface.co/datasets/peteabiome/flight-mh370-revisited-data);
  see [`LARGE_FILES.md`](LARGE_FILES.md) for the list and restore instructions.
- Exact reproduction, reconstruction, diagnostic sensitivity, and new analysis
  are deliberately distinguished; see the handoff dossier.
- The immutable migration snapshot and its checksums are release assets, not
  normal Git objects.

## Core artifacts

- `outputs/mh370_stage1_0011/`: integrated estimator through 00:11 UTC.
- `outputs/mh370_refined_bfo_0011_airborne/`: refined random BFO-noise study.
- `outputs/mh370_pleiades_bran_diagnostic/`: conditional Pleiades/BRAN study.
- `outputs/mh370_pp_descent_climb_sensitivity/`: Pulau Perak descent/re-climb
  fuel and posterior sensitivity.
- `outputs/mh370_search_evidence/`: searched-area evidence and provenance.
- `outputs/paper_draft/`: manuscript and end-of-flight evidence note.
- `output/graphics/`: received-power and HGA explanatory graphics.
- `library_full_audit/MH370/`: 148-file master archive materialized from the
  project Library, including the full SITA workbooks, aircraft-performance
  references, antenna specification, papers, source data and retained outputs.

The Library master archive intentionally overlaps some working files. Preserve
it unchanged as a provenance layer; develop against clearly documented working
copies elsewhere in the repository.

No public license is granted at this stage. See
[`handoff/DATA_AND_PROVENANCE.md`](handoff/DATA_AND_PROVENANCE.md).
