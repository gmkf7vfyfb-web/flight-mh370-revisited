# Ocean data manifest

Shared record of every ocean dataset downloaded to this machine for the project. Each module
appends a dated section; nothing already here is rewritten or reordered.

## GDP 6-hourly drifters (ocean drift, validation data)

Ocean Drift Module (Davey reproduction sub-session), 8 October 2026. Authorised by
`coordination/OCEAN_DRIFT.md`, overnight work plan item 4 (GDP 6-hourly, up to 1 GiB, to
`/Users/pete/Downloads/mh370-ocean-data/gdp/`). Validation and reproduction data for the
`gdp-empirical` arm (ruling A1); not a reanalysis product.

| Item | Value |
|---|---|
| Dataset | Global Drifter Program - 6 Hour Interpolated QC Drifter Data (NOAA AOML Drifter DAC) |
| ERDDAP dataset ID | `drifter_6hour_qc`, tabledap, ERDDAP 2.25 |
| DOI (from the dataset's `NC_GLOBAL doi` attribute) | 10.25921/7ntx-z961 |
| Dataset `date_modified` at retrieval | 2026-03-31T14:24:49Z |
| Dataset time coverage at retrieval | 1979-02-15T00:00:00Z to 2025-06-18T12:00:00Z |
| Base URL | https://erddap.aoml.noaa.gov/gdp/erddap/tabledap/drifter_6hour_qc.nc |
| Variables | `ID, time, latitude, longitude, sst, drogue_lost_date` |
| Subset | latitude -60 to 10; lon360 20 to 140; one request per calendar year 1979-2025 |
| Drogue split | done locally: undrogued = `time > drogue_lost_date` with `drogue_lost_date > 0`; missing (still attached) and 0 ("uncertain from beginning") excluded |
| Retrieved | 2026-10-08 (UTC times per file below) |
| Total downloaded | 359,465,828 bytes (342.8 MiB) in 41 files; 1979-1984 returned no rows in the box |
| Local path | `/Users/pete/Downloads/mh370-ocean-data/gdp/` |
| Fetch script | `engine/hypotheses/debris-drift/prepare/gdp/fetch_gdp.py` (branch `hypothesis/debris-drift`) |
| Machine-readable manifest | `gdp/manifest.json`, sha256 `ca56ee040f085b55d29d423a70d9e64b89b2d61eede5b4df0508e2018b1821a2` |
| Rows (6-hourly) / undrogued rows | 6,902,505 / 3,990,900 |
| Derived file | `gdp/derived/gdp_daily_undrogued.npz` (8,424,990 bytes, sha256 `d20e120f77c8527a2aabddaeff697b0a8b85358e4adbd473ca39308b265f6e81`): undrogued fixes at 00 UTC, 996,385 fixes, 3,264 drifters (`load_gdp.py`) |

Exact query, example (2015; the other years differ only in the two time bounds):

```
https://erddap.aoml.noaa.gov/gdp/erddap/tabledap/drifter_6hour_qc.nc?ID,time,latitude,longitude,sst,drogue_lost_date&latitude%3E=-60&latitude%3C=10&lon360%3E=20&lon360%3C=140&time%3E=2015-01-01&time%3C2016-01-01
```

| File | Bytes | sha256 | Retrieved (UTC) |
|---|---|---|---|
| `gdp6h_io_1979.nc` | 0 | — (no rows; not written) | — |
| `gdp6h_io_1980.nc` | 0 | — (no rows; not written) | — |
| `gdp6h_io_1981.nc` | 0 | — (no rows; not written) | — |
| `gdp6h_io_1982.nc` | 0 | — (no rows; not written) | — |
| `gdp6h_io_1983.nc` | 0 | — (no rows; not written) | — |
| `gdp6h_io_1984.nc` | 0 | — (no rows; not written) | — |
| `gdp6h_io_1985.nc` | 19,660 | af3e88f8d374af5d3b312d7ab9044fe11bf4444b983ccc02c6bfa43519f48832 | 2026-10-08T01:36:24Z |
| `gdp6h_io_1986.nc` | 183,824 | 8291205fc3989fe6f22d787e5ffb69e0de080145672507f73c93a667509aec02 | 2026-10-08T01:36:26Z |
| `gdp6h_io_1987.nc` | 30,320 | 3c8846b9caa5cb80eb649c97daeee69321f0946de756089263de4ac1e87d316a | 2026-10-08T01:36:28Z |
| `gdp6h_io_1988.nc` | 475,976 | b5ec77a17bde79e0fef6109210d65ba1f52233cfeeef6c8f2db1653696129536 | 2026-10-08T01:36:29Z |
| `gdp6h_io_1989.nc` | 333,424 | 5c80fdeeabfecf6864a0ff5d891a9a871b97f3a4bdef2db432a795ca63bd915d | 2026-10-08T01:36:31Z |
| `gdp6h_io_1990.nc` | 515,080 | 4ddb67abf0faaf74b266065e20a07d4bcc7e813b118dd2aae602e66ed952ce9c | 2026-10-08T01:36:33Z |
| `gdp6h_io_1991.nc` | 373,752 | ff33a64d6eda7db592cc595137a5f2dd6ee34de9500f08a358aba3d5abbcdc46 | 2026-10-08T01:36:34Z |
| `gdp6h_io_1992.nc` | 537,356 | a7122b4b2f62fb5fba674aac42899a3bb05fcfdc95cd1628e2a8f7db7e93974d | 2026-10-08T01:36:36Z |
| `gdp6h_io_1993.nc` | 466,856 | 3755570ea6a5e3c193a48f0ecc1238b67188d01755a8294565cd5ddfc4791e9b | 2026-10-08T01:36:38Z |
| `gdp6h_io_1994.nc` | 789,420 | 46f5039627f7491c2eb42117e24dc182e1658f179829602b072f993bd869baf8 | 2026-10-08T01:36:40Z |
| `gdp6h_io_1995.nc` | 5,234,820 | 375c8c7a9b552f61a5f7318a413221a5988c1e288eb5a6de2d35d201f0b75a88 | 2026-10-08T01:36:43Z |
| `gdp6h_io_1996.nc` | 7,270,532 | 67e4504d1aed416e234622ea2d9a672f62299549bb9dfb6507a400aec06065d5 | 2026-10-08T01:36:47Z |
| `gdp6h_io_1997.nc` | 6,165,512 | b9499a79d503083a31525586252746d2f993eea902e1a9f4ecb5b6f75875dfa7 | 2026-10-08T01:36:50Z |
| `gdp6h_io_1998.nc` | 5,669,616 | 40eada1798b4bad7c5e2296237dc268cd7854df42d32f79dc97af9a9cb76429d | 2026-10-08T01:36:52Z |
| `gdp6h_io_1999.nc` | 5,979,580 | aa7c20af8d70bbb69ac9441c8ccdfa7cf9e128f4eadd6b3222c8109a23ba4bfa | 2026-10-08T01:36:56Z |
| `gdp6h_io_2000.nc` | 6,770,732 | 6bb049cfb798d3ed424de9b560677db46436529367a5a69b1acbac71c8bb4e95 | 2026-10-08T01:37:04Z |
| `gdp6h_io_2001.nc` | 6,439,572 | 6976cec6e88746037ea341b28c55304489e06ba26496cbf2e2edbbf4f86aeafe | 2026-10-08T01:37:11Z |
| `gdp6h_io_2002.nc` | 6,213,548 | fef35ea07a6b4b9ac22e9e06591087aec44edfbd3f4428dd7f06d0a834857307 | 2026-10-08T01:37:20Z |
| `gdp6h_io_2003.nc` | 7,218,080 | 1a70adbcf14e4a1a63e16854440e4b7617609b9b2325799e6b5f70b9de9dd8eb | 2026-10-08T01:37:29Z |
| `gdp6h_io_2004.nc` | 7,392,684 | cb85a90e2b1138777b88697d06026c6cc4a60448d136faba6e6be85902d286cf | 2026-10-08T01:37:36Z |
| `gdp6h_io_2005.nc` | 8,029,392 | ea6a75959fca563884ca86522d213e7dfbdbfee063a6ec00bc4633ff6751a1cb | 2026-10-08T01:37:42Z |
| `gdp6h_io_2006.nc` | 10,338,268 | ce4c2337a002497efbd7fa62068a8c0343bd42744e4fe6d24565813af5d2126f | 2026-10-08T01:37:47Z |
| `gdp6h_io_2007.nc` | 10,808,128 | 3353dfe980f5967079f0bace4f667e7f1c843c3ace76e9a1f04b478bd8e2f780 | 2026-10-08T01:37:52Z |
| `gdp6h_io_2008.nc` | 11,985,900 | ca566fd26d086a398697d8d79dd56aa83c0ccbaa9c82339d439dc63354b933b5 | 2026-10-08T01:37:57Z |
| `gdp6h_io_2009.nc` | 11,381,480 | 4540d9768b6fc96baef526d470384746f10143e9c9bc22aaed486c863aaba3be | 2026-10-08T01:38:02Z |
| `gdp6h_io_2010.nc` | 17,400,216 | e570ff33738de9d9a5cbba2aaee746a452da09919f0b1e49e6685bd11bdb86ee | 2026-10-08T01:38:08Z |
| `gdp6h_io_2011.nc` | 13,838,248 | d448524ab29b8b70c529c6d33cb4eeb24d3835f5f3f8b305ea898017b91b6045 | 2026-10-08T01:38:16Z |
| `gdp6h_io_2012.nc` | 11,533,640 | 84b24f6acf2b0c18a37556ec212115b023254e1fb0419145d981223f5b7f96ff | 2026-10-08T01:38:26Z |
| `gdp6h_io_2013.nc` | 8,960,960 | 68284d53d7d95ffe34b15b22390ee418800009b6c2021ecbe518c81f11f323a2 | 2026-10-08T01:38:40Z |
| `gdp6h_io_2014.nc` | 14,428,840 | 3f703402e7e073c5b09932620ac43dae9bec32ba0ddb4be2b175bdb93efae457 | 2026-10-08T01:38:52Z |
| `gdp6h_io_2015.nc` | 12,646,896 | 3939c8e6f0f898427b2552d855dc63331a045f538895733affb499da0ca5cdf6 | 2026-10-08T01:39:09Z |
| `gdp6h_io_2016.nc` | 17,550,476 | 56bfd41997427f4365c19588bcf92840f3272b5c274441785cad1532b3f1b627 | 2026-10-08T01:39:27Z |
| `gdp6h_io_2017.nc` | 20,794,428 | 3b35eaa1b6a3fcd2e9d367bb194e9baed104c98cf77605de380f7a1c6b5d153d | 2026-10-08T01:39:44Z |
| `gdp6h_io_2018.nc` | 20,402,444 | 77089e762767ebce42d147754c86d8af091b07df4ae2309e6dfae5b9f75f333c | 2026-10-08T01:40:00Z |
| `gdp6h_io_2019.nc` | 19,629,968 | 76a2353cfc4120d1dd1917185dca061fa903f1b76f9e072febbe1decb88eeb40 | 2026-10-08T01:40:17Z |
| `gdp6h_io_2020.nc` | 20,718,036 | 1e84275c210052302763d0fd02683dd157ab22d85cf7a315ddd54b0c5079bc1d | 2026-10-08T01:40:28Z |
| `gdp6h_io_2021.nc` | 16,895,148 | 6fc4eaed8af3d0e707ce52c35186ca53b545d3738eebe438c6382fd4e29beab6 | 2026-10-08T01:40:37Z |
| `gdp6h_io_2022.nc` | 11,268,868 | 94f85fb9394c3ee792f0361920ad4e3faabed764f10c6ce4942190b5b2eddd71 | 2026-10-08T01:40:46Z |
| `gdp6h_io_2023.nc` | 10,372,920 | 8dc3c5fa74844ba09b851ce998bce0ff0d57b0c7a965f78ebf084d8ceb2dee9e | 2026-10-08T01:40:54Z |
| `gdp6h_io_2024.nc` | 14,131,948 | f2753ac01f79cbc9ae1f215d47957c35afa9e188c6f881201012dcc0733422aa | 2026-10-08T01:41:03Z |
| `gdp6h_io_2025.nc` | 8,269,280 | c8a5810f33fda51cc5ce1d5fbd8890151df4f961d4224263058df44f08c81587 | 2026-10-08T01:41:09Z |

## GLORYS12V1 surface currents, first slice (shared ocean transport)

Ocean transport (architecture sub-agent). Authorised by the architecture session's message of 9
October (brief deliverable 4/5; cap 2 GiB for this step, 25 GiB floor). Network access to
`stac.marine.copernicus.eu` and `s3.waw3-1.cloudferro.com` was approved by Pete. Free disk was
31.2 GiB before the download and 29 GiB after conversion.

| Item | Value |
|---|---|
| Product | GLOBAL_MULTIYEAR_PHY_001_030 (GLORYS12V1), Mercator Ocean International / Copernicus Marine |
| Dataset | `cmems_mod_glo_phy_my_0.083deg_P1D-m` (daily means), Toolbox service `arco-geo-series` |
| File attributes | `source` MERCATOR GLORYS12V1; `field_type` mean; `history` 2023/06/01 creation; Toolbox 2.5.0 |
| Variables | `uo`, `vo` (m s-1), stored as int16, scale 6.1037e-4 m/s (0.6 mm/s quantisation), fill -32767 |
| Box | 15-120 E, 50-0 S: 1,261 x 601 nodes at 1/12 deg |
| Depth | top level only, 0.494 m |
| Period | 2014-03-07 to 2014-04-30, 55 daily means. Time labels are 00:00 UTC ("hours since 1950-01-01") |
| Time placement | each mean placed at label + 12 h (interval centre). **Provisional**: if the label were the centre, the field shifts 12 h |
| Retrieved | 2026-10-08T14:22Z (machine clock), 16 s; network transfer 3.52 GB of ARCO chunks, disk footprint below |
| Local path | `/Users/pete/Downloads/mh370-ocean-data/glorys12/` |
| Toolbox request | `copernicusmarine.subset(dataset_id="cmems_mod_glo_phy_my_0.083deg_P1D-m", variables=["uo","vo"], minimum_longitude=15, maximum_longitude=120, minimum_latitude=-50, maximum_latitude=0, minimum_depth=0, maximum_depth=1, start_datetime="2014-03-07T00:00:00", end_datetime="2014-04-30T00:00:00", service="arco-geo-series")`, credential `COPERNICUS` |
| Conversion | `engine/crates/ocean/prepare/netcdf_to_grid.py` (branch `core/ocean-transport`, `f71a7d2`): float32 `[time][lat][lon][east, north]`, NaN at land; land fraction 0.174; max speed 3.07 m/s |
| Used by | drift (pilot transport), Pleiades (impact to 21 and 23 March), settling's float phase; first real product behind `GridField::load`; throughput measurement |

| File | Bytes | sha256 |
|---|---|---|
| `glorys12v1_uo_vo_surface_15-120E_50-0S_20140307-20140430.nc` | 166,764,464 | a1b9122138ddf47ee8da84e77576ba9f415e0e322138497ecc5ebff12af87667 |
| `glorys12v1_uo_vo_surface_20140307-20140430.f32` (derived) | 333,458,840 | 466ffb32b349e6e4cfac4a559136016be5404d2b6fb0f1e0d2ab7d3b87569bbf |
| `glorys12v1_uo_vo_surface_20140307-20140430.json` (derived manifest) | 19,662 | 6ec58172158cfba20bf08e9f3883773e1293f3f898f8600025309936dbc334c5 |

Total on disk: 500,242,966 bytes (477 MiB). This slice covers 54 days; drift's full period (8 March
2014 to 30 September 2016) over the same box is about 5.7 GB as float32, or roughly 2.9 GB as the
Toolbox's int16 netCDF.

