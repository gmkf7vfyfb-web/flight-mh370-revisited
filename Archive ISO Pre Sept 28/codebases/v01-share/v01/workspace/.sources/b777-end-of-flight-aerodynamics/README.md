# B777 end-of-flight aerodynamic and control model audit

## Result

**Blocked — `NO_PUBLIC_REDISTRIBUTABLE_MODEL_SPANS_REQUIRED_ENVELOPE`.**

No located public, legally redistributable candidate supplies traceable B777-200ER / RB211 Trent 892B-17 lift, drag, six-axis moments, control effectiveness, running and windmilling-engine forces, and degraded control-mode behavior from cruise through post-flameout transonic/high-angle-of-attack flight.

The machine contract therefore has:

- `admitted_candidate_family: null`
- `implementation_ready_conditional_aerodynamic_parameters: null`
- no prior, parameter, or model tuned to the 00:19 BFO or an assumed impact

The exact decision and release condition are in [`candidate-families.json`](candidate-families.json). The generated comparison is [`outputs/comparison.html`](outputs/comparison.html), and all calculated evidence is in [`outputs/results.json`](outputs/results.json).

The admission result remains unchanged: no family is a calibrated B777 terminal model.

**v0.1 conditional release use (2026-08-31):** Pete Large subsequently directed the
product to implement the best currently available approximation as a clearly labelled,
improvable release milestone. The product therefore exposes the already audited OpenAP
v2.6.0 and published-2020 B772 parabolic polars as *separate attached-flow conditional
proxies*. They carry no family probability, are not pooled, do not supply stall/post-stall
behavior, and are not described as admitted B777 terminal aerodynamics. The Boeing/ATSB
trajectory exports remain external behavioral comparators. This operational exception does
not change `NO_PUBLIC_REDISTRIBUTABLE_MODEL_SPANS_REQUIRED_ENVELOPE` or make the null
`admitted_candidate_family` non-null.

## Candidate disposition

| Family | Publicly available material | Licence / redistribution screen | Exact status |
|---|---|---|---|
| OpenAP B772 | Clean point-mass polar, performance thrust equations, climb-derived B772 estimates | v2.6.0 `4fb21d6…`, LGPL-3.0; dataset v2 CC BY 4.0 | `reference_only_not_admitted` |
| Community FlightGear/YASim 777 | Geometry, solver targets, generic stall knobs, jet scalars, control mappings | Modern fork GPL-2.0; historical FGMEMBERS file has unresolved licence | `rejected_identity_and_validation` |
| Official JSBSim | Six-degree-of-freedom framework and 62 bundled aircraft families | v1.3.1 `3b25f25…`, LGPL-2.1 | `not_a_candidate` — no 777/B772/Trent 892 model |
| ATSB/Boeing cases | Ten one-second X/Y/altitude engineering-simulator exports | Publicly shared by Iannello with ATSB permission; no general downstream archive licence located | `validation_only_not_implementable` |
| NASA GTM/TCM | Generic extended-envelope forces/moments and representative actuators | US Government public-use report; open-source Simulink release by request | `excluded_no_defensible_transfer` |
| ICAO Trent 892 row | Rated static thrust and four LTO fuel-flow points | Public link; no permissive data licence relied upon | `identity_reference_only` |
| EUROCONTROL BADA | Licensed performance model family | Reviewed, restricted, non-transferable licence required | `excluded_legal_and_scope` |

“Community”, “generic”, and “simulator framework” are used deliberately. None is described as aircraft-validated.

## Findings that control the decision

### OpenAP is useful attached-flow performance data, not an end-of-flight model

The pinned B772 definition lists GE90-77B, PW4077, Trent 877, GE90-94B, PW4090, and Trent 895. Trent 892 is absent. Executing `Thrust("B772", "Trent 892")` raises the upstream aircraft/engine mismatch; setting `force_engine=True` bypasses that guard but creates no validation.

The published 2020 B772 polar is `cd0=0.034`, `k=0.051`, `e=0.723`. OpenAP v2.6.0 instead carries `0.024`, `0.047`, `0.783`; commit `2ca2a05…` made that change without a B772 validation artifact in the commit. The paper's aerodynamic validation example is a B747, not B772.

