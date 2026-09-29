# NOAA IGRF-14 magnetic declination grid

This source package derives the compact east-positive magnetic-declination
input used by the MH371 control.

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
python .sources/noaa-igrf14-magnetic/code/build_mh371.py
~~~

The builder linearly interpolates spherical-harmonic coefficients between the
2010 and 2015 epochs at decimal year 2014.1785388127853, synthesises the field,
converts geocentric components back to geodetic north/east, and writes
east-positive declination over the same eight flight levels and 0.5-degree
regional grid as ERA5.

### MH370 accident-flight runtime grid

The accident-flight grid is compiled from the preserved independent IGRF-14
recreation with SHA-256
`642d6d57c121aeaefeb45c5539a5da0613d5b91bd118228354c689b4f43e3107`.
The compiler refuses any other source identity:

~~~bash
python .sources/noaa-igrf14-magnetic/code/build_mh370_from_preserved_npz.py \
  /path/to/igrf14-declination-grid.npz \
  inputs/environment/mh370-igrf14-grid.bin \
  inputs/environment/mh370-igrf14-grid.manifest.json
~~~

The 0.5-degree runtime grid covers 25,000-43,000 ft, 60°S-50°N, and
55-125°E. Its SHA-256 is
`9910a4952f43de2c3a5f07df3a7879139b9d23267a5d4e77dbfedae093973b0e`
and its size is 874,020 bytes.


## Integrity and result

- builder SHA-256:
  e89376d858909ff61c8485ea10eb6bfe844af650cd756b30637f9c02932aa4c0
- binary SHA-256:
  16d31a7db48e0440a46b1a77ae7bf2d3fa6963d834a560be20377b68d5390bec
- manifest SHA-256:
  52a3e1b95af255687d63faaa6c8a34ae7ed9a9ff3ad5ec48c89c58c5193a2383
- binary size: 634,188 bytes
- independent fixture at 5.624829 N, 99.048157 E and 35,000 ft:
  -0.409746922 degrees east-positive.

The Rust parser checks the exact binary layout, monotonic axes, finite values,
bounds, and trilinear interpolation. Its heading convention is explicitly
true heading = magnetic heading + east-positive declination.

## Limitations

IGRF represents the large-scale core field, not local crustal anomalies. A
single epoch is used for this six-hour control; secular variation over that
interval is negligible.
