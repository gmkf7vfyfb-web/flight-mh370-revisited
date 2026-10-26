<!-- ADOPTED by Pete, 2026-10-18 00:41Z (coordination session). Supersedes the previous master prompt, which is kept in git history. Source draft: threads/drafts/pleiades-v2-DRAFT.md -->

# Pléiades and COSMO-SkyMed — mission and master prompt, version 2 
> **STANDING RULE ON LABELS (Pete, 22 Oct 2026). Applies to every agent, thread, track and sub-agent.**
> 1. **No label may be added without Pete's explicit approval.** This covers every label that stops, limits or discounts the use of a source, dataset or file: "closed access", "paywalled", "not held", "unobtainable", "restricted", "blocked", "unusable", "GAP" set because of access, and any new one of that kind.
> 2. Pete holds the right to use everything stored in the repo, the Google Drive and the project source folders. A publisher's access status is not a reason to avoid, discount or leave out a source.
> 3. If a source cannot be fetched: search the artifact store (filenames can be raw DOIs, such as `art%3A10.1007%2F...pdf`), the repo papers folders on both branches, ~/Downloads and the Drive; then write exactly **"not retrieved — ask Pete"**, record where you searched in `results/source-access-ledger-2026-10-22.csv`, tell Pete, and carry on. Nothing is left out of an analysis or a note because of it.
> 4. To use any other label of this kind, ask Pete first and wait for his answer. Caveats Pete has already required (for example "PREDICTIVE, NOT CALIBRATED", C1/C2, "digitised", chart footnotes, provenance records) stay as written.


**Status.** of 17 Oct 2026, written by a general-profile session working to the v1 brief. It folds into one text the rulings
recorded in `coordination/PLEIADES.md` and `coordination/architecture.md` from 8 to 17 October, and the module's results to date.
Until Pete adopts it, `threads/master-prompts/pleiades.md` (v1, 8 Oct) stays in force. Where this draft and v1 differ, the
difference is a ruling or a result; the source is given in brackets.

**Authority, once adopted.** This file, then `ARCHITECTURE.md` (including the governing principle and composition rule 5 as revised
17 Oct), then `ISO Sept 28 Status/threads/master-prompts/common.txt` for the shared contract. Rulings in the inbox after the adoption
date override this file until it is next revised. Prose in the withdrawn prior-work share is reference only; its data and tests may be used.

**Module location.** Code: `engine/hypotheses/pleiades/` on branch `hypothesis/pleiades`. Results: `results/pleiades/` on
`claude-science-sep29`. Exchange: `~/Downloads/mh370-exchange/pleiades/`.

---

## 1. Mission (unchanged)

A conditional hypothesis, labelled as one on every figure, table and sentence.

**H: at least one of the objects imaged by Pléiades on 23 March 2014 (GA Record 2017/13) or detected by COSMO-SkyMed (four
possible contacts, F1-F4) came from 9M-MRO.** The module asks which impact locations are compatible with transport to the observed
positions at the observed times, and returns that as a log-likelihood on the shared impact samples. The prior π on H is swept.
Everything the module knows comes from where and when the objects were seen; nothing comes from what they look like.

## 2. Contract

- **Returns** a log-likelihood per impact sample, `ln L(s) = ln[(1 - π) + π Σ_c w_c p(y_c | s) / q_c]`, from normalised, analytic,
  seed-free transport densities. `absolute_scale = true`; never max-normalised.
- **Paired outputs, always:** the conditional PDF under H with its tension quantities - ln S with its p value, the two-way 90 % region
  overlap, and the mean and mode shift in NM. **A narrow conditional is not evidence of precision.** [v1 §2; ln S added 9 Oct]
- **Absolute Bayes factor and P(H | D) are not reported.** They carry the label "not interpretable until the Poisson and footprint
  term exists". The same holds for COSMO: no Bayes factor and no provenance probability. [P1-P3 endorsed; 9 Oct 18:30]
  **Exception:** likelihood ratios of another module's data under H against without H (for example the found debris, §9) are
  interpretable and are reported, because the missing background term cancels in them.
