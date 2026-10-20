"""Assemble the reviewable scientific account from completed control artifacts.

This module contains reporting prose and artifact selection, not inference.
The flight-assumption report calls it after regenerating the comparison plots.
"""

import datetime as dt
import hashlib
import json
import pathlib
import re
from html import escape


def _html(markdown):
    """Render the limited, internally generated document syntax used below."""
    def inline(text):
        text = escape(text)
        text = re.sub(r"\[([^\]]+)\]\(([^\s]+)\)", r'<a href="\2">\1</a>', text)
        return re.sub(r"`([^`]+)`", r"<code>\1</code>", text)

    parts, paragraph, code = [], [], None
    for line in markdown.splitlines() + [""]:
        if line.startswith("```"):
            if code is None:
                if paragraph:
                    parts.append("<p>" + inline(" ".join(paragraph)) + "</p>")
                    paragraph = []
                code = []
            else:
                parts.append("<pre><code>" + escape("\n".join(code)) + "</code></pre>")
                code = None
        elif code is not None:
            code.append(line)
        elif not line or line.startswith("#"):
            if paragraph:
                parts.append("<p>" + inline(" ".join(paragraph)) + "</p>")
                paragraph = []
            if line.startswith("#"):
                level = len(line) - len(line.lstrip("#"))
                parts.append(f"<h{level}>" + inline(line[level:].strip()) + f"</h{level}>")
        else:
            paragraph.append(line)
    return "".join(parts)