## Production surface forcing, 7 March 2014 to 31 January 2017 (shared ocean transport, item 2 of 9 October)

Ocean transport (architecture sub-agent). Fetched 9 October 2026 by
`engine/crates/ocean/prepare/fetch_forcing.py`, then converted by `prepare/netcdf_to_grid.py` into
`GridField` series (`<product>/grid/*.series.json`). The box for every product is 15-120 E, 50-0 S. Free
disk was 401 GiB before and is at least 360 GiB after, against a 100 GiB floor and a 300 GB budget. Every
series was checked with `examples/forcing_check.rs`: axes, uniform time step, and samples at the 7th arc,
off Réunion and in the Agulhas. Citations and licences are in `engine/crates/ocean/REFERENCES.md`.

### GLORYS12V1 surface currents (extends the 7 Mar to 30 Apr 2014 slice above)
- `cmems_mod_glo_phy_my_0.083deg_P1D-m`, version 202311, `uo`/`vo` at 0.494 m, service `arco-geo-series`, credential COPERNICUS.
- Series: 1,062 daily means placed at label + 12 h (provisional), with a constant 24 h step. Derived
  float32: 6,438,787,056 bytes in 5 parts.
- Downloaded: 3,052,804,284 bytes.

| File | Bytes | sha256 | Retrieved (UTC) |
|---|---|---|---|
| `glorys12_uo_vo_15-120E_50-0S_20140501-20141231.nc` | 742,738,824 | c376f47bcf36100ba971d64ee71c7f818f6d6fd3dd0762004f25f2357c04a3c7 | 2026-10-09T00:35:05Z |
| `glorys12_uo_vo_15-120E_50-0S_20150101-20151231.nc` | 1,106,512,104 | 06786a79426c034c76db83c1eaf32d9a617b8f7b6cc4e2812b1c5f06c9324c95 | 2026-10-09T00:36:04Z |
| `glorys12_uo_vo_15-120E_50-0S_20160101-20161231.nc` | 1,109,543,548 | fc909de6d865df66d0a8d5589defdaf1bf7f38e2b7d1fe26f10e66e07d3f85d6 | 2026-10-09T00:36:56Z |
| `glorys12_uo_vo_15-120E_50-0S_20170101-20170131.nc` | 94,009,808 | 46cba84c8aa7c2b30a7f5dc068fafc4d260f920427e5bb9616bce9d9d4d46951 | 2026-10-09T00:37:09Z |

