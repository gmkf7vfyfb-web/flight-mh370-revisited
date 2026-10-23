def r2(k,vn,c): return q2m[(q2m.key==k)&(q2m.variant==vn)][c].iloc[0]
README=f"""# Kadri H01W signal and Haixun 01 contact — FLIGHT leg (pre-registration Q1–Q3, Q4 undersampling)

18 Oct 2026. Leg owner: end-of-flight module session. Pre-registration: `../preregistration.md` (followed; statistics unchanged; deviations listed below).
**Source posterior: end-of-flight run J** (four route strata, 74 seeds, mixed by core P(family) 0.9982 / 0.0013 / 0.0003 / 0.0002) and, as a
separate labelled arm, **run-j-joined-v2** (planned descents with onset before 00:11, arm V2, waypoints only, seeds 1–21, D0–D4).
Every number carries its 00:19 option. Headline cells: `D{{d}} total q=0.333 (C2 silent)`. Run J is not formally declared final; Pete ruled (18 Oct) that enough is done to proceed.
Physics is PROVISIONAL (interim pitch-down, piloted turns, residual roll P(left) 0.8, round-3 free-flight laws). No search, drift, ocean or hydro-propagation term enters anything here.
**Primary locality: the 306.18 deg H01W bearing and its sea-level 7th-arc crossing X = 25.732 S 101.369 E (R7 = 1,591.3 km).** Haixun 01 (25.975 S 101.461 E) is a
secondary sensitivity line only (Pete, 18 Oct). Time origin: compact `T0_unix_s` = 1394236800 (00:00:00 UTC 8 Mar 2014), read through end of flight's loader; the 1394232081 origin was never used.

## Result in one paragraph

Run J *can* produce the Kadri arrival: 209,197 (00:52:03) and 222,368 (00:54:30) impact rows lie within 6 sigma of both arrival time and bearing, and 56,261 rows from 37,825
production parents end within 50 km of X 13–18 min after 00:19:29. But the satellite-conditioned flight posterior puts little mass there: 0.06–0.11 % in the bearing strip and
0.55–0.79 % within 200 km of X, depending on the 00:19 option. Against the pre-registered chance-transient background (18 transients / 21 min / 140 deg), the Bayes factor is
**below 1 under every 00:19 option and both readings**: ln B = {r2(HK[0],'T1.0','ln_B_rate'):.2f} (T) / {r2(HK[0],'C1.0','ln_B_rate'):.2f} (C) with the 00:19 data held out (D0), {r2(HK[2],'T1.0','ln_B_rate'):.2f} / {r2(HK[2],'C1.0','ln_B_rate'):.2f} with the R600 BTO+BFO (D2),
and −3.7 to −7.2 over D3–D5 and both bearing sigmas; arm V2 gives −4.5 to −9.6. A one-arrival background (no rate) adds ln 18 = +2.89, which is still below 0 everywhere.
**All of these are UNCONVERGED**: the conditional effective samples are 166 (D0, T) and 278 (D1, T) at best, 14–36 for the caption reading, and 1–27 under D2–D5, against
the end-of-flight thresholds (30 effective parents per seed for a Bayes factor, 1,000 effective impacts for a map). The trajectories selected by the sound are
**unpowered, piloted glides after fuel exhaustion**: final flame-out 00:16:30–00:18:30, 15–20 min aloft after flame-out, mostly families B (deliberate descent before
exhaustion, ~0.7) and A2 (~0.3), A1 ≈ 0. Most have turns (median heading change about 400–900 deg). Under the two-burst options (D3–D5) every selected row is an arrested dive
(−15,000 to −22,000 ft/min at 00:19:37) followed by such a glide. Powered flight after 00:19:29 (log-on cause other than fuel exhaustion) is in reach but carries ≤ 1 % of
the conditional. A targeted re-simulation (Q4) was designed, built and smoke-tested, but **not run**: the Mac had 15–18 GiB free against the 25 GiB floor.

## Q1 — run J posterior mass in the locality L (primary: bearing strip and discs around X)

Strip = 1,531.3–1,841.3 km from H01W, |cross-track| ≤ range × tan 1 deg. Share = posterior mass in the region (pooled, all four strata). ESS = Kish effective sample size of the
impacts in the region; eff. parents = (Σ_p M_p)² / Σ_p M_p². C1 share = fraction of the region's mass from the fuel-exhaustion log-on cause (q = 1/3, p(C1) = 0.75).
Seed SE = standard error of the share over the 24 waypoints seeds.

{MD_Q1}

Mass in L is almost the same under every option (0.06–0.11 % in the strip), but the **effective sample in the strip is below 200 for D2–D5** (175, 22, 13, 46): under-sampled (Q4).
By route stratum (conditional on stratum), the strip holds 0.085 % (waypoints), 0.198 % (free), 0.141 % (repro-radar) and 0.116 % (descent-climb) under D0 (`q1-by-route-stratum.csv`).
P(strip | family) under D0 is 0.080 % (A1), 0.071 % (A2), 0.096 % (B).

Impact time, final flame-out and minutes aloft after flame-out for impacts in L (5/50/95 %, minutes after 00:00 UTC; `q1-q4-timing-quantiles.csv`):
D0 strip: impact 20.5/30.5/45.5, flame-out 16.5/17.5/18.5, aloft 2.5/13.5/28.5 min; D2 strip 21.5/31.5/44.5, 16.5/17.5/18.5, 2.5/13.5/27.5; D4 strip 20.5/20.5/30.5,
16.5/17.5/18.5, 2.5/2.5/14.5. The share still powered at impact is 0.3–0.7 %. The final flame-out window 00:16:30–00:18:30 is set by the log-on lag model under C1 (C1 carries ≥ 99 %).

Arm V2 (planned descent before 00:11, joined at 00:11):

{MD_Q1J}

## Q2 — per-row acoustic likelihood and Bayes factor (all 470 M run J rows scored, not only rows in L)

L_i = N(t_obs − t_i − d_i/c; 0, s_t) N(306.18 − b_i; 0, s_b), c = 1.48 km/s, s_t² = (d_i 0.015/1.48²)² + 25 s², WGS84 geodesics from H01W (34.8903 S 114.1426 E).
B = Σ w_i L_i / λ, λ = 18 / (1,260 s × 140 deg) (Kadri Table 1 rate, pre-registered). The "one arrival" column uses λ = 1/(1,260 × 140) (sensitivity only).
Per-seed ln B is the same ratio within each waypoints seed.

{MD_Q2}

Arm V2:

{MD_Q2J}

Within-family Bayes factors (family prior held fixed, `q2-acoustic-bayes-factors.csv` columns ln_B_rate_A1/A2/B): A1 is strongly disfavoured (ln B −10 under D0, below −97 under D2–D5),
because uncontrolled A1 descents end within a few minutes of flame-out. A2 and B are about −5 to −7.

**Status: every Bayes factor above is UNCONVERGED.** The per-seed spread is 2–30 nats under D2–D5, and the conditional effective parents are below the threshold of 30 per seed.
The direction (ln B < 0) holds in all 24 options × readings and in the per-seed medians, but the magnitude is not established.

Conditional impact PDF (greyscale 50/90/99 % HPD) given each branch: `fig-conditional-impact-maps-sb1.0.png` (s_b 1 deg) and `-sb0.5.png`. Every panel is stamped NOT ESTIMABLE (ESS < 1,000).
The conditional is centred on X: the along-bearing offset from X is −3.5 km median (D0, T; 5–95 % −87 to +133 km), the cross-track offset is within about ±45 km, and
99 % of the D0 conditional lies inside 23.3–27.7 S, 99.1–103.6 E.

## Q3 — trajectories that fit the sound (top 1 % of rows by w_i L_i)

"Top 1 %" is applied to the rows that are acoustically compatible with the branch (6-sigma joint gate, s_b 1 deg: 209,197 rows for T, 222,368 for C). Their top 1 % (2,092 / 2,224 rows)
carries 97.3–100 % of Σ w_i L_i in every option. The weighted conditional (w_i L_i over all rows) is reported beside it (`q3-conditional-characterisation-weighted.csv`, `q3-top1pct-rows-summary.csv`).

Weighted conditional, 5/50/95 % (T = 00:52:03, C = 00:54:30; s_b 1 deg):

| option, branch | ESS | impact (min after 00:00) | min after 00:19:29 | final flame-out | min aloft after flame-out | A1/A2/B | powered after 00:19:29 | glide with turns | arrested dive (V/S < −8,000 ft/min at 00:19:37) | inside arc |
|---|---|---|---|---|---|---|---|---|---|---|
""" 
for _,r_ in CHW[CHW.variant.isin(['T1.0','C1.0'])].iterrows():
    f=lambda v: '/'.join(f'{x:.1f}' for x in v)
    README+=f"| {NM[int(r_.key[1])]}, {r_.variant[0]} | {r_.ess:.0f} | {f(r_['impact time, min after 00:00'])} | {f(r_['minutes after 00:19:29'])} | {f(r_['final flame-out, min after 00:00'])} | {f(r_['minutes aloft after flame-out'])} | {r_.share_A1:.2f}/{r_.share_A2:.2f}/{r_.share_B:.2f} | {r_.share_powered_after_0019a:.3f} | {r_.share_unpowered_glide_turns:.2f} | {r_.share_arrested_dive_after_steep_0019b:.2f} | {r_.share_inside_arc:.2f} |\n"
