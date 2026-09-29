# Native PHaRLAP spherical 2-D ray helper

This independently written shared-library boundary exposes PHaRLAP 4.7.4's
`raytrace_2d_sp_` engine without MATLAB. It contains no PHaRLAP source,
archive, or data. Every user must obtain PHaRLAP directly from Australia's
Defence Science and Technology Group and comply with the distribution's
release limitation, disclaimer, and acknowledgement requirements.

The spherical engine is intentional for this source audit. Candidate geometry
is defined on spherical great circles. A ray's horizontal coordinate is the
central angle times the caller-supplied Earth radius, so the scalar ray path
can be mapped back to one fixed, oriented great-circle branch without the
near-antipodal WGS84 bearing drift of `raytrace_2d_`. This is exact only within
the declared spherical model, not on the WGS84 ellipsoid.

## External identities and build

- `lib/linux/libpropagation.a` SHA-256:
  `f33616ee1ea695ab424b98a9ab5f6d9a8e0daf664d81f2822351788d40e627eb`
- `lib/linux/libmaths.a` SHA-256:
  `b5a894dd80b206c0e2d22f9ff543da398276135b278918de16ec2a7a76753eb3`

Build and test from this directory:

```sh
make -f Makefile.pharlap_sp \
  PHARLAP_HOME=/absolute/path/to/pharlap-4.7.4 verify all test
```

The output is `build/libpharlap_raytrace_2d_sp.so`. Set `BUILD_DIR` to put
generated files elsewhere. Linking uses the external archives in this order:

```text
libpropagation.a libmaths.a -lgfortran -lgomp -lm
```

Set `NRT_NUM_THREADS` explicitly and record it with results. The native engine
uses OpenMP internally; the helper serializes public calls to avoid concurrent
access to the persistent Fortran state and hidden ionosphere.

## Ionosphere boundary

Call `pharlap_raytrace_2d_sp_set_ionosphere` before tracing. Inputs are
range-major contiguous arrays:

```text
electron_density_cm3[range][height]
electron_density_5min_cm3[range][height]
collision_frequency_hz[range][height]
```

The five-minute density may be null to reuse the first density grid. Collision
frequency may be null to use zeros. IRI2020 profiles are in m^-3 and therefore
must be multiplied by `1e-6` before this call. Replace IRI's `-1` unavailable
sentinel deliberately; the helper rejects negative and non-finite grid values.

The authoritative compiled ABI permits up to 3,001 ranges and 3,001 heights,
despite stale MATLAB prose saying 2,001. The helper hides the fixed-stride
216,240,088-byte native structure and accepts compact caller arrays. It
intentionally disables field-aligned irregularities; this makes bearing
irrelevant to ray kinematics and avoids claiming an unsupported irregularity
model.

## Fan trace and zero-copy outputs

`pharlap_raytrace_2d_sp_trace` traces one elevation/frequency fan through the
configured range slice. All rays share bearing, Earth radius, hop limit, and
solver settings. Frequencies and elevations are one value per ray. Hops must be
1--50. The official solver bounds are enforced.

To avoid copying a potentially hundreds-of-megabytes path result, output stays
in the Fortran-native layout. With `R` rays:

```text
hop_data[hop][22][ray]
  offset = ray + R * (field + 22 * hop)

ray_labels[hop][ray]
  offset = ray + R * hop

path_data[point][9][ray]
  offset = ray + R * (field + 9 * point)
```

Only `hops_attempted[ray]` hop records and `points_in_ray[ray]` path records
are valid. The path buffer must reserve `20000 * 9 * R` doubles. A NumPy caller
can view it without copying as `(20000, 9, R)` and transpose axes logically.
The helper allocates an equally sized virtual scratch buffer for unreturned
state vectors because the supplied wrapper always gives the Fortran engine a
valid state buffer.

Useful hop fields are enumerated in `pharlap_raytrace_2d_sp.h`: ground range is
2, group range 3, apogee 4, range to apogee 5, initial/final elevation 6/7,
Doppler spread/shift 8/9, geometric path 10, effective range in metres 11,
deviative absorption 12, plasma frequency at apogee 13, virtual height 15,
phase path 16, TEC 17, total absorption 18, and FAI outputs 14/19/20/21. Slots
0 and 1 are unused common-layout placeholders and may be NaN.

Path fields 0--8 are ground range km, height km, group range km, phase path
km, geometric distance km, electron density cm^-3, refractive index, collision
frequency Hz, and cumulative absorption dB.

Ray labels are 1 for a ground return, 0 for evanescence, -2 for penetration,
-3 for range-grid exhaustion, -4 for negative angular coordinate, -5 for the
20,000-point limit, -6 for the engine's antipodal guard, and -100 for a
catastrophic failure. Treat any non-1 label as an explicit modeled outcome,
not a missing value.

## Verified spherical fixture

The test uses 201 ranges by 201 heights, 50 km horizontal steps, heights
0--600 km by 3 km, and a smooth Gaussian F2 layer. For one 10 MHz ray at 20
degrees elevation, bearing 324.7 degrees, one hop, and radius 6371.2 km:

```text
label                       1
path points                 80
ground range                1124.9340929149112 km
group range                 1238.5893823864571 km
apogee                      199.77471243063155 km
geometric path              1216.7201738709118 km
plasma frequency at apogee  4.1104155592089873 MHz
```

The terminal path point is at zero height and its range equals the hop ground
range. The underlying state-vector audit additionally found terminal central
angle `0.17656549675334493` radians; multiplying by 6371.2 km gives the ground
range exactly at printed-double precision. With irregularities off, changing
bearing produced identical hop and path values.

## Cache boundary

A cached spherical fan is reusable only when all of these are identical:

- Earth radius and oriented great-circle branch;
- the complete along-range density, five-minute density, collision, height,
  and range grid identity;
- epoch/quantization, frequency fan, elevation fan, hop count, and solver
  settings;
- bearing if a future interface enables irregularities.

The ray engine returns ground range rather than latitude/longitude. Map each
range externally with the same spherical direct-geodesic formula used to
define the candidate branches, and retain the spherical-model choice in every
artifact. A possible model ray is not evidence that the WSPR signal used it.
