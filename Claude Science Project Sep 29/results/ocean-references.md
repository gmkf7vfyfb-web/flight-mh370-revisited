# Shared ocean transport (`engine/crates/ocean`) — citation ledger

This ledger is kept under the architecture standing rule of 9 October (`coordination/architecture.md`,
commit 419a760; location ruled ~02:25 UTC: `results/`, since `AGENTS.md` allows no further `.md` under
`engine/`), with `ocean-references.bib` beside it. It has one entry per source, giving:
- what the source supports, and where in this crate it is used;
- how it was obtained;
- its licence.

Per-file sha256 values for downloaded data are in `results/ocean-data-manifest.md`. The data themselves are
in `/Users/pete/Downloads/mh370-ocean-data/`, never in git or the artifact store.

**Pages.** For a quoted value, "page verified" means the printed page was read from the running header.
"page not verified" means the value was taken from the producer's web page or metadata, and the printed
page is still to be read.

## Ocean and wave products

### GLORYS12V1 — `lellouche2021glorys12`, `cmems_glo_phy_001_030`
- **Reference:** Lellouche, J.-M. et al. (2021). The Copernicus Global 1/12° Oceanic and Sea Ice GLORYS12
  Reanalysis. *Frontiers in Earth Science* 9:698876. doi:10.3389/feart.2021.698876.
- **Dataset:** Copernicus Marine Service, GLOBAL_MULTIYEAR_PHY_001_030, dataset
  `cmems_mod_glo_phy_my_0.083deg_P1D-m`, version 202311 (from the Toolbox), doi:10.48670/moi-00021.
- **Supports:**
  - the `glorys12v1` record in `src/products.rs`;
  - surface `uo`/`vo` forcing for drift, Pléiades and settling's float phase;
  - the content declaration (geostrophic and Ekman included; no tides or Stokes; daily mean).
- **Quoted values:**
  - "daily means over a day (midnight to midnight, centred at noon)": CMEMS-GLO-PUM-001-030 (2017 issue),
    section II.4. **Page not verified.**
  - Time labels at 00:00 UTC: read from the downloaded files.
  - Placing each mean at label + 12 h is **provisional** until the producer confirms the convention.
- **Obtained:**
  - Copernicus Marine Toolbox 2.5.0, credential COPERNICUS, `prepare/fetch_forcing.py`;
  - 2014-03-07 to 2017-01-31, 15-120 E, 50-0 S, top level 0.494 m;
  - accessed 8-9 October 2026.
- **Licence:** Copernicus Marine Service product licence (free use, attribution required).

### WAVERYS — `lawchune2021waverys`, `cmems_glo_wav_001_032`
- **Reference:** Law-Chune, S. et al. (2021). WAVERYS: a CMEMS global wave reanalysis during the altimetry
  period. *Ocean Dynamics* 71, 357–378. doi:10.1007/s10236-020-01433-w.
- **Dataset:** GLOBAL_MULTIYEAR_WAV_001_032, `cmems_mod_glo_wav_my_0.2deg_PT3H-i`, version 202411 (from the
  Toolbox), doi:10.48670/moi-00022.
- **Supports:** surface Stokes drift `VSDX`/`VSDY`, 3-hourly instantaneous, as the `StokesDrift` component.
- **Quoted values:** forced by ERA5 winds and GLORYS12 currents, 0.2 degrees, 3-hourly (product page).
  **Page not verified.**
- **Obtained:** Toolbox 2.5.0, same box and period, accessed 9 October 2026.
- **Licence:** Copernicus Marine Service product licence.

### ERA5 10 m wind, via ARCO-ERA5 — `hersbach2020era5`, `carver2023arcoera5`
- **References:**
  - Hersbach, H. et al. (2020). The ERA5 global reanalysis. *Quarterly Journal of the Royal Meteorological
    Society* 146(730), 1999–2049. doi:10.1002/qj.3803.
  - Carver, R. W. and Merose, A. (2023). ARCO-ERA5: An Analysis-Ready Cloud-Optimized Reanalysis Dataset.
    22nd Conference on Artificial Intelligence for Environmental Science, AMS Annual Meeting.
- **Data:** `u10`/`v10`, store `gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3`, read
  over HTTPS. Every third hour (00, 03 ... 21 UTC) was taken, 2014-03-07 to 2017-01-31T21.
