# Australian non-recovery term: design (brief section 13 item raised by Pete, 12 Oct 2026)

12 Oct 2026 ~14:30 UTC, ocean drift module. Pete raised the priority (12 Oct, this thread) and extended it from Western Australia to
**all Australian coasts** ("It's actually all of Australia so far as I know").

## Evidence (sourced)

- No MH370 debris has been confirmed on any Australian coast; items reported were examined and ruled out, e.g. Augusta WA, April 2014
  (ATSB: "highly unlikely to be from MH370") and Kangaroo Island SA, June 2016 (ATSB examined and dismissed it). These show that finds on
  Australian coasts were reported and assessed from April 2014 (brief, p. "Context that governs how the debris is used").
- CSIRO Part I (griffin2016parti, printed p. 17): Australian observer density "is low compared to most shores in the west Indian Ocean
  but awareness of the significance of a find, and likelihood of reporting that find, is presumably high"; the WA absence argued against
  bands near 33-35, 36-37 and 39-42 S. p. 20: no debris ever found on Australian shores favours bands where the flow was westward.
- ATSB AE-2014-054 (2 Nov 2016), Fig. 11: simulated drifters from some arc regions made landfall on the WA coast, judged inconsistent with
  the observations. Undrogued drifters reaching Australia land mostly on the southern coast and Tasmania (third-party compilation; to be
  checked against GDP before use).

## Model (G1, already anticipated in the find-episodes design)

Each find enters as q_j(x, nu) / Q(x, nu); Q sums detection-weighted arrivals over every block (segment x period) with P_I > 0. Adding
Australian segments with zero finds adds their arrivals to Q only: sources that send debris to Australia lose likelihood in proportion,
through the shared latent levels nu (marginalised). No veto; explicit model error via nu's prior (brief).

- **Segments (proposal):** S7 south-west WA (Shark Bay to Esperance, populated), S8 north-west WA (Shark Bay north to the Kimberley),
  S9 southern coast (Esperance to Victoria, incl. Kangaroo Island), S10 Tasmania. GSHHG beaching already reaches all of them.
- **Levels (the choice for Pete):** ln nu prior mean by Australian segment and period, sigma 1 as for the find coasts. Options to be
  computed in ONE run (levels are linear in the stored coefficients, so alternatives cost almost nothing):
  - A: same as the find coasts in each period (ln 0.1 / ln 0.5 / ln 1 for I1 / I2 / I3);
  - B: high awareness from the start: ln 1 in every period for S7 and S9, ln 0.3 for S8 and S10;
  - C: low observer density: ln 0.3 in every period, all Australian segments;
  - D: none (current result), for comparison.
- **Code (module only):** per-segment level means (override of ln_mean_by_period per segment) and `levels.alternatives` producing extra
  columns `ln_l_lev_<name>` (+ halves). Tests: an Australian segment with level 0 changes nothing; a uniform level cancels (brief).

## Compute

The node tables store only the six find-coast segments, so the transport must be re-run with the new segments: full scale is about
15-17 h per ocean model under the heavy lock (710 nodes). Plan: **pilot first** (GLORYS12, every 4th node = 178 nodes, 10^5 particles,
about 4 h under the lock) to see whether the term matters; full both-model run after that. The full run can also raise particle counts at
the southern Mossel-Bay-limited nodes (pending Pete), so one run closes both items.

## Addendum (12 Oct, after Pete's notes): population density and the dedicated searcher

- **Population density (Pete, with the ABS Remoteness Areas map).** Australian segments are now built by ABS remoteness class
  (ASGS Ed. 3 RA 2021, `prepare/pilot/make_australia_segments.py`): region (WA; SA-Vic-Tas; NT-Qld-NSW; Indian Ocean territories) x class
  (major city + inner regional; outer regional; remote + very remote). Level priors are then set per class, on the same relative scale as
  the find coasts. RA 2021 is used for 2014-2016 (declared; remoteness changes slowly).
- **One dedicated searcher.** Blaine Gibson found the Vilanculos "No Step" panel with a local boat operator (27 Feb 2016) and, with locals he
  worked with, the Antsiraka items (June 2016); by his own count 9 of about 22 items were his finds (press, Dec 2016). Paindane was found
  independently (Liam Lotter, Dec 2015) and Pemba by residents. He went to Mozambique partly because oceanographers had told him debris
  might wash up there (press, Mar 2016): **search effort followed drift predictions**, a mild circularity, limited in q/Q but not zero.
- **Model consequence:** detection levels on S3 (southern Mozambique) and S5 (NE Madagascar) rose with his visits, not only with the
  general post-July-2015 rise. Labelled sensitivity "searcher": ln mu + ln 3 on S3 and S5 in I3 (Mar-Jun 2016), as a level alternative
  from the same run. Australia had high awareness but passive reporting (Augusta 2014, Kangaroo Island 2016), so its level relative to
  Gibson-searched coasts may be lower than "high awareness" suggests; hence options high / equal / low.
