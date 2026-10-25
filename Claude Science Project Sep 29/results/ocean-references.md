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
- **Status: DROPPED by Pete, 9 October 2026.** The NCI `gb6` licence requires CSIRO registration and restricts use to government-funded research. The 15 fetched files were never used and were removed on 9 October (`ocean-data-manifest.md`). The references below remain for the description of CSIRO's system only.
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

### Copernicus-GlobCurrent, MULTIOBS_GLO_PHY_MYNRT_015_003 — `cmems_mob_015_003`
- **Data:** E.U. Copernicus Marine Service Information, *Global Total (COPERNICUS-GLOBCURRENT), Ekman and
  Geostrophic currents at the Surface and 15m*, MULTIOBS_GLO_PHY_MYNRT_015_003. Datasets used:
  `cmems_obs-mob_glo_phy-cur_my_0.25deg_P1D-m` and `..._PT1H-i`, version 202411. CMEMS announces that this
  version retires on 24 November 2026.
- **Supports:** the `globcurrent-my-p1d` and `globcurrent-my-pt1h` catalogue entries. The total current
  is altimetric geostrophy plus an empirical Ekman current from ERA5 wind stress plus the barotropic tide
  (quality information document CMEMS-MOB-QUID-015-003, and the product page). The Stokes content is
  declared `Partial` by this module, because the Ekman transfer is fitted to drifters; that declaration
  is a modelling choice, not a statement in the source.
- **Files used (sha256), fetched 2026-10-09:**
  - `globcurrent_my_pt1h_uo_vo_0m_20140307-20140331.nc`
    3664986c503d319e19249ed0abe15363c4a14acf72b8bceb00328f4f4029a513
  - `globcurrent_my_p1d_uo_vo_err_0m_20140307-20170131.nc`
    4aa9366d43fc92561c813f914b921b799613842e797fab60f8870e4159b8ee8f
  - Derived grids are in `ocean-data-manifest.md`.
  - **Version 202411 retires on 24 November 2026**, as announced in the Toolbox warning. A re-fetch after
    that date gets a different version and must be re-verified against these hashes.
- **Ruling (architect, 9 October):** the second `ocean-model` value, a declared alternative at equal
  prior weight beside GLORYS12 + ERA5.
- **Licence:** Copernicus Marine Service product licence (free use with attribution).

### Global Drifter Program 6-hourly QC positions — `lumpkin2019gdp`
- **Reference:** Lumpkin, R. and Centurioni, L. (2019). Global Drifter Program quality-controlled 6-hour
  interpolated data from ocean surface drifting buoys. NOAA NCEI. doi:10.25921/7ntx-z961. These are drift's
  files and drift's citation (`debris-drift-references.md`).
- **Supports:** the transport-error replay `ocean-transport-error-gdp-replay.md`.

### OSCAR v2.0 Final — `esr2022oscar`, comparison product only
- **Data:** ESR; Dohan, K. (2022). *Ocean Surface Current Analyses Real-time (OSCAR) Surface Currents –
  Final 0.25 Degree (Version 2.0).* Version 2.0, PO.DAAC, CA, USA. doi:10.5067/OSCAR-25F20 (CMR collection
  C2098858642-POCLOUD; the citation fields are read from CMR). Accessed 9 October 2026.
- **Role: COMPARISON ONLY** (Pete, 9 October 2026). It is held to compare with prior work, which used OSCAR
  v2 Final over the upper 30 m. It is never a value of the `ocean-model` alternative: `ProductRole::Comparison`,
  and `Forcing::ocean_model()` returns `comparison:oscar-v2-final...`.
- **Contents**, from the OSCAR v2.0 user handbook (PO.DAAC public document):
  - geostrophic (CMEMS DUACS SSH) + wind-driven (ERA5 10 m wind, eddy viscosity) + thermal-wind adjustment;
  - averaged over the top 30 m of the mixed layer, with nominal depth 15 m;
  - array order (time, longitude, latitude), longitude 0–359.75. The array order was verified on the first
    file.
- **Time:** the handbook calls the file time "centered on the day", but the label reads 00:00 UTC. Each
  value is placed at 12:00 UTC of the averaged day.
- **Files:** 1,062 daily global files, 7 March 2014 – 31 January 2017, 33,255,376 bytes each and
  35,317,209,312 bytes in total.
  - Each was checked against PO.DAAC's published md5, then hashed with sha256 (per-file values in
    `oscar/grid/fetch-log.jsonl`), then cut to 15–120 E, 50–0 S. The global file was then discarded.
  - The md5 matches the prior work's source-file md5 (Drive `oscar2-currents-20140307-20160831.mhgrid.json`)
    for all 909 days that list covers. The remaining 153 days have no prior value.
