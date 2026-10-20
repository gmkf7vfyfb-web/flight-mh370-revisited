# MH370: three equal route priors, BFO sigma 4.3 Hz

## Result

Each leaf has prior probability exactly 1/3:

1. P627: last radar -> NILAM -> SANOB -> IGEBO -> POVUS.
2. IGOGU and published boundary: last radar -> NILAM -> IGOGU -> 6N 94d25E -> 6N 92E, then a southward command.
3. IGOGU and south continuation: last radar -> NILAM -> IGOGU, then a southward command.

The IGOGU group has 2/3 prior probability. Its two leaves each have 1/2 conditional prior probability within the IGOGU-only view. Posterior leaf weights are NOT forced to these priors.

No complete trajectory survives the current sampling and model gates. Consequently no normalized 00:11 density, mean location, credible contour, or posterior route weight is reported. The PDF's maps show prior geometry only. They do not reuse the old 7 Hz posterior.

The two larger P627 attempts each start with 250,000 draws and have zero joint early survivors. In P627 B, 39 physically admissible trajectories pass the range and BFO gates for all three early contacts, but fail the added nominal-arc crossing-time gate. The main IGOGU south/boundary runs each start with 180,000 draws; they retain 102/99 distinct early trajectories before resampling. Neither of their 90,000 first-call proposals passes the inherited condition of reaching IGOGU and completing the southward turn by 18:39:55.354 UTC.

That first-call turn deadline is a route-prior assumption carried over from the earlier hypothesis. This result must NOT be described as exclusion of IGOGU by BFO data alone. The control prior has a 600-second speed-capture constant, commanded acceleration capped at 0.25 m/s^2, and sparse target changes. These are sampling/control assumptions, not manufacturer-certified performance limits. Finite sampled absence is not a proof of infeasibility, and the early effective sample sizes remain poor (about 1.3 and 51.9 in the main IGOGU runs).

The public-data fuel/performance model is active, with an exhaustion selection window of 00:15-00:19. All new runs stop before reaching that final window. None of these new trajectories has been shown to pass the full-flight fuel and satellite conditions.

## Observations and exclusions

- First R600: 2014-03-07 18:25:27.421 UTC, raw BTO 17120 us minus 4600 us = 12520 us, BTO sigma 62 us, BFO 142 Hz. Its BFO is assumed valid as explicitly requested by the user; this differs from Davey's decision to discard restart BFOs.
- Seven stable R1200 observations: two at 18:28, then 19:41, 20:41, 21:41, 22:41 and 00:10:59.928. BTO sigma 29 us.
- BFO sigma 4.3 Hz and hard +/-8.6 Hz gates.
- Range hard gates +/-2 sigma. Independent additional condition: actual path crosses the contact-time, satellite-frozen nominal range locus within +/-60 seconds. Residuals are still evaluated at the actual observation timestamp.
- Both call clusters are configured: 51 and 29 receive BFOs, each checked at its timestamp; one effective mean-residual likelihood per call avoids treating all bursts as independent. These failed runs never reach the second call.
- Later restart transient messages, anomalous acknowledgement, all 00:19 BTO/BFO, radar-coverage likelihood, WSPR, debris and search coverage are excluded.
- Fuel amount and model uncertainty remain as declared in prior strict-filter work, with no jettison. No fuel parameter is fitted to force the exhaustion time.
- Current AIP/2024 FIR geometry is not independent authentication of the 2014 navigation boundary.

## Numerical corrections made in this continuation

The staged three-route script was unfinished. The continuation makes all priors 1/3, adds an explicit route selector, schedules every selected restart/stable observation exactly once, keeps the fuel anchor at 18:28:05.904 after adding the earlier R600, supports the different route lengths, tracks normalized BTO residuals, corrects the residual-array dimensions, records marginal-likelihood increments over ALL proposals, and writes explicit model/observation selections. Focused tests verify equal priors, observation scheduling/correction, every individual call gate, and ordered waypoint capture for all three leaves.

The main route-before-call criterion is explicit in every manifest. The manifest field named physics_survivors includes the route premise where that premise has been applied. For a pure physics count immediately before the first-call route gate use physics_before_call.

## Reproduce

Use Python 3.12 with numpy, scipy, pandas and matplotlib; package versions are in runtime_versions.json. No network is needed once the bundle is extracted. Work in its root. The binary weather grid is included as data/strict_airway/mh370-era5-grid.bin. The current script only adds non-mutating diagnostics relative to the per-run frozen source copies; random draws and path dynamics are unchanged by those diagnostic additions. Each run directory also contains its original source_run.py and manifest with exact configuration and source hashes.

Commands (outputs go to replay/ to preserve the archived outputs):

```bash
PYTHONPATH=src python -m unittest discover -s tests -p test_route_mixture43.py -v
PYTHONPATH=src python scripts/run_route_mixture43.py --route p627 --output replay/p627_a --initial 250000 --particles 10000 --branching 6 --max-stages 2 --seed 37062731 --initial-proposal data/strict_airway/initial_proposal.json --weather data/strict_airway/mh370-era5-grid.bin
PYTHONPATH=src python scripts/run_route_mixture43.py --route p627 --output replay/p627_b --initial 250000 --particles 15000 --branching 6 --seed 37094341 --weather data/strict_airway/mh370-era5-grid.bin
PYTHONPATH=src python scripts/run_route_mixture43.py --route igogu_south --output replay/igogu_south_a --initial 180000 --particles 15000 --branching 6 --seed 37094321 --initial-proposal data/route_mixture43/igogu_initial_proposal.json --weather data/strict_airway/mh370-era5-grid.bin
PYTHONPATH=src python scripts/run_route_mixture43.py --route igogu_boundary --output replay/igogu_boundary_a --initial 180000 --particles 15000 --branching 6 --seed 37094331 --initial-proposal data/route_mixture43/igogu_initial_proposal.json --weather data/strict_airway/mh370-era5-grid.bin
PYTHONPATH=src python scripts/report_route_mixture43.py
```

A failed selection is recorded as completed=false with a final stage stating zero sampled support; the process exits normally because this is a statistical outcome, not a software exception. Treat log_evidence=null and posterior_route_weight=null as undefined, not as a numeric zero to normalize. Diagnostic prefix candidates in prefix_diagnostic.npz are NOT necessarily accepted trajectories. Read their passed flags. failed_population.npz is NOT a posterior.

## Sources

- Davey et al., Bayesian Methods in the Search for MH370, sections 5.2-5.4 and Table 10.1: https://link.springer.com/content/pdf/10.1007/978-981-10-0379-0.pdf
- ATSB released signalling logs and R600 correction: https://www.atsb.gov.au/sites/default/files/media/5772619/public_mh370-data-communication-logs.pdf
- Current CAAM AIP P627 coordinates (not a claim of historical authentication): https://aip.caam.gov.my/aip/eAIP/2026-08-06-AIRAC/html/eAIP/WM-ENR-3.3-en-MS.html
- Airports Authority of India, Chennai FIR lateral limits, 13 June 2024: https://aim-india.aai.aero/sites/default/files/ais_docs/Chennai%20FIR.pdf

## Continuing research

Resolve early support before deriving any geographical density. Audit the exact nominal-arc crossing interpretation, quantify the effect of the assumed first-call turn deadline separately from the call measurements, and use a validated bridge/importance proposal to explore faster admissible control histories while retaining the declared prior or labelling any changed prior explicitly. Do not infer route impossibility, equal posterior weights, or fuel-window feasibility from these empty final populations.