README+="""
Residuals (residual/sigma, run J convention: BTO 29 µs at 00:10:59, 63 µs R600 00:19:29, 43 µs 00:19:37; BFO 4.3177 Hz, predictive with the hand-off bias variance), weighted 5/50/95 %:

| option, branch | BTO 00:10:59 | BFO 00:10:59 | BTO 00:19:29 | BFO 00:19:29 | BFO 00:19:37 | V/S 00:19:37 (ft/min) | impact speed (m/s) | flight-path angle (deg) | tau90 (s) | heading change (deg) |
|---|---|---|---|---|---|---|---|---|---|---|
"""
for _,r_ in CHW[CHW.variant.isin(['T1.0','C1.0'])].iterrows():
    f=lambda v,p=1: '/'.join(f'{x:.{p}f}' for x in v)
    README+=f"| {NM[int(r_.key[1])]}, {r_.variant[0]} | {f(r_['BTO 00:10:59 resid/sigma'])} | {f(r_['BFO 00:10:59 resid/sigma (predictive)'])} | {f(r_['BTO 00:19:29 resid/sigma'])} | {f(r_['BFO 00:19:29 innov/sigma'])} | {f(r_['BFO 00:19:37 innov/sigma'])} | {f(r_['V/S 00:19:37 ft/min'],0)} | {f(r_['impact speed m/s'],0)} | {f(r_['flight-path angle deg'])} | {f(r_['tau90 s'])} | {f(r_['heading change deg'],0)} |\n"