- **Declared alternatives, shared names:** `ocean-model` = GLORYS12 + ERA5 and GlobCurrent + ERA5 with product-relative windage
  (equal prior, marginalised jointly with every other ocean-dependent module) [9 Oct 17:50, 11 Oct]; `cosmo-contact-set` (F1-F3, F1-F4);
  `cosmo-pass` (dawn 20 Mar / dusk 21 Mar, equal prior, marginalised); `cosmo-date` (21 or 23 March, separate); `object-rating`;
  `cluster-weight` (equal, by count); transport-error correlation ρ in {0, 0.25, 0.5}. OSCAR is a comparison only and enters no likelihood.
  BRAN2016 is dropped. [9 Oct]
- **Headline setting:** ρ 0.25, both ocean models, GlobCurrent product-relative, Pléiades rating 5 (6 clusters, equal weights) plus all
  four COSMO contacts, pass-marginal. GLORYS12 only is shown beside it in every table. [11 Oct 20:55Z]
- **Never** pre-select impact samples, filter the core posterior or restrict a grid. Rows the module did not compute are carried at the
  neutral value; exclusion is a labelled sensitivity only. [composition rule 2; composer pass-0 ruling 1]
- **Whole arc (new, 17 Oct).** The likelihood must be valid across the whole arc span of the flight prior, not only 30-40 S, and the
  module's evidence is also reported **alone, on a prior uniform along the arc**, beside the core-combined result (composer.md §0,
  ARCHITECTURE.md rule 5 as revised). The wide surfaces span 45-5 S, 78-115 E at 0.05 deg; cells outside the computed support are
  stored as not computed and read as zero likelihood. Confirm that support covers the whole arc span before the composer's arc-wide pass.

## 3. There is no identity likelihood (unchanged)

The morphology screen (26,976 masks, eight families) is negative three ways: controls match as well as 777 parts, the flooding model is
not favoured, and PCA loss is not a probability. Do not redo it without a genuinely new approach, raised first. Shape evidence is never
presented as support for H. No imaged object is flaperon-sized (smallest rating-4 is 18 m², rating-5 23 m²; a flaperon is seven to nine
times smaller), so the flaperon-replica windage check is closed for Pléiades objects. [9 Oct]

## 4. Objects and timing

- **Pléiades:** GA Record 2017/13 Tables 1-4 (obtained from GA; cite its page numbers): 70 objects, rating 5 = 12, rating 4 = 27.
  The PHR_2 object 12 latitude-longitude transposition is a typo, corrected and recorded in the data manifest. Rating-5 objects form six
  clusters at a 3 km linkage threshold; the threshold is a declared parameter with reported sensitivity. Rating 4 is carried at a
  declared weight under `object-rating`, never dropped. Scenes are about 25 km x 20 km, about 100 km apart, cloud- and glint-affected.
- **Acquisition times, from orbit geometry** (both satellites sun-synchronous) [9 Oct]: Pléiades (descending node 10:30 local) 04:24 UTC
  at PHR_4 and 04:28 UTC at PHR_1/PHR_3, 23 March, ± 25 min. COSMO-SkyMed (dawn-dusk) has two candidate passes: dusk 11:52-12:00 UTC on
  21 March, or dawn about 23:52 UTC on 20 March, ± 25 min each. The COSMO-to-Pléiades interval is therefore about 40.5 h or 52.5 h.
- **COSMO-SkyMed contacts** F1-F4 (positions in the inbox, 9 Oct). F4 is the isolated south-western point; run with and without it.
  Footprint and target sizes are unknown and carried as missing. The footprint is needed only for an absolute background term, which
  also needs the contact catalogue, detection threshold and SAR mode; the conditional p(x0 | C, H) does not need it. [9 Oct 18:30]
- **CNES licence:** object crops are © CNES. Never commit them; read by path.

## 5. Transport and likelihood (done; keep the tests green)

Forward transport only, from candidate impact locations, through the shared `mh370-ocean` crate. Analytic Gaussian spread: random walk
plus Ornstein-Uhlenbeck transport-model error calibrated against drifters (measured 15-day error about 95-120 km per component),
plus position errors. Correlated transport errors between objects enter through ρ (measured 0.07-0.41 GLORYS12, -0.16 to 0.31
GlobCurrent at 40-80 km). Stokes is absorbed in the windage (leeway-absorbs-Stokes); an explicit WAVERYS-Stokes arm is an extension,
default off. Tests: the two ported transport tests, normalisation of p(y | s), seed independence, the enumeration counts, injection-recovery.
The prior-work likelihood-handoff builder (max-normalised) stays discarded.

