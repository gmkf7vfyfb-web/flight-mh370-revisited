# Where the wreckage is on the seabed, by type of flight end (core run (b))

Ocean settling, 10 Oct 2026, following the ruling of 15:20 -0600 (Pete): results per hypothesis family first, and any average only
beside a prior sensitivity. This splits settling's core-set result (`results/settling-core-set-next-run-b/`) by end of flight's
labels. `settling-seabed-wreckage-next-run-b-by-family.{pdf,png,json}` has rows A1 / A2 / B and columns for the five core 00:19 options.

**Update ~23:20 UTC 10 Oct: family mapping per ruling 6 as amended by end of flight (~22:45 UTC).** The primary figure and table now use
`family4_code` (code 4 maintained-then-lost → A2 'lost'; code 4 with an attempted but undemonstrated recovery → A1). The earlier
grouping (A1 = codes {1, 4}) is kept as a labelled sensitivity: `settling-seabed-wreckage-next-run-b-by-family-code4-A1.{pdf,png,json}`
and the section "Sensitivity: code 4 with A1" below. Samples: `mh370-exchange/settling/next-run-b-by-family/` (tag nrbg; ruling 6) and
`.../next-run-b-by-family-code4-A1/` (tag nrbf).

**Labels.** core (b) split-half NOT converged; two-tank bookkeeping only; dive class (b) PROVISIONAL; the point mass cannot unload;
breakup table PROVISIONAL; prior track 289.7°.

**Families.** These are end of flight's `family_labels(latent:onset_mechanism, latent:control_realised, latent:recovery_attempted)`
(smoke/compact_impacts.py at ba26890), `family4_code`, computed from the full-format columns (`WF_FAMILY_MAP=ruling6`, the default):
- A1 = family4 code 1: codes 1, plus code 4 where recovery was attempted but not demonstrated.
- A2 = family4 code 2: code 2, plus code 4 maintained-then-lost (sub-label 'lost').
- B = family4 code 3: codes 3 and 5 (5 = control lost en route).
- Code 6 (deliberate onset, then no intervention) lies outside B as ruled. It is in no panel, and its share is given in the table.

**Method.**
- Within an option, the posterior is restricted to the family and renormalised.
- Strata are weighted by P(stratum | data, option) × the family's share in that stratum. The first factor is end of flight's re-weighted
  P(family); it is fixed for Held Out, H1 and H2.
- Each option × family gets a systematic resample: 60,000 impacts for Held Out and 20,000 for the others.
- Each impact gets one settling draw on the real ocean (settling 9330d4c; 75-115 °E, 45-10 °S), with `unpowered` (airborne at 00:19:37,
  not powered at 01:15:56).
- Densities use a 0.02° grid with a 0.1° Gaussian; regions are HPD.

## 90 % area, same impacts → seabed (thousand km²), share of posterior probability, and impact ESS (ruling 6 mapping)

| 00:19 option | A1: exhaustion, no control | A2: exhaustion, controlled phase (incl. 'lost') | B: deliberate, before exhaustion | outside A1/A2/B (code 6) |
|---|---|---|---|---|
| 00:19 Held Out | 392 → 393 (+0.19 %); share 15 %; ESS 3.2 M | 671 → 673 (+0.32 %); share 33 %; ESS 7.2 M | 528 → 529 (+0.18 %); share 42 %; ESS 8.5 M | 10.8 % |
| 00:19 R600 BTO Only | 237 → 238 (+0.35 %); share 15 %; ESS 2.0 M | 387 → 389 (+0.39 %); share 38 %; ESS 5.2 M | 321 → 322 (+0.42 %); share 41 %; ESS 5.1 M | 6.0 % |
| 00:19 R600 BTO + Raw BFO | 85 → 86 (+0.77 %); share 11 %; ESS 52,856 | 244 → 245 (+0.39 %); share 25 %; ESS 120,516 | 220 → 221 (+0.31 %); share 57 %; ESS 279,970 | 7.6 % |
| 00:19 Holland H1 | not yet estimable (ESS 13; share 0 %) | not yet estimable (ESS 49; share 51 %) | not yet estimable (ESS 44; share 49 %) | 0.0 % |
| 00:19 Holland H2 | not yet estimable (ESS 4; share 0 %) | not yet estimable (ESS 29; share 31 %) | not yet estimable (ESS 103; share 68 %) | 0.7 % |


The share is the family's posterior probability under that option. End of flight reports that these shares are **close to its prior**
(about 56 % B, before code 6 was moved out of B) and barely updated by the data (~21:20 UTC). **Read each row as conditional on its
family, and not as evidence for that family.**

## What it shows

1. **Settling is the same small kernel in every family:** it adds 0.18-0.77 % to the 90 % area (the 0.77 % is A1 under R600 BTO + Raw
   BFO, the smallest region, 85,000 km²). Half the settled mass rests within 0.31-0.39 km of its impact and 90 % within 2.3-4.3 km.
   Family changes the impact PDF, not the settling.
2. **A2 gives the widest impact PDF in every estimable option**: 671,000 km² for Held Out, against 392,000 for A1 and 528,000 for B.
   A controlled or arrested descent can carry the aircraft further from the 7th arc. A1 is now the narrowest under every estimable
   option: with code 4 maintained-then-lost moved to A2, A1 holds only descents with no controlled phase (85,000 km² with the R600 BFO).
