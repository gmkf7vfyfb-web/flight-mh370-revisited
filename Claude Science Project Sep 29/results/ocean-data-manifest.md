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

## Bathymetry and sound speed (shared ocean transport, item 3 of 9 October)

Ocean transport (architecture sub-agent), 9 October 2026. Fetched by
`engine/crates/ocean/prepare/fetch_static.py`. Citations and licences are in `results/ocean-references.md`.

### GEBCO_2026 Grid (15 arc-second) and Type Identifier grid
- **Source:** BODC via CEDA, doi:10.5285/4f68d5c7-45eb-f999-e063-7086abc036fa. Global files.
  - The elevation grid is netCDF4 and int16.
  - The TID grid is classic netCDF3 and int8.
- **Derived:** `gebco/grid/` holds the region 40-180 E, 60 S-30 N (33,600 x 21,600 cells), copied
  unchanged by `prepare/gebco_to_grid.py`, for `bathy::Bathymetry`.
- **Used by:** settling (impact-point seabed and `bottom_relation`), hydroacoustics (geodesic paths with
  corridor maximum) and searched areas (terrain masking).
- **AusSeabed / GA MH370 Phase 1 150 m: obtained 9 October 2026** (section below). It is the first layer
  inside its coverage. It was not obtained earlier on 9 October because the GA geoserver returned 502.

| File | Bytes | sha256 | Retrieved (UTC) |
|---|---|---|---|
| `GEBCO_2026.nc` | 7,466,018,396 | 71ceeb56a4b917a3f2d9fe3c6da8e7c5c5e6d8185b373eca6bac9a4d61cb3223 | 2026-10-09T01:18:54Z |
| `gebco_2026_tid.nc` | 3,733,523,740 | 1a7f083ca2e7520720247aa3c5afa37a6407cb011bacb8c4cfebc4abdd9af9a4 | 2026-10-09T01:42:42Z |

| Derived file | Bytes | sha256 |
|---|---|---|
| `gebco_2026.json` | 609 | ad972eed6ea760daa7918451642f39a3c0c2627d21fb3a20810d56863d56d3af |
| `gebco_2026_elevation.i16` | 1,451,520,000 | 511ff809f08ba62c9a9198fef81904499b01dcd2579fc9813a12af5e233c60c0 |
| `gebco_2026_tid.u8` | 725,760,000 | 518303d2026da6d953c08a09435ac52628fe9482b1a852d2fa93916c81e7ec74 |

### World Ocean Atlas 2023, 1 degree
- **Source:** NCEI THREDDS. Temperature and salinity, monthly (01-12) and seasonal (13-16), for four decades:
  95A4, A5B4, B5C2 and decav. That is 128 files, 7,027,400,742 bytes in total.
- **Derived:** `woa23/soundspeed/woa23_<decade>_m<MM>.*` (740,318,562 bytes), made by
  `prepare/woa23_to_soundspeed.py` with official `gsw`.
  - Contents: TEOS-10 SA, CT and sound speed for each decade and month, monthly above 1,500 m and seasonal
    below.
  - Spread: from the decav `*_sdo` fields.
  - Region: 40-180 E, 60 S-30 N.

