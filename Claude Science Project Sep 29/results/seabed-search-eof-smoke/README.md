# Seabed search on end-of-flight impacts — smoke scale, 295.66° prior

Searched-areas module, 9 October 2026. Step 5 of the architecture sequence, first arm: the module's
likelihood evaluated on impacts from the **end-of-flight** terminal module instead of the arc-kernel
placeholder, with a **point-target placeholder** for the wreckage field (`g = 1`, as
`results/seabed-detectable-target.md` §6 defines it).

**THE DIVE CLASS IS ABSENT FROM THESE IMPACTS.** Pete, 9 October: the Boeing engineering-simulator
runs were tests of *uncontrolled* dives, and until the end-of-flight model is calibrated against the
dive cases (3, 4, 5, 6, 10) its impacts cover the **stable-glide regime only**. The descents used here
were generated before that calibration. Every number below is therefore conditional on a glide-class
impact distribution; a dive class would put impacts closer to the 7th arc, which is precisely the
corridor the ATSB searched, so **the search evidence is likely to be understated here, not
overstated**. This caveat travels with the numbers, not just with this paragraph.

**PROVISIONAL, smoke scale.** Hand-off `runs/fixture` (`config/integrated.toml` +
`config/smoke.toml` + `config/fixture.toml`: 20k particles per mode, seeds 1 and 2, 2,000 hand-off
rows), continued by `mh370 terminal` with `hypotheses/end-of-flight/smoke/terminal.toml` and
`children-4.toml`, `target = "none"`, 00:19 data option `none`. 70,704 impacts. The base prior is
`config/davey2016.toml`'s **295.66° track at 18:01:49**, as the architecture entry asks it be
labelled. Split-half agreement 0.846 before the search and 0.812 after: **not converged, and no
number here is evidence.** The end-of-flight samples are that module's, at its own smoke scale.

## What changes when the impacts are real descents

| | arc-kernel placeholder | end-of-flight, smoke |
|---|---|---|
| prior mass on Phase 2 searched ground | 0.664 | **0.232** |
| mass removed at ρ = 0, Phase 2 alone | 0.6274 | **0.2197** |
| evidence Z at ρ = 0.05 | 0.4040 | **0.7913** |
| median impact latitude, before → after | −37.62 → −37.24 | **−38.83 → −39.25** |
| mass left on searched ground, ρ = 0.05 | 0.173 | **0.032** |
| mass south of 39.5°S, after | 0.094 | **0.439** |

**The search is a much weaker constraint on real descents than on the placeholder, and it pushes the
distribution south rather than north.** The placeholder scattered impacts within ±50 NM of the 7th
arc, which is the corridor the ATSB searched, so two thirds of its mass was on searched ground and
the search removed 63% of it. The end-of-flight descents spread much further: 76.8% of the impacts
lie off searched ground before any search evidence is applied, so Phase 2 can only remove 22%.

What survives is a shift, not an exclusion. The median moves 0.42° south — about 25 NM — and the
posterior's mass south of 39.5°S rises from 0.33 to 0.44. The 95% interval widens at the southern
end (−42.04 → −42.19) and contracts at the northern (−34.23 → −33.78).

## Numbers, at ρ = 0.05 unless stated

```
before:  median -38.83, 95% -42.04 to -34.23, split-half 0.846, Kish ESS 64,119, on Phase 2 0.232

scenario                                 Z   median    q025    q975  N of 33S  S of 39.5  on P2     ESS   split
run.toml                            0.7913   -39.25  -42.19  -33.78     0.019      0.439  0.032  51,899   0.812
rho 0                               0.7803   -39.28  -42.19  -33.74     0.020      0.445  0.018  50,587   0.810
rho 0.02                            0.7847   -39.27  -42.19  -33.76     0.020      0.443  0.024  51,118   0.811
rho 0.1                             0.8023   -39.23  -42.18  -33.81     0.019      0.434  0.045  53,155   0.815
rho 0.2                             0.8242   -39.18  -42.16  -33.87     0.019      0.424  0.070  55,485   0.819
rho 0.3                             0.8462   -39.13  -42.14  -33.93     0.018      0.414  0.094  57,550   0.823
rho 0.5                             0.8901   -39.04  -42.11  -34.03     0.017      0.395  0.139  60,818   0.831
Phase 2 q 0.90                      0.8012   -39.23  -42.18  -33.81     0.019      0.435  0.044  53,038   0.814
Phase 2 q 0.98                      0.7836   -39.27  -42.19  -33.75     0.020      0.443  0.022  50,981   0.811
Phase 2 split, shared misses        0.7898   -39.26  -42.19  -33.77     0.019      0.440  0.030  51,723   0.812
Phase 2 split, independent misses   0.7885   -39.26  -42.19  -33.77     0.019      0.441  0.028  51,561   0.812
+ OI 2018 inferred, coverage 0.889  0.7865   -39.27  -42.19  -34.05     0.017      0.442  0.032  51,597   0.816
+ OI 2018 inferred, coverage 0.952  0.7861   -39.27  -42.19  -34.06     0.017      0.442  0.032  51,561   0.816

mass removed at rho 0:  Bluefin-21 0.0000,  Phase 2 0.2197,  + OI 2018 inferred 0.2248
```

Three things worth carrying forward:

1. **ρ matters less here, in absolute terms, than on the placeholder.** Across the full sweep the
   evidence runs 0.7803 to 0.8901 — an 11-point spread, against 31 points on the placeholder — simply
   because less mass is exposed to the search at all. The mass left on searched ground still varies by
   a factor of eight across the sweep (0.018 to 0.139), so ρ remains the parameter to report.
2. **Repeat-search dependence is smaller still on these samples**: 0.7898 against 0.7885, a gap of
   0.0013 in Z, because little of the mass sits on the 18,130 km² of doubly-swept ground.
3. **Ocean Infinity 2018 removes 0.0051 of the mass, against 0.0125 on the placeholder.** Its outline
   provenance problem continues to be worth less attention than its coverage.

## Provenance and open items

- The Ocean Infinity 2018 layer is read by path from `data/external/search-coverage/`, never
  committed, as the brief requires. The copy used is the one in the frozen September snapshot — see
  the licence item raised in `coordination/architecture.md`.
- The end-of-flight run is that module's smoke configuration, taken as given. If their fuel-state or
  onset work changes the descents, these numbers change with them; the module's likelihood does not.
- Full scale waits on the end-of-flight sweep, as the architecture entry sets out.

Figures: `search-evidence.pdf` and a PNG of each page.

---

*Searched areas, 9 October 2026.*
