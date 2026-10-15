
# The received-power / antenna-gain observable — assessment of the prior work

15 October 2026. Read from the August pre-September tree, `~/Downloads/flight-mh370-revisited/`
(import commit 7a1c507). Nothing here has entered this project's estimate.

## What the observable is

The aircraft's two satellite antennas are side-mounted conformal arrays. Their gain toward the
satellite depends on the direction of the satellite relative to the airframe, so the same map
position gives a different received power at a different heading. **If** the terminal does not
fully pre-compensate its transmit power for that gain, the received power logged by the ground
station carries information about **heading and attitude** at every burst — a different
quantity from what the BTO (range) and BFO (Doppler) carry.

That matters here specifically. In this project's base run the spread of misfit across the
five autopilot modes is at most 0.19 nat at every epoch from 18:25 to 21:41; only the last four
epochs discriminate modes at all, and the mode mixture is what controls the northern shoulder.
A heading observable at the mid-flight epochs is the one thing that could discriminate modes
where nothing else does.

## The decisive question, and what the prior work found

Everything rests on one hardware question: **does the terminal pre-compensate transmit power for
antenna gain?** If completely (β = 0), received power carries no heading information. If not at
all (β = 1), it carries the full gain pattern.

The prior work tested it on MH371 (9M-MRO's previous flight, known positions and headings) using
three phases on the same R1200 channel, with the free-space path change removed:

| phase | reconstructed gain (dBic) | path-corrected received power (relative dB) | n |
|---|---|---|---|
| 01:55 | 10.42 | 124.67 | 6 |
| 03:29 | 11.72 | 127.04 | 8 |
| 03:21 | 13.95 | 127.17 | 12 |

Result: β = 0.645, 95% interval 0.25–1.04. Complete pre-compensation rejected (p = 0.0014); no
compensation not rejected (p = 0.079); likelihood ratio 35 for no compensation against complete.

## Why it cannot be used as it stands

1. **Three points.** A free slope plus an offset leaves one degree of freedom. The free fit's χ²
   of 5.13 on that one degree of freedom is itself a poor fit (p ≈ 0.02): the 03:29 point sits
   about 1.5 dB above the line, so the slope is pinned almost entirely by 01:55 against the other
   two.
2. **The verdict depends on an assumed nuisance floor.** The episode-level noise floor τ was set
   at 0.5 dB. At τ = 0 both hypotheses are rejected outright (p = 2e-87 and 4e-13), and at
   τ = 0.25 dB no-compensation is still rejected (p = 0.0013). It first survives at the 0.05 level
   at τ = 0.45 dB (p = 0.053), so the chosen 0.5 dB sits just above the crossing and the headline
   verdict depends on that choice. The floor is a modelling choice, not a measurement.
3. **The gain values are reconstructed**, from a digitised gain curve with a side-selection and
   attitude assumption, and the prior work's own open-questions list names robustness to
   digitisation, side selection, attitude, fading and transmit-power state changes as undone.
4. **The posterior that used it no longer exists.** The prior work's own limitation note says the
   original particle checkpoint is unavailable and the published BTO+BFO+received-power posterior
   was reconstructed from its summary.

## Assessment

**Physically sound, potentially high-value, and currently unproven.** The value is real and
specific to this problem's weakest point — mode discrimination in the middle of the flight. The
evidence that the observable exists at all rests on three points and an assumed noise floor.

## What would settle it, cheapest first

1. **Primary documentation** on whether the satellite data unit applies EIRP control against
   antenna gain. A hardware fact, answerable from manufacturer or ARINC 741 documentation without
   any computation, and it may settle β outright. *Hours.*
2. **More phases.** The test needs tens of same-channel phases with known heading, not three.
   Davey's Table 5.1 used Inmarsat logs from 20 prior 9M-MRO flights for BFO; if those logs carry
   received power or C/N0 at known positions, the test can be repeated with an order of magnitude
   more data. Whether the project holds those logs, and whether they carry power, is the first
   thing to check. *A session.*
3. **Only then** a likelihood module, and only if β is shown materially above zero.

## Recommendation

Not in the paper as a result. One sentence in further work, naming it as the one SATCOM observable
not yet scored and the one most likely to discriminate autopilot modes in mid-flight. Step 1 is
worth an hour of a session's time at any point; nothing further should be built until it is done.
