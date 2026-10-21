# Would MH370 have left a contrail? Formation, persistence and satellite detectability, 7–8 March 2014

Status: provisional working note for the Journal of Navigation paper (satellite-coverage module, continuously recording sensors). Session 20 Oct 2026.

## 1. Result in brief

1. **Formation (Schmidt–Appleman criterion).** Along the posterior routes the air at FL300–FL360 was too warm for a contrail. The only exceptions are the last two route epochs (00:01:49 and 00:11:49 UTC, near 34–36 S). At FL350 the posterior probability of formation is 0.00 from 18:22 to 23:31. It is 0.01–0.11 at 23:41–23:51, 0.80–0.82 at 00:01:49 and 0.92–0.94 at 00:11:49 (band = propulsion efficiency 0.30–0.35). FL380–FL400 were cold enough for a contrail almost everywhere. FL380 formation depends on latitude (0 to 1); FL400 forms at every epoch.
   - Probability that a contrail formed somewhere between 18:22 and 00:11:49:
     - at FL350: 0.92–0.94;
     - with every level FL300–FL400 equally likely: 0.61–0.70;
     - under the posterior altitude distribution: 0.83–0.87.
   - Raw and humidity-corrected ERA5 give the same formation result to ±0.001.
2. **Persistence (ice supersaturation, RHi ≥ 100 %).** The posterior-weighted probability that a contrail formed *and* persisted is below 1e-6 at every level FL300–FL400, every epoch, both propulsion efficiencies, and raw, Teoh et al. (2022) and Teoh et al. (2024) humidity (maximum 4.2e-7). Along the routes the 99.9th percentile of raw RHi is 0.62–0.96 depending on level; the median at FL350 is 0.36. Stress tests, which are harsher than the published corrections:
   - RHi divided by 0.9: 0.0000;
   - RHi divided by 0.8: at most 0.021 at one level (FL340), 0.0018 under the posterior altitude distribution;
   - temperature 1 K lower: at most 0.004 (FL360), 0.0004 under the posterior altitude distribution;
   - temperature 1 K higher: 0.
   **Conclusion: on the posterior routes after 18:22, any contrail would have been short-lived. It would not have grown into a persistent, spreading contrail.**
3. **Known track 16:42–18:22.** At the known cruise level (FL350, 16:57–17:20), ERA5 gives −44.5 to −45.1 °C and RHi ≤ 0.45. That is warmer than the FL350 threshold (−51 to −52 °C in dry air), so no contrail formed. Ice-supersaturated air (RHi up to 1.19) lay above the aircraft, at FL390–FL400, between Kuala Lumpur and IGARI (2.8–6.8 N, 101.7–103.5 E). After 17:20 the altitude is unknown. Over the whole radar track only FL380–FL400 meet the criterion at every point (FL370 at 6 % of points for η 0.30, 37 % for η 0.35), and after 17:20 the air at those levels was subsaturated.
4. **Detectability.** A contrail that does not persist stays about 0.08–0.15 km wide during the wake-vortex phase (first ~200 s) and then sublimates. That is narrower than every pixel listed below, so **no continuously recording sensor had a detectable window on these routes**. *If* a contrail had persisted, the first-detection age would have been:
   - polar-orbiter imagers: 5–18 min (VIIRS 375 m to AVHRR 1.1 km);
   - geostationary 4–5 km IR: 31–77 min;

   Detection typically ends about 2 h after formation (Section 4).
5. **Night imagery.** The Moon was 43 % illuminated but was below the horizon at every route point from take-off (16:42, Moon elevation −1.5° at Kuala Lumpur) to 00:11. Moonlit day/night band imagery was therefore impossible. The Sun was above the horizon along most routes from 00:01:49 (mean elevation +1.5°; +3.6° at 00:11:49).
6. **Cloud masking.** Cloud at and above FL350 was small along the route: mean maximum-overlap cover 0.038. The exception is the equatorial band at 19:31, where the posterior mean reaches 0.56 and the probability of ≥ 0.5 cover reaches 0.89. Total cloud, mostly below flight level, rose to 0.97 at 00:11 near the 7th arc. Low cloud does not mask a contrail, but it reduces the 11–12 µm contrast. ERA5 high cloud cover was 0.55 at 18:22 (Andaman Sea) and below 0.01 south of 15 S. The prior arc-band summary (cloud-daily-summary.csv, 04:00 UTC on 8–15 Mar) shows arc-band high cloud 0.03 on 8 Mar and total cloud 0.79, consistent with this.

