# Ocean product recommendation, for the architect's ruling (ocean transport, 9 October 2026)

**Status: ruled by the architect on 9 October.** The reference is GLORYS12 + ERA5. GlobCurrent is the second `ocean-model` value, a declared alternative at equal prior weight. The text below is the recommendation as submitted. All products listed under "Available now" are
downloaded, converted and verified. sha256 values are in `ocean-data-manifest.md`, and citations are in
`ocean-references.md`.

## Available now, over 15–120 E, 50–0 S, 7 March 2014 – 31 January 2017 unless stated

| Role | Product | `Forcing::ocean_model()` |
|---|---|---|
| Reference current | GLORYS12V1 daily surface (0.494 m), 1/12° | `glorys12v1` |
| Wind | ERA5 10 m, 3-hourly (ARCO-ERA5) | `+era5-wind10` |
| Explicit Stokes | WAVERYS surface Stokes drift, 3-hourly, 0.2° | `+waverys` |
| **Second ocean model** | **Copernicus-GlobCurrent** (MULTIOBS_GLO_PHY_MYNRT_015_003, v202411), daily (full period) and hourly (7–31 March 2014) | `globcurrent-my-p1d`, `globcurrent-my-pt1h` |
| Profiles (settling) | GLORYS12V1 full depth, 80–112 E, 45–18 S, 7–14 March 2014 | `GridProfile` |

## Recommendation

1. **The reference current is GLORYS12V1 with ERA5 wind**, in the absorbed-Stokes leeway system
   (`leeway_absorbs_stokes`). The explicit-Stokes system adds WAVERYS. The D-b reproduction arm already runs
   on GLORYS12 as the declared departure from CSIRO's BRAN2016.
2. **The `ocean-model` discrete alternative gets a second value: Copernicus-GlobCurrent.**
   - Drift uses the daily product over the drift period.
   - Pléiades uses the hourly product for the 8–23 March window. That product contains the barotropic tide
     and hourly Ekman variability.
   - GlobCurrent is observation-based (altimetric geostrophy + empirical Ekman from ERA5 stress + tide),
     so it shares no ocean model with GLORYS12. That makes it a real alternative rather than a
     perturbation.
   - On the GDP replay it is no worse than GLORYS12, and better for undrogued drifters
     (`ocean-transport-error-gdp-replay.md`).
   - Drift and Pléiades marginalise it jointly under the same label (brief rule 7).
3. **Equal prior weight on the two values**, fixed before any likelihood is seen. The replay skill is
   reported as a diagnostic; it is not used to set the weights, because using drifter skill to weight
   a model that is then scored on debris would count related evidence twice.
4. **Composition rules for GlobCurrent:**
   - It already contains the wind-driven (Ekman) current, so windage terms keep their meaning as the
     object's leeway, exactly as with GLORYS12.
   - Its Stokes content is declared `Partial`, because its Ekman transfer is fitted to drifters. An
     explicit-Stokes arm on GlobCurrent therefore has to set `accept_partial_stokes_overlap`, and is not
     recommended.
5. **Not recommended now:**
   - **OSCAR v2.** Its construction is close to GlobCurrent's (geostrophic + Ekman from ERA5), so it adds
     little independent information. It also needs a separate Earthdata download.
   - **BRAN2016 or BRAN2020** as the CSIRO-system arm. The NCI `gb6` licence requires CSIRO registration
     and restricts use to government-funded research. The 15 fetched BRAN2016 files stay unused until
     Pete decides.
   - **HYCOM reanalysis.** Not fetched; it would be a third model-based alternative.
6. **Version note.** CMEMS announces that GlobCurrent v202411 retires on 24 November 2026. The files and
   sha256 values recorded here keep the runs reproducible; any re-fetch after that date will get a newer
   version and must be re-verified.

— ocean transport (architecture sub-agent)