- **Supports:**
  - the `Wind10m` component (`c_wind` and `leeway_speed_mps`);
  - the `era5-wind10` record.
  - This is genuine ERA5, so no wind-product substitution was made.
- **Obtained:** `prepare/fetch_forcing.py era5`, anonymous, accessed 9 October 2026.
- **Licence:** ERA5 is a Copernicus Climate Change Service product under the Copernicus licence, and
  ARCO-ERA5 redistributes it. **To verify:** the exact licence statement on the ARCO-ERA5 dataset page.

### BRAN2016 (Bluelink ReANalysis) — `oke2013ofam3`, `chamberlain2021bran2020`
- **References:**
  - Oke, P. R. et al. (2013). Evaluation of a near-global eddy-resolving ocean model. *Geoscientific Model
    Development* 6, 591–615. doi:10.5194/gmd-6-591-2013. This is the OFAM3 model behind BRAN.
  - Chamberlain, M. A. et al. (2021). Next generation of Bluelink ocean reanalysis with multiscale data
    assimilation: BRAN2020. *Earth System Science Data* 13, 5663–5688. doi:10.5194/essd-13-5663-2021. Used
    for its description of and comparison with BRAN2016.
- **Data:** NCI THREDDS `gb6/BRAN/BRAN_2016/OFAM/ocean_{u,v}_YYYY_MM.nc`, top level 2.5 m, through the
  NetCDF Subset Service.
- **Supports:**
  - the reproduction arm of ruling D-b (CSIRO system on BRAN2016);
  - the coverage finding: January 1994 to August 2016, from the NCI file list read 9 October 2026.
- **Status:**
  - **Not in use.** The CSIRO terms (`gb6_license.txt`) require registration with CSIRO *before access*
    and restrict use to government-funded research (clauses 1, 4 and 5).
  - 15 monthly files (March to October 2014, 544 MB) were fetched before the terms were read. The download
    is stopped pending Pete's decision.
  - Required acknowledgement if used: "The Bluelink ocean data products were provided by CSIRO. Bluelink is a
    collaboration involving the Commonwealth Bureau of Meteorology, the Commonwealth Scientific and
    Industrial Research Organisation and the Royal Australian Navy".
- **Licence:** CSIRO Bluelink terms (see Status).

### OSCAR v2.0 Final (catalogue record only; not downloaded) — `esr2021oscar`
- **Reference:** ESR; Dohan, K. (2021). Ocean Surface Current Analyses Real-time (OSCAR) Surface Currents -
  Final 0.25 Degree (Version 2.0). PO.DAAC. doi:10.5067/OSCAR-25F20.
- **Supports:**
  - the `oscar-v2-final` content declaration (geostrophic, Ekman and thermal wind; top-30 m average;
    `ug`/`vg` given with depth = 15 m), from the OSCAR v2.0 User's Handbook. **Page not verified.**
- **Licence:** NASA Earthdata open data.

## Bathymetry

### GEBCO_2026 Grid — `gebco2026`
- **Reference:** GEBCO Compilation Group (2026). GEBCO 2026 Grid. doi:10.5285/4f68d5c7-45eb-f999-e063-7086abc036fa.
- **Data:** the global 15 arc-second ice-surface elevation grid and its Type Identifier (TID) grid, from
  BODC via CEDA:
  - `https://dap.ceda.ac.uk/bodc/gebco/global/gebco_2026/ice_surface_elevation/netcdf/GEBCO_2026.nc`;
  - `.../type_identifier_grid/netcdf/gebco_2026_tid.nc`.
  The 40-180 E, 60 S-30 N region is copied unchanged by `prepare/gebco_to_grid.py`.
- **Supports:** the `gebco_2026` layer of `src/bathy.rs`, with its per-cell TID. It is the one bathymetry
  surface for settling, hydroacoustics and searched areas.
- **Licence:** GEBCO Grid terms of use (public domain, attribution requested). **To verify** against the
  statement distributed with the grid.

### AusSeabed / Geoscience Australia MH370 Phase 1, 150 m — `spinoccia2017mh370`
- **Reference:** Spinoccia, M. (2017). MH370 Phase 1 150m Bathymetry datasets (GA-4421, GA-4422 & GA-4430).
  Geoscience Australia. https://pid.geoscience.gov.au/dataset/ga/100315.