The probabilities are posterior-weighted over run J. The reported posterior *paths* are firm in the sense that all 148,000 routes were used. The atmospheric inputs are a single reanalysis without ensemble spread, so all probabilities are conditional on ERA5 HRES.

## 2. Method

- **Routes.** Run J core posterior, `routes.npy` (lat, lon) for every seed:
  - waypoints 24 seeds, free 18, radar reproduction 16, descent-climb 16, 2,000 routes each, 148,000 in total;
  - route weight = family posterior weight / (seeds × 2,000), family weights 0.9982 / 0.0013 / 0.0003 / 0.0002;
  - vertices every 600 s from 18:01:49; epochs 18:21:49–00:11:49 used (36 epochs);
  - the routes end at 00:11:49, so 00:11:49–00:19 is not covered.

  Known track: Geoscience Australia digital radar workbook, sheet Data-Cleaned-Estim-Time, 467 points 16:42:27–18:22:12, aggregated in 10-min bins.
- **ERA5.** Hourly 0.25° reanalysis on pressure levels 100–350 hPa:
  - variables: temperature, specific humidity, u, v, cloud fraction, cloud ice water; single-level high/medium/total cloud cover;
  - 7 Mar 16:00 to 8 Mar 01:00 UTC, box 12 N–42 S, 80–106 E;
  - read anonymously from the ARCO-ERA5 zarr (`gcp-public-data-arco-era5`, store `ar/full_37-1h-0p25deg-chunk-1.zarr-v3`);
  - interpolated linearly in time, bilinearly in latitude/longitude and linearly in ln p, to ISA flight-level pressures (FL300 300.9 hPa, FL350 238.4 hPa, FL400 187.5 hPa; FL300–FL400 in steps of 10).

  The ARCO store holds no relative humidity, so RHi = e/e_ice(T) with e from q and p.
- **Schmidt–Appleman criterion** (Schumann 1996):
  - mixing-line slope G = EI_H2O·c_p·p / (ε·Q·(1−η)), with EI_H2O = 1.25 kg/kg, Q = 43.2 MJ/kg, c_p = 1004 J/(kg K), ε = 0.6219;
  - η = 0.30 and 0.35. Schumann et al. (2017) give η between 0.1 and 0.4, mostly 0.3, for operating aircraft; ≈0.3 is the value commonly used for modern Rolls-Royce Trent engines;
  - T_LM from Schumann's approximation, refined by Newton iteration on de_liq/dT = G. The approximation is within 0.04 K of the exact value;
  - a contrail forms when T < T_LM and e + G·(T_LM − T) ≥ e_liq(T_LM);
  - saturation pressures from Sonntag (1994), as in CoCiP/pycontrails.
  - Check values: at FL350, T_LM = −42.2 °C (η 0.30) and −41.5 °C (η 0.35); the dry-air threshold is −51.7 / −51.0 °C. At 250 hPa the code gives −41.7 / −41.0 °C against −42.0 / −41.2 °C in the OpenAP library documentation.
- **Persistence:** the criterion is met and RHi ≥ 1.
- **Humidity corrections.** Both raw and corrected are reported.
  1. Teoh et al. (2022), Eq. 1: RHi/0.9779, and where that exceeds 1, (RHi/0.9779)^1.635, capped at 1.65. This is the North Atlantic calibration.
  2. Teoh et al. (2024), Eqs. 2–4: latitude-dependent sigmoid coefficients, with the cap set by liquid saturation or the homogeneous-nucleation limit. It is the appropriate correction for these latitudes: it lowers ISSR coverage in the tropics and raises it south of 40 S.
     - Coefficients follow the authors' reference implementation, pycontrails `ExponentialBoostLatitudeCorrectionHumidityScaling`, pressure levels: a = 0.062621/(1+exp(0.45893(|φ|−39.254))) + 0.95224, b = 1.4706/(1+exp(0.44312(|φ|−18.755))) + 1.4325.
     - The paper's printed Eq. 3 reads 0.04431 for the b slope; the code uses 0.44312. This does not affect the result, because no point reaches RHi ≥ 1 after the first scaling step.
  3. Stress tests: constant division by 0.9 and 0.8. Wolf et al. report that older work divided ERA5/IFS RHi by factors of 0.8–0.9 (Schumann & Graf 2013; Schumann et al. 2015). Also T ± 1 K: ERA5 has a cold bias of 0.1–0.7 K at 200–250 hPa against IAGOS, mid-latitudes (Wolf et al.).