| File | Bytes | sha256 | Retrieved (UTC) |
|---|---|---|---|
| `woa23_95A4_t01_01.nc` | 39,081,875 | c9b965f7e4db2394cfc8dd9cbbef9988851a206660ce5bb82a48a128303f003c | 2026-10-09T00:59:20Z |
| `woa23_95A4_t02_01.nc` | 39,274,359 | 963d7b40fb943701bae12a85d2a09baa974d28bdd3bf6fd6f1850ed89233232f | 2026-10-09T00:59:22Z |
| `woa23_95A4_t03_01.nc` | 40,433,051 | 3b6489b926e96e1f5799db05cf5febc940781b4799560065148475c34a33fabf | 2026-10-09T00:59:24Z |
| `woa23_95A4_t04_01.nc` | 40,509,308 | f6c3ed364fc6aed8a5362c5bbd85c3c12f3e2a31bb06ad4e5cd81a4fac37fa16 | 2026-10-09T00:59:31Z |
| `woa23_95A4_t05_01.nc` | 40,199,570 | 1caf495a03cb8987f35f1ce1cb112db4690ea21bba8acb267a3183e81fa7c63f | 2026-10-09T00:59:33Z |
| `woa23_95A4_t06_01.nc` | 39,473,621 | 82aa8e8aca71b3715b472ae466f4469dcd9bad59c34661ff7bdc13b89dc8457c | 2026-10-09T00:59:36Z |
| `woa23_95A4_t07_01.nc` | 40,278,989 | 8fd8d8c9713c424134a3e2f248362cc54d954558ac10111e5c36d73d397f70d4 | 2026-10-09T00:59:38Z |
| `woa23_95A4_t08_01.nc` | 40,771,511 | 733ae5f9db0ab1949f343e6ea309b35c051137d295124937b1f31f6ddd402ef8 | 2026-10-09T00:59:40Z |
| `woa23_95A4_t09_01.nc` | 40,139,409 | 95ebb26b737e4d797f7acd1225c4d2f3664b0b1468cda28e0d3a4b2062e21c41 | 2026-10-09T00:59:42Z |
| `woa23_95A4_t10_01.nc` | 40,824,766 | 5509f8757dcca363fb30d4eebd1a1b1f6cf108c25e3174eb6de128da7f941d3e | 2026-10-09T00:59:44Z |
| `woa23_95A4_t11_01.nc` | 40,473,135 | 221556538a3975a607a4b9c0139188e2672e7e6cdc83c99d00e7ce5b67850b9b | 2026-10-09T00:59:46Z |
| `woa23_95A4_t12_01.nc` | 40,117,338 | 7589ec432ff23aa1d57ae1272b286bcf27e907c57255cac999fa14b4af9df912 | 2026-10-09T00:59:49Z |
| `woa23_95A4_t13_01.nc` | 61,347,101 | 14601299513ef2c34afa1505ed0f7169b9a8872d9298dffc8f4505a661a0b6c7 | 2026-10-09T00:59:52Z |
| `woa23_95A4_t14_01.nc` | 61,936,100 | 7d52db0f298f5f4e22c6a19d1bdba48634a965712bdbe4a62937798a36d18239 | 2026-10-09T00:59:57Z |
| `woa23_95A4_t15_01.nc` | 62,283,225 | 29ef22e5bf51b437fb4f7ffd30ed0398251cc0f85b98efc1412b88f36aa0a173 | 2026-10-09T01:00:00Z |
| `woa23_95A4_t16_01.nc` | 62,722,200 | 5e6517b973f9b7bb3c6d609aeeb521e7549f1d13eff0c4c2c64404c5d0cb6f39 | 2026-10-09T01:00:04Z |
| `woa23_95A4_s01_01.nc` | 28,992,922 | 52d81dafedd0888cff56a859e0a7f90ab51ea27ca4cf1dcd1568aaa41a88ad60 | 2026-10-09T01:00:06Z |
| `woa23_95A4_s02_01.nc` | 29,255,890 | ed9a5aeea80b438e5d4569ef00a164f798f1794dea0d1a9e6c5f379b9ff0f6e7 | 2026-10-09T01:00:08Z |
| `woa23_95A4_s03_01.nc` | 29,612,333 | 0e41d51c691fb08f8f3a1d62b69c037315fe890e6a859f23790c9711a7b00f1d | 2026-10-09T01:00:11Z |
| `woa23_95A4_s04_01.nc` | 30,712,538 | 84acc6e0e087e69ce3c751848cd29b35d8a8957d706739e485e38da1458284ea | 2026-10-09T01:00:13Z |
| `woa23_95A4_s05_01.nc` | 30,292,347 | 5fab73e8b70226ef04c1bfec3623d48e9756cf7359ac122a172678387870b1e2 | 2026-10-09T01:00:21Z |
| `woa23_95A4_s06_01.nc` | 30,176,750 | 63e23fdbbbc19fe1e6e792afd40e1d31d84de9ea7bee5889cb67ed82db4ce170 | 2026-10-09T01:00:28Z |
| `woa23_95A4_s07_01.nc` | 31,061,949 | e9dcbc9f88bd7f311d9379ba649e8ee546d8fe0fb825217d8597b67b9b7575bd | 2026-10-09T01:00:30Z |
| `woa23_95A4_s08_01.nc` | 31,287,267 | 6c7cde62d8d0b93e17eac68ba0f08acb0920977d352958f79df6128081ab66a2 | 2026-10-09T01:00:32Z |
| `woa23_95A4_s09_01.nc` | 31,298,292 | f6436746f6648958a067e81ef5985b2fa2af29832a02fa30ba231d9646fdedb6 | 2026-10-09T01:00:35Z |
| `woa23_95A4_s10_01.nc` | 31,564,611 | 1e62587973d1df93d1706b39a9cc1782a8c7b4b0c2e3651884742fc4b3ab9bfc | 2026-10-09T01:00:36Z |
| `woa23_95A4_s11_01.nc` | 30,827,533 | a119f32bd89b48385abc089651869169168cc8066e10d1f302f7173f2a248491 | 2026-10-09T01:00:38Z |
| `woa23_95A4_s12_01.nc` | 30,344,349 | de59ef6145433f9a07eddd3ed06d388e47c4ffd3aebd74f47a60e20582401203 | 2026-10-09T01:00:40Z |
| `woa23_95A4_s13_01.nc` | 47,611,918 | 9736840ee5cddc5ab21be24d55f4ab23ab71d68bdc7cfbaae2deeb9adb7c2766 | 2026-10-09T01:00:42Z |
| `woa23_95A4_s14_01.nc` | 49,115,765 | 945abf7aee4407ad077eb38cf41dd7c714cebf2bdd42788bf00bf9408c6bda4b | 2026-10-09T01:00:45Z |
| `woa23_95A4_s15_01.nc` | 49,891,779 | acf7e39bdb47b6f780b0bbb0c5d1dec420e5e9dc298976d6951ed0b7cead6c5c | 2026-10-09T01:00:48Z |
| `woa23_95A4_s16_01.nc` | 50,644,376 | a985836a11e35d06a381b3814fda0b8207e3305dd78d9dba3ce4c0b352e9076c | 2026-10-09T01:00:50Z |
| `woa23_A5B4_t01_01.nc` | 54,086,893 | 18862cf4c1fb19e4d1d55979d210455d57ff6a29676f679963485e8d57e7138f | 2026-10-09T01:00:53Z |
| `woa23_A5B4_t02_01.nc` | 54,285,456 | c29f73a8361697e68fc218c4d9b7a711df7d97df0a86c13efbe91792e45c7668 | 2026-10-09T01:00:55Z |
| `woa23_A5B4_t03_01.nc` | 54,926,376 | 7915e694a7ca255b96a6bbda25cb02f410d9b83cfcad8fb6f50af47e8a4b955c | 2026-10-09T01:00:58Z |
| `woa23_A5B4_t04_01.nc` | 54,811,305 | 091284a79ec78957554d8681824bae00b6093f8077ad2602445788fe7aaf3a1f | 2026-10-09T01:01:01Z |
| `woa23_A5B4_t05_01.nc` | 54,731,576 | 4fb56d52fe03b85052d98a4e15087fc75a9bb52a04e376c966c8f3b57c7b4426 | 2026-10-09T01:01:03Z |
| `woa23_A5B4_t06_01.nc` | 54,186,541 | c13a5a1c4c425311ef83f3dfd2d791a71e6942e7b5e241e082f3e1c3218c9033 | 2026-10-09T01:01:05Z |
| `woa23_A5B4_t07_01.nc` | 55,167,946 | 1d0e19cd147f70d51fd49cc8d9834a4b3f20f22682d628fe56758fb7daabbba1 | 2026-10-09T01:01:07Z |
| `woa23_A5B4_t08_01.nc` | 55,437,036 | a6cff9c7d382ff86b54ce61b5a025ac0a57599228d5f1f8fd8f56b877a0d3e69 | 2026-10-09T01:01:10Z |
| `woa23_A5B4_t09_01.nc` | 55,388,496 | 3a67f4feddaf62e46706983eb354c20b1ec0fe128eb16e1662c557f0edb1512c | 2026-10-09T01:01:16Z |
| `woa23_A5B4_t10_01.nc` | 54,888,188 | 03d8110d74ffbde54b0ab477bb02c6a28ac2271ef89705db807a245ce37c5690 | 2026-10-09T01:01:19Z |
| `woa23_A5B4_t11_01.nc` | 54,193,568 | 7791371b46aef8491db6ab76507e6c9df0ac8ab50465dcb52378d332ae13acf8 | 2026-10-09T01:01:24Z |
| `woa23_A5B4_t12_01.nc` | 54,529,600 | 4b5099be494668484b1619521106f93751deb9d1b72e8ba62f82e184087f76a7 | 2026-10-09T01:01:26Z |
| `woa23_A5B4_t13_01.nc` | 78,667,297 | b1462972a5bcc01475db41ebbd71514f01b3b5a6f049475e6828fde659913732 | 2026-10-09T01:01:31Z |
| `woa23_A5B4_t14_01.nc` | 78,529,884 | 4f1adbbefbde2ac97e29909c1d0b05ab36bae9c92a8dd4b31b5733f683fde133 | 2026-10-09T01:01:36Z |
| `woa23_A5B4_t15_01.nc` | 78,662,241 | dd04f4f08fe6245e58da4a236bc4467b87e453d4601711a13e39ce6ed6f4e04c | 2026-10-09T01:01:39Z |
| `woa23_A5B4_t16_01.nc` | 77,719,047 | 9586465d591a6d98ec78d08193ccc73cbf58a681f6235d987fd97f476b668ee7 | 2026-10-09T01:01:43Z |
| `woa23_A5B4_s01_01.nc` | 47,849,711 | cd8fae28586c5fe6eedebcae23029848d21f0e59e0141b20977c33a74c296182 | 2026-10-09T01:01:46Z |
| `woa23_A5B4_s02_01.nc` | 47,494,304 | 6717b31f70aa3132282ffac75b956b156aa4ebeef5e234169cecbf75d04f8990 | 2026-10-09T01:01:53Z |
| `woa23_A5B4_s03_01.nc` | 48,164,163 | 3bbf80839289c008a9e0e33c244e5d2f2d05d30b3bba73531d24fc75354e1041 | 2026-10-09T01:01:56Z |
| `woa23_A5B4_s04_01.nc` | 48,086,262 | 1dfbb609187c1408fb2addcec18b8483705a5a0f150fa2da1eefb8ac25ba78e9 | 2026-10-09T01:01:59Z |
| `woa23_A5B4_s05_01.nc` | 47,932,097 | 1753cd164808686ad6cf742f4cdf1499f9465fffce67558c81c5cd69f51ce878 | 2026-10-09T01:02:01Z |
| `woa23_A5B4_s06_01.nc` | 47,425,145 | 32947d998f1cc5ed3db0176905f29e95914b1e56ae6bcf5b60b81b95597ee972 | 2026-10-09T01:02:04Z |
| `woa23_A5B4_s07_01.nc` | 48,311,944 | 608a1d1a1b5b879b80899bd53621f31befaaa16ed8a3e45b3e2cda73b3401e41 | 2026-10-09T01:02:07Z |
| `woa23_A5B4_s08_01.nc` | 48,733,126 | af7cc7fda0192991357dc7219c92b19cde277018a794cdaf79671bc3fbb060ae | 2026-10-09T01:02:10Z |
| `woa23_A5B4_s09_01.nc` | 48,660,566 | 6623361b174617a5cebbe4d734a4bd55aff68f22bcf0b02cfb3189ff570f899f | 2026-10-09T01:02:12Z |
| `woa23_A5B4_s10_01.nc` | 48,387,387 | 4596576467828912e4c62de53935e16bb763430b11ef9109ceb411ce92f0ca1d | 2026-10-09T01:02:16Z |
| `woa23_A5B4_s11_01.nc` | 47,874,552 | 2e5b33255e92bf5e0300be44d4e0d6e50cbfd9c9d669fc181341761bb7231b8f | 2026-10-09T01:02:20Z |
| `woa23_A5B4_s12_01.nc` | 48,208,451 | b8b5b938d8f56b75ae3cc7be175c6125d49c75f316027a373bee2d0a31365a66 | 2026-10-09T01:02:23Z |
| `woa23_A5B4_s13_01.nc` | 69,555,692 | 3819cfa962f5c27b61df5131078e10888e34fd685c50fcfd4551a32fe808236a | 2026-10-09T01:02:26Z |
| `woa23_A5B4_s14_01.nc` | 69,357,988 | 71f0a1e5806f6a0d3c949561d983bf8020253cdea8e6af50cc6a2d68662f5f49 | 2026-10-09T01:02:30Z |
| `woa23_A5B4_s15_01.nc` | 69,508,618 | 2920af6ca474b8b543af5d04e34de8d96ff15b6eb04c1ec43b47af125b4f98cc | 2026-10-09T01:02:32Z |
| `woa23_A5B4_s16_01.nc` | 68,791,469 | 05608522f2a7bb6a1334f42ed0b835eb734ed25fe0843adc1e9ee0437983e3e0 | 2026-10-09T01:02:36Z |
| `woa23_B5C2_t01_01.nc` | 54,893,098 | a97d95a51bf540798e264bba293fc02aaac9d87b80f219ad543ab8c7841cf49b | 2026-10-09T01:02:38Z |
| `woa23_B5C2_t02_01.nc` | 54,968,235 | ddff66d590a7a9863a912080f16bcba2715040e6536c82c2f1ca9c5f0ce2227b | 2026-10-09T01:02:41Z |
| `woa23_B5C2_t03_01.nc` | 55,042,284 | 74094ba6b4bfc784fe44b837464da29a2169e63fd1a6f07d7026148954eabb79 | 2026-10-09T01:02:44Z |
| `woa23_B5C2_t04_01.nc` | 54,934,508 | 225d64c446b04993beed6d4605ed9abdf35527991519a6dacbab74abdeb7bb45 | 2026-10-09T01:02:47Z |
| `woa23_B5C2_t05_01.nc` | 54,954,563 | 92b5d6e53db4fa3bf12e13203f8639f3bfe630890223ed9ab0684bc7e09f2022 | 2026-10-09T01:02:50Z |
| `woa23_B5C2_t06_01.nc` | 54,602,042 | 96bc8642dd649ee1904f7e3153598b935f19e578bbe078a11cb469b651852272 | 2026-10-09T01:02:53Z |
| `woa23_B5C2_t07_01.nc` | 54,864,644 | a61559b0b498c5a53a9dbc34c82ce2fcb1350cc91a20702f2f0f113af70d0830 | 2026-10-09T01:02:56Z |
| `woa23_B5C2_t08_01.nc` | 55,087,260 | 1dc05bbb74667fdd7fdec8fea6ba37f33f005c73b1b44b8d9f5bd1d99de960ce | 2026-10-09T01:02:59Z |
| `woa23_B5C2_t09_01.nc` | 55,013,522 | 6246c567b2704aa1f710d1944aa635a40eeb4d31cdebc180f418f669bb244302 | 2026-10-09T01:03:01Z |
| `woa23_B5C2_t10_01.nc` | 54,599,167 | a90898edf044681ef00d0664d809a1f99ce52274233924edf2f2f86e08aafe74 | 2026-10-09T01:03:04Z |
| `woa23_B5C2_t11_01.nc` | 54,425,447 | 44d7e64f1abf4f18ee476548e077c4bdb60883b2f57e46c4cccb5af15c9a3b4f | 2026-10-09T01:03:07Z |
| `woa23_B5C2_t12_01.nc` | 54,648,715 | 9a872203b584986928f42e4812cf3d47f3137fac76c14ed46ea28a0dbb0606d8 | 2026-10-09T01:03:09Z |
| `woa23_B5C2_t13_01.nc` | 79,855,442 | dadb244397d23b821bb2a965aec6b13cee76780817518e957edb5cc5f3267c90 | 2026-10-09T01:03:14Z |
| `woa23_B5C2_t14_01.nc` | 79,746,847 | 8d3c15ff2ce95a43405521422965517d56c7d5628f66b1d00b8015f554ae7550 | 2026-10-09T01:03:19Z |
| `woa23_B5C2_t15_01.nc` | 79,883,154 | 765e3782b9d327fd956c91367036ad25b1eac8ecb7c38ca2fb1e4fc9105f88a4 | 2026-10-09T01:03:23Z |
| `woa23_B5C2_t16_01.nc` | 79,184,930 | c62aa101b06692f0b5e2687a856d173c5154a7e4a805b5de50d25b9ba74e5a6f | 2026-10-09T01:03:26Z |
| `woa23_B5C2_s01_01.nc` | 47,859,622 | 84e13f7be0b6ddb7cb0a01457450cf4b13389bfb8a4f5bdd9557804e0c52f319 | 2026-10-09T01:03:29Z |
| `woa23_B5C2_s02_01.nc` | 47,190,311 | 6233653fbf23bbd93c1795d04f050dae8b97b793233c422f88019424d64e6e17 | 2026-10-09T01:03:31Z |
| `woa23_B5C2_s03_01.nc` | 47,641,025 | 79778ad73d64c1087af2b6b4d02e5d2e53f89d295d3494439120f85fc026a199 | 2026-10-09T01:03:33Z |
| `woa23_B5C2_s04_01.nc` | 47,430,056 | 4e0d2abdaaab01433caff8134515345d3bf5b6fa3559dfff77a896bb696baf22 | 2026-10-09T01:03:36Z |
| `woa23_B5C2_s05_01.nc` | 47,482,575 | 7f836f84b9895a9e27fbc9f35fa819350666235776d958a688099a5617d9f3c9 | 2026-10-09T01:03:39Z |
| `woa23_B5C2_s06_01.nc` | 47,138,187 | 18163cbc8c49be748252718d12fcf6d22e4de6e37a662918bc1dcd59149b696d | 2026-10-09T01:03:42Z |
| `woa23_B5C2_s07_01.nc` | 47,312,468 | 5ae9de76ba1105eb5ae7302d781192489b006bc6795499ba7baf7e03eebe836e | 2026-10-09T01:03:45Z |
| `woa23_B5C2_s08_01.nc` | 47,360,600 | 5c2373dded70f582ec564f6515ddb4686f76a9453db31c7c87a6dd55db68cc96 | 2026-10-09T01:03:48Z |
| `woa23_B5C2_s09_01.nc` | 47,467,972 | a6aa85ad910257e0801753b1ac304c1e7a3eaee95de2bb229e477beb40747bec | 2026-10-09T01:03:51Z |
| `woa23_B5C2_s10_01.nc` | 47,177,090 | d00d1044b963d578ac85cd2c9d6865d2789d710282506241f4251f07ad9b3e06 | 2026-10-09T01:03:54Z |
| `woa23_B5C2_s11_01.nc` | 46,759,157 | aa37e26119d30cee27d8472b1b08fd387e0bff7b475c315f590a4566a6f95e00 | 2026-10-09T01:03:56Z |
| `woa23_B5C2_s12_01.nc` | 47,148,986 | eb23cbf4c3430c75e2f35a3be913f2187f8e5ea368c26d8253f0e109c4ca279b | 2026-10-09T01:03:58Z |
| `woa23_B5C2_s13_01.nc` | 69,799,350 | 8099d6ae61f49cf2dbd73833752c69d797ccc14cb5ba057fa3675c1b5d4fd320 | 2026-10-09T01:04:01Z |
| `woa23_B5C2_s14_01.nc` | 69,664,631 | 654d32985be39a17317e6a4e62b66d0269abb0d92f4c2fcd8d33e408de377520 | 2026-10-09T01:04:04Z |
| `woa23_B5C2_s15_01.nc` | 69,868,733 | a0ada6d0b218f123f675aec61ef0ce2b8f2e2e89c5d4b75c33a6232496a5be18 | 2026-10-09T01:04:07Z |
| `woa23_B5C2_s16_01.nc` | 69,133,409 | b505f4895f20962559745055b7586b92321d06c9a7086bd2fe22321d15f3a772 | 2026-10-09T01:04:10Z |
| `woa23_decav_t01_01.nc` | 62,186,937 | 2311eb2642e8ebe4da8c9e122ffcb83acff66c000300280f907d20be9a659676 | 2026-10-09T01:10:11Z |
| `woa23_decav_t02_01.nc` | 62,319,903 | 4d5651c1e68b4454f98bb22829e5603f34a342c1e5460abb48ec51b5a5f6a9d9 | 2026-10-09T01:10:13Z |
| `woa23_decav_t03_01.nc` | 62,495,914 | 1b0d08bed78b208a2b2021fed28fee95f8670e9c719493d159733ee18fdca955 | 2026-10-09T01:10:16Z |
| `woa23_decav_t04_01.nc` | 62,479,447 | 1c2ef79123d4cfd62f77705a7d44195a9bb0b369d5ab5bf5f871f824182f94f3 | 2026-10-09T01:10:19Z |
| `woa23_decav_t05_01.nc` | 62,149,455 | 8229c678835fdcd597789728acaf5923bea0169a870848fc457ba4bb852ef7ea | 2026-10-09T01:10:22Z |
| `woa23_decav_t06_01.nc` | 61,781,381 | c0f9554cc6b909ba7667e8d76ce692df028d695f4e51b69925d16998cd40c66a | 2026-10-09T01:10:24Z |
| `woa23_decav_t07_01.nc` | 62,098,858 | d057c9da5f534fa9969a6ca7c1ac1d2f1d3c1d8d74fe3835e7b3a634bce60245 | 2026-10-09T01:10:27Z |
| `woa23_decav_t08_01.nc` | 62,535,646 | a20fcb7446175a0040ea80cf5be2e12de0d8b1af608e73ea2287f04f2544047a | 2026-10-09T01:10:30Z |
| `woa23_decav_t09_01.nc` | 62,546,905 | 2149ccd124c39851036bc528fd6f0a324f7f36cc91bc40bd4fe9bf8afef033d5 | 2026-10-09T01:10:34Z |
| `woa23_decav_t10_01.nc` | 62,156,732 | 870ec7a62e083e2ad1674cb281fada663280c001d28ccb3e8805c5fc9fdbff77 | 2026-10-09T01:10:37Z |
| `woa23_decav_t11_01.nc` | 61,736,080 | 07a93453e63de59e421f2965069d520c07dd21a7816e22280d718abc64630264 | 2026-10-09T01:10:40Z |
| `woa23_decav_t12_01.nc` | 61,989,442 | 38e685762cf1df303dcc367d1102c0b0eaa7291ea3dd7aa540756e197d1b95b5 | 2026-10-09T01:10:42Z |
| `woa23_decav_t13_01.nc` | 89,316,410 | 7edfbba8c30f4e3faa32fc89f2629e2119b110d30430e02ace56308384bd07f8 | 2026-10-09T01:10:49Z |
| `woa23_decav_t14_01.nc` | 89,460,608 | fbd26fc9fe124a90ef20c6e47c56923f81b623a85c281750f345714e482b17ac | 2026-10-09T01:11:00Z |
| `woa23_decav_t15_01.nc` | 89,528,977 | 53e87a378c08cb55e012bad1fe0ab611fb22c9e4028f8e931760fe0b886b0f43 | 2026-10-09T01:11:06Z |
| `woa23_decav_t16_01.nc` | 88,818,356 | a9055c6e1a11414ddf9cff1bd671ab37ad8c6abc6ddd3fe5af4be0d476b4a472 | 2026-10-09T01:11:09Z |
| `woa23_decav_s01_01.nc` | 55,456,076 | 437b2c2b472ceccbbecc563beefefe801557feaa6eb556c1f0075b39904105bf | 2026-10-09T01:11:12Z |
| `woa23_decav_s02_01.nc` | 55,610,405 | b384e1d3c45e1e166606b39ff90edc04b2666c7dfa366e4f8376a4a9f98b34a5 | 2026-10-09T01:11:14Z |
| `woa23_decav_s03_01.nc` | 55,774,035 | 7e8b8fa4fcb9762468fffd69b789f11960440c4992a336b8112216eaade616c5 | 2026-10-09T01:11:17Z |
| `woa23_decav_s04_01.nc` | 55,665,196 | 2e1c46417a1574a7254cb9cebf115acff3b502b62f5f957f0b85b7912b445af5 | 2026-10-09T01:11:21Z |
| `woa23_decav_s05_01.nc` | 55,381,305 | 665d8177a8d26bb23b187415a5bc166b880ef56c3e15a25312242bf58429bb48 | 2026-10-09T01:11:24Z |
| `woa23_decav_s06_01.nc` | 55,072,788 | ac8523da5087f5b35dae8a7bb71148eb1583682be9e15ff5fc7ebaf58b019084 | 2026-10-09T01:11:28Z |
| `woa23_decav_s07_01.nc` | 55,375,068 | ac3ac2c3247fe5076cd408d41c6621fb674ee7b0fb58ed078363eb52f53cab07 | 2026-10-09T01:11:31Z |
| `woa23_decav_s08_01.nc` | 55,793,507 | 0f4998095d63365a4c192c8e41950675c3eb17165f9563cbbc0973edce3fc006 | 2026-10-09T01:11:34Z |
| `woa23_decav_s09_01.nc` | 55,885,703 | 56d3de89af309a3e83f33cf90748af7cfae6e118511438bb496ea8aa78841298 | 2026-10-09T01:11:37Z |
| `woa23_decav_s10_01.nc` | 55,631,467 | 84280698779afaf3573da23888ed730b1131fdba2fbdfa6550bec7194dc8b9c8 | 2026-10-09T01:11:39Z |
| `woa23_decav_s11_01.nc` | 55,188,441 | ddc364cf72ada7a7f2f61068067f579e22a9f5000a5067da2aefad1b7e2471a7 | 2026-10-09T01:11:41Z |
| `woa23_decav_s12_01.nc` | 55,229,948 | fb37d5e97280c20d3eb9db69c0db785da6f1131c4edc446301b9eb6b21d3d65a | 2026-10-09T01:11:44Z |
| `woa23_decav_s13_01.nc` | 79,413,206 | f47d614eadc8898f694dd8c4df2fa1595c72a09fe09de891961ea5c5dfa22d18 | 2026-10-09T01:11:47Z |
| `woa23_decav_s14_01.nc` | 79,553,930 | a750de497f7b04b747b53c9313016fa1ecb3b18d8ba257362c3d99f2bc4552e8 | 2026-10-09T01:11:52Z |
| `woa23_decav_s15_01.nc` | 79,537,903 | b903f847df0be8308c9222108ee41ad2a6cee8cb30fa630a1f3cbf24b384c4e3 | 2026-10-09T01:12:13Z |
| `woa23_decav_s16_01.nc` | 78,983,581 | e46097cad0547e28bee6551083590027970517a50429c4757348dd498532bb44 | 2026-10-09T01:12:17Z |

