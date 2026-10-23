cat > hydro_ot_entry.txt <<'EOF'

## 2026-10-09 - interface request from hydroacoustics (sound speed, path bathymetry), and a stub disclosed

Hydroacoustics needs two things from the shared layer. Neither is a likelihood input on its own:
both feed a propagation engine (KRAKEN normal modes; RAM PE as a cross-check), whose transmission
loss and travel time then enter the module's predictions.

**1. Sound-speed profiles.** c(z) from the surface to the local bottom at an arbitrary
(lat, lon, time), from the same TEOS-10 evaluation that serves settling's density, as settling
recommended. Climatology is adequate for propagation, but the time axis must be at least seasonal
and should be monthly in the upper 1,500 m. I need the product's own spread as well as its mean
(WOA's standard deviation or an ensemble), so that sound-speed uncertainty becomes a declared
alternative rather than a hidden constant. Times needed: October 2001 (Blackman airgun lines),
May-June 2003 (Blackman A1-A11), March 2014 (MH370), and the F-35A event at H11 (Brown et al. 2026).
Product choice is yours.

**2. Bathymetry along geodesic paths, not at points.** Depth along WGS84 geodesics of 1,600 to
about 10,000 km: source region to H01 and H08 for MH370 and Blackman, and to H11 for the F-35
calibration. It should come at the native grid resolution, with the Type Identifier kept per sample
and with a cross-track corridor query (the maximum elevation within a stated half-width), because
blockage is set by the shallowest feature in the ensonified corridor, not only on the track. It
should be one surface shared with settling's impact-point lookup (AusSeabed near source, GEBCO
elsewhere, with a provenance flag), never two.

Frame: geographic WGS84, depth positive down in metres, pressure from depth by gsw.

**Stub disclosed (approved 2026-10-09, morning rulings item 5), so that you can reject it rather than
inherit it.** It lives in `hypotheses/hydroacoustics/data/stub/`, built by
`prepare/build_path_stub.py`. Every number through it is PROVISIONAL, and it is deleted when this
API serves profiles and bathymetry. Its assumptions:
- **Two paths only:** air9 (line midpoint -27.5612, 98.8821) to the H01W and H08S triad centroids
  (FDSN). The H08S position is the 2002 FDSN epoch, used for a 2001 event.
- **Bathymetry:** GEBCO_2026 ice-surface grid and TID via OPeNDAP at CEDA. Nearest cell (no
  interpolation) every 0.5 km along track, plus the corridor maximum within +/-2 km across track.
- **Sound speed:** WOA23 decade 95A4 (1995-2004), season 16 (Oct-Dec), 1.00 deg, t_an and s_an only
  (no spread yet), bilinear in latitude and longitude, native levels, every 25 km. gsw SA_from_SP,
  CT_from_t, sound_speed at in-situ pressure. A level is NaN where WOA has no data, never filled.
- **What it does NOT do:** no time interpolation within a season, no mesoscale variability, no
  sediment or geoacoustic bottom model (that is mine to declare inside the propagation engine), no
  uncertainty.
EOF
echo drafted