# Binary restore instructions

The Blackman structured-data archive is stored as Base64 text in:
`Blackman_2004_extracted_data_2026-09-27.zip.b64`.

Restore with:

```bash
base64 --decode "Blackman_2004_extracted_data_2026-09-27.zip.b64" > Blackman_2004_extracted_data_2026-09-27.zip
unzip Blackman_2004_extracted_data_2026-09-27.zip
```

The repository baseline remains the 14 August 2026 snapshot. This directory is a delta backup of subsequent ChatGPT-assisted MH370 research.

The full local delta bundle created on 27 September 2026 is:
`MH370_Sept_27_2026_backup_PL_ChatGPT_instance_v2.zip`.

Because the available GitHub connector in this ChatGPT environment exposes text-oriented content writes rather than arbitrary local-file upload, the remote backup prioritizes machine-readable research state and Base64-wrapped binary bundles.