## GSHHG 2.3.7 (coastline), fetched 2026-10-09

Source: `https://www.soest.hawaii.edu/pwessel/gshhg/gshhg-bin-2.3.7.zip`. Stored at
`/Users/pete/Downloads/mh370-ocean-data/gshhg/` (unzipped beside the archive). The crate reads `gshhs_f.b`
directly; there is no derived file.

| File | Bytes | sha256 | Fetched (UTC) |
|---|---|---|---|
| `gshhg-bin-2.3.7.zip` | 118,617,033 | 28600e8f7a08645aab43079326df6504212ec5ccb2b4bcf3b5f4f12ed60e82bc | 2026-10-09T04:50Z |
| `gshhs_f.b` | 95,809,336 | af9215d58ebc525b2d09654a89959829f09e6edc457f3666759cded37be4ecf6 | (from the zip) |

## AusSeabed / GA MH370 Phase 1 150 m bathymetry (ga/100315, CC BY 4.0), fetched 2026-10-09

Source: `https://files.ausseabed.gov.au/survey/Southern%20Indian%20Ocean%20(MH370)%20Bathymetry%202017%20150m.zip`
(the link in GA eCat record d887e71a-71dc-4851-94a9-920f7b7cc7e5). Stored at
`/Users/pete/Downloads/mh370-ocean-data/ausseabed/`.

