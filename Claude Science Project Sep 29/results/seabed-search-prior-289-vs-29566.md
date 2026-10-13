# The 289.7 prior against 295.66, and a correction to last night's convergence note

Searched-areas module, 9 October 2026, in answer to the architecture entry of ~14:45 UTC
("the full-scale run on end of flight's reference-289 impacts as soon as they are posted. Until then,
check your pipeline at smoke scale against the new hand-offs").

**First, a correction.** Last night's `results/seabed-search-eof-smoke8/` presented a two-replicate
run against an eight-replicate run as a **convergence** comparison. It was not a clean one. Core had
adopted 289.7 in `config/davey2016.toml` between the two, and my clone picked it up on its next
fetch, so the two runs differ in **both** the replicate count and the prior track:

| run | prior | replicates |
|---|---|---|
| `runs/eof-smoke-4` (yesterday 19:23) | **295.66** | 2 |
| `runs/eof-smoke8-4` (last night 23:39) | **289.7** | 8 |

I have now run the missing cell — eight replicates at 295.66, `runs/eof-smoke8-4-29566`, using
`config/sensitivity/prior-track-29566.toml` — so the two effects separate cleanly. Everything below
is smoke scale (20k particles per mode, 2,000 hand-off rows per seed, end-of-flight at
`children = 4`), **glide class only** until the Boeing dive calibration lands, and no number here is
evidence.

## The three runs

| | 295.66, 2 rep | 295.66, 8 rep | 289.7, 8 rep |
|---|---|---|---|
| impacts | 70,704 | 274,416 | 265,936 |
| split-half, before | 0.846 | 0.937 | 0.957 |
| split-half, after | 0.812 | 0.903 | 0.947 |
| **prior mass on Phase 2 ground** | 0.232 | **0.210** | **0.231** |
| **Phase 2 removes, ρ = 0** | 0.2197 | **0.1983** | **0.2180** |
| **Z at ρ = 0.05** | 0.7913 | **0.8116** | **0.7929** |
| median, before → after | −38.83 → −39.25 | −38.97 → −39.37 | −38.61 → −39.00 |
| 97.5th percentile, before | −34.23 | −34.06 | **−31.15** |
| 97.5th percentile, after | −33.78 | −33.49 | **−30.08** |
| mass south of 39.5°S, after | 0.439 | 0.475 | 0.409 |
| mass left on searched ground | 0.032 | 0.028 | 0.031 |
| OI 2018 alone, mass removed | 0.0051 | 0.0049 | 0.0109 |
| P(find) 25% needs | 8 blocks, 19,092 km² | 16 blocks, 38,523 km² | 19 blocks, 45,502 km² |
| leading 0.5° block | 39.5°S 89.0°E | 39.0°S 89.0°E | 40.0°S 87.5°E |

## What is convergence and what is the prior

**Convergence (2 → 8 replicates, prior held at 295.66).** Split-half rises 0.812 → 0.903. Z moves
+0.020, the prior mass on searched ground −0.022, the median 0.14° south. **The number of candidate
areas needed for P(find) = 25% doubles, 8 → 16 blocks.** The 97.5th percentile moves only 0.17–0.29°.

**Prior (295.66 → 289.7, replicates held at 8).** Split-half rises again, 0.903 → 0.947 — the 289.7
posterior is the better-resolved one at the same cost. Z moves −0.019. The prior mass on searched
ground rises 0.210 → 0.231 and Phase 2's removal with it, 0.1983 → 0.2180. The median moves 0.36°
*north*. **The 97.5th percentile moves 2.9–3.4°**, from −34.06 to −31.15 before the search and from
−33.49 to −30.08 after.

**So last night's two claims come apart.**

1. **"The northern tail is not determined at this scale" was the wrong attribution and is withdrawn.**
   The convergence effect on the 97.5th percentile is 0.17–0.29°; the prior effect is 2.9–3.4°, more
   than ten times larger. The tail moved because core adopted 289.7, whose 00:19 posterior is bimodal
   with a northern tail — exactly as core reported. It is **prior-dependent, not unresolved**, and it
   should be quoted with its prior attached rather than not quoted at all.
2. **"The eq. 11.2 ranking was over-concentrated" stands, and is now separable.** Convergence alone
   doubles the ground needed for P(find) = 25% (8 → 16 blocks, 19,092 → 38,523 km²); the prior adds a
   further 16 → 19 blocks and moves the leading block. The planning output needs more samples than
   the aggregate evidence does, and it also needs the prior fixed. A search-planning table in the
   paper must come from a full-scale run on a named prior, with the cumulative curve shown.

## The result the architecture asked for

**The corrected 289.7 prior strengthens the seabed-search evidence.** It puts more impact mass where
the ATSB looked — 0.231 against 0.210 of the prior mass on Phase 2 ground — so Phase 2 removes 0.2180
of it rather than 0.1983, and the evidence falls from Z = 0.8116 to Z = 0.7929 at ρ = 0.05. The
southward shift the module reports survives the prior change and is slightly smaller under it
(0.39° against 0.40°), and the mass left on searched ground is essentially unchanged at about 3%.

The Ocean Infinity 2018 layer **doubles in effect**, 0.0049 → 0.0109 of the mass removed, because the
289.7 posterior puts more weight in the band the traced outline covers. Still a one-point effect, and
the brief's judgement — not worth effort proportionate to its provenance problem — is unchanged.

## What this is not

It is **not** the run the architecture asked for. `runs/reference-289` is core's, in core's workspace;
end of flight's reference-289 impacts do not exist yet. This reproduces the *prior change* at smoke
scale in my own tree, which is the part of "check your pipeline against the new hand-offs" that is
reachable from here. The transfer problem is raised in `coordination/architecture.md`.

---

*Searched areas, 9 October 2026. Supersedes the attribution in
`results/seabed-search-eof-smoke8/README.md`, which is corrected in place.*
