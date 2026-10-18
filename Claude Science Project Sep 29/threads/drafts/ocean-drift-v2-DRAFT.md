# Ocean drift: module brief (v2, 17 Oct 2026)

Supersedes v1 (8-9 Oct 2026, kept unchanged as `threads/master-prompts/archive/ocean-drift-v1.md`; its §9
record of what the prior work measured and got wrong remains valid reading). Read
`threads/master-prompts/shared-contract.md` first and `threads/status/ocean-drift.md` after this file. This brief
holds what is stable; current numbers, run names and file locations are in the status file only.

## 1. Purpose

Ocean drift is one of several sparse lines of evidence (shared contract, "Pete's research principle"). Its job is
to say, honestly and with its own uncertainty, how the recovered debris and the absence of debris on populated
Australian coasts bear on the impact location: what drift says alone, how it changes the core estimate, and how far
it disagrees with the core. It is neither the referee of the core nor something to be reconciled away.

Forward physics, inference by Bayes: drift runs forward only and returns L_s = p(debris evidence | impact sample s).
Reverse drift is a diagnostic at most.

Act as an expert in ocean drift and transport modelling, working from the literature and from cases with later
ground truth (AF447, drifter studies), not from this project's prior code. Finding errors in published or prior
methods is part of the job.

## 2. Contract (changes need Pete's agreement)

1. Return a likelihood, never a map. No source-cell area factor in the weighted-sample update.
2. Each find is used once per run, with declared IDs. Primary evidence is the stringent identity set of
   `debris-evidence-audit.csv`; the expanded set is partly circular (identification cites drift modelling) and is a
   labelled sensitivity only. Published drift results are an overlay, never evidence.
3. Score the shared impact samples; the source grid is a numerical device, not a second posterior.
4. Smooth, with explicit model error, no floors. Not computed is flagged, counted and carried at the seed's weighted
   mean (shared contract rule 4).
5. Be accurate where the core has its mass and along the whole arc the core allows, including its thin northern tail.
6. Measure Monte Carlo adequacy and report unconverged results as unconverged (§6).
7. **Ocean models.** `ocean-model` is a declared alternative shared with Pleiades: GLORYS12V1 (0.494 m) + ERA5
   windage, and GlobCurrent (0 m total current) + ERA5 with product-relative windage (audit F1). Policy:
   - headline: equal prior weights, combined in likelihood (mean of L, never of normalised maps);
   - main sensitivity: GlobCurrent alone, because the independent GDP drifter replay favours it for undrogued
     drifters (2-day error 14 km against 19-21 km; `results/ocean-transport-error-gdp-replay.md`);
   - GLORYS12 alone is always reported too (it resolves the Leeuwin Current better, which matters for Australia);
   - weights updated by the debris evidence itself are a labelled diagnostic only: the same few finds would both
     choose the model and locate the impact, and the update depends on the flight-path prior.
8. Marginalise the shared ocean once, outside the product over objects.
9. Declare every sampling distribution; an object's windage persists along its track.
10. Do not double-count wind or waves: GlobCurrent's 0 m current already carries wind-driven flow (audit F1).
11. One synthetic-recovery test plus hand-computed fixtures.
12. **Rescoring rule.** A new core or end-of-flight run is a scoring pass on the stored node surfaces (minutes, no
    transport). New transport is justified only by a failure in §6.
13. **Durability.** Node tables, surfaces and harness source are committed to `results/`; per-impact columns and
    large binaries go to `mh370-exchange/debris-drift/` with SHA256SUMS. Never leave them only in a workspace (the
    run A surfaces were lost this way once and had to be rebuilt).

## 3. What drift consumes and returns

- Consumes: end of flight's impact samples (`impacts32.npy`, compact float32, read with end of flight's
  `compact_impacts.load`), row-aligned per stratum and seed; end of flight's own per-impact weights, built by
  `option_table_0019.seed_terms` unchanged.
- Returns: per-impact columns `drift-lnL.npy` (`export_per_impact.py`: lnL per model and bandwidth, state flags,
  equal-weight mean), node tables `nodes.csv` per model, and the composition statistics of §5.