### WAVERYS surface Stokes drift
- `cmems_mod_glo_wav_my_0.2deg_PT3H-i`, version 202411, `VSDX`/`VSDY`, service `arco-time-series`.
- Series: 8,489 instantaneous 3-hourly fields, 2014-03-07T00 to 2017-01-31T00. Derived float32:
  8,966,149,712 bytes. Values are quantised at 0.005 m/s. The maximum speed in 2016 is 1.4 m/s, which is
  unusual and will be checked.
- Downloaded: 4,483,225,576 bytes.

| File | Bytes | sha256 | Retrieved (UTC) |
|---|---|---|---|
| `waverys_VSDX_VSDY_15-120E_50-0S_20140307-20141231.nc` | 1,267,488,632 | 19880a71debe1d8ae801f40cd3f440ca003789539cc382248e0624f9122a41c5 | 2026-10-09T00:39:36Z |
| `waverys_VSDX_VSDY_15-120E_50-0S_20150101-20151231.nc` | 1,542,104,792 | c1577d83f86c9ff2fc3523832a028fce51043a6ef6b950e76145616264ec6119 | 2026-10-09T00:41:57Z |
| `waverys_VSDX_VSDY_15-120E_50-0S_20160101-20161231.nc` | 1,546,329,656 | e70e951f1c4b0c1b592bc820539f7a9634fa2fceb5e191c860ea5cc2e5164389 | 2026-10-09T00:46:55Z |
| `waverys_VSDX_VSDY_15-120E_50-0S_20170101-20170131.nc` | 127,302,496 | 908df8a61bf9e1ca86a0ac26f7067c79edaa46ae4d5e2d264448f8f7177ccdf7 | 2026-10-09T00:49:35Z |