The independently inspected B772 dataset contains 100 coefficient rows, 97 finite fits, and 101 climb-trajectory files (54,487 rows). Its observed envelope is:

- altitude 125–24,975 ft
- Mach 0.100–0.768 where present
- true airspeed 44–462 kt where present
- vertical rate −896 to 4,608 ft/min

The finite means are `cd0=0.0341265`, `k=0.0508020`, `e=0.723295`, and fitted mass `208,525.6 kg`. `cd0` and `k` correlate at `0.999998`; these are coupled estimation outputs, not independent priors. There is no AoA, moment, control, flameout, or windmilling state.

An actual pinned-source runtime probe at FL350/M0.84 and the audit's neutral dataset-mean mass returned 159.900 kN clean drag. The accepted Trent 895 pairing returned 172.760 kN modeled maximum cruise thrust. Trent 892 was rejected unless forced; the forced result was 172.111 kN. OpenAP modeled descent idle was about 10.1 kN total because its implementation defines idle as 7% of available thrust. None of those values is a flameout/windmilling model.

### The community YASim files fail identity before fidelity is considered

The historical file activates two 93,400-lb jets described in its header as Trent 895. It never identifies Trent 892, and no root or file licence was located at its pinned commit. The modern GPL file activates two GE90-115B jets at 115,540 lb despite its 777-200ER label. Both use generic YASim geometry/stall parameters and control mappings without a located primary B777 calibration or uncertainty report.

The official JSBSim v1.3.1 tar was inventoried independently. It includes examples such as `787-8` and `B747` but has no path matching 777, B772, or Trent 892. JSBSim is a suitable framework; that does not make it a candidate B777 dataset.

### The Boeing exports are the strongest public B777 behavior check, but not an implementation

ATSB reports that Boeing's engineering simulator used the same aerodynamic model as a Level D simulator, but also warns that some motion left the simulation database. Iannello reports that legal restrictions prevented release of per-case details. The public archive contains only time, X, Y, and integer-foot altitude; its final records are 473–1,131 ft above sea level.

One-second backward differences independently reproduce the published high-rate partition: cases **3, 4, 5, 6, and 10** exceed both 15,000 ft/min downward rate and 0.67 g downward acceleration. The chord from first 15,000-ft/min crossing to the last exported row is **4.707–7.923 NM**, reproducing the published 4.7–7.9 NM range without using the 00:19 observations as a tuning target.

The five-case classification is stable after resampling at 2, 4, and 8 seconds. At 16 seconds case 5 falls below the acceleration threshold, and at 32 seconds only case 3 remains. Peak acceleration is therefore derivative-window dependent; the one-second result is a reproduction of the published export, not a robust state estimate.

### A generic high-AoA model cannot be silently transferred

NASA's Transport Class Model is the strongest located public generic alternative: its tables extend over alpha −5° to 85° and beta ±45°, and it includes representative hydraulic actuator limits. It is explicitly a generic mid-weight twin with generic 40,000-lbf engines. No primary source provides a B777 similarity transform or uncertainty model. Importing its tables would invent a cross-aircraft prior.

The ICAO 03/2026 database row `2RR027` confirms a generic Trent 892 rated static thrust of 411.48 kN and LTO fuel flows of 3.91/3.10/1.00/0.30 kg/s. Those emissions-test points do not supply altitude/Mach thrust, spool-down, windmilling drag, or installed 892B-17 behavior.

## Independent numerical checks

These checks diagnose the public equations; they do not elevate either polar to an admitted model.

At FL350/M0.84 ISA using the mean fitted mass solely as a numerical fixture:

| Polar | Required thrust | L/D at fixture | Analytic maximum L/D | Best-glide Mach | Best-glide descent rate |
|---|---:|---:|---:|---:|---:|
| OpenAP v2.6.0 | 159.922 kN | 12.79 | 14.89 | 0.632 | 2,474 ft/min |
| Published 2020 | 213.620 kN | 9.57 | 12.01 | 0.591 | 2,864 ft/min |
| ATSB public comparator | — | — | approximately 17 | — | — |

