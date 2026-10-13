# Australian non-recovery pilot (drift, G26): result

13 Oct 2026 ~01:40 UTC, ocean drift module. Pre-registration: `debris-drift-australia-preregistration.md` (primary B, Pete).

> **Labels:** PILOT; **REACH-LIMITED** (domain 15-120 E: debris carried east of 120 E counts as never found, so the southern penalty is
> probably understated); GLORYS12 + ERA5 only; 178 of the 710 run A nodes; beaching on entry to the land mask (GSHHG snap 25 km), no refloat; interim, not evidence;
> run I NOT CONVERGED. Do not compose until the 160 E fields and the full run.

## Run

GLORYS12 + ERA5, every 4th run A node (178) in 2 chunks, 10^5 particles/node, 12 threads under the heavy lock (19:12-21:06 and
23:46-01:34 UTC; walls 6,807 / 6,445 s), binary sha256 56be04bc3c8c605f (module commit 59f4759b code; config d76c50db), 175 nodes scored
in all options, 3 unresolved (southern). Check: the "off" column reproduces the run A surface (correlation 1.00, SD 0.15, a constant
-0.93 offset from the level-draw stream, which cancels in every posterior).

## Result

Change in ln L from the Australian term, mean by band (split-half noise of the change 0.30-0.47):

| band | B (primary) | A | C | searcher |
|---|---|---|---|---|
| 37-42 S | -7.55 | -5.37 | -4.14 | -4.88 |
| 34-37 S | -3.47 | -2.37 | -1.73 | -2.30 |
| 31-34 S | -1.92 | -1.22 | -0.87 | -1.20 |
| 28-31 S | -1.19 | -0.69 | -0.53 | -0.55 |
| 25-28 S | -0.58 | -0.35 | -0.23 | -0.06 |
| 20-25 S | -0.21 | -0.22 | -0.08 | +0.25 |

Mechanism: southern sources put 15-22 % of floating debris on WA coasts within the window (south-west WA city 2.8 %, outer 6.5 %,
remote 6.3 %) against 4-7 % on the find coasts; north of 25 S under 0.5 %. B treats WA as watched from March 2014.

**Drift alone** (GLORYS12, uniform grid prior): median 30.7 S (off) -> 28.2 S (B), 28.7 S (A), 29.2 S (C); 2.5 % limit 39.5 -> 34.2 S.

**Composed run I, approximate** (composer pass 2 maps re-weighted by exp(Delta), IDW to the 0.1 deg map; GLORYS12 Delta applied to the
ocean-model mixture): median (5-95 %), 50 / 90 % area (k km^2):

| 00:19 cell | product | off | B (primary) | A | C |
|---|---|---|---|---|---|
| D0 Held Out | + drift | -36.9 (-38.3 to -30.7), 39 / 270 | -31.7 (-37.1 to -25.4), 118 / 486 | -35.0 | -35.8 |
| D0 Held Out | + drift + searches | -36.0, 84 / 432 | -30.7 (-36.7 to -25.2), 126 / 511 | -31.6 | -34.0 |
| D1 R600 BTO Only | + drift | -37.1 (-38.4 to -33.4), 29 / 165 | -34.8 (-37.3 to -25.2), 88 / 354 | -35.7 | -36.3 |
| D1 R600 BTO Only | + drift + searches | -36.8, 51 / 308 | -30.6 (-36.9 to -24.9), 97 / 392 | -33.2 | -35.4 |
| D4 (Holland H1 cell) | + drift + searches | -36.1, 32 / 188 | -30.1, 37 / 187 | -31.3 | -35.2 |

The "off" column reproduces the composer's published values (e.g. D0 + drift -36.86 (-38.24 to -30.60), 270k km^2).

## Reading (provisional)

- The Australian absence is **a large term, not a correction**: under B it moves the composed median 2-6 degrees north and makes the
  posterior multi-modal (peaks near 36, 30.5 and 26.5 S, panel b). Under C it is 1-1.4 degrees.
- It runs opposite to CSIRO's reading (which kept 35-36 S): CSIRO combined the WA absence with Africa's late arrivals, used BRAN2015, its
  own leeway and qualitative detection; our drift factor already includes the Africa timing. The difference needs to be understood
  before this is read as a result.
- **Model-error checks needed before production:** (1) refloat: beached items stay on the coast for the rest of the window
  here, so every WA beaching keeps its exposure to finders; CSIRO's model sent items back to sea in summer. (Correction, 13 Oct
  ~01:58 UTC: an earlier version of this note named the 25 km GSHHG snap as a possible cause of over-stranding. That is wrong:
  beaching happens only when a particle enters the GLORYS12 land mask; the snap only decides whether such a stranding counts as a
  beaching at the nearest GSHHG shore or as model error. It does not catch particles offshore.) A refloat option is now in the
  module (835bdf52) and a sensitivity run is queued; (2) the domain to 160 E; (3) GlobCurrent; (4) the level prior sigma (1 nat)
  and the WA early-awareness assumption, which is what makes B strong (WA level 1 in 2014 against 0.1 for the find coasts).

## COVERAGE

(a) Feasible set: impacts as in run I. (b) Model reach: 178 nodes; Australian coasts west of 120 E only (east of 120 E unreachable: GAP,
fix requested); refloat not modelled (GAP); breakup origin not modelled (GAP). (c) Proposal: 10^5 particles/node; 3 nodes unresolved
(south); split-half noise of the change 0.30-0.47. Parameter bounds: levels pre-registered (B/A/C/off/searcher); sigma 1 (no source,
declared); window to 30 Jun 2016.