- **Altitude cases:**
  - each level FL300–FL400 separately;
  - FL300–FL400 equally likely;
  - posterior altitude distribution: core `trace.npy` altitude at 18:42:40, pooled with the family weights (5/50/95 % = 29,000/37,000/40,000 ft). It is held constant after 18:42 and assumed independent of route, because trace rows are not row-linked to routes rows (checked: same-row distance equals shuffled distance). Mass below FL300 (6.2 %) is given no formation, since FL300 never meets the criterion and lower levels are warmer. FL410 (0.8 %) takes the FL400 result.
- **Cloud:**
  - cloud fraction interpolated to flight level;
  - cover above flight level from the native levels above it, by maximum overlap (lower bound) and random overlap (upper bound);
  - ERA5 high cloud cover (p < 450 hPa) and total cloud cover.
- **Wind shear at FL350** from u, v at 225 and 250 hPa, with hypsometric layer thickness: median 0.0044 1/s (5–95 % 0.001–0.007 1/s).
- **Sun and Moon:** Skyfield with JPL DE421 on a 1° grid per epoch, bilinear to the route points.

## 3. Contrail width and optical depth versus age (literature)

| Age | Ice-supersaturated air | Subsaturated air | Source |
|---|---|---|---|
| < 200 s (jet and wake-vortex phase) | width ≈ 80–150 m, growing slowly | same; most ice lost by the end of the vortex phase | Schumann et al. 2017 (Fig. 2 discussion; lidar of Freudenthaler et al. 1995) |
| Example, FL350, RHi 39 %, T −63 °C | — | width ≈ 55 m; effective depth decreasing by sublimation | Busen et al. 1994, via Schumann et al. 2017 |
| 150 s → 1,200 s | depth 120 → 150 m, width 350 → 1,800 m (shear 0.005–0.01 1/s) | — | in-situ case in Schumann et al. 2017 §3.1 |
| 1 min – 1 h | mean horizontal spread 2.3 m/s (≈ 8 km/h), vertical 0.3 m/s; areal spread 60–420 m²/s | does not apply | Freudenthaler et al. 1995, via Schumann et al. 2017 |
| ≈ 1 h | width ≈ 1.35 km, τ ≈ 0.15 (0.1–0.4) | — | Freudenthaler et al. 1994 |
| Hours | spread 7–8 km/h, maximum width after 2–4 h, mean width 14.5 ± 9 km, τ 0.23 ± 0.14 | — | 11 Sept 2001 shutdown contrails (GOES/AVHRR/MODIS), Schumann et al. 2017 §3.2.9 |
| Satellite-tracked life | mean (max) duration 1 h (17 h) after 0.5–1 h dwell before visibility, width 8 km (14 km), τ 0.34 (2) | — | ACTA, Meteosat 3 km rapid scan (Vázquez-Navarro et al. 2015, via Schumann et al. 2017) |
| Optical depth vs age | largest in young contrails, then a near-constant median ≈ 0.3 | — | Schumann et al. 2017 (Fig. 3d) |

Teoh et al. (2024) count a contrail as persistent only if its ice water content survives the wake-vortex phase. They note that contrails in subsaturated air do not sublimate instantly; the rate depends on the background RHi. Schumann et al. (2017) call contrails in subsaturated air "short-lived". The literature read here gives no general lifetime-versus-RHi relation, so "minutes" is used qualitatively.

## 4. Detectability thresholds and age windows

Detection rules (Driver et al. 2025, synthetic 11/12 µm split-window detection over a clear ocean background):
- contrails with optical depth below about 0.05 are undetectable at any width;
- detection starts once the width reaches slightly below the imager pixel size;
- median age at first detection is 21 min (quartiles 10–94 min) at 2 km and 9 min (5–70 min) at 0.5 km;
- only 46 ± 2 % of a global contrail population is observable at 2 km, mostly because the rest are optically too thin.

