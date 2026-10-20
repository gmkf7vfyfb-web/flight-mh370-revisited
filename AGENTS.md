# Project instructions for AI agents and collaborators

These instructions are binding across the repository. They preserve the
scientific framing agreed during development and prevent accidental conversion
of hypotheses or diagnostic assumptions into facts.

## Scientific scope

1. The primary estimator begins from the post-radar state around 18:11 UTC and
   uses observations through 00:11 UTC.
2. Do **not** place the 00:19 observations into the airborne-through-00:11
   likelihood. Analyse 00:19 and later evidence in a separately labelled
   end-of-flight stage.
3. Keep three states distinct:
   - aircraft position/state at 00:11;
   - aircraft state associated with the 00:19 exchange;
   - eventual surface-impact position.
4. Do **not** assume that the aircraft was uncontrolled at any time. Priors and
   sensitivity cases must remain open to human control, early descent,
   re-climb, powered descent, controlled glide and attempted ditching.
5. Do **not** constrain the impact point to a narrow strip around the seventh
   arc. Controlled glide or terminal manoeuvring may place impact 100 NM or
   more from the arc where performance and wind feasibility allow it.
6. Do not force high-altitude/high-speed flight. Low-altitude solutions must be
   tested against speed-over-ground, fuel, BTO/BFO and trajectory feasibility,
   rather than excluded by assumption.

## Evidence treatment

1. BTO, BFO and received power are model-mediated observables, not direct
   positions.
2. Estimate fast BFO random noise separately from slow or intermittent bias.
   The current pooled within-cluster successive-difference estimate is
   approximately 0.995 Hz (95% interval about 0.859–1.183 Hz).
3. Treat received-power precompensation as an empirical hypothesis. Preserve
   both the estimated/marginalized compensation model and the no-precompensation
   sensitivity; do not silently select either.
4. Drift evidence is marginalized/model-averaged. Do not convert a drift study
   into a hard impact mask.
5. Pleiades imagery is conditional evidence. Report results as “objects assumed
   to be MH370 debris”; do not assign a probability to that premise without a
   defensible base-rate model.
6. Search non-detection is probabilistic. Bathymetric mapping alone has zero
   aircraft-debris-field detection probability. High-resolution sonar coverage
   has uncertain, non-binary detection probability and uncertain footprints.
7. Do not describe ship/AIS tracks as searched seabed. They are proxies for a
   latent AUV coverage field unless exact AUV swaths are published.

## Provenance labels

Every substantive statement, figure and numerical result must be labelled or
clearly classifiable as one of:

- **Established fact** — supported directly by authoritative primary evidence.
- **Published finding** — a result reported by an identified external study.
- **Reproduced result** — regenerated from available source data/code.
- **Reconstructed analysis** — rebuilt from summaries, digitized figures or
  incomplete upstream states.
- **New analysis** — produced within this project.
- **Diagnostic/sensitivity** — tests implications without claiming a full
  posterior rerun.

Never present a reconstruction or diagnostic as an exact reproduction.

## Reproducibility requirements

For every new computational result:

1. Preserve raw inputs unchanged.
2. Record source paths, URLs and provenance grade.
3. Record software versions, random seed, sample counts, priors, likelihoods,
   coordinate convention and observation cutoff in a run manifest.
4. Save machine-readable summaries and posterior samples where practical.
5. Separate numerical computation from plotting.
6. Add at least one smoke test or reference-output check.
7. Do not overwrite a released result; create a new versioned output folder.

Coordinates use signed decimal degrees internally (south and west negative).
Human-facing southern latitudes should be unambiguous, for example 37.3°S.

## Manuscript conventions

The target is a generally accessible *Journal of Navigation* paper that remains
rigorous for statistical-estimation specialists. Preserve the distinction
between unconditional results and conditional scenarios. Avoid implying a
prespecified end-of-flight scenario. Target approximately 7,200–7,600 words
and 18–20 submission pages unless the journal’s current guidance changes.

## Safety, privacy and publication

- Keep the repository private until source-document rights, personal data and
  unpublished analysis have been reviewed.
- Never commit credentials, tokens, cookies or signed download URLs.
- Do not redistribute restricted Boeing/Inmarsat/SITA material publicly merely
  because it is present in the private research archive.