- Does not own: `crates/ocean` (shared transport). Changes there go through a request in `coordination/`.

## 4. Model settings (declared; change only with a recorded reason)

- Domain 15-160 E, 50 S-0 for anything that touches Australia; 15-120 E is acceptable for find-coast-only work.
- Objects: three classes (flaperon, low-exposure exterior, high-windage interior) with persistent windage draws.
- Transport error: eddying ocean-error model sized from the GDP replay; diffusivity K log-uniform 100-1000 m2/s;
  four environment realisations per run.
- Recovery model: segment arrivals with an exponential reporting delay (60 d), awareness periods split at
  29 Jul 2015 and 1 Mar 2016, window end 30 Jun 2016; find-coast relative levels 0.1 / 0.5 / 1 by period
  (provisional prior, log-normal SD 1); importance splitting for rare find coasts (Rodrigues, Mossel Bay).
- Refloat off by default; 1/69 and 1/200 per day are declared sensitivities.
- No sinking or break-up is modelled; a survival-weighting sensitivity is reported (§5).

## 5. The Australian non-recovery term

- Only coast where people go can support "debris did not arrive" (Pete, 15 Oct 2026). Detection is stated relative
  to the find coasts, never as an absolute probability (Pete, 17 Oct 2026: his absolute tiers are not used).
- **Headline scheme (Pete, 17 Oct 2026):** ABS RA 2021 tiers from the segment map: major city + inner regional
  weight 1, outer regional 0.3, remote and very remote 0. Australian level relative to the find coasts' peak
  awareness: central 0.5, declared range 0.3-0.65. Basis: an Augusta item was reported to police and assessed in
  April 2014; the ATSB was still receiving public reports from Australian beaches in October 2014, when it also
  said publicly that debris had more likely drifted west; 95 % of modelled Western Australian arrivals come before
  the flaperon (median about September-November 2014). The likelihood compares each coast's alertness when its own
  debris arrived; on that basis option B (Australia at 1) makes Perth about 1.8 times as alert as the find coasts.
- Always report beside the headline: no Australian term; populated (major city + inner regional) only; the full
  detection curve; the sinking and refloat sensitivities.
- The term is reconstructed with the fitted law Delta = -k ln(1 + W/(cF)) from the 15-160 E pilot and was defined
  after results were seen: it is labelled post hoc until a dedicated run with these tiers produces it directly.

## 6. Required statistics, adequacy and the triggers for new transport

Every result reports, per ocean model and for the mixture, per 00:19 treatment and per end-of-flight family:
mean-latitude shift, log Bayes factor of the core against a uniform reference, drift mass in the core 90 % region
and core mass in the drift 90 % region, mode displacement (NM), ESS ratio, not-computed share; plus drift alone with
a flat prior along the arc. Error bars: transport-noise replicates from split halves (95 %), seed bootstrap, and
the bandwidth (25/50/100/200 km) and thinned-grid checks.

New transport is justified only if one of these fails (thresholds set 17 Oct 2026):
- not-computed share above 1 % of core mass in any reported cell;
- 95 % transport-noise half-width on the mean-latitude shift above 0.5 deg, or SD of ln BF above 0.3;
- a bandwidth or thinned-grid change moving the shift by more than its 95 % transport-noise half-width;
- a new region or time window that no stored run covers.
The remedy is targeted (more particles at the nodes carrying the core mass), not a full re-grid.

## 7. When drift disagrees with the core

Report the disagreement; do not reduce it. Diagnose it by component: ocean model, bandwidth, each find, the
Australian term and its detection assumption, 00:19 treatment and family, and the thinness of the core's northern
tail (drift cannot add mass where the core has few samples). State which components carry it and how much.

## 8. Deferred

Forcing beyond 30 Jan 2017 (5-year extension; GlobCurrent multi-year product retires 24 Nov 2026); sinking and
break-up physics; the five-class Australian segments (needs regenerated segments and a transport run); OSCAR
(comparison only, Pete 9-12 Oct).
