# MH370 engineering contract

One product: a reproducible Bayesian estimate of the MH370 position at the final
SATCOM arc (the **core**), plus optional **hypotheses** that may change it. Each
hypothesis is a self-contained module. Keep the whole inference path small
enough to read in an afternoon.

## Layout

```text
crates/geo         shared WGS-84 geometry and units
crates/satcom      BTO/BFO measurement model, observation loading
crates/flight      cruise + manoeuvre dynamics, ERA5/IGRF environment
crates/hypothesis  the fixed hook API between core and hypotheses
crates/mh370       runner: config, filter, hypotheses, artifacts, local app (ui/)
hypotheses/<name>/ one directory per hypothesis (discovered automatically)
config/            base config (davey2016.toml), smoke override, sensitivity/ overrides
report/            build_report.py: run artifacts -> PDF
data/              measured inputs (README lists provenance)
.sources/          papers, digitised reference curves, input-preparation scripts
.archive/          frozen previous codebase: read-only reference, never used
```

The core spokes (`satcom`, `flight`) depend only on `geo`. Hypotheses depend
only on `hypothesis`, `geo`, `serde` and `toml`. They never depend on core
crates or on each other, and the build fails if a hypothesis references
another. The runner composes everything and holds no scientific equations.

## Two kinds of work

### Hypothesis work (scoped)

If you are asked to work on hypothesis `<name>`:

- Work on branch `hypothesis/<name>`. Create the directory with
  `make new-hypothesis H=<name>` if it does not exist.
- **Touch only `hypotheses/<name>/`.** Its `lib.rs` (plus submodules), its
  `hypothesis.toml`, its `run.toml`, its tests and any small data files.
  Nothing else: no core crates, no configs, no report, no README or
  status.md. `make scope H=<name>` must pass before you hand back.
- A hypothesis acts only through the hooks in `crates/hypothesis`:
  - in the filter: adjust the prior, request extra epochs, add epoch
    log-likelihood, add final-state log-likelihood;
  - after it: impact log-likelihood and named predictions per impact sample
    (impact modules), or the end-of-flight model (the terminal module);
  - declarations: the observations it uses, each at most once, and any
    discrete alternatives.

  If you need anything else (a new hook, a new state field, a new
  dependency), write it in `core_requests` in `hypothesis.toml` and stop. Do
  not work around the API.
- Iterate with `make smoke H=<name>` (about a minute; code paths only). Judge
  with `make hypothesis H=<name>`, which runs at full scale and writes
  `runs/<name>/report.pdf` comparing against the base estimate.
- Record the outcome in `hypothesis.toml`: set `status` and a one-line
  `summary` quoting the numbers from the report. That file is the
  hypothesis's only status record.
- The `lib.rs` doc comment states the assumption, its source, and how it
  enters the estimate. Include at least one test against an independently
  computed value.

### Core work

Everything outside `hypotheses/<name>/` is core.

- Core changes that are not meant to change the estimate must pass
  `make regress`: the base output must be byte-identical to `main`.
- An intended change to the estimate needs its own commit, a rerun of
  `make report`, and an update to `status.md`.
- Changing the hook API (`crates/hypothesis`) is a core change. Keep it
  backward-compatible with existing hypotheses, or update them in the same
  commit.
- Sensitivities to core inputs (e.g. the weather field) are core-owned overrides
  in `config/sensitivity/`, run with `make sensitivity S=<name>`. The report
  labels them; they never replace the base estimate.
- Combining hypotheses happens only in core-owned configs. It is reported
  as an explicit alternative, never as the base estimate.

## Rules for everyone

- **One implementation.** Change it in place. No numbered copies, "final" or
  "withdrawn" variants, derivation folders or parallel pipelines. A rejected
  hypothesis keeps its directory with `status = "not-supported"`. Its code is
  the record of what was tried.
- **Exactly three markdown files: README.md, this file, and status.md.**
  status.md is the one canonical place for the core's current state, open
  problems and next steps. The core owner updates it in place and keeps it
  short.
- **Absolutely no other .md "reports".** No findings, summaries, ledgers,
  audits, handoffs, plans, reviews or per-directory READMEs, anywhere in the
  tree. Results belong in the generated PDFs; hypothesis outcomes belong in
  `hypothesis.toml`; explanations belong in code comments or README.md. If
  you are about to create a new .md file, stop.
- **Generated output is never committed.** Runs go to `runs/` (ignored).
  Reports are rebuilt from runs by `report/build_report.py`. Never hand-edit
  numbers in a report.
- **Estimates must be seed-stable.** A result whose replicates disagree is
  reported as unconverged, not tuned until it looks right. Smoke runs are
  never evidence.
- **Tests are few and meaningful:** independent fixtures, limiting cases,
  distribution checks. `cargo test --release` must stay under a minute.
- **Published work is input, not truth.** Record departures from a paper and
  why: README for the core, the `lib.rs` doc comment for a hypothesis.
- **`.archive/` is the frozen previous codebase.** Read it for reference
  only. Never import from it, run it, or add to it.

Before adding a file, dependency, abstraction or test, ask whether it makes the
estimate more correct, faster to iterate, easier to inspect, or easier to
reproduce. If not, don't add it.