## 6. Two-epoch windage calibration: done, negative, demonstrated [9-11 Oct, `results/pleiades/d5-two-epoch.md`]

Matching enumerated, never sampled (229 to 18,001 assignments; 2,202,409 for the 39 rating-4-plus-5 objects, also enumerable), with the
pass time marginalised jointly. **The pair carries no usable windage information: at most 0.15 bits.** Injection-recovery shows it is the
data, not the method: recovery needs a transport spread of about 6 km or less per component and a confident counterpart prior. The pass
time adds a second, smaller loss. Report this as a result; it is not re-opened without a new data source.

## 7. What the module has found (latest first; every entry provisional on its run's labels)

- **Run J waypoints, found debris (17 Oct, `results/pleiades/finds-test/`).** Likelihood ratio of the drift data under H against the
  flight posterior, Held Out, both models: finds only +0.78 (field) / +0.49 (shared impact point), within noise; with the Australian
  non-recovery term (populated coasts, reconstructed) +1.52 / +0.81. The support is for the 34-36 S band, not for the field (65th-72nd
  percentile among drift nodes there). Agrees with drift's Australian-only figure (+0.75).
- **Run I (12 Oct, `results/pleiades/run-i/`).** Under H every 00:19 treatment moves to about 35.5-35.6 S, 92.0-92.4 E, 109-140 NM
  north-east of the flight-only PDF; ln S -1.07 to -1.65 (p 0.03-0.16). H barely separates the 00:19 treatments (ln E[L_H] within 0.25 of
  Held Out). D3, D4, D5 under H are below the ESS gate of 1,000.
- **Earlier runs** (B, C, D-he, H) are superseded by run I and run J for every purpose except provenance.
- **§11 western residual (8-9 Oct, `results/pleiades/s11-western-reach.md`, `rerun-289/`).** The flight and fuel posterior does not decide
  it; the descent reach does. Recorded: 4-5 % of the conditional mass in the western lobe at 30 NM or more inside the arc, about 2 % at
  50 NM or more, provisional on the 295.66 reference.

## 8. Current work, in order

1. **Pléiades on run J, all strata** (waypoints 24 seeds, free 18, descent-climb 16, repro-radar 16; both-burst supplementary set for D3
   and D4, normalised by `thinning.weight_sum_in`; joined V2 for planned descents before 00:11). Per-impact columns in the exchange format,
   the H-conditional two-factor table, tension, close-ups to Pete's standard. Lookup on the existing surfaces; no new transport.
2. **§11 on run J impacts directly** (column `arc_distance_nm`, Boeing-calibrated glide), replacing the declared-reach sweep.
3. **The module's evidence alone on a uniform-along-arc prior** (composer §0), when the arc-wide sample set exists.
4. **After all searches** on run J, once searched areas posts run J columns with Ocean Infinity in the base (ruling 13 Oct).
5. **Holland H1/H2 under H** on the both-burst supplementary set, reporting ESS against the gate.

## 9. Deferred, to raise again with Pete

A correlated multi-object likelihood beyond the ρ surfaces; the Poisson term for debris that should have been seen and was not, over the
scene footprints (which are not assembled); COSMO as its own observation ID for the composer (composer ruling 7); a field-release version
of the found-debris test (release from the field on 23 March, test C of the 17 Oct design) if the 8 March approximation is ever decisive;
the seabed imagery question.

## 10. Standing rules (unchanged; text in v1)

Side questions (Pete, 10 Oct): answer, then return to the work; end a turn only when the backlog is empty or blocked, and write which items are
blocked and on what. Sampling coverage (Pete, 10 Oct): every results note has a COVERAGE section (feasible set, model reach, proposal
coverage, gaps, ESS per option). Charts: footnoted with run, parameters and assumptions in two short versions; no project codes in titles,
axes or legends; standard statistical terms used as such.

**Files held off the Mac (Porsche drive):** some project files are only on Pete's external drive. Read `coordination/README.md`, section "Files held off the Mac (Porsche drive)", before you take a file as lost. (26 Oct 2026)