Geostationary studies report first detection 10–45 min after formation (Chevallier et al. 2023; Gryspeerdt et al. 2024; Geraedts et al. 2024, cited in Driver et al. 2025). The 2025 attribution benchmark (AMT 18, 3495) states that virtually all GOES-detectable contrails become detectable within 2 h.

Width model used here: W = 0.15 km at 200 s, then linear growth at s = 2.3 m/s (fast, observed mean) or s = S·D = 0.0044 1/s × 250 m = 1.09 m/s (slow, ERA5 median shear). First detection when W ≥ pixel, and W ≥ pixel/2 as the optimistic case. The model reproduces the Driver medians: 5.9–8.7 min vs 9 min at 0.5 km, and 16.7–31.5 min vs 21 min at 2 km.

| Sensor class (2014) | Nominal pixel | First detection, fast / slow spread (min) | Optimistic (half pixel, fast) | Window if ice-supersaturated | Window on MH370 routes |
|---|---|---|---|---|---|
| VIIRS I5 11.45 µm single band (Suomi NPP) | 0.375 km | 5.0 / 6.8 | 3.6 | ≈ 5–120 min | none |
| VIIRS M15/M16 split window | 0.75 km | 7.7 / 12.5 | 5.0 | ≈ 8–120 min | none |
| VIIRS day/night band (moonlit) | 0.742 km | 7.6 / 12.4 | 4.9 | in principle ≈ 8–120 min | none: no moonlight (Moon set before take-off) |
| MODIS 31/32 (Terra, Aqua) | 1 km | 9.5 / 16.3 | 5.9 | ≈ 10–120 min | none |
| AVHRR 4/5, full resolution | 1.1 km | 10.2 / 17.8 | 6.2 | ≈ 10–120 min | none |
| Geostationary IR 2 km (reference only) | 2 km | 16.7 / 31.5 | 9.5 | ≈ 17–120 min | none |
| Geostationary IR 4 km | 4 km | 31.2 / 62.0 | 16.7 | ≈ 31–120 min | none |
| Geostationary IR 5 km | 5 km | 38.5 / 77.2 | 20.4 | ≈ 39–120 min | none |

Notes on the classes:
- **Scan-edge pixels are larger.** Computed geometry gives about 2.0× (MODIS, 55°), 2.2× (AVHRR, NOAA-19, 55.4°) and 2.2× (VIIRS without its on-board aggregation) at scan edge.
- **Geostationary pixels grow with viewing angle.** 1/cos(view zenith) at the route points 6.6 N 96.3 E / 20 S 95 E / 35 S 93 E is 1.03–1.36 from 82–105 E, 1.4–1.8 from 57.5 E and 1.8–2.6 from 145 E. All of these delay first detection proportionally.
- **VIIRS 375 m.** I5 is a single 11.45 µm band. The split-window brightness-temperature difference used by contrail algorithms needs the 750 m M15/M16 pair.
- **Day/night band.** No published quantitative contrail threshold for moonlit day/night band imagery was found. The IR width rule is applied at its pixel size as an assumption. With the Moon below the horizon, only airglow illumination was available.
- **End of window.** About 2 h is a typical end (ACTA mean duration of 1 h after a 0.5–1 h dwell; Driver et al. 2025). Contrails can stay detectable for many hours; 11.5 h and 17 h are the observed maxima.

## 5. Limitations

- ERA5 0.25°/1 h with 25 hPa spacing at 200–250 hPa and 50 hPa at 250–300 hPa. Thin moist layers and sub-grid ISSR patches are smoothed. The humidity corrections are calibrated on IAGOS data dominated by northern mid-latitudes, with only some tropical coverage (2019 global set). No radiosonde check was made for 7 Mar 2014 over the Indian Ocean (Cocos Island, Christmas Island, Perth soundings are a possible follow-up).
- No ensemble: the ERA5 10-member ensemble spread was not used.
- No CoCiP simulation. Contrail lifetime and width are not computed for this flight; the literature envelopes in Sections 3–4 are used instead. With no ISSR on the routes a CoCiP run would terminate the contrails in the wake-vortex phase, but that was not run.
- Altitude after 18:42 is unknown. The posterior altitude case is an assumption (constant altitude, independent of route). The descent-climb family's altitude is set by how the family is built (recorded in project memory), but its weight is 0.0002.
- The routes end at 00:11:49. The last minutes to fuel exhaustion and the descent are not covered. By 00:01–00:11 the Sun was rising, so a contrail formed then would have been sunlit, but in subsaturated air it would still have been short-lived.
- Geostationary platform list and sub-satellite longitudes for March 2014 (MTSAT-2, FY-2D/E, INSAT-3D, Kalpana-1, Meteosat-7 IODC, COMS-1) are from general knowledge and are not verified here. The 2 km class is shown for reference only. Global AVHRR archives for NOAA satellites are largely reduced-resolution GAC; full 1.1 km data exist globally for MetOp and otherwise only where a receiving station recorded. Not verified in this session.

