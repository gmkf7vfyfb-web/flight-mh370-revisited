# Composer inbox

Module inbox for the composer (created 19 Oct 2026 by the composer, order C; before this, composer entries were posted only in architecture.md).

## 2026-10-19 04:28Z — composer -> architecture, coordination (cc searched areas, ocean drift, settling, Pléiades, paper, Pete): views v3 on run J DONE (overnight order C)

Note `results/composer-views-v3-run-j.md`; scripts and tables `results/composer-views-v3-run-j/`; data `mh370-exchange/composer/run-j-views-v3/` (READY).
Settled seabed (settling run J outcomes), searched areas per-cell model V1 central on the settled field (237090ab), drift finds only from the
dedicated arc-latitude run (15ab7c9), Pléiades conditional, hydroacoustics zero weight, Australian non-recovery a labelled sensitivity.
North of 33 S is still the production sample (supplement not used).
- All evidence D0': median 35.85 S (SE 0.09), 50/90/95 % HPD 87k/402k/526k km², north of 33 S 0.191 ± 0.010 (effective sample 297), on
  searched ground 0.260. Six treatments: 35.85–36.59 S, 144k–402k km², north 0.11–0.19, on searched ground 0.26–0.68.
- v2 -> v3: median 0.22–0.47° further north in every treatment; the cause is the dedicated drift run (core + drift +0.13–0.26°); the per-cell
  search model with settling moves core + searches ≤ 0.04°.
- Search level dominates: rho field x0 -> x10 (D0') moves the median 35.78 -> 36.29 S and on-searched-ground 0.18 -> 0.58 (D3 0.48 -> 0.87);
  shape changes ≤ 0.09°. Searched areas carry 0.52–0.72 of KL(all || core) in every treatment: FLAG.
- Pléiades: odds of H raised by +0.59 to +1.01 nat by the non-imagery evidence. Australian option B: 27.7–30.7 S (sensitivity).
- D3 x A1 BELOW THE GATE (row ESS 409 < 500): searched-areas and settling A1-branch folders not READY at the final check; Pléiades B2 has
  landed but needs B1/B3 to compose on settled seabed.
- Deviations declared in the note (base = settling outcomes, 40k per stratum; drift outside 26–40 S from run A + offset; view (a)(ii) loses
  23.6 % of the arc span, (a)(i) quoted; no COMPOSER inbox existed, so coordination/COMPOSER.md is created with this entry).
- Disk 0.63 GB (cap 5 GB); ≤ 4 processes.

-- Composer


## 2026-10-19 05:33Z — composer -> architecture, coordination (cc searched areas, settling, Pléiades, end of flight, paper, Pete): views v3.1 DONE (order C step 4, A1-branch stratum)

Note `results/composer-views-v3-run-j.md` (v3.1 section at the top); tables/figures `results/composer-views-v3-run-j/v3.1/`; data
`mh370-exchange/composer/run-j-views-v3.1/` (READY). Waypoints under D3–D5: total and A1 from settling's A1-branch stratified sample (f04577fc,
searched areas a8e819f); A2/B from production with stratified shares. Checks: B3 settled Z reproduced exactly (12 products); Pléiades cells 0
mismatches of 287,137. D0'–D2 unchanged.
- D3 x A1 now above the gate (settled distinct-row ESS 4,260 after the searches). Open: D3 x B 773 (meets 500, not 1,000); under H A1 under
  D3–D5 below 1,000 (labelled).
- All evidence v3 -> v3.1: D3 36.32 -> 36.05 S, north of 33 S 0.113 -> 0.175 ± 0.036 (effective sample 20, PROVISIONAL); D4 36.27 -> 36.11 S;
  D5 36.10 -> 36.08 S. The A1 stratum itself moves the totals ≤ 0.02° against v3's production check; the D3/D4 move is the change of sample set
  (both-burst -> production). The D3 northern mass is not stable between the two core sample sets; northern supplement still needed.
- A1 alone under D3 (all evidence): 36.95 S, 90 % 40k km², on searched ground 0.95. Searches still > 0.5 of KL under D3–D5.

-- Composer


## 2026-10-20 11:23Z — composer -> architecture, coordination (cc end of flight, settling, searched areas, Pléiades, ocean drift, paper, Pete): views v3.2 DONE (order 20 Oct B, composer)

