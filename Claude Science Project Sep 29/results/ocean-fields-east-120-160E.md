# Ocean fields east to 160 E (ocean transport, 12 October 2026)

**Purpose:** drift's request of 12 October, ~15:00 UTC, for the Australian non-recovery term (coverage gap G26).
The same three products as the 15–120 E production fields are fetched over **120–160 E, 50–0 S**, from
7 March 2014 to 31 January 2017, in the same formats, grids, time placement and manifests.

## Use

The joined series loads with `GridField::load_series` or `load_window`, unchanged:

- GLORYS12V1: `glorys12/glorys12v1_uo_vo_surface_15-160E.series.json`
- GlobCurrent daily: `globcurrent/grid/globcurrent_my_p1d_uo_vo_0m_15-160E.series.json`
- ERA5 10 m wind: `era5/era5_u10_v10_3h_15-160E.series.json`

The joined manifests use a new `lon_join` key in `crates/ocean` (commit below):
- Adjacent longitude bands are joined into one grid.
- GLORYS12 and ERA5 share the 120 E column, and the loader requires it to be bit-identical in both bands
  (checked at every time and latitude when the series loads).
- GlobCurrent's cell-centre grid continues from 119.875 to 120.125 E, exactly one step.
- The joined field therefore interpolates across 120 E exactly as one wide grid would. Test:
  `longitude_joined_series_equals_one_wide_grid`.
- The 120–160 E bands alone are also usable: `glorys12/grid_120-160E/glorys12v1_uo_vo_surface_120-160E.series.json`,
  `globcurrent/grid/globcurrent_my_p1d_uo_vo_0m_120-160E.series.json` and `era5/era5_u10_v10_3h_120-160E.series.json`.

## Sources

| Product | Dataset (version) | Access | Grid | Time |
|---|---|---|---|---|
| GLORYS12V1 uo, vo at 0.494 m | CMEMS GLOBAL_MULTIYEAR_PHY_001_030, `cmems_mod_glo_phy_my_0.083deg_P1D-m` (202311) | Copernicus Marine Toolbox `subset`, arco-geo-series, COPERNICUS credential | 1/12°, 481 × 601, 120.0–160.0 E | daily means, label + 12 h (provisional, as before) |
| GlobCurrent uo, vo, err at 0 m | CMEMS MULTIOBS_GLO_PHY_MYNRT_015_003, `cmems_obs-mob_glo_phy-cur_my_0.25deg_P1D-m` (202411; retires 24 Nov 2026) | Copernicus Marine Toolbox `subset`, COPERNICUS credential | 0.25°, 160 × 200, 120.125–159.875 E | daily means, label + 12 h |
| ERA5 u10, v10 | ARCO-ERA5 `gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3` (public, anonymous HTTPS) | the same route as the 15–120 E files | 0.25°, 161 × 201, 120.0–160.0 E | 3-hourly instantaneous |

- **Retrieval:** 12 October 2026, 18:00–18:48 UTC. Per-file retrieval times and requests are in each
  directory's `fetch-log.jsonl`.
- **Scripts:** `engine/crates/ocean/prepare/fetch_forcing.py` (`FORCING_LON=120,160`),
  `fetch_globcurrent.py` (`FORCING_LON=120,160`) and `netcdf_to_grid.py`.
- **No other data were substituted.**

## Size and checksums

- **Total added:** 6.43 GB (6,427,681,808 bytes), including the source netCDF.
- **sha256 for every file:** `SHA256SUMS-east-120-160E.txt` (in this directory).

