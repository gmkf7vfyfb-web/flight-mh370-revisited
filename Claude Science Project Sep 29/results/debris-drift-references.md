# Ocean drift: citation ledger

The drift module's ledger under the standing rule of 9 October (`coordination/architecture.md`,
~01:20 UTC). The matching BibTeX is `engine/hypotheses/debris-drift/references.bib`. The ledger is
**here in `results/`, not in the module directory**, because the engine tree allows only three `.md`
files (ARCHITECTURE.md, conventions) and this module's own instructions forbid new `.md` inside
`engine/`. The conflict has been raised; the file moves if ruled otherwise.

Printed pages are from running footers (CSIRO reports) or running headers (Springer), checked page by
page. No unauthorised copy of a copyrighted work is cited.

| key | source | printed pages: what each supports | used in | obtained from, licence |
|---|---|---|---|---|
| davey2016 | Davey, Gordon, Holland, Rutten, Williams (2016) *Bayesian Methods in the Search for MH370*. Springer. DOI 10.1007/978-981-10-0379-0 | p. 103: eq. 11.4, the per-particle update; 508 ± 30 days. p. 106: eq. 11.9, the density ratio with ε. p. 109: the "negligible" northward shift | `results/davey-ch11-reproduction.md`; `prepare/gdp/`; `tests.rs` (508-day check) | Springer open access, CC BY-NC 4.0; artifact `10.1007_978-981-10-0379-0_11.pdf` |
| griffin2017partii | Griffin, Oke, Jones (2017) *The search for MH370 and ocean surface drift - Part II*. CSIRO Oceans and Atmosphere, report EP172633, 13 April 2017 | p. iv: arrival consistent with 40-30.5°S; Africa arrivals after Dec 2015 favour south of 32°S. p. 1: replicas' shape and flotation. p. 2: cut-down flaperon's waterline. p. 7: trial design (days 11-13); 1.2% from Stokes drift; replica leeway. p. 10: extra leeway ~10 cm/s, constant; 16° mean angle; replica 4°; trial angles 10° and 20°. p. 11: 10 cm/s + 1.2% wind (Fig. 2.3.1). p. 12: Part I assumption; arrival flat over 40-30.5°S. p. 17: range 0-30° left; 10 cm/s in excess of Stokes; "not a precise guide" | rulings D-a, D-b, D-c; `pilot.toml` flaperon class; `results/debris-drift-flaperon-provenance.md`; review E1, E15 | project Drive copy, id `1S-WCMaRKt0lRlV0Uv3bfVSKZvEd8TjDf`, 2,007,478 B (ATSB release; the ATSB server refuses automated clients); © CSIRO 2017, all rights reserved; cited, not redistributed |
| griffin2017partiii | Griffin, Oke (2017) *The search for MH370 and ocean surface drift - Part III*. CSIRO Oceans and Atmosphere, report EP174155, 26 June 2017 | p. 6: 1.2% of wind for items "subject to Stokes Drift but not direct wind forcing", added to BRAN2015's 0-5 m surface layer; 3% for items floating higher; random walks of 5 NM/day r.m.s. p. 8: windage factors 0, 1.2% and 3% | `pilot.toml` low-exposure and high-windage priors; review §9 claim 6 (K = 248 m²/s) | artifact `csiro-part-iii.pdf` (version 571717b4); © CSIRO 2017; cited, not redistributed |
| griffin2016parti | Griffin, Oke, Jones (2016) *The search for MH370 and ocean surface drift*. CSIRO report EP167888, 8 December 2016. DOI 10.4225/08/5892224dec08c | cited through Part II only (replica trials). **Not yet read in primary form** | review | Drive copy `CSIRO I mh370_ocean_driftv29.pdf` exists, not yet read |
| sutherland2020 | Sutherland, Soontiens, Dufois, et al. (2020) "Evaluating the leeway coefficient of ocean drifters using operational marine environmental prediction systems". *J. Atmos. Oceanic Technol.* DOI 10.1175/JTECH-D-20-0013.1; arXiv:2005.09527 | implicit and explicit leeway coefficients are different quantities, estimated per system | rule 10; review E1; `leeway_absorbs_stokes` | arXiv open access. **Pages to be added when read in primary form** |
| gdp6h | Lumpkin, Centurioni (2019) Global Drifter Program quality-controlled 6-hour interpolated data. NOAA NCEI. DOI 10.25921/7ntx-z961 | undrogued fixes, 1979-2025, 60°S-10°N, 20-140°E | `prepare/gdp/`; Davey reproduction | AOML ERDDAP `drifter_6hour_qc`; 41 files, sha256 in `results/ocean-data-manifest.md`; public domain (US Government) |
| glorys12 | E.U. Copernicus Marine Service, Global Ocean Physics Reanalysis GLOBAL_MULTIYEAR_PHY_001_030 (GLORYS12V1). DOI 10.48670/moi-00021 | surface currents uo, vo at 0.494 m, daily means | `pilot.toml`, `smoke-fields.toml` (through `crates/ocean`) | downloaded by ocean transport; manifest in `results/ocean-data-manifest.md`; Copernicus Marine licence |
| era5 | Hersbach et al. (2020) "The ERA5 global reanalysis". *Q. J. R. Meteorol. Soc.* 146, 1999-2049. DOI 10.1002/qj.3803. Via ARCO-ERA5 (Carver et al. 2023) | 10 m wind u10, v10, 3-hourly | `pilot.toml`, `smoke-fields.toml` | downloaded by ocean transport; Copernicus licence |
| mot2018 | Ministry of Transport Malaysia, *Summary of Possible MH370 Debris Recovered*, updated 30 December 2018 | item classifications and dates in the evidence table; Mossel Bay item 4 listed 22 March 2016 | `data/debris-evidence-audit.csv` (via the frozen audit); `results/debris-drift-find-episodes.md` | through the hand-curated evidence table. **Primary copy to be located and its page cited** |
| durgadoo2021 | Durgadoo, Biastoch, et al. (2021) "Dynamics of the MH370 debris drift" (stringent nine-object set) | the stringent identity set; dates marked `primary_date_from_durgadoo` | evidence table selection | **Not re-read in primary form; full reference and pages to be verified before the paper** |

**Open items in this ledger:**
1. Durgadoo et al. 2021: full reference and pages.
2. MOT 2018: a primary copy.
3. Part I: read in primary form.
4. Sutherland et al. 2020: pages.

The prior-work review (`results/debris-drift-review.md`) cites further literature (AF447/BEA, Stone
et al. 2014, Breivik and Allen 2008, Nesterov 2018, Maximenko et al. 2018 and others). Those enter
this ledger as each value is used in code or a ruling, per the standing rule.