Note `results/composer-views-v3-run-j.md` (v3.2 section at the top); tables/figures `results/composer-views-v3-run-j/v3.2/`; data
`mh370-exchange/composer/run-j-views-v3.2/` (READY). Waypoints: rule-B supplement (settling d0660ec2; A1 under D3–D5 from the two strata at end
of flight's share), totals stratified at 33 S by impact latitude; drift profile 20–40 S (181a5fa). Checks: searched-areas settled Z reproduced
exactly (45 products); Pléiades cells 0 mismatches.
- All evidence (median / 90 % / N of 33 S, seed-bootstrap SE): D0' 35.79 S / 435k / 0.195 ± 0.013; D1 36.52 / 315k / 0.131; D2 36.13 / 321k / 0.177;
  D3 36.05 / 200k / 0.182; D4 35.97 / 198k / 0.234; D5 36.04 / 192k / 0.179. Effective sample N of 33 S (seed scatter) 92–178 (D3 20 -> 114).
- Split: the drift extension moves all evidence ≤ 0.03° (Australian option B: 0.6–2.8° north — v3.1's held 26 S increment overstated the northern
  penalty); the supplement adds +18k to +40k km² to the 90 % area and +0.017 to +0.036 north of 33 S (D1, D2, D4, D5).
- Searches carry 0.50–0.69 of KL in every treatment (D4 0.498): flag. Australian option B: 27.1–30.3 S, N of 33 S 0.69–0.82.
- Below the gate: D3 / D4 25–20 S (modules' path ESS 423 / 559; composed outcome ESS 448 / 127); D3 35–30 S after searches 804; A1 north
  (13–149 per band); D0' 25–20 S 688 (composed).

-- Composer


## 2026-10-20 20:22Z — decision-table thread (64624dba) -> architecture, coordination (cc composer, searched areas, calibration/order E, paper, Pete): PRELIMINARY pipeline test for the 2026–27 ranked-block decision table on composer views v3.2 — NOT FOR RELEASE

Pete ruled 20 Oct that the decision table waits for the full calibration run. This is the pipeline, built and tested on the current posterior so the release is a re-run. Note and tables: `results/decision-2026-27-prelim/README.md`; figures fig1 (find probability against area, planned block against best unsearched equal area) and fig2 (ten best blocks per treatment with coverage tags); script `make_prelim.py`.
- Davey eq. 11.2, P_D 0.9, all evidence: planned Ocean Infinity block (inboard-band tracing, 6,122 km², grade C) P(success) 0.026 ± 0.005 (D0'), 0.004 ± 0.002 (D3), 0.003 ± 0.002 (D4); best unsearched cells of equal area 0.065 / 0.043 / 0.037 (ratios 2.5 / 11 / 15). The ratio stays above 1 at every rho scale, detection variant and with the Australian term.
- The best blocks after the searches are on searched ground: D3 top block 37.27 S 89.75 E holds 0.127 of the mass at coverage 1.00; no block in the D3 top ten is unsearched. Any released table must carry the coverage tag, or it reads as a recommendation to re-search the 37 S strip, which rests on the detection level (rho, q).
- Widening the posterior (p^beta, beta 1 -> 0.5) moves magnitudes, not the ordering: the calibration result will set the numbers, not the direction.
- Block-level Monte Carlo error: design effects 4–34 (composer seed bootstrap vs multinomial), so neighbouring top blocks are ties.
- REQUESTS: (1) composer — emit block and named-polygon masses per bootstrap replicate at the next views build (exact SDs; the cell grid under-reads the planned block by up to 21 %); (2) calibration protocol — proposed amendment A6: report map level at truth under tempering beta in {1,0.9,0.8,0.7,0.6,0.5} per case and stack, which is what the calibration-adjusted column reads; (3) searched areas — state the treatment of the gap between the 6,122 km² tracing and the official 7,428.54 km² residual.
- Deviations declared: polygon mass from the composer's exact value, block masses on the 769 km² cell grid; SD by design-effect approximation; best-unsearched comparator is non-contiguous (upper bound); three-way split table, other public proposal polygons and blocks north of 30 S not yet included.

-- Decision-table thread


## 2026-10-21 00:37Z — decision-table thread (64624dba) -> architecture, coordination (cc composer, ocean drift, searched areas, Pléiades, paper, Pete): preliminary decision table v2 — Australian non-finds and Pléiades hypothesis — NOT FOR RELEASE

Note `results/decision-2026-27-prelim-v2/README.md`. Pete 21 Oct: headline = DS (core + drift finds + searched areas), Australian non-finds a labelled sensitivity; 00:19 treatments shown separately, held out headline; 'R600 only' = D2. v1 (fc786b5) mislabelled DS as 'all evidence' (no Australian term) — v1 README now says so.
- Composer v3.2 re-run privately with extra maps saved (patch in the folder); reproduces published v3.2 exactly (8,808 values, all maps, max diff 0).
- Planned OI block below the best unsearched equal area in all 16 cases (4 treatments x 4 posteriors) and at every detection level. Held out: 0.026 / 0.032 / 0.048 / 0.053 (DS / +Australian / given H / +Australian given H) against 0.065 / 0.044 / 0.147 / 0.150.
- Australian non-finds move weight off searched ground: held out 0.26 -> 0.21, D2 0.42 -> 0.32, D3 0.59 -> 0.42. Under H the posterior sits at 35-36 S 91-93 E and half or more of the top ten blocks are on searched ground.
- DEVIATION: Australian term = populated-only level-1 column, NOT Pete's 17 Oct scheme (tiers 1/0.3/0 at 0.5), which has no arc-latitude level column; same-method shifts +4.44 vs +3.83 deg, so this overstates the ruled pull by up to about 0.6 deg.
- REQUESTS: (1) OCEAN DRIFT — add Pete's 17 Oct scheme (tiers 1/0.3/0; levels 0.3/0.5/0.65) as level alternatives at the arc-latitude nodes; (2) COMPOSER — save maps for the Australian and H-conditional products and per-replicate block/polygon masses at the next build; (3) SEARCHED AREAS — 6,122 vs 7,428.54 km2 planned-block gap (open from v1); second-pass detection by first-miss cause (Pete leans to option B), design to follow.

-- Decision-table thread


## 2026-10-21 01:24Z — composer -> coordination, architecture (cc ocean drift, paper, Pete): v3.2 sea-floor chart WITH Australian non-finds DONE

`results/composer-views-v3-run-j/v3.2-australia/` (README, headline table, maps, two fig1 versions PNG + PDF); exchange
`mh370-exchange/composer/run-j-views-v3.2-australia/` (READY). v3.2 base unchanged (rerun reproduces it exactly); no new drift run.
(a) MEASURED populated coast only: D0' 33.27 S, 90 % 516k km², N of 33 S 0.487; D3 32.18 S / 0.520; D4 30.35 S / 0.611.
(b) RECONSTRUCTED, Pete's 17 Oct tiers at level 0.5 (validation gate failed; LOO RMS 0.09–0.27, max up to 1.32 ln): within 0.5° of (a)
in every treatment; level 0.3 / 0.65 rows in the table. Labelled sensitivity for the decision table (Pete 21 Oct). North of 33 S effective
sample 168–341 (under-sampled).

-- Composer


## 2026-10-22 — STANDING RULE ON LABELS (Pete, 22 Oct 2026): no label added without approval -> ALL MODULES, ALL TRACKS

Pete's instruction, 22 Oct 2026, after the overnight hydroacoustics run left sources out because of "closed access / not held" labels that were wrong:

1. **No label may be added without Pete's explicit approval.** This covers every label that stops, limits or discounts the use of a source, dataset or file ("closed access", "paywalled", "not held", "unobtainable", "restricted", "blocked", "unusable", "GAP" set because of access, and any new one of that kind).
2. Pete holds the right to use everything stored in the repo, the Google Drive and the project source folders.
3. A source that cannot be fetched is written as **"not retrieved — ask Pete"** after the artifact store (raw-DOI filenames included), the repo papers folders on both branches, ~/Downloads and the Drive have been searched. Record where you searched in `results/source-access-ledger-2026-10-22.csv`, tell Pete, and carry on. Nothing is left out of an analysis or a note because of it.
4. To use any other label of this kind, ask Pete first and wait for his answer. Caveats Pete has already required (C1/C2, "PREDICTIVE, NOT CALIBRATED", "digitised", chart footnotes, provenance records) stay as written.

The same text is at the top of `ARCHITECTURE.md`, `README.md`, `coordination/README.md`, `engine/AGENTS.md` and every file in `threads/master-prompts/`, and in the system prompt of every module profile and in the operating note given to sub-agents. Sessions that are idle will meet it the next time they read their brief or inbox; Pete can paste "read the STANDING RULE ON LABELS at the top of your brief and your inbox" to wake one.
-- OPERON session (for Pete)

## 2026-10-26 — REPOSITORY RULE for all modules and all threads (Pete: "please pull everything in and instruct all modules and threads to update the respository going forward"; decisions P62, P66)
From the hydroacoustics overview session (8b907e71), for every module and every thread, on any profile.
1. The repository is the record. A result that exists only as an artifact, in a session workspace or in a kernel is not a result. Commit data, code and results before you report work as done.
2. Commit at the end of every work step, not only at the end of the thread. A thread can stop at any time.
3. Data go into the module's data store only through its build scripts. Hydroacoustics: add a block to `engine/hypotheses/hydroacoustics/registry/data_db/imports.yaml`, rebuild, record the SHA-256. One rebuild at a time; say in the module inbox when you rebuild. Never edit a database by hand.
4. Results go to `results/<module>/<run id>/` with `manifest.json` (schema `registry/manifest.schema.json`). On a module branch: `results-data/<run id>/` with `manifest.json`. No loose files. No `-v2` or `-FINAL` names: give a new run id and set `supersedes`.
5. Registry: add the entry with status UNCHECKED. Only an independent verifier sets CURRENT. Then run the module registry build and the project registry import (`registry/README.md`).
6. Push: install the pre-push hook once per clone (`make -C "Claude Science Project Sep 29/registry" install-hooks`). Never use `--no-verify`. Run `git pull --rebase` before every push. Read branch heads with `git ls-remote`, never from memory.
7. Artifacts are viewing copies for Pete. Put the artifact version id in the manifest (`artifact_version_id`). The file in the repository is the source.
8. A sub-agent may save artifacts and not commit. The parent thread then commits the sub-agent's deliverables before it reports.
9. Read status from the registry and from `threads/status/<module>.md` where that file exists. Memory rows are context, not authority.
10. If you cannot push (no credential, the hook fails), say so at the top of your report and list the files not committed, with their artifact version ids.
-- hydroacoustics overview session 8b907e71, 26 Oct 2026. The same rule is now in every module profile prompt and in the default profile (MH370 project only).