### ERA5 10 m wind (ARCO-ERA5; genuine ERA5, no substitution)
- `gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3`, `10m_u_component_of_wind` and
  `10m_v_component_of_wind`, every third hour. The files are written directly as `GridField` parts
  (`era5/era5_u10_v10_3h.series.json`).
- Series: 8,496 instantaneous 3-hourly fields, 2014-03-07T00 to 2017-01-31T21, on 0.25 degrees,
  421 x 201.
- Total: 5,751,658,092 bytes.

| File | Bytes | sha256 | Retrieved (UTC) |
|---|---|---|---|
| `era5_u10_v10_3h_15-120E_50-0S_20140307-20141231.f32` | 1,624,723,200 | 1e5fd870960d90e1e09820eccea36bccd8c0988ef159d45d8b5d071dbe5e84e0 | 2026-10-09T00:40:58Z |
| `era5_u10_v10_3h_15-120E_50-0S_20140307-20141231.json` | 38,355 | a99b276e605791c238de49bb658dc6e49cac8e82e43d71051d77181fee7636bb | 2026-10-09T00:40:58Z |
| `era5_u10_v10_3h_15-120E_50-0S_20150101-20151231.f32` | 1,976,746,560 | f7258691d318f6a0527b918ef5521ab6b1636c14c2aac5817580f62aea7c757c | 2026-10-09T00:49:04Z |
| `era5_u10_v10_3h_15-120E_50-0S_20150101-20151231.json` | 45,635 | 4522ff40056f1b445b93be4e5a5a385b249f0eb21c13a2f414d169e218a190eb | 2026-10-09T00:49:04Z |
| `era5_u10_v10_3h_15-120E_50-0S_20160101-20161231.f32` | 1,982,162,304 | f7aadb97ad5b3217beba6c15e478f1c67ca7d300bf359f2191cc722832411c24 | 2026-10-09T00:56:52Z |
| `era5_u10_v10_3h_15-120E_50-0S_20160101-20161231.json` | 45,747 | 6db72d6dbc1f6a82da0e946fff02bd5bc7ed19f07f29a369f1d1ac3ba3c422e4 | 2026-10-09T00:56:52Z |
| `era5_u10_v10_3h_15-120E_50-0S_20170101-20170131.f32` | 167,888,064 | d6286a5395e8ca0706992afcb1c6cbcfbda4e3198f47f951256080de92c103e2 | 2026-10-09T00:57:52Z |
| `era5_u10_v10_3h_15-120E_50-0S_20170101-20170131.json` | 8,227 | 104c787d5d1ed557c6d20f9052173a02b0ba278176b80a0f91c0f08b93ae9c0e | 2026-10-09T00:57:52Z |

