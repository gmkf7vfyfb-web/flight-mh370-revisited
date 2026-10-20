# Independent audit of the fuel model: brief

Modular Architecture, 9 October 2026, at Pete Large's request. The brief is written to be
self-contained. The same text is given to two auditors who work independently, for model diversity:
an architecture-run sub-agent, and a separate agent that Pete runs himself.

## Why this audit

The project reproduces and extends Davey et al., *Bayesian Methods in the Search for MH370* (Springer
2016, CC BY-NC 4.0). Davey's filter assumes infinite fuel (book p. 60, assumption 4) and applies fuel
only afterwards, as a constraint on trajectories. This project puts a fuel model **inside** the
particle filter, as an extension. A smoke test shows that **the fuel model is what moves the
posterior north**. Before any result built on it goes into a paper, the model has to be shown
rigorous, defensible and free of bugs.

## What to audit

**1. The code, line by line.** It is on GitHub `gmkf7vfyfb-web/flight-mh370-revisited`, branch
`claude-science-sep29`, folder `Claude Science Project Sep 29/engine/`:
- `crates/flight/src/fuel.rs`: fuel flow, interpolation, and table handling;
- the fuel-related parts of `crates/flight/src/lib.rs`: burn integration, the fuel factor, and the
  exhaustion prediction;
- the fuel-related parts of `crates/mh370/src/filter.rs`: how fuel enters the likelihood or weights, and
  the exhaustion time;
- `crates/mh370/src/terminal.rs` (`takeover`, `FuelFlow`), and `crates/hypothesis/src/lib.rs` where it
  references fuel;
- `.sources/fuel-performance/extract.py` and `validate.py`;
- the fuel settings in `config/davey2016.toml`, `config/sensitivity/no-exhaustion-prior.toml` and
  `config/sensitivity/stage2-fuel*.toml`.

**2. Check for at least:**
- units (lb against kg, per engine against total, per hour against per second);
- interpolation at the table edges, and extrapolation outside them;
- the handling of `filler`, `derived` and `vmo-limit` cells (the docstring in `extract.py` says consumers
  must drop `filler`);
- the weight update per step;
- the temperature correction (±3% per 10 °C TAT);
- Mach against KIAS against TAS conversions;
- climbs and descents;
- the starting fuel and weight at 17:06:43 and 18:01:49;
- the fuel factor's prior and how it is updated;
- the exhaustion-time computation and its time resolution;
- the "no-exhaustion-prior" overlay;
- float32 storage;
- any place where a test asserts the wrong thing;
- any double counting of fuel information between the filter and the end-of-flight stage.

**3. Reproduce the numbers independently:**
- burn rates at representative states against the source tables;
- Boeing's SIR Appendix 1.6E Table 3: five segments from the last ACARS report, 96,562.5 lb at 17:06:43,
  gross weight 480,600 lb;
- Boeing's Table 4: endurance from arc 1 for 22 flight-level and speed pairs;
- the 00:17:30 fuel-exhaustion timing;
- the burn rates of the posterior trajectories. The reference run's mean burn is recorded in the
  project's memory as 36,160 kg against 36,609 kg available; check that.

**4. Cross-check against every available performance source:**
- the Malaysian SIR (Safety Investigation Report) fuel figures;
- Boeing's analyses in SIR Appendix 1.6E;
- the ATSB reports;
- Bobby Ulich's public fuel model (v5.6) and its documentation;
- the prior project work in `Archive ISO Pre Sept 28/codebases/v01-share/v01/workspace/.sources/ulich-mh370-fuel-performance/`;
- the ten Boeing engineering-simulator runs (end of flight's calibration targets), where they bear on
  burn or endurance.

**5. Provenance and licence, which is critical for publication.** `extract.py` states that the tables
come from Ulich's public workbook, and that some cells are transcribed from Boeing Flight Planning and
Performance Manuals "from a confidential source". The project's standing rule is never to cite an
unauthorised copy of a copyrighted manual. Report:
- which cells the filter actually uses, by source class;
- whether the result changes if `fppm-confidential` cells are excluded;
- what a publishable, defensible source for each used value would be.

## Rules for the auditor

- **Independence.** Form your findings from the code and the primary sources first. Only then read the
  project's own notes on the fuel model (`results/`, `coordination/`), and say where you agree and
  disagree.
- **Read-only.** Change no code and no config. Findings go to Pete and to core; core owns the fix.
- **Compute.** Light only: unit-level Python reproductions, small table queries. Take no heavy lock and
  run no filter.
- **Citations.** Printed page numbers from running headers or footers, with the document and its
  version. Grade each source as primary or secondary.
- **Data handling.** `data/fuel-tables.json` is local and must not be redistributed. Do not upload it
  to any third-party service. An external auditor without it should use Ulich's public workbook
  (public Google Drive copy, link in `extract.py`) and say so.

## Deliverable

A report, `results/fuel-model-audit-<auditor>.md`. The architecture sub-agent uses `<auditor>` =
`architecture`; the external agent chooses its own name. It contains:
1. A findings table: id, severity (critical / major / minor / note), file:line, what is wrong, the
   evidence, and the suggested fix.
2. The reproduction tables (item 3), showing model against source, with the differences.
3. The provenance table (item 5).
4. **A verdict on whether "the fuel model moves the posterior north" is a property of correct physics
   or of a defect,** with the evidence for it.
5. What you did not check, and why.

Every chart carries a footnote stating the run, the parameters and the assumptions it uses.