README+=f"""
Residuals at 18:25–23:15 are **not assessed at this depth**: core run J does not store per-parent residuals before the 00:11 hand-off. Every row is conditioned on them through
its hand-off weight. The 00:10:59 values were recomputed from the m0011 hand-off states (engine forward model, `h0011_worker.py`). The matching rows sit near 0 sigma in BTO
and at about −0.7 sigma in BFO at 00:10:59, which is the value for paths ending north of 30 S. Columns that a given option does not use (for example the 00:19:29 BFO under D0) are shown for description only.

**Is a 15–17 min post-00:19 flight ending near 25.7 S in the feasible set, and how is it achieved?** Yes; it is in the model's reach and in the proposal (`q3-feasibility-near-crossing.csv`).
Within 50 km of X, 13–18 min after 00:19:29, there are 56,261 rows from 37,825 parents, carrying posterior mass 1.5e-4 (D0) to 2.9e-4 (D2). By mechanism:
- **Unpowered glide with turns** (flame-out before 00:19:29, ≥ 1 turn): 28,643 rows; 1.2e-4 (D0), 2.4e-4 (D2). This is the dominant route under every option.
- **Unpowered glide without turns**: 7,927 rows; 3.2e-5 (D0).
- **Arrested dive after a steep 00:19:37 descent** (V/S < −8,000 ft/min at 00:19:37, then > 10 min aloft): 6,291 rows; 6.5e-6 (D0), but under D3–D5 it carries all the mass near X (1.8e-4 under D3, 7.0e-5 under D4).
- **Powered after 00:19:29** (final flame-out after 00:19:29, log-on cause other than exhaustion): 19,691 rows, but only 6e-7 (D0) and ≤ 1e-7 (D2–D5). Inside the C2 cell alone
  (`q3-c2-cause-cells.csv`), these rows are powered to a fuel exhaustion at 00:31–00:37 and impact 1–3 min later (ESS 150 for D0 T). The competing-cause total gives this route ≤ 1 % because
  the 00:19:29 log-on is much more probable under C1 (lag density) than under C2 (uniform over 3,898 s).

**Position relative to the arc.** Kadri's eq. 4 places the impact inside the arc only for flight along the bearing after 00:19:29. The run J rows that fit the sound are not
constrained to that track. Their impacts straddle the arc: 49 % inside under D0 T, 26 % under D0 C, 14–25 % under D2, 3–89 % under D3–D5 (very few effective rows there).
Haixun 01 is 28.5 km outside the arc and inside the 99 % region of every estimable-direction panel. That is a sensitivity check only.

Haixun-centred sensitivity line (secondary): posterior mass within 50/100/200/400 km of Haixun under D0 is 0.105 % / 0.255 % / 0.700 % / 1.20 %. These are close to the
values around X because the two centres are 28.5 km apart (`q1-locality-mass.csv`, regions H50–H400).

## Q4 — under-sampling and the targeted run

ESS in the strip is below 200 for D2–D5, and the acoustic conditional has an effective sample of 1–278. This is a **coverage gap of the proposal (set c)**, not of the model's reach (set b).
Rows that fit the sound exist in every option, but too few children per parent land there.

Designed and built (`targeted_build.py`, `targeted_seed.sh`, `flight_leg_worker.process_targeted`); smoke-tested end to end on 40 parents × 16 children (seed 1, mechanics only;
not evidence). The combined seed's ln Z reproduced production to 5e-5:
- **Proposal**: re-simulate, in each of the 24 run-j-waypoints seeds, every parent with at least one production child that is acoustically compatible (6-sigma gate, either branch)
  or lies in the strip or within 200 km of X (mean 1,860 parents per seed, range 1,176–3,417), with **256 children** (production 16). Use a fresh RNG stream (seed 1000 + k).
- **Weights**: exact. Within-parent weights are unnormalised (row.weight × p/q / (M × children)), so every parent's children estimate its hand-off weight for any N.
  The selected parents' production children are **discarded and replaced** (stratified replacement; unbiased because the fresh draws are independent of the selection).
  Targeted cells get the production seed normaliser (cells_t + ln W_t − ln W_prod). The prior and every option likelihood are unchanged.
- **Expected gain**: about 16× in the conditional ESS where the parent count is not limiting (D0/D1/D2: about 2,600 / 4,400 / 380 for the 00:52:03 reading). D3–D5 stay limited by parent
  diversity (1–27 effective parents); they would need an aimed descent proposal (arrested-dive + glide branch) with the same exact correction.
- **Cost**: about 45.7 M rows; about 1.5 h at production rate behind the heavy lock; about 3.4 GB transient disk per seed (full impacts deleted after reduction).
- **Status: NOT RUN.** The Mac had 15–18 GiB free during this session (other modules' data), below the 25 GiB floor. Run when ≥ 30 GiB is free:
  `for k in 1..24: lockf -k /tmp/.mh370-heavy.lock bash targeted_seed.sh k <TDIR> children-256.toml`.

Fuel-exhaustion time for trajectories ending in L: see Q1. The final flame-out is 00:16:30–00:18:30 in every option and region (C1 share ≥ 0.99). Only the C2 cells reach later exhaustion (00:31–00:37 for the matching rows).

## COVERAGE

1. **(a) Feasible set** (777-200ER): powered flight to fuel exhaustion; at exhaustion either an uncontrolled descent (spiral/phugoid; A1) or a piloted glide, ditching attempt or circuit (A2, B).
   Glide from FL350–FL400 at L/D about 17–20 lasts 20–30 min (Boeing performance data as used in end of flight's descent-idle-floor/round-3 laws: grade C here, not re-read in this leg).
   A powered descent or a later flame-out under a non-exhaustion log-on cause is also in the set. Rapid descents (Holland-type, 15,000–22,000 ft/min at 00:19:37) with recovery are in the set.
2. **(b) Model's reach**: all of the above are produced by run J, with these limits: maximum time aloft after final flame-out is about 37 min, there is no flight at all beyond about 01:42,
   and piloted rapid descents are capped at 40,000 ft/min (end of flight's holland-estimable overlay: a declared cap, i.e. a reach limit). Stepped profile shapes are not eligible for push-over (declared gap in end of flight's README).
3. **(c) Proposal coverage**: 470 M impact rows; acoustically compatible rows 209,197 (T) / 222,368 (C); ESS per option in the strip 1,763 / 1,803 / 175 / 22 / 13 / 46 (D0–D5);
   conditional ESS 166 / 278 / 24 / 1.4 / 27 / 5.6 (T, s_b 1 deg) and 14 / 36 / 14 / 3.1 / 7.4 / 2.3 (C).
   By family (D0, T): A1 share 0.002 (ESS < 5), A2 0.26, B 0.74; per-family conditional ESS in `q2-acoustic-bayes-factors.csv`.
4. **Gaps**: (G1) proposal thinness near the bearing for D2–D5 and for every option given the caption reading. The fix is the targeted run (Q4); NOT RUN, disk floor.
   (G2) Residuals before 00:11 per parent are not stored, so they are not assessed. (G3) Arm V2 has no D5 and no tau90/attitude sidecar, so those are not assessed for V2.
   (G4) The 40,000 ft/min cap on piloted rapid descents is a reach limit (from end of flight; it does not bind for the matching rows, whose 00:19:37 V/S is −14,000 to −22,000 ft/min).
   (G5) run-j-both-burst (supplementary D3/D4 set) is not used in this leg.
5. **Parameter bounds used here** (all from the pre-registration): c = 1.48 km/s ± 0.015 (sound-speed spread); timing floor 5 s; s_b 0.5 / 1.0 deg; background 18 transients in 00:36–00:57, 200–340 deg (Kadri 2024, Table 1, grade B: cited, not re-read in this leg).

## Deviations from the pre-registration

- "Top 1 %" is applied to the acoustically compatible rows (6-sigma joint gate) rather than to all 470 M rows. In all rows it would be 4.7 M rows, almost all with L_i ≈ 0.
  The chosen set carries ≥ 97 % of Σ w_i L_i, and the weighted conditional is reported as well.
- The Q4 targeted run was designed and smoke-tested but not run (disk floor).
- Residuals at arcs before 00:11 are not assessed (not stored per parent).
- Arm V2 joined estimate uses seeds 1–21 only (22–24 were finishing at the time), and D0–D4 only.

## Reproduction and files

- Weights: `option_table_0019.seed_terms` from branch hypothesis/end-of-flight (5d060f0) exec'd unchanged with only its final reduction replaced, as in `results/drift-runj-2026-10-17`.
  This reproduces `run-j/summary/table-0019-mixture.json` exactly (ln Z and ESS of every D cell, e.g. D0 −7.5251 / 1,946,624). Arm V2 reproduces `joined-s1.txt` ln Z to 1e-6.
- Scripts: `flight_leg_worker.py`, `run_flight_leg.py`, `aggregate_flight_leg.py`, `figures.py`, `targeted_build.py`, `targeted_seed.sh`, `h0011_worker.py` (copy of the run J hand-off residual parser).
- Tables: `q1-locality-mass.csv`, `q1-by-route-stratum.csv`, `q1-q4-timing-quantiles.csv`, `q2-acoustic-bayes-factors.csv`, `q3-conditional-characterisation-weighted.csv`,
  `q3-top1pct-rows-summary.csv`, `q3-feasibility-near-crossing.csv`, `q3-c2-cause-cells.csv`, `q3-joined-v2-characterisation.csv`.
- Figures: `fig-conditional-impact-maps-sb1.0.png/.pdf`, `fig-conditional-impact-maps-sb0.5.png/.pdf`, `fig-bayes-factors.png/.pdf`, `fig-timing-distributions.png/.pdf`.
- Per-row stored subsets (4.5 M rows, 1.6 GB) stay in the session workspace (`kh/out/rows/`); they are not committed.
"""
open(f'{OUTD}/README.md','w').write(README); print(len(README))