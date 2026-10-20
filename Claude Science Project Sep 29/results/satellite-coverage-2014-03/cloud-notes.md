# Cloud layer for the MH370 satellite-coverage study — method note

Study box 20-45 S, 70-110 E. Days 8-27 March 2014 (period A 8-15 Mar, period B 16-27 Mar). Reference hour 04:00 UTC
(about 10:00-10:45 local solar time across the box, the descending-node pass time of the sun-synchronous optical imagers).

## Source 1 — ERA5 (primary, drawn in the maps)
- Dataset: ERA5 hourly data on single levels (ECMWF / Copernicus C3S), CDS identifier `reanalysis-era5-single-levels`.
- Variables: total_cloud_cover (tcc), high_cloud_cover (hcc), medium_cloud_cover (mcc), low_cloud_cover (lcc); fractions 0-1.
- Grid 0.25 deg; valid time 04:00 UTC each day; subset latitude -20 to -45, longitude 70 to 110 (101 x 161 cells).
- Access route actually used: the Analysis-Ready Cloud-Optimized ERA5 public mirror (Google Research / ECMWF),
  `gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3`
  (HTTPS: https://gcp-public-data-arco-era5.storage.googleapis.com/ar/full_37-1h-0p25deg-chunk-1.zarr-v3), mirror last_updated 2026-10-19 16:52:53.440217+00:00.
  The CDS API (https://cds.climate.copernicus.eu/api) was not used: the stored Copernicus credential is an account login, the CDS API needs the
  personal access token from the profile page, and the ECMWF single-sign-on host (auth.ecmwf.int) was unreachable from the sandbox even after a grant.
  The ARCO fields are the same ERA5 reanalysis fields the CDS serves. Licence: Copernicus licence.
- File: cloud-era5-04utc-2014-03-08-27.nc (NetCDF4, dims time=20, latitude=101, longitude=161).

## Source 2 — MODIS Terra MOD08_D3 (independent check, tabulated)
- Dataset: MODIS/Terra Aerosol Cloud Water Vapor Ozone Daily L3 Global 1Deg CMG, short name MOD08_D3, Collection 6.1, CMR concept id C1443727145-LAADS.
- Variables: Cloud_Fraction_Day_Mean (daytime passes only, the relevant one for optical imaging) and Cloud_Fraction_Mean (day + night); scale 1e-4, fill -9999 -> NaN.
- Files: MOD08_D3.A2014067.061.*.hdf to MOD08_D3.A2014086.061.*.hdf (20 files, ~195 MB each), downloaded with the NASA Earthdata login from the
  LAADS Earthdata-Cloud distribution https://data.laadsdaac.earthdatacloud.nasa.gov/prod-lads/MOD08_D3/ (redirects to a signed CloudFront URL).
  The classic archive https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/61/MOD08_D3/2014/ refused the login
  ("Please update your profile for application required attributes Organization"), an Earthdata-profile setting, not a sandbox block.
- Terra's descending node is ~10:30 local solar time, so the daily daytime aggregate over the box samples 03:30-05:00 UTC, matching the ERA5 hour.
- File: cloud-modis-mod08d3-2014-03-08-27.nc (dims time=20, lat=27, lon=42, 1 deg; subset 19.5-45.5 S, 69.5-110.5 E so the box edge cells are included).

## Arc band statistic
7th-arc coordinates from arcs-sea-level.csv (columns lat, lon_arc7), densified to 0.05 deg in latitude. A grid cell is in the band when its centre lies
within 150 km great-circle distance of the arc (ERA5: 2014 cells; MODIS: 130 cells), restricted to the box (20-45 S).
Means are area-weighted by cos(latitude). 'Usable for optical imaging' = fraction of band area with cloud cover < 0.3.

## Summary table columns (cloud-daily-summary.csv)
date, time_utc, era5_box_mean_tcc, era5_arcband_mean_tcc, era5_arcband_frac_tcc_lt_0p3, era5_arcband_mean_low, era5_arcband_mean_high,
modis_box_mean_cf_day, modis_arcband_mean_cf_day, modis_arcband_frac_cf_day_lt_0p3, modis_arcband_mean_cf_all.

## Result in brief
Arc-band total cloud cover at 04:00 UTC (ERA5) ranged 0.57-0.87 over the 20 days
(mean 0.75); the usable (<0.3) fraction of the band never exceeded 0.27
(24 March) and was below 0.06 on 8, 9, 14, 15, 16, 17 and 19 March (7 days). MODIS daytime cloud fraction over the band agrees in pattern
(r = 0.86) and reads 0.08 higher on average,
the usual sign for a passive cloud-mask product against reanalysis.

## Figures
cloud-cover-daily-7-15mar2014.png (8-15 Mar; 7 Mar not included — the period starts on the first full day after the loss) and
cloud-cover-daily-16-27mar2014.png: ERA5 total cloud cover, viridis 0-1 (dark = clear, light = covered), 7th arc solid, 6th arc dashed,
study box dotted, Natural Earth 110m coastline, 300 dpi. Footnotes: plain-language and technical.