The derived grid is the GeoTIFF's EPSG:3857 cells copied unchanged into
`grid/ausseabed_mh370_150m_elevation.f32` (float32 little-endian, rows south to north, nodata NaN). It is made by
`engine/crates/ocean/prepare/ausseabed_to_grid.py`; the manifest is `grid/ausseabed_mh370_150m.json`.

| File | Bytes | sha256 | Fetched (UTC) |
|---|---|---|---|
| `mh370_phase1_150m.zip` | 202,911,079 | 17b310edaf77859159947b8791bacd39e547246a5b3db2e7398d6f53b3b7480c | 2026-10-09T05:13Z |
| `Southern_Indian_Ocean__MH370__Bathymetry_2017_150m_MSL_cog.tif` | 207,058,753 | 247f4be9f1044eb1ca9305369fc117be9ab9f375632f2772c3af788c1794094e | (from the zip) |
| `grid/ausseabed_mh370_150m_elevation.f32` (derived) | 2,965,161,264 | 8d404ffb6be5299caecfd1aef7eb114e28f8f9755734541024001c9a210bc32e | 2026-10-09T05:15Z |

## GLORYS12V1 full-depth profile fields for settling (`GridProfile`), fetched 2026-10-09

`cmems_mod_glo_phy_my_0.083deg_P1D-m` (v202311) uo, vo, thetao, so, all 50 levels (0.494–5,727.9 m), plus
`cmems_mod_glo_phy_my_0.083deg_static` part `bathy` (deptho, deptho_lev, mask). Box 80–112 E, 45–18 S (385 × 325
columns); daily means labelled 7–14 March 2014 and placed at label + 12 h (PROVISIONAL, as for the surface
series). Fetched by `engine/crates/ocean/prepare/fetch_profile.py` (service arco-geo-series) and converted by
`prepare/profile_to_grid.py`. Stored at `/Users/pete/Downloads/mh370-ocean-data/glorys12/profile/`.

