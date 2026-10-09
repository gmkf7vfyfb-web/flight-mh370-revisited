# End of flight: smoke on the 3b code (00:11 contract, 8 seeds) and the 22:41 BTO-only arms

9 October 2026. **SMOKE SCALE, not evidence.** 295.66° prior, superseded by `reference-289`. Module code
`9d109c8`, spiral weight 0.

## 1. The 00:11 contract, 8 seeds, N = 4 (`runs/eof-3b-n4-all`, `contract-8seed-n4.json`)

- **Core request 3b holds in every seed:**
  - the onset prediction is priced by core's fuel model for 100% of rows;
  - no mechanism is relabelled dry;
  - no row has unpriced fuel seconds.
- **The weight flown dry by core before takeover** fell from 50.2% (median 42 s) before 3b to
  **3.1–3.9% per seed (median 5–10 s)**. It is not zero. The remainder is consistent with the takeover
  falling a few seconds after core's realised exhaustion at integration resolution; it is not yet
  explained, and is recorded here.
- **Fuel below tables / extrapolated:** 9–12% and 30–33% of rows are nonzero, with means of 23–31 s and
  119–146 s.

## 2. The 22:41 arms, BTO only, seed 1, N = 4 (**NOT THE ARM**: the 00:11 BFO waits on core request 14)

The snapshot has 19,999 rows, not 20,000, which is a property of core's hand-off. Every parent has all 16
of its impacts. Weighted impact latitude 5/50/95%:

| option | V1b (flame-out only) | V2 (all mechanisms) | effective parents V1b / V2 |
|---|---|---|---|
| none (held out after 22:41) | −39.80 / −36.02 / −21.13 | −38.74 / −32.48 / −23.02 | 19,999 / 19,999 |
| m0011.bto | −39.68 / −37.31 / −27.61 | −39.20 / −35.19 / −28.33 | 504 / 863 |
| m0011.bto + m0019a.bto | −39.87 / −38.19 / −27.76 | −39.71 / −37.79 / −26.57 | 302 / 232 |

- **Under `none`, V2's median lies 3.5° north of V1b's.** Anticipatory onsets begin the descent earlier
  and shorter of the arc.
- **Scoring the BTOs closes most of the gap:** 0.4° remains with both scored.
- This is one seed at N = 4. The V1b-against-V2 difference **is** attributable to the descent hypothesis
  (same hand-off, same scoring). It is not yet the arm's result, because the 00:11 BFO is missing.