- **Use:** the first layer of `src/bathy.rs` inside its coverage, ahead of GEBCO_2026.
- **Obtained 9 October 2026** from the download link in GA's eCat record d887e71a-71dc-4851-94a9-920f7b7cc7e5
  (`files.ausseabed.gov.au`, `Southern Indian Ocean (MH370) Bathymetry 2017 150m.zip`, last modified
  14 April 2022).
  - The record gives the publication date as 14 July 2017.
  - Contents: one cloud-optimised GeoTIFF on EPSG:3857 (WGS 84 / Pseudo-Mercator) with 150 m projected
    cells, float32 elevation relative to MSL. 27,012 × 27,443 cells cover 79.37–115.77 E and 42.14–9.52 S;
    47,052,808 cells hold values, from −7,013 to −11 m.
  - sha256 values are in `ocean-data-manifest.md`.
- **Kept on its own grid** rather than resampled. `bathy.rs` gained EPSG:3857 layers (exact spherical
  Mercator with a = 6,378,137 m on WGS84 geodetic coordinates, per the EPSG definition), so every answer is
  a distributed cell value. On this grid, 150 m projected cells are about 123 m on the ground at 35 S.
- **Relation to GEBCO_2026:** at 254,015 random valid cells, AusSeabed − GEBCO = +0.3 m mean, 20.6 m SD,
  and 5–95% −25.2 to +26.8 m. 99.6% of those GEBCO cells are TID 11 (multibeam). GEBCO_2026 therefore
  already carries these surveys at 15 arc-seconds, and the AusSeabed layer adds resolution rather than new
  soundings.
- **Licence:** CC BY 4.0, as stated in the eCat record (verified 9 October 2026).

## Thermodynamics and geodesy

### TEOS-10 — `ioc2010teos10`, `mcdougall2011gsw`, `roquet2015polynomial`
- **References:**
  - IOC, SCOR and IAPSO (2010). *The international thermodynamic equation of seawater – 2010: Calculation and
    use of thermodynamic properties.* Intergovernmental Oceanographic Commission, Manuals and Guides No. 56,
    UNESCO.
  - McDougall, T. J. and Barker, P. M. (2011). *Getting started with TEOS-10 and the Gibbs Seawater (GSW)
    Oceanographic Toolbox.* SCOR/IAPSO WG127. ISBN 978-0-646-55621-5.
  - Roquet, F. et al. (2015). Accurate polynomial expressions for the density and specific volume of
    seawater using the TEOS-10 standard. *Ocean Modelling* 90, 29–43. doi:10.1016/j.ocemod.2015.04.002.
- **Software:**
  - the official Python `gsw` (GSW-C wrapper), used in preparation for `SA_from_SP` and `CT_from_t`;
  - GSW-rs (`gsw` crate 0.2.3), used at runtime for `rho`, `sound_speed`, `p_from_z`, `ct_from_pt` and
    `sr_from_sp`.
  - The two agree to 1e-9 on the fixtures in `tests/transport.rs`.
- **Supports:** `src/teos10.rs`, `src/soundspeed.rs`, `prepare/woa23_to_soundspeed.py`.
- **Licence:** TEOS-10 and the GSW software are distributed openly (GSW: BSD-style). **To verify** per
  package.

### WGS84 geodesics — `karney2013geodesics`
- **Reference:** Karney, C. F. F. (2013). Algorithms for geodesics. *Journal of Geodesy* 87, 43–55.
  doi:10.1007/s00190-012-0578-z.
- **Implementation:** `geographiclib-rs` 0.2.7.
- **Supports:** `Bathymetry::path` and `Bathymetry::inverse`. Air9 to H01W is 1,662.83 km, matching the
  1,662.8 km of ruling H1.
- **Licence:** MIT.

## Climatology

### World Ocean Atlas 2023 — `reagan2024woa23`, `locarnini2024woa23t`, `reagan2024woa23s`
- **References:**
  - Reagan, J. R. et al. (2024). World Ocean Atlas 2023. NOAA NCEI. doi:10.25921/va26-hv25.
  - Locarnini, R. A. et al. (2024). *World Ocean Atlas 2023, Volume 1: Temperature.* A. Mishonov, Technical
    Editor. NOAA Atlas NESDIS 89, 52 pp. doi:10.25923/54bh-1613.
  - Reagan, J. R. et al. (2024). *World Ocean Atlas 2023, Volume 2: Salinity.* A. Mishonov, Technical Editor.
    NOAA Atlas NESDIS 90. doi:10.25923/70qt-9574.
