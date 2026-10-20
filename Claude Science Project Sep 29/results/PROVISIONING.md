# Engine data files that are not in git

These four files are excluded from the repository and so are absent from any fresh clone or
git bundle. Three are excluded for size; `fuel-tables.json` is excluded because it is
transcribed from Boeing Flight Planning and Performance Manual tables, some of them marked
confidential, and the repository is public. Keep that file out of GitHub and out of any public
host; this archive is private to the project.

Unpack into `Claude Science Project Sep 29/engine/`:

    tar xzf engine-data.tar.gz -C "Claude Science Project Sep 29/engine"

| bytes | path | origin |
| --- | --- | --- |
| 374,809,120 | `data/era5-wind-temperature.bin` | ECMWF ERA5 via `gs://gcp-public-data-arco-era5`, built by `.sources/era5-weather/extract.py` (17:00-01:00 UTC) then `extend.py` (02:00). The 9-hour base grid is 337,328,648 bytes with sha256 `73a14bf7e931da9f4f3f034b77ac24b9514fdef727b82eb9e30c67df938489f4`, recorded in `.sources/era5-weather/mh370-era5-grid.manifest.json`. |
| 99,986,408 | `data/merra2-wind-temperature.bin` | NASA MERRA-2 `inst3_3d_asm_Np`, 3-hourly, built by `.sources/weather-sensitivity/extract.py merra2`. Needs a NASA Earthdata login, so this one is the hardest to regenerate. Used for the weather-model sensitivity run, not the base estimate. |
| 12,497,900 | `data/igrf14-declination.bin` | IGRF-14, built by `.sources/igrf14-declination/build_generation.py 14 data/igrf14-declination.bin` from the NOAA coefficient package already committed at `.sources/igrf14-declination/pyIGRF14.zip`. Seconds to rebuild. |
| 124,193 | `data/fuel-tables.json` | Extracted by `.sources/fuel-performance/extract.py` from Ulich's 9M-MRO fuel model V5.6 workbook. Under a second to rebuild given the workbook. NOT REDISTRIBUTABLE. |

Why this archive exists. Regenerating ERA5 inside the analysis sandbox is not practical: the
ARCO store chunks as `[1, 37, 721, 1440]`, one chunk per hour holding all 37 pressure levels,
so producing the 337 MB grid means pulling 2.93 GB of compressed chunks (the figure the grid
manifest itself records as `source_chunk_compressed_bytes`) in a few enormous single-object
reads. The extractor was written to run on Modal next to the data. Restore from here instead.