def _page(title, body):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title>
<style>*{{box-sizing:border-box}}body{{font:16px/1.6 system-ui,-apple-system,sans-serif;color:#243746;background:#f2f5f6;margin:0}}main{{max-width:780px;margin:auto;padding:24px 18px 50px;background:white}}h1{{font-size:1.8rem;line-height:1.2}}h2{{font-size:1.25rem;margin-top:28px}}a{{color:#145e87}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;padding:14px;background:#f2f5f6;font-size:.85rem}}img{{width:100%;height:auto}}figure{{margin:24px 0}}figcaption{{font-size:.9rem;color:#526571}}@media print{{body,main{{background:white}}main{{max-width:none}}body{{font:11pt/1.4 Georgia,serif}}nav{{display:none}}figure{{break-inside:avoid}}h2{{break-after:avoid}}a{{color:inherit}}}}</style>
</head><body><main><nav><a href="./">← Comparison plots</a></nav>{body}</main></body></html>'''


def write_results(original, output):
    """Return the short outcome panel and write the detailed review documents."""
    web = output / "web"
    paths = {
        "witnesses": "witness-assumption-audit.json",
        "fuel": "exact-replay-summary.json",
        "cruise": "cruise-exploration/cruise-exploration-summary.json",
        "broad": "command-sampler/residual-drift-eight-settings/numerical-assessment.json",
        "known": "command-sampler/mh371-flexible-control/numerical-assessment.json",
        "simple": "command-sampler/coherent-conditional/numerical-assessment.json",
        "synthetic": "command-sampler/synthetic-coherent-control/numerical-assessment.json",
        "budget": "sampling-compute-ledger.json",
        "terminal": "terminal-final-contact/summary.json",
        "bfo": "final-bfo-comparison/summary.json",
        "bias": "final-bfo-comparison/bias-sensitivity.json",
        "refinement": "terminal-refinement/summary.json",
        "timing": "terminal-timestamp-correction.json",
        "antenna": "antenna-comparison/likelihood-comparison.json",
        "kadri": "kadri-preferred-event/impact-comparison-summary.json",
        "ranges": "terminal-final-contact/impact-ranges.json",
        "validation": "final-workspace-validation.json",
    }
    if (output / 'user-direction.json').exists():
        paths['user_direction'] = 'user-direction.json'
    if any(not (output / path).exists() for path in paths.values()):
        return ""
    data = {name: json.loads((output / path).read_text()) for name, path in paths.items()}
    w, budget, terminal, bfo = [data[k] for k in ["witnesses", "budget", "terminal", "bfo"]]
    north, south = -w["latitude_span_deg"][1], -w["latitude_span_deg"][0]
    bias_min = min(r["minimum_required_bias_sd"] for r in data["bias"]["comparison_counts"]
                   if r["minimum_required_bias_sd"] is not None)
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%d %B %Y, %H:%M UTC")
    by_allowance = {r['maximum_direction_settings']: r['latitude_span_deg']
                    for r in w['steady_cruise_direction_allowance_spans']}
    paragraphs = [
        f"The useful achievement is a repaired and checked flight-to-impact calculation, {w['nominal_examples']} explicit flight examples, and a clearer account of what the evidence can support. The examples reach about {north:.0f}–{south:.0f}°S at 00:11 under the declared flight and fuel models. They do not measure the full possible region or its probability. Broad probability sampling failed independent-run checks, and none of the {bfo['resolved_pair_count']:,} tested final-BFO pairs satisfies both readings under the audited conditions. The defensible material is the conditional sensitivity and validation evidence; a combined crash-location PDF and an optimal search box have not been established.",
        "Finding a few routes that fit is much easier than assigning reliable probabilities to all routes that could fit. The broader samplers repeatedly concentrate on different small parts of that space, so a smooth-looking plot can conceal a failed calculation. Missing aircraft, startup and evidence calibration adds a separate problem that more particles cannot solve. Future work needs a small, explicit scientific question, independent known-answer checks before scaling, one maintained implementation, and a firm stop when extra work does not stabilize the result.",
        f"My recommendation is to stop further production sampling with the present method. The sampling ledger allocates {budget['allocated_seconds']/60:.1f} of its 120-minute limit, including conservative failure/control allowances. A useful paper can now be built around trajectory flexibility, conditional evidence and demonstrated inference limitations; the local working draft below follows that scope. Allow roughly three to five focused author working days for source reconciliation, specialist review and manuscript preparation, with less than an hour of routine figure and control computation once inputs are frozen. A reliable all-evidence impact posterior still has no defensible short completion estimate; it requires a corrected sampling method and better-supported physical/evidence models before another production run is justified.",
    ]
    if 'user_direction' in data:
        paragraphs[2] = data['user_direction']['current_summary']
    results = "# Results and decision\n\nUpdated " + timestamp + "\n\n" + "\n\n".join(paragraphs)
    results += "\n\n[Comparison plots](index.html) · [Working paper draft](paper-draft.html) · [Reproduction and computational record](reproduction.html)\n"
    (web / "results.md").write_text(results)
    (web / "results.html").write_text(_page("MH370 results and decision", _html(results)))

    manuscript = f'''# Trajectory flexibility and uncertainty in MH370 reconstruction

## Working draft: scope and abstract

This is a local manuscript draft for author and scientific review, generated from the completed analysis artifacts. It supports a study of conditional feasibility and numerical validation. It does not present a validated crash-location posterior, a certified outer feasible boundary, or a recommended search area.

Sparse satellite observations admit substantial trajectory flexibility under explicitly declared flight and fuel models. A bounded search retained {w['nominal_examples']} nominal-fuel examples with 00:11 endpoints spanning approximately {north:.0f}–{south:.1f}°S. Allowing more direction changes exposed paths far from the simpler conditional family. Independent probability-sampling runs nevertheless disagreed, including a withheld known-flight control, so their geographical populations were not accepted as posterior estimates. Conditional terminal calculations produced {terminal['impact_examples']:,} impact examples, but none of {bfo['resolved_pair_count']:,} resolved final-checkpoint pairs matched both observed final burst-frequency offsets under the audited startup/error conditions. Antenna, drift, image, acoustic and search evidence were assessed at their supported conditional scope. The findings demonstrate why feasible paths, modelling assumptions, numerical uncertainty and calibrated probabilities must remain distinct.

## 1. Scientific question

The question is how allowing additional manoeuvres changes the set of paths compatible with the declared observations and aircraft approximation, and whether a probability estimator can reliably explore that set. A Bayesian estimate requires both an observation model and a prior on flight histories. There is no assumption-free density over unknown pilot actions. A trajectory that keeps one navigation mode and makes one turn defines a useful conditional hypothesis; its narrow result cannot by itself establish the uncertainty under more flexible flight histories. The distinction follows the model-based Bayesian formulation in [Davey and colleagues, The Bayesian Approach, equations 3.2–3.7](https://link.springer.com/chapter/10.1007/978-981-10-0379-0_3).

Here a history is the candidate aircraft state and control sequence over the modelled flight. The flexibility comparison concerns the post-18:25 portion; the preceding radar-to-18:25 segment remains conditional on its declared starting state and cruise behaviour. Gaps between found endpoints remain unresolved. A span between extreme examples does not show that every intervening location is feasible, and does not exclude separate feasible regions elsewhere.

## 2. Inputs and model choices

The central runner composes typed flight dynamics, SATCOM, fuel and selected evidence modules. Latitude/longitude, WGS84 satellite geometry, units, UTC epoch conventions and environmental input identities are explicit. The flight comparison uses BTO and BFO observations through the nominal 00:11 epoch, with the configured Gaussian observation treatment and a shared Gaussian steady BFO bias. Nine BFO entries use a declared 7 Hz standard deviation, including two channel aggregates. This does not independently calibrate their correlations or all systematic errors.

The declared broad support is Mach 0.30–0.87 and 500–43,000 ft, together with a 330-knot calibrated-airspeed limit, a stall margin, finite bank/roll and speed/climb/descent changes. These are a reproducible performance approximation, not a manufacturer-validated envelope for every manoeuvre. All retained examples query the public thrust approximation beyond the separately audited climb-trajectory coverage; that coverage itself is not engine validation. The thrust multiplier, drag allowance and broad fuel corrections are declared model choices.

Fuel is propagated with a public long-range-cruise proxy and explicit extensions for Mach, altitude, bank and vertical motion. The nominal comparison imposes a calculated 18:28 fuel anchor and equal engine-feed shares. It conditions on exhaustion 30–300 seconds before the R600 log-on, corresponding to approximately 00:14:29–00:18:59. This is an analyst-selected interval, not a measured 00:17:30 uncertainty distribution. {w['nominal_examples']-w['examples_without_source_fuel_domain_exit']} examples leave the source fuel-table domain; the remaining {w['examples_without_source_fuel_domain_exit']} retain the same demonstrated latitude span, while still depending on that model's other assumptions.

The final logged observations are 182 and −2 Hz at 00:19:29.416 and 00:19:37.443 UTC. These are recorded ground-station timestamps used as declared state epochs; their millisecond resolution does not imply millisecond aircraft-state accuracy. The R600 timing observation uses the separately stated 4,600 microsecond correction. The anomalous final R1200 BTO is not used in the terminal comparison. [Inmarsat/DCA communication log, December 2014 update, pages 1 and 41](https://www.atsb.gov.au/sites/default/files/media/5772619/public_mh370-data-communication-logs.pdf).

## 3. Feasibility and coherence comparisons

The bounded optimization varies direction-setting allowances of 1, 2, 4, 8 and 16, with separate speed and altitude allowances of 0, 2, 4 and 8. The expanded initial-cruise check evaluates 800 fixed-setting profiles using Mach 0.50, 0.65, 0.78 and 0.84 and initial altitudes 1,000, 10,000, 20,000, 30,000 and 40,000 ft. This sparse grid does not establish complete support within the continuous bounds. The new check took {data['cruise']['elapsed_s']/60:.1f} minutes and retained 66 examples after finer replay.

Found paths must satisfy the declared performance/fuel conditions and a screening rule: absolute BTO and BFO residuals within three declared standard deviations, a combined standardized residual sum no greater than 38, and the stated bias/fuel conditions. These are screening choices, not a confidence set with calibrated coverage. The probability experiments separately use their declared Gaussian likelihood; they are not obtained by normalizing the accepted-example counts.

With steady cruise targets, the found spans for one, two, four, eight and sixteen direction settings are approximately {-by_allowance[1][1]:.1f}–{-by_allowance[1][0]:.1f}°S, {-by_allowance[2][1]:.1f}–{-by_allowance[2][0]:.1f}°S, {-by_allowance[4][1]:.1f}–{-by_allowance[4][0]:.1f}°S, {-by_allowance[8][1]:.1f}–{-by_allowance[8][0]:.1f}°S and {-by_allowance[16][1]:.1f}–{-by_allowance[16][0]:.1f}°S, respectively. Eight settings expose the much more northerly examples in this probe. Sixteen extend the found southern end modestly while retaining the same northern end. This is a practical sensitivity observation, not proof of an optimal command cap or diminishing uncertainty beyond it.

Direction settings, mode switches, accumulated heading change, path length relative to direct start-to-end distance, total climb/descent and Mach variation provide separate descriptive measures of coherence. A step climb as mass decreases is not automatically treated as equivalent to a course reversal. No weighted coherence score is inferred from the observations. Giving simpler values higher prior probability would be an explicit behavioural hypothesis; deliberate unpredictable action remains within the wider declared family.

## 4. Probability estimation and validation

The isolated command-space experiment uses sequential tempering with a normalized computational guide q, explicit parameter prior p and observation likelihood L. The intermediate unnormalized target is q^(1−β)(pL)^β. Incremental weights divide out the guide, and whole-history Metropolis moves include their full forward/reverse proposal ratio. A deliberately biased guide recovers an independently calculable 0.700 mode probability, and additional continuous/discrete normalization controls pass. The importance-weight principle is described in [Del Moral, Doucet and Jasra (2006), section 2.1, equation 4](https://www.stats.ox.ac.uk/~doucet/delmoral_doucet_jasra_sequentialmontecarlosamplersJRSSB.pdf).

The flight experiments keep fixed labelled command counts as separate families. Their uniform time/target choices and equal navigation-mode probabilities are declared priors, not estimates of pilot behaviour. No posterior probability across different command counts or model families is reported. Passing mathematical controls does not establish exploration of the full constrained flight target.

In the broader MH370 comparison, independent increased-work runs placed approximately 2% and 14% of their numerical populations north of 35°S. Their central locations were similar, but the tail disagreement invalidates a released PDF. A flexible MH371 control also failed: the fraction below 5°N changed from approximately 83% to 4%, and quarter-degree histogram total variation was approximately 0.86. The withheld aircraft positions were reserved for scoring after inference and did not select its proposals.

The one-direction, constant-cruise family repeated more closely, with a maximum latitude empirical-CDF difference of {data['simple']['latitude_empirical_cdf_max_difference']:.2f}. Its central numerical spans remain conditional on that narrow family, fuel and observation model, and its mode weights need stronger validation. A separate noisy synthetic flight had its generating endpoint inside both runs' central 90% coordinate spans and a CDF difference of {data['synthetic']['latitude_empirical_cdf_max_difference']:.2f}. It uses the same forward model for generation and inference and is only one fixture, so it does not validate physical accuracy or repeated-data coverage.

The sampling effort stopped under its two-hour numerical-batch allowance. More particles were not commissioned after these failures. Effective sample size, retained ancestry and smooth plots cannot substitute for distribution agreement and independent recovery checks. Correlated, resampled particles are not treated as independent observations in significance tests.

## 5. Terminal flight and final BFO

An exact changing-flow fuel-boundary defect was repaired by bracketed reintegration. An independently integrated changing-Mach fuel law and integration refinement check its numerical behaviour. All 158 original examples pass replay through the repaired boundary. The approximately 0.0011-second agreement with earlier fine continuation describes numerical integration, not uncertainty in the actual fuel state.

Each nominal source path was continued with its last powered command, then subjected to two separate public attached-flow polar alternatives. Terminal controls hold lift coefficient constant and either maintain bank or bring an initial bank to zero after a sampled interval. The 258 cases per source form a declared Sobol design, not a probability distribution over failures or pilot action. The corrected {terminal['witnesses']*terminal['terminal_cases_per_witness']:,}-attempt batch took {terminal['elapsed_s']:.0f} seconds and produced {terminal['impact_examples']:,} resolved impacts. Weather-domain failures, declared-envelope exits and one unresolved near-vertical trial remain unresolved outcomes.

Representative refinement passed for {data['refinement']['passed']}/{data['refinement']['cases']} selected impacts using 1, 0.5 and 0.25 second steps. Correcting the last logged timestamp changed paired impact locations by at most {data['timing']['maximum_impact_position_change_nm']:.3f} NM and times by at most {data['timing']['maximum_impact_time_change_s']:.3f} seconds. These controls check integration, not post-stall, compressible, breakup or water-entry physics. The public polar's numerical speed bound is not a validated Boeing terminal-flight bound.

The final-BFO comparison keeps the two oscillator offsets linked by a common startup event and tests a separate no-warm-up alternative. It recreates [Holland's 2018 version, sections III–VI](https://arxiv.org/html/1702.02432v3), retaining the paper's differing prose/table error-sign conventions. Historical error extrema and prior log-on envelopes are conditional bounds, not calibrated new-event probability densities. Neither convention admits any of the {bfo['resolved_pair_count']:,} resolved pairs at the carried steady-bias mean. None is admitted within three conditional bias SD; the nearest otherwise eligible case requires approximately {bias_min:.0f} SD. This does not make Gaussian tails zero, and does not exclude the corresponding locations under untested terminal or startup models.

Impact time, position, horizontal/downward velocity and kinetic energy are calculated jointly. Ground-relative entry angle is not aircraft body pitch. Acoustic energy is conditional on an unknown coupling fraction, and an energy budget does not determine a receiver amplitude. The APU preset supplies a separate illustrative power flag; it is not a calibrated restart-time likelihood and is not multiplied into the already fuel-window-conditioned examples.

## 6. Additional evidence and search implications

The conditional antenna comparison uses actual replayed heading/bank with separate compensation and pitch alternatives. Full compensation discriminates little among the found paths, while the no-compensation alternative gives a largest found-example likelihood ratio of approximately {data['antenna'][-1]['largest_likelihood_ratio_among_witnesses']:.0f}:1 at an assumed 3° pitch. The reconstruction and shared channel/installation calibration remain unresolved. No antenna-updated geographic PDF is produced from unweighted witnesses.

Existing drift calculations are retained as separate source-prior-removed sensitivity families. GLORYS12 currents and WAVERYS wave/Stokes inputs are a supported starting point for further transport work, but rare-event sampling, coast treatment, recovery/discovery and object response still prevent a validated joint flight–drift update. The Pléiades comparison is conditional on object identity and has a limited computed spatial strip; outside that strip is unsupported, not zero likelihood. The original report itself does not identify the objects as MH370 debris. [Griffin and Oke (2017), Ocean Surface Drift, Part III, executive summary](https://www.atsb.gov.au/sites/default/files/2024-02/mh370_csiro-ocean-drift-iiil.pdf).

Kadri's preferred table entry is the 00:54:30 arrival at bearing 306.18°, distinct from the other reported feature. Conditional timing/bearing/R600-BTO selection retained {data['kadri']['conditional_counts_by_bearing_half_width_deg']['0.5']} impacts from {data['kadri']['selected_source_paths']} source paths, but none passes the joint final-BFO check and no common steady-bias shift rescues their frequency change. These are partial-condition examples, not an MH370 signal association or samples from an event-conditioned prior. The source's printed velocity/range/time illustration also requires reconciliation. [Kadri (2024), pages 13–14 and Table 1](https://www.nature.com/articles/s41598-024-60529-1).

Godfrey and colleagues' 2023 tabulated route was assessed as a proposed hypothesis. Some nominal legs and BTO comparisons require coordinate/time/performance reconciliation; the limited audit is not a proof that every nearby continuous route is impossible. Acoustic arrival windows from its position/time illustrations overlap already processed publication traces, which cannot establish event identity or calibrated non-detection. The public WSPR work has not supplied an admitted geographic likelihood. [Godfrey, Coetzee and Maskell (2023), pages 48–53](https://pedrocarvalho.es/docs/WSPR%20report.pdf).

Negative search evidence requires both attributed coverage and the probability of finding the target if it lies there. Historical outlines, vessel tracks and catalogue extents cannot simply delete probability. The [ATSB 2022 data review](https://www.atsb.gov.au/mh370-data-review) concerns a particular reviewed region; its gap/quality findings are not a global detection map. A 7,500 km² planning budget has no defensible optimal placement without a stable impact distribution and credible detection information. A broad feasible span alone also does not show that searching is futile.

## 7. Supported conclusions and remaining work

The results support a conditional account of how manoeuvre freedom changes demonstrated flight solutions, and a reproducible warning against interpreting unstable numerical populations as physical uncertainty. They do not establish the true outer extent x of all possible trajectories, a calibrated coherent-family width y, a model-averaged impact density, or a search-location ranking. The tested terminal family fails additional final satellite conditions. Further production sampling with the same failed method is not recommended.

Before a localization paper could be supported, a corrected method must demonstrate stable whole-distribution recovery on appropriate independent controls, the aircraft/fuel/startup conditions need better support, and later evidence must have adequate spatial support and calibration. Those are scientific development tasks with no justified short completion estimate. A methods and conditional-evidence paper can be completed from the retained findings after author and specialist review, source reconciliation, and preparation of a versioned archival package.

## Data, code and computation

This draft, the plots and numeric summaries are generated from saved artifacts. [Reproduction instructions](reproduction.html) distinguish rendering from optional numerical batches. Seeds, model choices, input identities and runtimes are retained. The workspace has no Git metadata, so recorded source/executable hashes identify runs; historical experimental code revisions are not all available as checkouts. Figures and numerical-diagnostic summaries can be regenerated from retained artifacts. A publication deposit still needs the exact permitted inputs, source snapshots and retrieval instructions rather than private workspace paths. No external manuscript was submitted and no geographic posterior was released.
'''
    if 'user_direction' in data and not data['user_direction']['alternative_paper_accepted']:
        manuscript=manuscript.replace('## Working draft: scope and abstract',
            '## Unaccepted alternative scope\n\nPete has not accepted this alternative paper. The project objective remains a reliable broad trajectory estimator and the originally requested uncertainty analysis. This document preserves the earlier draft for reference.\n\n## Working draft: scope and abstract',1)
    (web / "paper-draft.md").write_text(manuscript)
    figures = [
        ("support-comparison.svg", "Found 00:11 endpoints by manoeuvre allowance. Counts are unweighted examples; gaps are unresolved."),
        ("coherence-comparison.svg", "Descriptive route detour and direction settings. No pilot-behaviour probabilities are assigned."),
        ("known-flight-disagreement.svg", "Independent numerical MH371 populations disagree. The later known position was withheld from proposal construction."),
        ("final-bfo-pairs.svg", "Calculated final-frequency pairs and linked startup/error conditions. These points have an illustrative R600 BTO band, not geographic weights."),
        ("search-context.svg", "Attributed coverage context. The plotted hypotheses are not accepted impact solutions or a ranked search distribution."),
    ]
    figure_html = "<h2>Figures for review</h2>" + "".join(
        f'<figure><img src="{name}" alt="{escape(caption)}" loading="lazy"><figcaption>Figure {i}. {escape(caption)}</figcaption></figure>'
        for i, (name, caption) in enumerate(figures, 1)
    )
    (web / "paper-draft.html").write_text(_page("MH370 working paper draft", _html(manuscript) + figure_html))

    reproduction = f'''# Reproduction and computational record

## Render the retained analysis

Run from the project root with Python, NumPy, SciPy and Matplotlib available. This command regenerates the comparison plots, the results page and working draft from retained artifacts; it does not run a flight sampler:

```bash
python crates/reporting/scripts/flight_assumption_report.py \\
  /path/to/flight-assumption-preanalysis \\
  --progress-from /path/to/overnight-analysis
```

The current retained directories are `{original}` and `{output}`. Run manifests record input identities. The plot/draft source is in `crates/reporting/scripts/flight_assumption_report.py` and `flight_analysis_results.py`. Machine-readable manuscript inputs and their hashes are in [document-inputs.json](document-inputs.json). This report reproduces saved results; it does not imply that every historical experimental revision remains available as a checkout.

An [overnight source snapshot](source-snapshot.tar.gz) preserves the product code, configurations, compact inputs and the independent source comparisons at the close of the overnight attempt. Its [inventory](source-snapshot.json) records individual hashes, the runner binary identity and the large environmental inputs retained separately. It also preserves the final rejected sampling prototype as an external research artifact; that code is not integrated into the product. Later presentation and user-direction updates are recorded by the current document hashes. This snapshot is not a complete data deposit and does not reconstruct missing earlier experimental source revisions.

## Measured computation and the stopping decision

The sampling ledger allocates {budget['allocated_seconds']/60:.1f} minutes out of 120, including conservative allowances for a failed deadline run and smaller mathematical/proposal controls. This is the sum of numerical-batch wall times, not total author/agent elapsed time, CPU-hours, or a credit bill. Worker counts are in individual manifests. The broad validation failure stopped further flight sampling.

The additional cruise grid took {data['cruise']['elapsed_s']:.1f} seconds. The corrected terminal batch took {terminal['elapsed_s']:.1f} seconds for {terminal['witnesses']*terminal['terminal_cases_per_witness']:,} attempts. The independent final-BFO comparison took {bfo['elapsed_s']:.1f} seconds; its common-bias sensitivity took {data['bias']['elapsed_s']:.1f} seconds. Seventeen representative terminal refinements took {data['refinement']['elapsed_s']:.1f} seconds. These small forward calculations do not resolve the separate probability-sampling problem. No new multi-year drift ensemble was run.

The final locked, offline Rust workspace check passed {data['validation']['tests_passed']} tests in {data['validation']['elapsed_s']:.1f} seconds, with {data['validation']['tests_ignored']} explicitly ignored tests left outside the ordinary check. Maximum recorded child-process RSS was approximately {data['validation']['maximum_child_rss_kib']/1024:.0f} MiB; it is not a concurrent-process total. Rust formatting checks also passed. These software checks do not establish physical calibration or posterior validity.

## Optional focused forward controls

Build the canonical runner before replays. Numerical control output directories must be empty. The following command recreates the synthetic observation fixture; the generating truth is stored separately and the command performs no inference:

```bash
cargo build --release --locked --offline -p mh370-runner -j 2
python crates/controls/flight_evidence.py synthetic-fixture \\
  --seed 37090840 --output /path/to/empty-synthetic-fixture
```

Add `--compare-fixture /path/to/synthetic-command-control` to compare observation bytes and withheld truth with the saved fixture. A fresh reproduction matched both exactly. Source-row metadata in its CSV identifies the observation template; the generated BTO/BFO values are synthetic.

The selected terminal experiment, with the logged fractional-second checkpoints, is reproducible as:

```bash
python crates/controls/flight_evidence.py terminal \\
  --samples 64 --workers 2 --seed 37090830 \\
  --final-contact-bto --turn-capture --acoustic-arrivals \\
  --witnesses /path/to/flight-assumption-preanalysis /path/to/cruise-exploration \\
  --output /path/to/empty-terminal-output
```

Refinement uses `terminal-refinement --refine-from /path/to/terminal-output`. Selected path plotting uses `terminal-traces --terminal-from /path/to/terminal-output --selected-examples /path/to/selection.json`. Both also require an empty `--output` directory. The source-specific Kadri, Holland and Godfrey READMEs provide their independent comparison commands and located citations. These commands are documented for reproduction; the completed experiments need not be repeated to read the report.

## Numerical and scientific limits

The source-corrected final timestamp replay keeps the physical cases identical and records its comparison in `terminal-timestamp-correction.json`. The old rounded-checkpoint artifacts are retained as a focused numerical timing control. They are not another accepted physical model or an additional ensemble to pool.

Software checks, a model-consistent synthetic recovery and close integration refinement do not establish calibrated posterior coverage, complete feasible support, a manufacturer-validated terminal envelope, or calibrated hydrophone/search detection. The three-to-five-working-day manuscript allowance is for author review and writing on the supported methods scope. It is not an estimate for solving those missing scientific problems.
'''
    (web / "reproduction.md").write_text(reproduction)
    (web / "reproduction.html").write_text(_page("MH370 reproduction record", _html(reproduction)))
    manifest = {
        "updated_utc": timestamp,
        "status": "conditional evidence and numerical-validation draft; no localization posterior",
        "source_inputs": {name: {"path": str(output / path), "sha256": hashlib.sha256((output / path).read_bytes()).hexdigest()}
                          for name, path in paths.items()},
        "document_source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        "outputs": {name: hashlib.sha256((web / name).read_bytes()).hexdigest()
                    for name in ["results.md", "results.html", "paper-draft.md", "paper-draft.html", "reproduction.md", "reproduction.html"]},
    }
    (web / "document-inputs.json").write_text(json.dumps(manifest, indent=2))
    return ('<section id="results-and-decision"><h2>Results and decision</h2>'
            + "".join("<p>" + escape(p) + "</p>" for p in paragraphs)
            + '<p><a href="paper-draft.html">Read the working paper draft</a> · <a href="reproduction.html">Reproduction and compute record</a></p></section>')
