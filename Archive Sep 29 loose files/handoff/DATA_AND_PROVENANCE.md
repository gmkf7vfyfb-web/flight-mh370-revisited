# Data, provenance, privacy and publication controls

## Provenance ledger

The principal source ledger is:

`outputs/mh370_search_evidence/source_register.csv`

It records source URLs, grades, claims used and search-coverage evidence. New
sources should be added there or to a successor ledger with compatible fields.

## Data layers

### Raw/source material

`downloads/`, `downloads_refined_bfo/`, the raw SITA workbook at repository
root, and uploaded source files are treated as immutable source material. Do
not edit them in place.

### ChatGPT Library master archive

`library_full_audit/MH370/` is a byte-preserving materialization of all 148
files found in the project's `/MH370` Library folder on 2026-08-14. It adds
source material that was absent from the original workspace, notably the full
SITA received-power workbooks, a larger `MH370 calcs.xlsx`, Boeing performance
references, the AES antenna specification, key papers and the research
conversation/audit document.

Treat this directory as an immutable archival and provenance layer. It
deliberately contains duplicates and historical output versions; filenames
alone are not evidence that two copies have identical bytes. Use the snapshot
inventory and SHA-256 manifest for comparison. Temporary files containing
`.openai-download-` are transfer residue and are excluded from the snapshot.

### Processed data

CSV/JSON/GeoJSON files under `outputs/` may be derived inputs or summaries.
Each should remain traceable to code, a run manifest and raw sources.

### Released outputs

PDF, DOCX, XLSX and selected figures under `outputs/` and `output/` are retained
research releases. New versions should use new filenames or directories rather
than overwriting a cited result.

### Temporary/intermediate material

`tmp/` and rendered-page folders contain useful reconstruction evidence and
are included in the immutable snapshot. They may later be omitted from the
working branch only after dependencies have been moved to stable locations.

## Private-repository requirement

Keep the initial GitHub repository private. The workspace contains unpublished
manuscript material, raw communications/log workbooks, aircraft fuel-model
material, third-party PDFs, extracted images and downloaded web content. The
Library archive also contains large raw spreadsheets that may be sensitive or
contractually restricted. Their presence in a private research archive does
not establish permission for public redistribution.

Before any public release:

1. Review each raw source for copyright, contractual and privacy restrictions.
2. Replace restricted source bytes with a citation/acquisition instruction
   where necessary.
3. Remove temporary signed URLs, cookies, tokens and account identifiers.
4. Review imagery rights and obtain permission or redraw figures.
5. Publish only data/code that can legally and ethically be shared.

## Integrity

The migration package contains a CSV inventory and SHA-256 manifest. These are
the authoritative byte-integrity checks for the handoff snapshot. Git and Git
LFS hashes provide an additional version-control layer after upload.
