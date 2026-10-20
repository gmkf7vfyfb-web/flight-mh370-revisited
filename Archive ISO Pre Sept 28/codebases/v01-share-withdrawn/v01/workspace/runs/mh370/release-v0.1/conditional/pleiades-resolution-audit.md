# Pléiades numerical-resolution audit

The frozen release executable was run at 512, 2,000, 8,000, and 30,000 impact draws per
seed across five numerical seeds. BRAN2016, OSCAR v2 Final, GLORYS12 + WAVERYS, and the
uncalibrated equal-family surface were applied separately; no surfaces were pooled or
stacked.

At 150,000 total impact particles, conditional ESS was only 5.63 (BRAN2016), 9.14
(OSCAR), 6.13 (GLORYS/WAVERYS), and 5.63 (equal-family). The conditional centroids lay
42.38–58.27 NM from the baseline centroid. From 40,000 to 150,000 particles, centroid
movement was 3.19, 0.76, 1.37, and 3.19 NM respectively; native-cell total variation was
0.365, 0.0046, 0.0023, and 0.365. Even where a native grid mode stabilized, one particle
still carried 22–36% of conditional mass.

Native support retained 99.9203% of baseline mass, and floored particles received
negligible conditional mass, so neither support truncation nor the numerical floor caused
the collapse.

**Conclusion:** no Pléiades-conditioned centroid, HPD contour, or area is numerically
resolved in this release. All four branches are display-only diagnostics and must not be
used to rank locations, allocate search area, or update the central posterior. The
150,000-particle pilots establish this failure and are not promoted.

See [machine audit](pleiades-resolution-audit.json), [complete ladder table](pleiades-resolution-audit.csv),
and the [conditional branch README](README.md).