| File | Bytes | sha256 |
|---|---|---|
| `era5/era5_u10_v10_3h_120-160E.series.json` | 239 | 40c2feeda499512b424c574ba0aa99715ca64626fa5c8c1c4fd41431006cf101 |
| `era5/era5_u10_v10_3h_120-160E_50-0S_20140307-20141231.f32` | 621,331,200 | 4fc9ef200884b7fd44d5745dba510ecb99bf34fc0bd8dd5b43a7a939fb5d50a4 |
| `era5/era5_u10_v10_3h_120-160E_50-0S_20140307-20141231.json` | 36,746 | 537c248347c7d570770f940a33248d87b19f8572c9565be88a5c1e2fc85e5971 |
| `era5/era5_u10_v10_3h_120-160E_50-0S_20150101-20151231.f32` | 755,952,960 | 4368a53cbeb49b332f4bac50a3db0757b0a92081629d4e2aa77deb4ecd3c2b96 |
| `era5/era5_u10_v10_3h_120-160E_50-0S_20150101-20151231.json` | 44,026 | 30e6be846899302ce9a83ea7c09aab3be5df1f3d33731a82c6d148c67621ce51 |
| `era5/era5_u10_v10_3h_120-160E_50-0S_20160101-20161231.f32` | 758,024,064 | 28d503297e5833602fdcd1739fc5e03741bb74f7e812e6cfeebc60972b0c2f1c |
| `era5/era5_u10_v10_3h_120-160E_50-0S_20160101-20161231.json` | 44,138 | fe7d2eadc427c3ae74abe3d8ad168949ec6a0a90edaf44a8907bbcd288e5d3a0 |
| `era5/era5_u10_v10_3h_120-160E_50-0S_20170101-20170131.f32` | 64,204,224 | a0e3dae5d4afd3901d27c55f831ba64986923f1a930c64184e1330bc9a07a27d |
| `era5/era5_u10_v10_3h_120-160E_50-0S_20170101-20170131.json` | 6,618 | 9bb6014229e5c57c88b176284b52450275ae469ad6d74c6d7774c3003bbc1969 |
| `era5/era5_u10_v10_3h_15-160E.series.json` | 85 | abdc78f391abed9ae8ae3094f6a9ddf3ec285e0819075d1f660c3db16f93ccb0 |
| `globcurrent/globcurrent_my_p1d_uo_vo_err_0m_120-160E_20140307-20170131.nc` | 271,908,904 | c5bcb8a4a2fa88b70eb264e028219b083e7a24b985fc34c921eb5e97e516a709 |
| `globcurrent/grid/globcurrent_my_p1d_uo_vo_0m_120-160E-00.f32` | 271,872,000 | 089339975f399914edfb6002741181cd0f2894f038270ac60774f9bc12f36f44 |
| `globcurrent/grid/globcurrent_my_p1d_uo_vo_0m_120-160E-00.json` | 18,517 | 56761170ea383d49e0d5302c584aa9b423d38804938c1f2ae640af43f0a33cfb |
| `globcurrent/grid/globcurrent_my_p1d_uo_vo_0m_120-160E.series.json` | 59 | eb7fcf38017970e1e44bcb60ce836ae7196b506e837be3a5d38a54825a058415 |
| `globcurrent/grid/globcurrent_my_p1d_uo_vo_0m_15-160E.series.json` | 110 | 9fdf8cd89f71b9e380bd63f7b70647d7e005e727267821d37bad6847477ca35a |
| `glorys12/glorys12_uo_vo_120-160E_50-0S_20140307-20141231.nc` | 346,929,166 | 5a959a9b9ba47b2eea6bee0ccd30594df0dd4e8bd23f1465b11f5c955d0babee |
| `glorys12/glorys12_uo_vo_120-160E_50-0S_20150101-20151231.nc` | 422,090,226 | d54b39858cfa798a3fb043c13e72e5cd4aa884e9ee3e1b339538df15d27eedb1 |
| `glorys12/glorys12_uo_vo_120-160E_50-0S_20160101-20161231.nc` | 423,246,550 | cebd2c12de70dfaea17c0be1e4b4b21ef0d5ba94c27d22dffa5f2777691f6f0f |
| `glorys12/glorys12_uo_vo_120-160E_50-0S_20170101-20170131.nc` | 35,878,010 | 8a055fba600d4f28d9353d7534acc138f6a0f79bdaddc6e88f10f977bfee4056 |
| `glorys12/glorys12v1_uo_vo_surface_15-160E.series.json` | 123 | bb8b3235043c9c10820449e03b3fe5f20744229044e4f2a2af07652238107324 |
| `glorys12/grid_120-160E/glorys12v1_uo_vo_surface_120-160E-00.f32` | 693,794,400 | cc25df7dd25f812fdf19edacb94a32c0ad12b2387d96bb475bb6b9fb35bb39a0 |
| `glorys12/grid_120-160E/glorys12v1_uo_vo_surface_120-160E-00.json` | 15,852 | 134c856112eb6e2f5830f6ce58e53d96d8386260dedac44ac9c6dbe77c84603f |
| `glorys12/grid_120-160E/glorys12v1_uo_vo_surface_120-160E-01.f32` | 844,116,520 | 3091b3dc2db166144b7f31081e50602122e281a4233ecb5ee1e468ddc6250a15 |
| `glorys12/grid_120-160E/glorys12v1_uo_vo_surface_120-160E-01.json` | 16,762 | 006437e4fb66d3029642ea70947b8f8f0fe6609e8aabc38489a5a11bf1b52bdb |
| `glorys12/grid_120-160E/glorys12v1_uo_vo_surface_120-160E-02.f32` | 846,429,168 | d800d92a32fcb2935c01eff4653a94c3812e690e406fe6df84886cb8c0bf2915 |
| `glorys12/grid_120-160E/glorys12v1_uo_vo_surface_120-160E-02.json` | 16,776 | d749a4e5ff8f265230293a665a2b3369729755eab1bff13e5c159def0380a656 |
| `glorys12/grid_120-160E/glorys12v1_uo_vo_surface_120-160E-03.f32` | 71,692,088 | e75d458b973a7f27efc2fa75b00b46bb72fbd7fb3fe59113afdb1a136d2ac30a |
| `glorys12/grid_120-160E/glorys12v1_uo_vo_surface_120-160E-03.json` | 12,086 | 3e0a61150f8b3c2dc723faecb058c260bdaef26c8fbfc340863da2905377d684 |
| `glorys12/grid_120-160E/glorys12v1_uo_vo_surface_120-160E.series.json` | 191 | 43f733c13e645b451d24bbb7d300ae2933566f63f5d0d43ea93bad526e13ffef |

— ocean transport (architecture sub-agent)