3. **The mapping moves probability from A1 to A2:** A1's share falls from 27 % to 15 % (Held Out) and A2's rises from 21 % to 33 %.
   B and code 6 are unchanged. The shares remain mostly prior (end of flight; coverage gaps G1-G4).
4. **H1 and H2 are not yet estimable in any family** (ESS 4-103). Under ruling 6 they have no A1 weight at all (share 0 %). Splitting by
   family does not help, because the shortage is in the 00:19 push-over, not in a family.
5. **Resample noise measured.** B has the same posterior under both mappings, and only the resample differs. Its 90 % seabed area differs
   by +0.5 % (Held Out, 60,000 draws), +2.1 % (R600 BTO Only, 20,000) and -1.5 % (R600 BTO + Raw BFO, 20,000) between the two runs.
   Differences between panels smaller than about 2 % are within resample noise.
6. **Not converged.** Core (b) does not pass split-half, so every area here inherits that.

## Sensitivity: code 4 with A1 (earlier PROVISIONAL grouping, `WF_FAMILY_MAP=code4-A1`)

| 00:19 option | A1: exhaustion, no control | A2: exhaustion, controlled to the surface | B: deliberate, before exhaustion | outside A1/A2/B (code 6) |
|---|---|---|---|---|
| 00:19 Held Out | 522 → 524 (+0.24 %); share 27 %; ESS 5.9 M | 714 → 716 (+0.35 %); share 21 %; ESS 4.5 M | 526 → 527 (+0.20 %); share 42 %; ESS 8.5 M | 10.8 % |
| 00:19 R600 BTO Only | 287 → 288 (+0.36 %); share 30 %; ESS 4.1 M | 416 → 417 (+0.40 %); share 23 %; ESS 3.1 M | 315 → 316 (+0.38 %); share 41 %; ESS 5.1 M | 6.0 % |
| 00:19 R600 BTO + Raw BFO | 159 → 160 (+0.42 %); share 21 %; ESS 107,703 | 273 → 275 (+0.43 %); share 14 %; ESS 66,614 | 223 → 224 (+0.30 %); share 57 %; ESS 279,970 | 7.6 % |
| 00:19 Holland H1 | not yet estimable (ESS 32; share 37 %) | not yet estimable (ESS 29; share 14 %) | not yet estimable (ESS 44; share 49 %) | 0.0 % |
| 00:19 Holland H2 | not yet estimable (ESS 21; share 25 %) | not yet estimable (ESS 18; share 7 %) | not yet estimable (ESS 103; share 68 %) | 0.7 % |


## COVERAGE (ruling ~15:45 -0600)

Settling's own sets, gaps and status are as in `results/settling-core-set-next-run-b/README.md` §COVERAGE: single release point, first seabed
contact, more than 48 h afloat handed to drift, the ocean window, and the PROVISIONAL breakup table. None of these changes the areas at 6 NM.
The family-specific gaps are inherited from end of flight (~21:20 UTC), and each panel carries them:
- **A2** is only commanded profiles (ditching approach, best glide, demonstrated recovery) at up to 6,500 ft/min. There is no deliberate
  push-over, and no Boeing case calibrates A2.
- **B** is only deliberate descents starting after 00:11. Earlier ones exist only in end of flight's 22:41 arms and in core's descent-climb
  stratum.
- **A1** is not yet Boeing-calibrated (fixed-C_L point mass; it cannot unload).
- **Code 4 → A1** is PROVISIONAL; its sensitivity (with A2) is not yet drawn.
- **Code 6** (10.8 % of Held Out, 6.0 % of R600 BTO Only, 7.6 % of R600 BTO + Raw BFO) is in no family panel.

## Not computed, and published samples

Impacts north of 10 °S (outside settling's window) are **carried at the impact position** (architecture 16:25 -0600, item 1): 2 per family
under Held Out (weight 3.3e-5 each family) and 1 for B under R600 BTO + Raw BFO (5.0e-5); none elsewhere (both mappings). They are reported per panel in the JSON.

`mh370-exchange/settling/next-run-b-by-family/` (1.7 GB; ruling 6) holds `nrbgF{0,1,2}_{impacts,elements}.f64`, `nrbgF{0,1,2}_source.npy` (stratum
index, seed, impacts.npy row; composer gap 16), `nrbg_draws.npz`, `nrbg_info.json`, `SHA256SUMS` and `READY` (the code4-A1 sensitivity is in `next-run-b-by-family-code4-A1/`, tag nrbf). F0 = A1, F1 = A2, F2 = B.
Layout: `mh370-exchange/settling/next-run-b-core-set/README.txt`.

## Reproduce

    WF_FAMILY_MAP=ruling6 python3 wf_family.py prep   <EoF smoke dir at ba26890 or later> <mh370-exchange/end-of-flight/next-run> <summary/family-evidence-next-run-b.json> nrbg
    SETTLING_FIELD_IN=field/nrbgF<j>_impacts.f64 SETTLING_FIELD_OUT=field/nrbgF<j>_elements.f64 cargo test --release -p mh370-hypotheses settling::tests::wreckage_field -- --ignored   (j = 0, 1, 2)
    python3 wf_family.py render <EoF smoke dir> <core runs/reference-289/run.json> nrbg next-run-b 9330d4c ba26890     # sensitivity: WF_FAMILY_MAP=code4-A1, tag nrbf, EoF 43262c31

The prep took 15 min (two passes over 16 seed files) and the settling passes took 8.6 min, both at 2 threads outside the heavy lock.
For run C the same scripts read the compact format; the family codes are already in it.
