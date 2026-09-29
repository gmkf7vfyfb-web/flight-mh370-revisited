# NOAA IGRF-14 magnetic declination grid

This source package derives the compact east-positive magnetic-declination
inputs used by the MH370 broad inference and the MH371 control.

## Source and claim

NOAA/NCEI describes IGRF as the standard mathematical representation of the
Earth's main magnetic field and provides IGRF-14 coefficients and software:
https://www.ncei.noaa.gov/products/international-geomagnetic-reference-field

The exact NOAA Python package is data/pyIGRF14.zip, SHA-256
82202de7057e9525509b4b288b1e52d2c272543b5dedf89f2bbbddb83b1352f2.
The embedded IGRF14.SHC coefficient file hashes to
716f9fa7c531933e74447c345224721111061313dbeb9419f8f3fd7f0ba3e65b.

## Reproduction

~~~bash
python .sources/noaa-igrf14-magnetic/code/build_mh370.py
python .sources/noaa-igrf14-magnetic/code/build_mh371.py
~~~

Each builder linearly interpolates spherical-harmonic coefficients between the
2010 and 2015 epochs, synthesises the field, converts geocentric components
back to geodetic north/east, and writes east-positive declination on the same
pressure-altitude and horizontal axes as its ERA5 counterpart.

### MH370 accident-flight runtime grid

The accident-flight grid is now derived directly from the frozen NOAA package
in this source directory. At decimal year 2014.1808219178083 it covers the
complete globe at 0.5-degree spacing and all twelve configured pressure
altitudes from 500 to 43,000 ft. The `+180`-degree column exactly duplicates
the `-180`-degree physical meridian so the non-periodic runtime interpolator
can bracket every valid longitude.

The two exact geographic-pole rows use the finite one-sided meridional limit
at `+/-89.999999` degrees. The official helper can otherwise round an internal
cosine outside `[-1,1]` at a few altitude/pole combinations. Declination and
the north/east coordinate basis are physically undefined at the exact poles;
this finite representation prevents a numerical NaN but does not claim extra
physical information there.

- builder SHA-256:
  `a2b67a4069f3c6ac959b597f49b7ebdd87528ac057738090408024b77dfaca80`
- binary SHA-256:
  `ad71fa679c7933858e8748fa34b124f4e405921b337c92aeb7efeb1002ac6ac1`
- manifest SHA-256:
  `6539167e7c8dcac8d6007517eca41aa3987b367791fa40bb768a37bb1b703b16`
- binary size: 12,497,900 bytes

An immediate second build reproduced both the binary and manifest byte for
byte. An independent binary-layout scan found shape `12 x 361 x 721`, strictly
increasing altitude/latitude/longitude axes, 3,123,372 finite values, and exact
equality of every `-180`/`+180` seam pair. Five ordinary grid nodes compared
directly with the frozen NOAA synthesiser to at most
`7.260e-6` degrees (the expected float32 storage error). Four off-node checks,
including both sides of the date-line, compared the runtime's circular
trilinear interpolation with direct IGRF synthesis to at most
`5.410e-4` degrees. The exact-pole rows were separately checked finite. The
canonical Rust artifact-loader and trajectory partition-invariance test also
passes against these installed files.

## MH371 integrity and result

- builder SHA-256:
  `48d72702d9d440c75a445cddb8d29bfbc24273a0e6e6a9528ea0724d7306fe2c`
- binary SHA-256:
  `fbedb84fe68c6e547ff484fec47fbc89e28660fb2010ba4f336d0622467c933f`
- manifest SHA-256:
  `ea6a110a48de056523d5c8116784e406834ef21d16d01fd5247e2b33e95b7797`
- binary size: 5,564,268 bytes
- independent fixture at 5.624829 N, 99.048157 E and 35,000 ft:
  -0.409746922 degrees east-positive.

The Rust parser checks the exact binary layout, monotonic axes, finite values,
bounds, and trilinear interpolation. Declination is interpolated as a circular
direction, so neighboring `+179` and `-179` degree values interpolate near
180 degrees rather than spuriously through zero. Its heading convention is
explicitly true heading = magnetic heading + east-positive declination.

## Limitations

IGRF represents the large-scale core field, not local crustal anomalies. One
epoch is used for each approximately five- or six-hour inference interval;
secular variation over either interval is negligible.