## 6. Queries for Pete

1. Confirm the geostationary imagers and sub-satellite longitudes that covered 80–105 E in March 2014, and whether full-resolution archives exist (needed only for the persistent-contrail hypothetical).
2. Decide whether a pycontrails CoCiP run along a few representative routes, with ERA5 omega and radiation fields, is wanted for the paper. It would turn the "short-lived" statement into computed lifetimes and widths.
3. Decide whether to add a radiosonde check (Cocos/Christmas Island, 8 Mar 2014 00 UTC) of upper-tropospheric humidity.

## 7. Files

- `contrail-probability-along-route.csv` — long table, 6,992 rows: segment (known radar track 10-min bins / posterior routes), time, altitude case (FL300…FL400, FL300–FL400 uniform, posterior altitude), propulsion efficiency, humidity (raw, teoh2022, teoh2024, rhi/0.9, rhi/0.8, T−1K, T+1K), p_form, p_persist, probability of any formation/persistence 18:22–00:11:49, posterior mean and 5–95 % latitude.
- `contrail-environment-along-route.csv` — per epoch: temperature and RHi percentiles, T_LM, cloud at and above FL300/FL350/FL400, high and total cloud, FL350 shear, Sun and Moon elevation.
- `contrail-probability-by-latitude.csv` — 5° bands.
- `contrail-detectable-age-window-by-sensor.csv` — Section 4 table.
- `contrail-formation-persistence-detectability.png/.pdf` — figure.
- Code:
  - `contrail_lib.py` (physics);
  - `era5_extract.py` (ARCO ERA5 subset, 25 s, 52 MB, not stored);
  - `run_contrail_analysis.py` (regenerates the posterior part of the main CSV; checked identical, 2,808 rows, maximum difference 0).

## References

- Driver O.G.A. et al. (2025) Factors limiting contrail detection in satellite imagery. AMT 18, 1115–1134. doi:10.5194/amt-18-1115-2025
- Schumann U. (1996) On conditions for contrail formation from aircraft exhausts. Meteorol. Z. 5, 4–23.
- Schumann U. (2000) Influence of propulsion efficiency on contrail formation. Aerosp. Sci. Technol. 4, 391–401. doi:10.1016/S1270-9638(00)01062-2
- Schumann U. et al. (2017) Properties of individual contrails: a compilation of observations and some comparisons. ACP 17, 403–438. doi:10.5194/acp-17-403-2017 (source for Freudenthaler et al. 1994/1995, Busen et al. 1994, Minnis et al. 2002, Vázquez-Navarro et al. 2015 values quoted)
- Sonntag D. (1994) Advancements in the field of hygrometry. Meteorol. Z. 3, 51–66.
- Teoh R. et al. (2022) Aviation contrail climate effects in the North Atlantic from 2016 to 2021. ACP 22, 10919–10935. doi:10.5194/acp-22-10919-2022
- Teoh R. et al. (2024) Global aviation contrail climate effects from 2019 to 2021. ACP 24, 6071–6093. doi:10.5194/acp-24-6071-2024
- pycontrails, humidity_scaling.py and sac.py (github.com/contrailcirrus/pycontrails, main branch, read 20 Oct 2026)
- Wolf K. et al. Correction of ERA5 temperature and relative humidity biases by bivariate quantile mapping for contrail formation analysis (ACP; bias values and the 0.8–0.9 scaling statement quoted from the abstract and introduction as indexed; full text not read)
- Benchmarking and improving algorithms for attributing satellite-observed contrails to flights, AMT 18, 3495 (2025) (2 h detectability statement, abstract-level)
- Hersbach H. et al. (2020) The ERA5 global reanalysis. QJRMS 146, 1999–2049; ARCO-ERA5 (Google Research) public zarr.