- **Data:** 1-degree `woa23_{95A4,A5B4,B5C2,decav}_{t,s}{01..16}_01.nc` from NCEI THREDDS.
- **Supports:**
  - the decade means (`*_an`) for each epoch;
  - the spread, from the all-decade objectively analysed standard deviations (`*_sdo`).
  - **Finding (from the files):** the decadal `*_sd` fields exist in only 16-38% of cells, and the 1995-2004
    `*_sdo` are exactly zero in about 30% of ocean cells. That is why the spread comes from `decav`.
- **Licence:** NOAA NCEI public domain (CC0 for the Atlas volumes).

## Object response and method

### Sutherland et al. (2020) — `sutherland2020leeway`
- **Reference:** Sutherland, G. et al. (2020). Evaluating the leeway coefficient of ocean drifters using
  operational marine environmental prediction systems. *Journal of Atmospheric and Oceanic Technology*
  37(11), 1943–1954. arXiv:2005.09527, doi:10.48550/arXiv.2005.09527. **Journal DOI to verify.**
- **Supports:** the `leeway_absorbs_stokes` refusal. Implicit and explicit leeway models differ in whether
  Stokes drift is inside the coefficient (abstract).

### Griffin, Oke and Jones (2017), CSIRO Part II — `griffin2017partii`
- **Reference:** Griffin, D. A., Oke, P. R. and Jones, E. M. (2017). *The search for MH370 and ocean surface
  drift – Part II.* CSIRO Oceans and Atmosphere, Australia.
- **Supports:** `ObjectResponse::leeway_speed_mps` (ruling D-d). The constant-magnitude flaperon leeway of
  about 10 cm/s, about 16 degrees left of downwind, is on pp. 9–10.
- **Page note:** taken from drift's provenance note `results/debris-drift-flaperon-provenance.md`, **not read
  by this module**.
- **Also supports:** `ObjectResponse::wind_angle_deg` (ruling D-f, 9 Oct). CSIRO rotates only the extra
  constant-magnitude leeway, not the proportional windage (p. 13, Fig. 3.1 caption, as cited in the
  architecture ruling; **not read by this module**).

### Random-flight and random-Fourier error models — `griffa1996stochastic`, `rahimi2007random`
- **References:**
  - Griffa, A. (1996). Applications of stochastic particle models to oceanographic problems. In Adler, R.,
    Müller, P. and Rozovskii, B. (eds.), *Stochastic Modelling in Physical Oceanography*, Birkhäuser,
    113–140.
  - Rahimi, A. and Recht, B. (2007). Random features for large-scale kernel machines. *Advances in Neural
    Information Processing Systems* 20.
- **Supports:**
  - `Diffusion::RandomFlight`, an Ornstein-Uhlenbeck velocity;
  - the `Eddying` ocean-error field, a Gaussian-spectrum streamfunction drawn as random Fourier modes.
  - These are method citations only; no value is quoted.

### Copernicus Marine Toolbox — `copernicusmarine_toolbox`
- **Software:** `copernicusmarine` 2.5.0, for server-side subsetting of GLORYS12 and WAVERYS.

### GSHHG shoreline database, version 2.3.7 — `wessel1996gshhg`, `gshhg237`
- **Reference:** Wessel, P. and Smith, W. H. F. (1996). A global, self-consistent, hierarchical,
  high-resolution shoreline database. *Journal of Geophysical Research: Solid Earth* 101(B4), 8741–8743.
  doi:10.1029/96JB00104 (verified on Crossref).
- **Data:** GSHHG 2.3.7 (15 June 2017), binary distribution `gshhg-bin-2.3.7.zip` from the SOEST mirror,
  full-resolution shorelines `gshhs_f.b`. Licence: GNU LGPL version 3 or later (`LICENSE.TXT` in the
  distribution). sha256 values are in `ocean-data-manifest.md`.
- **Supports:** `gshhg::PolygonCoast`, the real coastline. It uses level-1 (ocean/land) polygons, the
  big-endian header and micro-degree point layout of the distribution's `README.TXT`, and WGS84 geodetic
  coordinates (README note C, which also says the WDBII-derived lakes may be WGS72 and that offsets from
  modern GPS positions have been noted).
