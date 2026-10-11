# Hydroacoustics: arrival windows and validation gate on end of flight's run C

*Hydroacoustic Module, 11 Oct 2026 ~06:40 UTC. Data: `results-data/search_windows/next-run-c/` on `hypothesis/hydroacoustics`.*

**Scripts:**
- `search_windows.py` with a format-only amendment (`b6cbf599`). Regression: next-routes 72/72 arms identical.
- `search_windows_mixture.py`, amendments 2 and 3 (`25ad0b1c`, `10c28721`), pre-registered before use.

**Inputs:**
- End of flight run C: 4 strata × 8 seeds, compact format.
- P(family) is EoF's `p_core`: 0.589 / 0.252 / 0.135 / 0.024.
- Ẑ_00:19 per family and option from `summary/family-evidence-run-c.json`, including EoF's own `+unpowered`. The
  earlier "+alive for +unpowered" approximation is retired.

**Labels:**
- Core split-half for run C pending (core's report).
- Residual roll P(left) = 0.8 PROVISIONAL.
- Trim at loss and two-tank takeover not applied.
- Rapid descents above 6,500 ft/min not reachable by the model (end of flight's labels).
- The `~v212` version: "impacts faster than 212 m/s removed (no structural limit in the model)".

## Validation gate: PASSED
Every arm in the 4 strata was checked against end of flight's `impact-time-shares`:
- 24/24 arms in each stratum;
- worst |Δ share before 00:19:37 or after 01:15:56|: 1.7e-18;
- worst |Δ impact quantile|: 1.00 s (the 2 s grid).

## Windows (SOFAR branch; families re-weighted; window = [q0.5 − 10 min, q99.5 + 20 min], rounded to 5 min)

| 00:19 option (variant) | ESS | Cape Leeuwin H01W median (0.5–99.5 %) → window | Diego Garcia South H08S median (0.5–99.5 %) → window |
|---|---|---|---|
| Held Out (+unpowered) | 55.6 M | 01:04:02 (00:42:16–01:32:00) → 00:30–01:55 | 01:22:52 (01:01:30–01:53:10) → 00:50–02:15 |
| R600 BTO Only (+unpowered) | 37.6 M | 01:05:00 (00:43:04–01:31:48) → 00:30–01:55 | 01:24:12 (01:02:16–01:53:56) → 00:50–02:15 |
| R600 BTO + Raw BFO (+unpowered) | 1.27 M | 00:58:30 (00:40:24–01:16:00) → 00:30–01:40 | 01:16:54 (01:02:04–01:34:44) → 00:50–01:55 |
| same three, `~v212` | 50.0 / 33.8 / 1.10 M | medians later by 0.8–1.0 min; windows unchanged except BTO Only H01W from 00:35 | medians later by 0.8–1.0 min; windows unchanged |
| same three, +silent | 2.6 / 1.8 / 0.12 M | 00:25–01:45 / 00:25–01:45 / 00:25–01:40 | 00:50–02:05 / 00:50–02:05 / 00:50–02:00 |
| Holland H1 / H2 | 66 / 171 (fixed weights) | **not yet estimable – targeted sampler in progress** | |

- **Core-set request windows on run C (+unpowered):** H01W 00:30–01:55 UTC; H08S/H08N 00:50–02:15/02:20 UTC.
  - Core (b) gave 00:25–02:05 and 00:50–02:30, so run C is narrower at both ends.
  - The raw-data request already proposed to Pete (H01W 00:25–02:20, H08S/H08N 00:45–02:50) still covers every
    run C window, including H1/H2's provisional ranges. **No change to the request is needed.**
- The fixed-weight and re-weighted versions agree to ≤ 2 s in every quantile shown.

## COVERAGE
See `hydroacoustics-coverage.md` (G1–G6). Specific to this note:
- **(c) Proposal's coverage:** options 1–3 have ESS ≥ 1.1 M in every version.
- **G1 is still open:** H1/H2 ESS is 66/171 on run C.
- **New gap G13 (end of flight's, carried):** speeds above 212 m/s are not credible because the model has no
  structural limit. Both versions are shown. They move the windows by ≤ 5 min, because the removed rows are mainly
  steep, fast entries with similar impact times.

- Hydroacoustic Module