| File | Bytes | sha256 | Fetched (UTC) |
|---|---|---|---|
| `glorys12v1_static_bathy.nc` | 7,277,456 | e7e7e9db4b9ae4f560e9fda93ffb6e9c36f10a54556418057490454826fbc1dc | 2026-10-09T05:22:44Z |
| `glorys12v1_uo_vo_thetao_so_20140307-20140314.nc` | 400,435,174 | 65ffe88d0717784f884310066b6a4462df61ae05295b5fde7e3aee66d5f0a4b6 | 2026-10-09T05:23:57Z |
| `grid/glorys12v1_uo_vo_thetao_so_20140307-20140314.profile.f32` (derived) | 800,800,000 | f2c19df0065c24abcace26edb42426c6432b2552f5f805980f472208fab3ade5 | 2026-10-09 |
| `grid/glorys12v1_deptho.f32` (derived) | 500,500 | ddf66c4b1fa2972c29f1a5713cd0518f3fd88613ee9ac2647bf9ea989eb10c5e | 2026-10-09 |

## Copernicus-GlobCurrent (MULTIOBS_GLO_PHY_MYNRT_015_003, v202411), fetched 2026-10-09

- **Content:** total current `uo`, `vo` at 0 m over 15–120 E, 50–0 S (420 × 200 cells at 0.25°).
  - Hourly instantaneous fields, 7–31 March 2014: 600 fields.
  - Daily means with `err_uo` and `err_vo`, 7 March 2014 – 31 January 2017: 1,062 days, placed at
    label + 12 h (PROVISIONAL).