- **Licence:** NASA open data through PO.DAAC. The CMR record states no use constraints; PO.DAAC asks for
  citation.

<!-- memory-records:start (generated by registry/import_memory_records.py; do not edit by hand) -->

## External facts moved from memory (25 October 2026)

These rows are records of what project memory said about external sources. They are not verified facts unless the
status column says VERIFIED or CORRECTED, and even then the check was the memory track's check of the held source.
Status values: VERIFIED (claim found in the source), CORRECTED (claim corrected against the source; use the corrected
text), PARTIAL (part of the claim found), UNVERIFIABLE (no held copy, or the claim was not found). The last column gives
the finding of the independent verifier of 25 October 2026 where there is one. Text that names a restricted source is
withheld here; the memory export row holds it.

| mem_id | written (UTC) | memory text | status | source | method and evidence | corrected text | verifier |
|---|---|---|---|---|---|---|---|
| `mem_86059d0ce98d` | 2026-10-08 14:43 | WOA23 OPeNDAP path convention at NCEI: https://www.ncei.noaa.gov/thredds-ocean/dodsC/woa23/DATA/{temperature/salinity}/netcdf/<decade>/1.00/woa23_<decade>_{t/s}<period>_01.nc. Decades: 5564..B5C2, decav, decav71A0, decav81B0 and decav91C0. Periods 00 (annual) and 13-16 (seasons) are full depth to 5,500 m on 102 levels; the monthly fields stop at 1,500 m. Variables are t_an/s_an with a time dimension of length 1; open with decode_times=False. GEBCO releases 2014-2026 (each with ice_surface_elevation, sub_ice_topography_bathymetry and type_identifier_grid) are at dap.ceda.ac.uk/thredds/catalog/bodc/gebco/global/. | UNVERIFIABLE |  | : ; held candidate files existed but the claims were not found in needle snippets or best-ranked full pages; searched: 729 Downloads PDFs + 658 artifact PDFs/texts (text needle search), Drive title search (97 queries), 15 named-report Drive searches |  |  |
| `mem_5db1021a8635` | 2026-10-09 01:45 | BRAN2016 (CSIRO Bluelink, NCI THREDDS gb6) licence terms require registration with CSIRO before access and restrict use to government-funded research. Ocean transport stopped its download on 9 Oct 2026 after 15 monthly files (Mar-Oct 2014, 544 MB, ~/Downloads/mh370-ocean-data/bran2016/); architect ruled they stay unused and unredistributed until Pete decides; the D-b reproduction arm runs on GLORYS12 as a declared departure meanwhile. | VERIFIED | https://thredds.nci.org.au/thredds/fileServer/gb6/BRAN/BRAN_2016/gb6_license.txt (HTTP 200; sha256 d4bdc483ba03... equals the row) | web fetch + session-model reading |  |  |
| `mem_e8f3151ec665` | 2026-10-09 01:45 | WOA23 decadal *_sd fields exist in only 16-38% of cells and 1995-2004 *_sdo are zero in ~30% of ocean cells; the ocean crate takes sound-speed spread from decav *_sdo instead. GEBCO_2026 TID grid is distributed as classic netCDF3 (read with scipy), elevation as netCDF4. AusSeabed MH370 150 m was unobtainable on 9 Oct (GA geoserver 502, not on NCI rr1). | UNVERIFIABLE |  | : ; held candidate files existed but the claims were not found in needle snippets or best-ranked full pages; searched: 729 Downloads PDFs + 658 artifact PDFs/texts (text needle search), Drive title search (97 queries), 15 named-report Drive searches |  |  |
| `mem_22d8763e0a29` | 2026-10-09 05:20 | AusSeabed MH370 Phase 1 150 m bathymetry (ga/100315, CC BY 4.0) IS obtainable: the direct link in GA eCat record d887e71a-71dc-4851-94a9-920f7b7cc7e5 is files.ausseabed.gov.au/survey/Southern%20Indian%20Ocean%20(MH370)%20Bathymetry%202017%20150m.zip (203 MB, one EPSG:3857 150 m float32 COG). Obtained 9 Oct 2026 to /Users/pete/Downloads/mh370-ocean-data/ausseabed/; the ocean crate reads it natively as a Web Mercator layer ahead of GEBCO. It differs from GEBCO_2026 by +0.3 m mean, 20.6 m SD (GEBCO already has these surveys as TID 11), so it adds resolution only. Supersedes the earlier 'AusSeabed unobtainable' finding. | PARTIAL | GA eCat d887e71a-71dc-4851-94a9-920f7b7cc7e5 XML; HEAD files.ausseabed.gov.au zip (202,911,079 bytes); /Users/pete/Downloads/mh370-ocean-data/ausseabed/ | web fetch + local file; VERIFIED: eCat holds the direct link, ga/100315, 'Creative Commons Attribution 4.0 International Licence'; zip 203 MB, same size on disk. Not re-run: GEBCO difference statistics (project computation). |  |  |
| `mem_ef89bbdc95b5` | 2026-10-09 15:00 | BRAN2016 licence: the CSIRO Bluelink terms are at https://thredds.nci.org.au/thredds/fileServer/gb6/BRAN/BRAN_2016/gb6_license.txt (sha256 d4bdc483ba03bfbe3c3e178df24e2d8d368122bf19084a97752ea680f461384e). Clause 1 requires registration with CSIRO (name, email, intended use) before access and feedback afterwards. Clauses 4–5 grant use only for government-funded research. Clause 9 fixes a mandatory acknowledgement wording, and clause 10 forbids sub-licensing. BRAN2020 is in the same NCI gb6 collection; its own licence file was not checked. | VERIFIED | https://thredds.nci.org.au/thredds/fileServer/gb6/BRAN/BRAN_2016/gb6_license.txt (HTTP 200; sha256 d4bdc483ba03... equals the row) | web fetch + session-model reading |  |  |
| `mem_9ab6cf6307b2` | 2026-10-09 16:49 | GlobCurrent documentation: CMEMS-MOB-QUID-015-003, issue 2.0, 3 May 2024 (sha256 afa73f97c4d3ab8b1a02f9676a212692e0a6295a5ce174028bac14285a1cefd7), from documentation.marine.copernicus.eu (allowlisted). It gives the method on pp. 5-10: geostrophy from DUACS 008_047 with a 100 km Bessel filter, Ekman U=β e^{iθ} τ with β and θ fitted to SVP drogued drifters 1993-2020 and YoMaHa as functions of latitude and ARMOR3D MLD, and FES2022 tide. OSCAR v2 user guide sha256: ffc6f6a2e5a0c16e3c9a268e466a32c16eef193e2719ccf689c51984f40d29e2. | PARTIAL |  | needle snippets from held files; VERIFIED: 1 [globcurrent-quid.pdf (ART#05a555fa), printed page 2 (header 'page 2/ 29'), PDF p. 2; also ] ; VERIFIED: 2 [globcurrent-quid.pdf (ART#05a555fa), PDF p. 6 (printed page not determined from snippet) a] ; NOT_FOUND: 3 [globcurrent-quid.pdf (ART#05a555fa), PDF pp. 3, 5 (printed page not determined)] |  |  |
| `mem_410de27d9c88` | 2026-10-09 22:37 | Raw ocean-field JSON metadata: glorys12v1_uo_vo_surface_20140307-20140430.json and globcurrent_my_p1d_uo_vo_0m-00.json say 'time_placement: label + 12 h', but their time_unix_s values already include that +12 h (the first value is 12:00 UTC on 7 Mar 2014). Use time_unix_s as given. Adding another 12 h gives 10-50 km track errors; used as given, an independent RK4 matches the mh370-ocean release tables to ≤0.07 km. | UNVERIFIABLE |  | : ; no held copy found; searched: 729 Downloads PDFs + 658 artifact PDFs/texts (text needle search), Drive title search (97 queries), 15 named-report Drive searches |  |  |
| `mem_2815bfff7531` | 2026-10-17 15:59 | Drift forcing on disk (mh370-ocean-data) ends 30 Jan 2017 (2.9 yr after impact). The CMEMS GlobCurrent multi-year product cmems_obs-mob_glo_phy-cur_my_0.25deg_P1D-m (202411) retires on 24 Nov 2026, so any extension past 2017 using it must be downloaded before then. ERA5 comes from the public ARCO-ERA5 zarr (anonymous); GLORYS12/GlobCurrent need the COPERNICUS credential. | UNVERIFIABLE |  | : ; held candidate files existed but the claims were not found in needle snippets or best-ranked full pages; searched: 729 Downloads PDFs + 658 artifact PDFs/texts (text needle search), Drive title search (97 queries), 15 named-report Drive searches |  |  |

<!-- memory-records:end -->
