# Open questions and prioritized next work

## Priority 1 — Complete the migration and reproducibility baseline

- Obtain the verbatim MH370 conversation export and convert only the relevant
  chats to Markdown/JSON.
- Locate or reconstruct `run_pleiades_bran_fl400_expanded.py`.
- Locate the refined-v3 particle checkpoint, if it still exists.
- Replace hard-coded workspace paths with repository-relative configuration.
- Add smoke tests and a clean-clone reproduction report.

## Priority 2 — Received-power model

- Formalize and document the gain/power-precompensation hypothesis test using
  MH371 heading changes and known-position MH370 phases.
- Confirm terminal-specific HGA hardware/control behavior from primary source
  documentation.
- Complete the publication graphics for side-mounted 45° conformal arrays and
  the measured three-dimensional gain surface.
- Quantify robustness to gain-curve digitization, side selection, attitude,
  fading and possible transmit-power state changes.

## Priority 3 — Integrated estimator refinements through 00:11

- Recover or regenerate the full particle lineage so correlations among
  location, Mach, heading, gain, BFO bias and fuel are preserved.
- Couple the fuel workbook/performance model directly rather than through static
  interpolated tables.
- Replace digitized/summary weather with exact ACCESS-G or equivalent fields
  where available.
- Test alternative priors without constraining control, altitude or terminal
  intent.

## Priority 4 — Full Pleiades/BRAN analysis

- Recover full BRAN2015/2016 trajectory fields or archived MATLAB outputs.
- Run a two-dimensional seed grid extending across the maximum feasible
  controlled-glide area, without the historical CSIRO search-area mask.
- Build a reproducible catalogue of the approximately 70 identified objects,
  including dimensions, spectra/appearance, uncertainty and negative controls.
- Compare candidate dimensions and appearance with confirmed/likely recovered
  MH370 debris, including the flaperon, without overclaiming resolution.

## Priority 5 — End of flight

- Perform the separate deep dive on Holland (2017), identifying evidence,
  assumptions and counterarguments.
- Build a dedicated 00:19 likelihood rather than treating the exchange as a
  simple extension of stage one.
- Model controlled and uncontrolled terminal trajectories, flameout sequence,
  glide, descent, ditching and impact dynamics.
- Recover flight-level wind fields for the relevant terminal region and time.

## Priority 6 — Search non-detection

- Convert ATSB and Ocean Infinity campaigns into uncertain detection fields.
- Obtain exact AUV swaths if released; otherwise marginalize plausible coverage
  subject to published totals and ship-track proxies.
- Update the 2026–2027 Ocean Infinity remaining-search geometry only when new
  official evidence becomes available.
- Overlay unconditional and Pleiades-conditional PDFs with probabilistically
  downweighted search coverage.

## Priority 7 — Manuscript

- Complete the received-power/antenna-gain section.
- Integrate the end-of-flight evidence note without allowing it to dictate the
  stage-one posterior.
- Reproduce or redraw dissertation forest plots with explicit provenance.
- Maintain the 7,200–7,600-word budget and general-reader/statistical-expert
  dual accessibility.

