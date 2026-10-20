# Native PHaRLAP IRI2020 helper

This is an independently written C boundary around the Fortran ABI exported by
PHaRLAP 4.7.4. It makes the official wrapper's default IRI2020 profile usable
without MATLAB. It contains no PHaRLAP source, binary, or reference data.

This helper is supporting code for the WSPR propagation audit, not a product
dependency and not evidence that a modeled ray was the propagation mode of a
particular WSPR observation.

## External requirements and identity

Obtain PHaRLAP directly from Australia's Defence Science and Technology Group.
The supplied release limitation prohibits redistributing PHaRLAP. The helper
source may be shared, but each user must obtain the libraries and data
separately and comply with `DISCLAIMER.txt`, `RELEASE_LIMITATION.txt`, and
`ACKNOWLEDGEMENT.txt` in that distribution.

The verified Linux dependency is:

- PHaRLAP release: 4.7.4, released 2025-07-14
- platform ABI: ELF64 little-endian x86-64
- `lib/linux/libiri2020.a` SHA-256:
  `76064dc26d638918c65bed977f9581b0c64bc5dfbdd1f6d3c6bb3758f1d9e400`
- required IRI data-manifest SHA-256:
  `5da7f44900ffb7855beb3673fae61bb632e652f83971f5b887d18ef08a7534c7`

The data-manifest digest is the SHA-256 of the textual `sha256sum` output in
this exact order, under `dat/iri2020` with `LC_ALL=C`:

```sh
sha256sum apf107.dat ig_rz.dat ccir*.asc ursi*.asc mcsat*.dat \
  dgrf*.dat igrf*.dat | sha256sum
```

The build checks the archive hash. `make verify` additionally checks the data
manifest. At runtime the helper checks that every required coefficient, index,
and geomagnetic file is readable before allowing the first model call.

The host needs a C11 compiler, POSIX threads, `libgfortran.so.5`, and `libm`.
A Fortran compiler frontend is not needed because PHaRLAP supplies compiled
objects.

## Build and test

From this directory:

```sh
make -f Makefile.pharlap \
  PHARLAP_HOME=/absolute/path/to/pharlap-4.7.4 verify all

make -f Makefile.pharlap \
  PHARLAP_HOME=/absolute/path/to/pharlap-4.7.4 test
```

The outputs are `build/pharlap_iri2020` and
`build/libpharlap_iri2020.so`. Set `BUILD_DIR` to place generated files
elsewhere. Nothing from `PHARLAP_HOME` is copied into the build directory.

`PHARLAP_HOME` is required while linking. At runtime, reference data are found
in this order:

1. the CLI's `--data-root` argument or a call to
   `pharlap_iri2020_set_data_root`;
2. `DIR_MODELS_REF_DAT`, which must name the directory containing `iri2020/`;
3. `$PHARLAP_HOME/dat`.

The root cannot be changed after the first model call because the Fortran model
uses persistent global state.

## CLI

The audit-friendly command emits one JSON object and writes errors only to
stderr:

```sh
build/pharlap_iri2020 \
  --lat-deg -30 \
  --lon-deg 90 \
  --utc 2014-03-08T00:00:00Z \
  --height-start-km 100 \
  --height-step-km 10 \
  --height-count 41 \
  --r12 -1 \
  --data-root /absolute/path/to/pharlap-4.7.4/dat
```

`--r12` defaults to `-1`, which selects the historical or projected R12,
IG12, F10.7, and F10.7_81 values from PHaRLAP's index files and leaves the
foF2 storm model enabled. A supplied value in `(0, 200]` uses the same F10.7
and IG12 formulae as the official wrapper and disables that storm model.

The JSON schema is `pharlap-iri2020-profile-v1`. In particular:

```text
profiles.height_km
profiles.electron_density_m3
profiles.neutral_temperature_k
profiles.ion_temperature_k
profiles.electron_temperature_k
profiles.o_plus_density_m3 ... profiles.n_plus_density_m3
profiles.d_region_model_auxiliary
profiles.plasma_to_gyro_frequency_ratio
iono_extra
```

There are 15 named profile arrays and 100 `iono_extra` values. The native
model computes float32 values. JSON uses `null` for a non-finite float and
retains IRI's documented `-1` unavailable-value sentinel. `iono_extra[0]` is
NmF2 in m^-3 and `iono_extra[1]` is hmF2 in km.

The helper uses geographic coordinates, UTC (`25 + decimal UTC hour` in the
IRI ABI), ion densities in m^-3, ion drift enabled, spread-F probability
enabled, and IRI diagnostic messages disabled. These are the PHaRLAP 4.7.4
MATLAB wrapper defaults. Seconds are accepted as a direct refinement of its
minute-resolution input and are included in the decimal UTC hour.

Calendar dates are validated and then checked against both `ig_rz.dat`'s
month coverage and `apf107.dat`'s day coverage before invoking IRI.

## Batch C ABI

Include `pharlap_iri2020.h` and load `libpharlap_iri2020.so`. The main batch
entry point is:

```c
int pharlap_iri2020_profiles(
    const struct pharlap_iri2020_request *requests,
    size_t request_count,
    float *profile_rows,
    size_t profile_stride,
    size_t profile_rows_capacity,
    float *iono_extra,
    size_t extra_stride,
    size_t iono_extra_capacity,
    size_t *failed_request,
    char *error_message,
    size_t error_message_capacity);
```

For request `i`, its output starts at `profile_rows + i*profile_stride` and is
row-major `[15][height_count]`. Its extras start at
`iono_extra + i*extra_stride`, where `extra_stride` is at least 100. This lets
a Python `ctypes` worker load the model once and fill NumPy arrays without JSON
or one process launch per spatial cell. Requests may have different grids if
`profile_stride` is large enough for the largest one.

The library owns a process-wide mutex and runs the batch serially. Do not fork
after initializing the Fortran model. For reproducible large grids, quantize
space/time explicitly in the caller, retain the quantization in artifact
metadata, group cache misses into batches, and record the archive/data hashes.

## Verified fixture

For latitude -30 degrees, longitude 90 degrees, 2014-03-08 00:00 UTC,
100--500 km in 10 km steps, and historical `R12=-1`, the retained fixture is:

```text
Ne(100 km) = 2.19484549e10 m^-3
Ne(300 km) = 2.73383801e11 m^-3
Ne(500 km) = 8.28074230e10 m^-3
NmF2       = 2.82978517e11 m^-3
hmF2       = 275.058929 km
foF2       = 4.77697611 MHz
```

The test also calls two profiles through the batch shared-library ABI and
checks rejection of a date outside the supplied index coverage.