- **Provenance:** fetched by `engine/crates/ocean/prepare/fetch_globcurrent.py` and converted by
  `prepare/netcdf_to_grid.py`.
- **Stored at** `/Users/pete/Downloads/mh370-ocean-data/globcurrent/`. The series manifests are
  `grid/globcurrent_my_p1d_uo_vo_0m.series.json` and `grid/globcurrent_my_pt1h_uo_vo_0m.series.json`.

| File | Bytes | sha256 | Fetched (UTC) |
|---|---|---|---|
| `globcurrent_my_pt1h_uo_vo_0m_20140307-20140331.nc` | 201,631,684 | 3664986c503d319e19249ed0abe15363c4a14acf72b8bceb00328f4f4029a513 | 2026-10-09T05:28:51Z |
| `globcurrent_my_p1d_uo_vo_err_0m_20140307-20170131.nc` | 713,703,014 | 4aa9366d43fc92561c813f914b921b799613842e797fab60f8870e4159b8ee8f | 2026-10-09T05:29:32Z |
| `grid/globcurrent_my_pt1h_uo_vo_0m-00.f32` (derived) | 403,200,000 | 1e6d0ecddd2fea45870a56cebf478dcef55d48d02f1e990e9acfd8d0d4efa4a5 | 2026-10-09 |
| `grid/globcurrent_my_p1d_uo_vo_0m-00.f32` (derived) | 713,664,000 | bd8fb65d0421ceb7bf4a4f9ce1e05c5ffb217e37ec1976f37b7b2846cb4d8fd5 | 2026-10-09 |

