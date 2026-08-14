# Large files hosted outside this repository

Seven source files exceed what is comfortable to store in Git. One of them is
larger than GitHub's hard 100 MB per-file limit, so the tree in this repository
is complete except for the files listed below. They are hosted as a companion
Hugging Face dataset and are part of the same snapshot: the SHA-256 manifest in
`transfer_metadata/` covers them alongside everything committed here.

**Companion dataset:** <https://huggingface.co/datasets/peteabiome/flight-mh370-revisited-data>

## The files

| Size | Path in the project tree |
| --- | --- |
| 335.7 MB | `library_full_audit/MH370/Backup Copy of AUG 4 SITA data with CNo BTO BFO rx dBm 1 Oxford.xlsx` |
| 83.5 MB | `library_full_audit/MH370/SITA data with CNo BTO BFO rx dBm 1 Oxford.xlsx` |
| 51.2 MB | `library_full_audit/MH370/MH370 calcs.xlsx` |
| 26.8 MB | `library_full_audit/MH370/A META ANALYSIS OF GEOSPATIAL ESTIMATES IN THE CASE OF MALAYSIAN AIRLINES FLIGHT MH370.pdf` |
| 26.8 MB | `library_full_audit/MH370/A%20META%20ANALYSIS%20OF%20GEOSPATIAL%20ESTIMATES%20IN%20THE%20CASE%20OF%20MALAYSIAN%20AIRLINES%20FLIGHT%20MH370.pdf` |
| 11.5 MB | `library_full_audit/MH370/airborne_0011_posterior_samples.csv` |
| 11.5 MB | `outputs/mh370_refined_bfo_0011_airborne/airborne_0011_posterior_samples.csv` |

The two `A META ANALYSIS...` entries are a same-size pair differing only in
URL-encoding of the filename; the two `airborne_0011_posterior_samples.csv`
entries are the Library archive copy and the working-output copy. Both pairs
are preserved rather than deduplicated, consistent with the provenance rules in
`handoff/DATA_AND_PROVENANCE.md`.

## Restoring the complete tree

```bash
pip install huggingface_hub
hf download peteabiome/flight-mh370-revisited-data --repo-type dataset --local-dir /tmp/mh370-large
```

The dataset preserves the original relative paths, so the files can be copied
straight over a clone of this repository:

```bash
cp -R /tmp/mh370-large/library_full_audit /tmp/mh370-large/outputs .
```

Integrity can then be rechecked against the preserved manifest:

```bash
shasum -a 256 -c transfer_metadata/MH370_file_manifest_2026-08-14.sha256
```

## Why not Git LFS

The tree originally shipped a `.gitattributes` routing PDFs, spreadsheets and
figures to Git LFS. That would place roughly 774 MB under LFS, against a free
GitHub allowance of 1 GB of storage and 1 GB of bandwidth per month — on a
public repository, a couple of clones would exhaust the monthly allowance and
break downloads for everyone else. Splitting the seven largest files out
instead keeps this repository at about 249 MB in plain Git, with no LFS
dependency and no quota, and puts the bulk data on a host built for it.