The 17:1 value is a comparator, not a calibration target. The discrepancy is retained rather than tuned away.

For both parabolic polars:

- drag remains positive for positive dynamic pressure;
- induced drag diverges as dynamic pressure tends to zero;
- implied lift coefficient becomes unbounded because there is no stall or `CLmax`;
- a 600-second unpowered two-dimensional RK4 check balances mechanical-energy loss against integrated drag work;
- 4-second steps differ from the 0.125-second reference by less than 0.01 m in range and altitude, and 8-second steps by less than 0.1 m.

That numerical convergence validates the integration and energy bookkeeping only. It says nothing about post-stall B777 fidelity.

## Reproduce

Python's standard library and `curl` are sufficient for the audit. All upstream files and Python bytecode stay under `/tmp`:

```bash
cd /jackbox/home/MH370/.sources/b777-end-of-flight-aerodynamics
audit_cache=/tmp/b777-end-of-flight-audit
PYTHONPYCACHEPREFIX=/tmp/b777-end-of-flight-audit/pycache \
  python3 code/audit.py --cache-dir "$audit_cache"

B777_AUDIT_CACHE="$audit_cache" \
PYTHONPYCACHEPREFIX=/tmp/b777-end-of-flight-audit/pycache \
  python3 code/test_audit.py
```

On the audit host, a warm-cache offline `--no-write` run took 4.183 seconds wall time and peaked at 81,836 KiB RSS. Repeated runs of the 12 focused tests took 2.471–4.464 seconds. These are iteration measurements, not scientific outputs.

After the first run, `--offline` makes network access an error and re-verifies every cached hash:

```bash
python3 code/audit.py \
  --cache-dir /tmp/b777-end-of-flight-audit \
  --offline
```

The optional exact OpenAP runtime probe uses a `/tmp` virtual environment and the source already fetched by the audit:

```bash
mkdir -p /tmp/b777-end-of-flight-audit/openap-src
tar -xzf /tmp/b777-end-of-flight-audit/openap-v2.6.0-4fb21d6e.tar.gz \
  -C /tmp/b777-end-of-flight-audit/openap-src
python3 -m venv /tmp/b777-end-of-flight-audit/openap-venv
PIP_CACHE_DIR=/tmp/b777-end-of-flight-audit/pip-cache \
  /tmp/b777-end-of-flight-audit/openap-venv/bin/pip install \
  numpy pandas scipy PyYAML matplotlib
PYTHONPATH=/tmp/b777-end-of-flight-audit/openap-src/openap-4fb21d6e402fd1f4a48b191ad6801c74479e71f5 \
  /tmp/b777-end-of-flight-audit/openap-venv/bin/python \
  code/openap_runtime_probe.py
```

Do not set `force_engine=True` in an estimator. It appears only in the probe to demonstrate the upstream guard.

## Package contents

- [`candidate-families.json`](candidate-families.json) — machine-readable admission contract
- [`data/source-pins.json`](data/source-pins.json) — URLs, commits/versions, licences, and SHA-256 pins
- [`data/openap-runtime-observation.json`](data/openap-runtime-observation.json) — pinned full-execution observation
- [`CITATIONS.md`](CITATIONS.md) — primary-source passage ledger
- [`code/audit.py`](code/audit.py) — download verification, source inspection, calculations, and output generator
- [`code/test_audit.py`](code/test_audit.py) — focused provenance/scientific tests
- [`code/openap_runtime_probe.py`](code/openap_runtime_probe.py) — optional exact upstream execution
- [`outputs/results.json`](outputs/results.json) — generated evidence
- [`outputs/comparison.html`](outputs/comparison.html) — self-contained browser comparison
- [`SHA256SUMS`](SHA256SUMS) — local source-package checksums

No upstream archive, paper, workbook, or trajectory CSV is redistributed here. See [`CITATIONS.md`](CITATIONS.md) for exact source locators and [`data/source-pins.json`](data/source-pins.json) for legal intake details and hashes.
