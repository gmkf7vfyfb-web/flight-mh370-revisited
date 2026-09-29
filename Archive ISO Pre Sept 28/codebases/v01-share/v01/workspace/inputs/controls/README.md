# Truth-separated control inputs

This directory separates inference-visible inputs from scorer-only truth. The
MH371 files are a known-flight control of the inference technique, not evidence
about MH370's location.

## File roles

| File | Reader | Contents |
| --- | --- | --- |
| `mh371-inference.json` | legacy inference and broad-input derivation | Initial 01:48 UTC position/heading prior, six selected R1200 BTO/BFO observations, satellite states, and traced BFO-correction components; no later aircraft state |
| `mh371-broad-satcom.csv` | `estimate-broad-flight` | Runner-input truth-separated SATCOM projection with no later aircraft-state fields |
| `mh371-broad-satellite.csv` | `estimate-broad-flight` | Runner-input truth-separated satellite ECEF position/velocity projection with no later aircraft-state fields |
| `mh371-truth.csv` | scoring/reporting only | Held-back later ACARS aircraft states used after inference |

The inference files contain the six epochs at 01:56:47.921, 03:20:22.428,
04:04:57.916, 05:11:37.411, 06:09:44.409, and 06:48:33.907 UTC. Time is
measured from 2014-03-07 01:48:00 UTC. The selection method, eligible-row
rules, source workbook identities, and correction trace are recorded in
`.sources/mh371-known-flight-data/README.md` and in the JSON package itself.
The final window was moved from 07:00 to 06:48 after a pilot inspection of the
held-back ACARS track showed that 06:59 was already mixing the descent turn.
No later aircraft state enters the inference bytes, but this truth-informed
design choice means the control is not a fully preregistered blind trial and
cannot by itself calibrate general coverage.

## Deterministic broad-input mapping

For every entry of `mh371-inference.json`'s `observations` array, the SATCOM
adapter maps fields as follows:

| Broad CSV column | Source or declaration |
| --- | --- |
| `epoch_id` | `epoch_id` |
| `time_utc` | `time_utc` |
| `seconds_from_t0` | `seconds_from_t0` |
| `bto_us` | `bto_us` |
| `bto_sd_us` | `bto_sd_us` |
| `bfo_hz` | `bfo_hz` |
| `bfo_sd_hz` | 7 Hz published-error evidence-family declaration; not aircraft truth |
| `satellite_afc_hz` | `combined_satellite_ges_hz`, equal to `satellite_oscillator_hz + perth_ges_afc_hz` |
| `raw_source_rows` | decimal `sita_source_row` |
| `note` | constant provenance label |

The satellite adapter maps `sat_position[0..2]` to `x_km`, `y_km`, and `z_km`
and `sat_velocity[0..2]` to `vx_km_s`, `vy_km_s`, and `vz_km_s`, retaining the
same `epoch_id` and `time_utc`. Positions are Earth-centred Earth-fixed
kilometres and velocities are kilometres per second, as required by the broad
SATCOM spoke.

`combined_satellite_ges_hz` is deliberately not folded into the latent
aircraft BFO bias. No value is read from `mh371-truth.csv` during either
projection or broad inference. The scorer may open the truth file only after
the inference artifacts have been finalized.

## Integrity

```text
e097dcfb303acb515a8b6bee90450574b88968d647b82d5b3d3eea5bf56c37ec  mh371-inference.json
0f1b0ff72b4385a53fae0e2cd86831ec65c60f37ad73ac07862cbbb96dfe6177  mh371-broad-satcom.csv
43f0e2445b9e979a8cdc5ac375294dd41050505b4d57c074bf923a9f359871fa  mh371-broad-satellite.csv
65de30cc4e20fc77a1d6048449d5654046fd78f83f325d14d2d26c6ccd9751c9  mh371-truth.csv
```

Verify the committed bytes with:

```bash
sha256sum \
  inputs/controls/mh371-inference.json \
  inputs/controls/mh371-broad-satcom.csv \
  inputs/controls/mh371-broad-satellite.csv \
  inputs/controls/mh371-truth.csv
```

The legacy `infer-known-flight` command uses a single constant magnetic
heading and cannot validate the current broad repeated-manoeuvre model. A
valid broad MH371 assessment must use the two broad adapters, keep truth
unavailable during inference, and report both per-arc held-back-truth error and
the same seed/root/stratum numerical diagnostics required for MH370.

The v0.1 broad control also reuses the accident configuration's declared
source mass/fuel proxy because no MH371 fuel state is exposed. It has no Arc-1
fuel anchor. That proxy and its flow-scale range are model assumptions, not
known-flight truth.
