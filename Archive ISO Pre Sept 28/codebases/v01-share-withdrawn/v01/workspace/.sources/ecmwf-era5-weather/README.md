# ECMWF ERA5 weather grids

This source package prepares the compact ERA5 pressure-altitude grids used by
the MH370 accident flight and the MH371 control. Python, xarray, Modal, cloud
credentials, and the remote Zarr store are source-only dependencies; the
product consumes only the hash-pinned binaries in `inputs/environment/`.

## Pinned public source

The canonical MH370 extraction reads the public ARCO ERA5 pressure-level store:

- `gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3`
- access recipe: `google-research/arco-era5@8fb5e9b982f489ba91af3ced9ce0b0a8ade8dd7d`
- Zarr consolidated-metadata generation: `1787799989791674`
- consolidated-metadata SHA-256:
  `b53631fb7e4767108275025f12d9c304da8d849d7862ac0e1439ab6634ab8fbd`
- dataset `last_updated`: `2026-08-27 03:06:29.062321+00:00`
- retrieval: 2026-08-27 UTC

The ARCO bucket is updated in place rather than exposed as a named immutable
snapshot. To make that limitation explicit, the extractor also pins the GCS
generation, MD5, CRC32C, and size of every one of the 27 historical source
chunks. Their canonical metadata-record SHA-256 is
`eed7079e6bbd5260d95f965071ed656d9667d43864f720207021fc1fb5bfb887`.
The script refuses a changed consolidated-metadata or chunk identity instead
of silently regenerating from a different public field. The complete object
list is in `inputs/environment/mh370-era5-grid.manifest.json`.

The source variable metadata declares temperature in K, U wind as eastward in
`m s**-1`, and V wind as northward in `m s**-1`. ERA5 analysis validity time is
hourly UTC with analysis step zero.

## MH370 expanded field

`code/extract_mh370.py` selects these axes before writing `MHERA5V1`:

- UTC: 2014-03-07 17:00 through 2014-03-08 01:00, inclusive (9 hours)
- region: 50 degrees N to 60 degrees S, north-to-south; 55 to 125 degrees E,
  west-to-east; 0.5-degree spacing
- source pressure levels in hPa: 150, 175, 200, 225, 250, 300, 350, 400, 450,
  500, 550, 600, 650, 700, 825, 850, 975, 1000
- target pressure altitudes in ft: 500, 5,000, 10,000, 15,000, 20,000, 25,000,
  28,000, 31,000, 34,000, 37,000, 40,000, 43,000
- output shape: 9 x 12 x 221 x 141 in time, pressure-altitude, latitude,
  longitude order
- binary fields: temperature K, east wind m/s, north wind m/s; float32,
  little-endian, C order with longitude varying fastest

The altitude coordinate is ISA pressure altitude, not observed geopotential or
geometric height. ISA pressure uses 1013.25 hPa and 288.15 K at sea level, a
0.0065 K/m lapse rate through 11 km, 216.65 K above it, standard gravity
9.80665 m/s2, and dry-air gas constant 287.05287 J/(kg K). Each target field is
linearly interpolated in natural-log pressure between adjacent ERA5 pressure
levels; the manifest records every pressure, bracket, and weight.

The lowest target is 500 ft (995.075397 hPa), bracketed by 975 and 1000 hPa.
Exact ISA 0 ft is 1013.25 hPa, outside the public pressure-level range, so it
is not extrapolated and no surface field is substituted.

Density is not stored in `MHERA5V1`. A consumer that needs it must use the
documented dry-air contract

```text
rho_kg_m3 = target_pressure_hpa * 100 / (287.05287 * temperature_k)
```

where target pressure is the manifest value for the pressure-altitude axis and
temperature is the interpolated value from the binary. Humidity is not applied.
Vertical wind is not retrieved, inferred, stored, or implied.

## Deterministic reproduction

The local Modal client used for this retrieval was 1.5.4. The remote image in
the extractor pins Python 3.12, NumPy 2.2.6, xarray 2025.6.1, Zarr 3.1.2,
gcsfs 2025.5.1, and Dask 2025.5.1. Keep the local environment temporary and
outside the repository:

```bash
python3 -m venv /tmp/mh370-era5-retrieval
/tmp/mh370-era5-retrieval/bin/python -m pip install modal==1.5.4
PYTHONDONTWRITEBYTECODE=1 /tmp/mh370-era5-retrieval/bin/python -m modal run \
  .sources/ecmwf-era5-weather/code/extract_mh370.py
/tmp/mh370-era5-retrieval/bin/python -m modal volume get --force \
  mh370-environment-v1 \
  mh370/2014-03-07_2014-03-08/mh370-era5-grid.bin \
  .sources/ecmwf-era5-weather/outputs/mh370-era5-grid.candidate.bin
/tmp/mh370-era5-retrieval/bin/python -m modal volume get --force \
  mh370-environment-v1 \
  mh370/2014-03-07_2014-03-08/mh370-era5-grid.manifest.json \
  .sources/ecmwf-era5-weather/outputs/mh370-era5-grid.candidate.manifest.json
PYTHONDONTWRITEBYTECODE=1 python3 \
  .sources/ecmwf-era5-weather/code/validate_mh370.py \
  .sources/ecmwf-era5-weather/outputs/mh370-era5-grid.candidate.bin \
  .sources/ecmwf-era5-weather/outputs/mh370-era5-grid.candidate.manifest.json \
  --record .sources/ecmwf-era5-weather/outputs/mh370-era5-validation.json \
  --report .sources/ecmwf-era5-weather/outputs/mh370-era5-validation.html \
  --install-directory inputs/environment
```

The remote entrypoint performs two independent public-bucket reads with
filesystem instance caching disabled. It publishes only if source identities,
raw spot values, field statistics, and the binary bytes agree. The candidate
staging files and the temporary virtual environment are deleted after a
successful local installation; neither is a source artifact.

## Validation and integrity

The two final publication runs produced byte-identical binaries. Run A took
24.478 s and peaked at 2,412,318,720 bytes RSS; run B took 31.295 s and peaked
at 2,670,948,352 bytes RSS. The 27 compressed source chunks total
2,926,778,130 bytes. Local validation scanned all 3,365,388 values in each of
the three fields in 1.558 s, peaking at 89,341,952 bytes RSS.

The independent standard-library validator checks the exact header, byte
count, axes, orientations, units, finite ranges, source-object identity,
interpolation plan, density contract, and absence of vertical wind. It
recalculates float32 outputs from raw lower/upper ARCO values at the first
time/lowest altitude/northwest corner, a central time and location at 20,000
ft, and the last time/highest altitude/southeast corner. All nine field checks
were bit-exact (absolute error zero). Details are in the JSON validation record
and the browser-viewable HTML report.

- installed binary: 40,386,248 bytes; SHA-256
  `261f4e1442ffac69df0201371f7dbf42da0ac0fa30065fc04e0e6293677a2a53`
- installed manifest: 33,189 bytes; SHA-256
  `3dc2ba3e19406bc2707b72e2428511da7f10abba0b6f76f270af5bc5895ff43e`
- extractor SHA-256:
  `5630165bd11d6a8d99a132dea6aad2a61c50017ecb690b5e30a8b8bd651677c2`
- validator SHA-256:
  `77cdc98f0baf6db5cfc56aef076f0901587fff8a0a6348dbbab73eb8addabb67`
- validation JSON SHA-256:
  `451f2ee30056f7ed4cc6b3da2db3c9b9e2ad0651c74847cb809bdedaa14295eb`
- HTML report SHA-256:
  `80e674fd3bbc37dec312ff13b7daf54b4c80d36d3891863286ca57616b2d2391`

The validation record also preserves the hashes and sizes of the superseded
MH370 binary and manifest that remained installed until every candidate check
passed.

## MH371 control remains unchanged

`code/extract_mh371.py` and the existing MH371 inputs are retained unchanged.
The control covers 2014-03-07 01:00-08:00 UTC, 15 degrees S-60 degrees N,
75-140 degrees E, and 10,000-43,000 ft.

- extractor SHA-256:
  `172ef2d87f867aa34fda3ff574125ef3ac888e283a6f9b6563c4c96147041162`
- binary SHA-256:
  `0419e87362969f9ac1bc948b7461a471e998fa52d369f59a3a66a5c4e1c52b40`
- manifest SHA-256:
  `3dcd37c46a7577aae2d18316fcae1dfb0571f2cd70f0f5e9f09b728e936de2ad`

## Limitations

ERA5 is a reanalysis, not a direct measurement at the aircraft. The 0.5-degree
downsampling, ISA pressure-height mapping, log-pressure interpolation, and
dry-air density equation are explicit model choices. They are not estimates of
weather-field uncertainty. The public store is mutable; the generation pins
make source changes fail closed but cannot guarantee that Google retains old
object generations indefinitely.
