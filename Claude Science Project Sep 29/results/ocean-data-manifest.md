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
