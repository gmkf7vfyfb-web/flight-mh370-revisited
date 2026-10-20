# ECMWF ERA5 weather grids

This source package prepares the compact ERA5 pressure-altitude grids used by
the MH370 accident flight and the MH371 control. Python, xarray, Modal, cloud
credentials, and the remote Zarr store are source-only dependencies; the
product consumes only the hash-pinned binaries in `inputs/environment/`.

## Pinned public source

The canonical MH370 extraction reads the public ARCO ERA5 pressure-level store:

- `gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3`
- access recipe: `google-research/arco-era5@8fb5e9b982f489ba91af3ced9ce0b0a8ade8dd7d`
- Zarr consolidated-metadata generation: `1788578126795769`
- consolidated-metadata SHA-256:
  `409449e1c7c4ec56159d7031d8756c76cb25619c6b5da005d15eaaf85eaaaf78`
- dataset `last_updated`: `2026-09-05 03:15:26.016363+00:00`
- retrieval: 2026-09-06 UTC

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

## MH370 global broad-flight field

`code/extract_mh370.py` selects these axes before writing `MHERA5V1`:

- UTC: 2014-03-07 17:00 through 2014-03-08 01:00, inclusive (9 hours)
- region: 90 degrees N to 90 degrees S, north-to-south; complete longitude at
  0.5-degree spacing. The `+180`-degree axis column is an exact duplicate of
  the `-180`-degree physical meridian, closing the non-periodic runtime
  interpolator for valid aircraft longitudes below `+180` degrees.
- source pressure levels in hPa: 150, 175, 200, 225, 250, 300, 350, 400, 450,
  500, 550, 600, 650, 700, 825, 850, 975, 1000
- target pressure altitudes in ft: 500, 5,000, 10,000, 15,000, 20,000, 25,000,
  28,000, 31,000, 34,000, 37,000, 40,000, 43,000
- output shape: 9 x 12 x 361 x 721 in time, pressure-altitude, latitude,
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

This spatial domain is global, rather than a corridor inferred from an
assumed southern route. It therefore cannot reject any valid WGS-84 trajectory
from the repeated-event prior. The manifest additionally records a deliberately
conservative kinematic check for the 22,150-second M1822-to-M0011 interval:
Mach 0.87, the maximum grid temperature (315.414368 K), and the maximum grid
wind-vector magnitude (100.845898 m/s) give a ground-speed ceiling of
410.591361 m/s and a path-length ceiling of 4,910.690 nm. The corresponding
latitude-change bound is 82.249 degrees using the minimum WGS-84 meridional
radius. The 0.5 nm source-position Gaussian is mathematically unbounded, but
the environmental grid covers every valid runtime latitude and longitude;
invalid source latitude draws are handled by the estimator's declared source
logic, not by a hidden environmental corridor.

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

The two final global-grid runs produced byte-identical binaries. Run A took
35.468 s and peaked at 2,865,037,312 bytes RSS; run B took 33.002 s and peaked
at 4,491,255,808 bytes RSS. The 27 compressed source chunks total
2,926,778,130 bytes. Local validation scanned all 28,110,348 values in each of
the three global fields in 12.943 s, peaking at 585,125,888 bytes RSS.

The independent standard-library validator checks the exact header, byte
count, axes, orientations, units, finite ranges, source-object identity,
interpolation plan, density contract, and absence of vertical wind. It
recalculates float32 outputs from raw lower/upper ARCO values at the first
time/lowest altitude/northwest corner, a central time and location at 20,000
ft, and the last time/highest altitude/southeast corner. All nine field checks
were bit-exact (absolute error zero). Details are in the JSON validation record
and the browser-viewable HTML report.

- installed binary: 337,328,648 bytes; SHA-256
  `73a14bf7e931da9f4f3f034b77ac24b9514fdef727b82eb9e30c67df938489f4`
- installed manifest SHA-256:
  `4a312d7d733851fc03cf96fd5bcad65eeb4c42e1a5c1451aeb3a3654706adad0`
- extractor SHA-256:
  `59cb163416150b758361ede8c50028296d8ee0b5b2ec33393528e7cd38011cdd`
- validator SHA-256:
  `0dda3cfbc67e1986fdcada80626dcc19890c3b53b60925debece1e11a640536e`
- validation JSON SHA-256:
  `e404ffa192f4203522f28ef2b6454425f3ddcaae67b25467e65a8af67e82829d`
- validation HTML SHA-256:
  `2a4e3fd439b8e1213cc6851e7d3a2519276f313c0f13abd063a8c3b24d1ef601`

The validation record also preserves the hashes and sizes of the superseded
MH370 binary and manifest that remained installed until every candidate check
passed.

## MH371 broad-flight control

`code/extract_mh371.py` prepares the truth-separated broad control. It covers
2014-03-07 01:00-08:00 UTC, 30 degrees S-90 degrees N, complete seam-closed
longitude, and 10,000-43,000 ft.

- extractor SHA-256:
  `40ad92ece175d5c5ea70a36bea7c52ed05d62b826170639b02535a5f5280452e`
- binary SHA-256:
  `44a65c9b043be2a71754722275877d9bff66df1342eb616d883159c65d3f63aa`
- manifest SHA-256:
  `a291817d4354137f3d04d98bdfb75688489c1a06c76a117c8b0c6219a517d297`

## Limitations

ERA5 is a reanalysis, not a direct measurement at the aircraft. The 0.5-degree
downsampling, ISA pressure-height mapping, log-pressure interpolation, and
dry-air density equation are explicit model choices. They are not estimates of
weather-field uncertainty. The public store is mutable; the generation pins
make source changes fail closed but cannot guarantee that Google retains old
object generations indefinitely.