## GDP drifter replay products, 2026-10-09

Stored at `/Users/pete/Downloads/mh370-ocean-data/products/gdp-replay/`. The statistics are copied into
`results/ocean-transport-error-gdp-replay.json`.

| File | Bytes | sha256 |
|---|---|---|
| `segments_20140308-20170130.json` | 31,027,918 | a44e5ba0f09278104c7bcf490e81e9174ddf42a927b9a0cba985e167d12d67dd |
| `sep_glorys12.f32` | 13,511,040 | e9422ee056fee2d54992c11b6de4c41b9b7eba0634cdaba64db92a05ede43442 |
| `sep_glorys12_era5w01.f32` | 13,511,040 | 531c0fbf6baf0b9bb4a59b8640dd01ef4f191b73901f71bb63ffa94aeb9b365d |
| `sep_globcurrent_p1d.f32` | 13,511,040 | 9043b4ec072515c7d9c52343973a0ad117f637af710dede61131f871f5288c81 |
| `sep_glorys12_waverys.f32` | 13,511,040 | 6ec06771ac09c7706fd73510921501b263ec6ba32096b69b707779eeb92aac57 |
| `sep_glorys12_waverys_era5w01.f32` | 13,511,040 | 9a9472842dfe53d1f4506c900a36ca6aa96c60b134c081d7e7ed9c2e9dd61e3c |
| `sep_globcurrent_p1d_era5w01.f32` | 13,511,040 | cebc38234ee5d9226e5f5f0044b88fbf8e42d893450e2a63b4d35034c0bd8c09 |
