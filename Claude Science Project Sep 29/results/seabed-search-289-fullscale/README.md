# The seabed search on full-scale reference-289 impacts

Searched-areas module, 9 October 2026. Brief §7 item 5, full-scale arm: the module's likelihood on
end of flight's reference-289 evidential sweep, with a **point-target placeholder** for the wreckage
field. This is the first time the module has met a converged impact distribution.

## Provenance (run-provenance convention, architecture ~16:40 UTC)

| | |
|---|---|
| source impacts | `runs/eof-289-full-s<k>/bto-bfo/seed-<k>/impacts.npy`, k = 1–4, read in place from end of flight's workspace at the path they posted at 16:50 UTC |
| run name | `reference-289` |
| **prior track** | **289.7°** at 18:01:49, read from `eof-289-full-s1/run.json` |
| terminal module | `end-of-flight` |
| particles per mode | 1,000,000 / 500,000 / 2,500,000 / 500,000 / 2,500,000 |
| impacts | **3,200,000 per seed, 12,799,968 pooled**, 90 columns |
| 00:19 data option | `none` — the held-out case |
| seabed-search columns in the source | none; the double-application guard passes |

**Convergence is good at this scale.** Split-half agreement on the impact-latitude distribution is
**0.973 before the search and 0.968 after**, against the project's 0.924 floor. Kish ESS 12.36 M
before, 9.48 M after.

**Two caveats that travel with every number below.**

1. **The dive class is end of flight's provisional class (b)**, and Pete's instruction of ~17:30 UTC
   is that its implementation "looks poor compared to Boeing's set"; end of flight is now rebuilding
   the simulator against the ten Boeing engineering-simulator runs. These impacts therefore carry *a*
   dive class, not the right one. The Boeing glide band is likewise provisional.
2. End of flight's own sweep reports **11 of 16 option × cause rows converged**; the held-out `none`
   option used here is not among the unconverged ones, but the impact distribution is theirs and
   inherits their status.

## The result

| | smoke scale, 289.7 | **full scale, 289.7** |
|---|---|---|
| impacts | 265,936 | **12,799,968** |
| split-half, before → after | 0.957 → 0.947 | **0.973 → 0.968** |
| median impact latitude, before | −38.61 | **−36.78** |
| 95% interval, before | −42.0 to −31.2 | **−40.29 to −26.88** |
| **prior mass on Phase 2 ground** | 0.231 | **0.297** |
| **Phase 2 removes at ρ = 0** | 0.2180 | **0.2805** |
| **Ocean Infinity 2018 alone removes** | 0.0109 | **0.0400** |
| both together | 0.2288 | **0.3202** |
| **Z at ρ = 0.05** | 0.7929 | **0.7335** |
| median, before → after | −38.61 → −39.00 (0.39° **south**) | **−36.78 → −36.58 (0.20° north)** |
| mass left on searched ground | 0.031 | **0.044** |
| mass south of 39.5°S, after | 0.409 | **0.094** |
| mass north of 33°S, after | — | **0.138** |

**Three things change at full scale, and all of them matter.**

**1. The search evidence is much stronger than smoke scale suggested.** Nearly **30% of the impact
mass lies on ground the ATSB searched**, against 23% at smoke scale, and the searches remove **32%**
of the probability at ρ = 0 rather than 23%. The evidence falls to Z = 0.7335 at the reference
ρ = 0.05. This is the module's headline and it is now on a converged distribution.

**2. The shift reverses direction.** At smoke scale the search pushed the distribution 0.39° *south*;
at full scale it moves the median 0.20° *north*, from −36.78 to −36.58. The reason is the shape of the
full-scale impact distribution: its mass sits inside the searched corridor with a long **northern**
tail (95% upper bound −26.88, and 13.8% of the posterior north of 33°S after the search), so removing
searched ground pushes probability into the north rather than the south. The southward shift reported
at smoke scale was a property of the under-resolved distribution, not of the search evidence.

**3. Ocean Infinity 2018 is no longer a one-point effect.** It removes **0.0400** of the mass alone,
nearly four times its smoke-scale figure, and pulls the median back south to −36.76 — because the
full-scale distribution puts real weight in the band the traced outline covers. **This raises the
stakes on the outline's provenance.** The brief's judgement that "the coverage-fraction uncertainty
inside the OI outline is immaterial" still holds — 0.889 gives Z = 0.6958 and 0.952 gives 0.6931 —
but the brief's other judgement, that OI 2018 is "a 1.2-point effect, do not spend effort on its
outline proportionate to its provenance problem", **no longer follows at full scale.** The licence
question now sits in front of a four-point result.

**Repeat-search dependence stays small**: shared 0.7318 against independent 0.7301, a gap of 0.0017,
because little of the mass sits on the 18,130 km² of doubly-swept ground. **The 2025–26 inferred
variant** moves Z by 0.0037 (0.7335 → 0.7298) — ten times its smoke-scale effect, still minor.

## Davey eq. 11.2, where to look next

On the residual posterior, 0.5° blocks, planning `P_D` = 0.9:

| rank | block | residual mass | P(find) | km² | before the search |
|---|---|---|---|---|---|
| 1 | 35.5°S 91.0°E | 0.0235 | 0.0212 | 2,524 | 0.0172 |
| 2 | 35.0°S 91.5°E | 0.0189 | 0.0170 | 2,540 | 0.0139 |
| 3 | 36.5°S 89.5°E | 0.0178 | 0.0160 | 2,493 | 0.0141 |
| 4 | 37.0°S 89.0°E | 0.0155 | 0.0140 | 2,477 | 0.0166 |
| 5 | 36.0°S 90.5°E | 0.0153 | 0.0138 | 2,509 | 0.0152 |

**P(find) = 25% needs the best 21 blocks and 51,977 km²; 50% needs 62 blocks and 152,587 km²; 75%
needs 231 blocks and 580,334 km².** The leading areas are north-east of the smoke-scale ones, around
35–37°S and 89–91.5°E, following the full-scale distribution's northern weight. Rank 4 is the only
block in the top five that the search *reduced* — it lies inside Phase 2 coverage.

These numbers are converged in the sense that matters for the aggregate, but the block ordering is a
tail-sensitive statistic and should be read as the cumulative curve, not as a league table.

Figures: `search-evidence.pdf` and a PNG of each page.

---

*Searched areas, 9 October 2026.*