### BRAN2016 surface currents: **stopped, not in use**
- NCI THREDDS NetCDF Subset Service, `gb6/BRAN/BRAN_2016/OFAM/ocean_{u,v}_YYYY_MM.nc`, top level 2.5 m,
  every day of each month.
- The download was stopped after 15 monthly files
  (561,197,188 bytes, March to October 2014). The CSIRO
  Bluelink terms (`gb6_license.txt`) require registration with CSIRO before access and limit use to
  government-funded research. **These files are not used until Pete decides.**
- An earlier attempt returned one day per month. Those files were moved to the Trash with approval, and
  their fetch-log lines are kept for the record.

| File | Bytes | sha256 | Retrieved (UTC) |
|---|---|---|---|
| `bran2016_ocean_u_2p5m_15-120E_50-0S_2014_03_daily.nc` | 37,712,278 | b8ea76a3e37ef929ddf14602a645d81d2acb55c21d29989d27c4333f4eb9afbd | 2026-10-09T01:07:57Z |
| `bran2016_ocean_v_2p5m_15-120E_50-0S_2014_03_daily.nc` | 38,068,643 | 6e859693d66a4b5737c0f398e7d8aa73dd9745ddf16f38511573a143ebdd5ddf | 2026-10-09T01:08:26Z |
| `bran2016_ocean_u_2p5m_15-120E_50-0S_2014_04_daily.nc` | 36,504,786 | 643b4ac30ad7f13e4e331021439cd7d758d236ee4faa3001840978d19d0d3355 | 2026-10-09T01:08:53Z |
| `bran2016_ocean_v_2p5m_15-120E_50-0S_2014_04_daily.nc` | 36,745,125 | a44abe2cdb42c55dde69c02efc843589976d940c03a82ce47d87ca70ec2ae676 | 2026-10-09T01:09:21Z |
| `bran2016_ocean_u_2p5m_15-120E_50-0S_2014_05_daily.nc` | 37,667,698 | 443f30500bc8001f7cfb205146440c1a7effd31e3151c5430228897a52ed9cf3 | 2026-10-09T01:09:48Z |
| `bran2016_ocean_v_2p5m_15-120E_50-0S_2014_05_daily.nc` | 37,985,718 | 1b81465f3822a49a44944d5db956dd5bdafd19f84fcd20cf2b45245968c7512a | 2026-10-09T01:10:14Z |
| `bran2016_ocean_u_2p5m_15-120E_50-0S_2014_06_daily.nc` | 36,428,880 | 7224a334f0d9f2ed143ebd27d1b0c150e13e4ff6a01a1de31b82b94904605391 | 2026-10-09T01:10:42Z |
| `bran2016_ocean_v_2p5m_15-120E_50-0S_2014_06_daily.nc` | 36,732,859 | d1d0e0f7b1b0da023bbe3da5e938c2013d663d9f4a2eab541f7472b0c55ec406 | 2026-10-09T01:11:11Z |
| `bran2016_ocean_u_2p5m_15-120E_50-0S_2014_07_daily.nc` | 37,653,198 | 93cc81b16a461a1cef1887847bc6a7b4884d251911961edbf1e7c6e2217659ef | 2026-10-09T01:11:39Z |
| `bran2016_ocean_v_2p5m_15-120E_50-0S_2014_07_daily.nc` | 37,951,802 | d49b3fd20f559a01ca9c306b378c3bc6bd939f9037df7cecb1547a13a66deb19 | 2026-10-09T01:12:11Z |
| `bran2016_ocean_u_2p5m_15-120E_50-0S_2014_08_daily.nc` | 37,800,770 | 2f04caf52824f51dc84cb5b7a195e1fe2ccda31539a1703e5f70926ff20abae0 | 2026-10-09T01:12:29Z |
| `bran2016_ocean_v_2p5m_15-120E_50-0S_2014_08_daily.nc` | 38,101,291 | 2898b8ea64d6785472df1e62830b930ab1db214d3f94c0bea2f608705036ffa4 | 2026-10-09T01:12:51Z |
| `bran2016_ocean_u_2p5m_15-120E_50-0S_2014_09_daily.nc` | 36,748,501 | 9b9d759ac5828be92cf2add161764948500d9708cebc84414f164229c4f3cdc9 | 2026-10-09T01:13:10Z |
| `bran2016_ocean_v_2p5m_15-120E_50-0S_2014_09_daily.nc` | 37,081,022 | 5b19c12aa53578505e32fe5638de4e70272425fca72439539e3240181f27a10e | 2026-10-09T01:13:36Z |
| `bran2016_ocean_u_2p5m_15-120E_50-0S_2014_10_daily.nc` | 38,014,617 | 5ef6f5866847064919880a894258fece7fdef11974a5375f312084b4bfddc78d | 2026-10-09T01:13:57Z |
