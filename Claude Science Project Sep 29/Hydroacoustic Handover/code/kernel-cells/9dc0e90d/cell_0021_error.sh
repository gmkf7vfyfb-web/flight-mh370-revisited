cd out && python - <<'EOF'
p='evidence-sweep-2026-10-17.md'; s=open(p).read()
add='''
### E. Second pass (17 Oct 2026, later): further items

| # | Evidence | Observable and likelihood form | Informs | Status | Sources |
|---|---|---|---|---|---|
| E1 | Positive controls for sonar detection: the two 19th-century shipwrecks found in ATSB Phase 2 | Known targets found by the same sensors and processing give an empirical check on the detection ratings (q) and on ρ | seabed-search q and ρ (today ρ has no published value) | NOT USED for detection (cited only in settling) | Anderson 2018, WA Museum for the ATSB |
| E2 | Merchant, fishing and transiting search vessels as opportunistic surface observers (AIS tracks, Mar-May 2014) | Low-POD surface non-detection over a large area and time, added to A1 in the same drift observation model | impact latitude | NOT FOUND | AIS archives (commercial) |
| E3 | Sea state, wind, cloud cover and daylight on each search and imaging date | NOT evidence. These are the covariates that set POD for A1, A2, A3, E2 and Pléiades. Without them, any surface term uses a constant POD | all surface terms | NOT FOUND (no sea-state or cloud fields in the repository) | ERA5 waves and wind; MODIS/Himawari/Meteosat-7 cloud |
| E4 | Expanded debris set beyond the stringent nine | About 60 items have been picked up and more than 30 examined; some were handed in but not collected or examined. "NO STEP 2" (Evatra, Madagascar, about 25° S 47° E, find date unknown) was reported in 2025. Each enters as a provenance-weighted observation, P(from MH370) × drift likelihood + (1 − P) × background, with interval-censored find dates | impact latitude; find timing on the south Madagascar coast | PARTIAL (drift scores 9) | Malaysian debris summaries 2017 and 2018; Gibson; Changing Times Dec 2025 |
| E5 | Contrails seen from satellites (Meteosat-7 IODC, MODIS long-wave IR) | Contrail formation from ERA5 temperature and humidity (Schmidt-Appleman) along each candidate path, then detection against the image. The 2014 claims are disputed (resolution, wind advection) | early turns 18:22-18:40; southern track | NOT FOUND (core has the Poll-Schumann performance model only) | Ulich and Prostyakov (claim); Vasquez/Meteosat-7 2014; Metabunk critique |
| E6 | Indian (Andaman) radar non-detection | As A7, with the alternative "not operating" | early route | NOT FOUND | press reports, Mar 2014 |

Screened on the second pass (no location information under the model):
- **US infrared early-warning satellites: no explosion.** This is a statement about the period near Malaysia, not the southern ocean at 00:19, and the data are not public. It bears only on in-flight-explosion hypotheses.
- **Fire or plume at impact (VIIRS night fires, the MODIS "plume" candidate).** After fuel exhaustion no fuel fire is expected, so absence carries no information. The candidates have no trials accounting.
- **ATSB finding that the Madagascar items were not exposed to heat.** This bears only on fire hypotheses.
- **SIGINT-satellite receptions of the satcom bursts.** Speculative and not available.
'''
s=s.replace("\n## 3. Suggested order of work", add+"\n## 3. Suggested order of work")
s=s.replace("8. D1: only through the pre-registered gate.",
"8. D1: only through the pre-registered gate.\n\nSecond-pass additions to the order: E3 is a prerequisite of item 1 and must be built with it. E1 is cheap and goes to searched areas now. E4 goes to drift as an extension of the find list. E2 and E5 come last (high effort, low or disputed information).")
open(p,'w').write(s)
EOF
grep -c "^| E" out/evidence-sweep-2026-10-17.md