md = f"""# Kadri-Haixun conditional test, drift leg (pre-registration Q7): results

18 Oct 2026, ocean drift module. Status: **INTERIM.** The dedicated L-point release run at the branch impact times is queued on deskstar
(job 10b3068e, behind the drift arc-latitude scan). Numbers that rest on the stored run A surfaces are labelled *existing surfaces*.
Every likelihood number is labelled with its prior: **run J, four route families (waypoints 0.9982, free 0.0013, repro-radar 0.0003,
descent-climb 0.0002; 74 seeds), end-of-flight cell 'D{{d}} total q=0.333 (C2 silent)'**. The 00:19 option is D0 unless stated.
Run J is not formally declared final by end of flight (Pete ruled on 18 Oct that enough is done to proceed).
Primary locality (Pete, 18 Oct): Kadri's 306.18 deg bearing at its sea-level 7th-arc crossing (25.732 S 101.369 E) and the run J impacts
that the acoustic evidence selects along or near that bearing. **Haixun 01 (25.975 S 101.461 E) is a sensitivity line only.**

## 1. Answer in brief

1. **Debris likelihood (finds and populated-coast non-recovery).** The run J impacts selected by the H01W arrival are about 3 log units
   better than the run J posterior average. For H_K^T the log-likelihood ratio is **+2.86 ± 0.40 (2-sigma)**, and for H_K^C it is **+2.82 ± 0.40**
   (D0, two-model likelihood mixture, Australian populated-coast term at the current setting).
   With the finds alone the ratios are **+0.83 ± 0.70** (T) and **+0.81 ± 0.70** (C). The ratio is almost the same for every 00:19 option
   (D0-D5: +2.82 to +3.49 with the populated term; +0.81 to +1.12 with finds only).
2. **This term is not specific to the bearing.** On the 7th arc, the debris evidence is a flat plateau from 26 S to 33 S
   (finds only +0.65 to +1.61; with the populated term +1.09 to +3.44; maximum near 30-31 S). The bearing locality is on that plateau,
   0.6 log units below its maximum. Drift therefore says: "a northern impact, of which this is one", and does not single out
   25.7 S. Almost all of the ratio is the penalty on the run J mass near 37 S (-0.55 finds only; -2.25 with the populated term).
3. **Forward drift to 5 Apr 2014.** Floating debris from the crossing moved 600-650 km (median) to the west or west-south-west in 28 days.
   At 03:15 UTC on 5 Apr, when white objects were seen 'about 90 km from the detection area', 98 % of the objects were 190-1,140 km
   from the Haixun 01 contact. Only 5.7e-4 (GlobCurrent) and 2e-5 (GLORYS12) of the objects were in the 70-110 km ring. The strip points 50-200 km inside
   the arc give ≤ 2.5e-4. The white objects were checked and found unrelated (JACC 7 Apr, grade A), so this is a consistency statement
   ('a sighting within ~90 km, checked, unrelated'), not a detection. With the time and position of an MH370 field from the bearing,
   the field could not have been near Haixun on 4-5 Apr.
4. **Backward test (ring around Haixun on 5 Apr back to 8 Mar).** Objects in the 70-110 km ring started 150-500 km south-west or east of the contact,
   not on the bearing. None of 1,200 objects from the crossing, or from any strip point, reached the ring (P < 8e-4). The posterior mass within 50 km of the crossing is
   2e-4 (GlobCurrent) and 3.6e-4 (GLORYS12). PROVISIONAL: 10-15 % of the origin probability is at the edge of the grid; the wider grid is
   in the queued job.
5. **Indonesia and the northern coasts: not assessed at this depth as a likelihood term.** The existing three-year snapshot runs give first-beaching
   shares on the south coasts of Sumatra, Java and Nusa Tenggara by 30 Jun 2016 of 0.08-0.15 % from 25 S. The shares are 0.45-0.59 % from 35-40 S.
   So a no-find term for Indonesia can only make the northern locality *more* favoured, and it is small. The dedicated run adds three provisional
   Indonesian segments with level alternatives.

## 2. Log-likelihood ratios, H_K against the run J reference (row-level, primary)

Method: every run J impact row i carries end of flight's two-factor weight w_i (option_table_0019.seed_terms, unchanged; times from
run.json T0_unix_s = 1394236800) and the pre-registered Q2 acoustic likelihood
L_i = N(t_obs - t_i - d_i/c; 0, s_t) x N(b_obs - b_i; 0, s_b), with c = 1.48 km/s, s_t^2 = (d_i/c x 0.015/c)^2 + 5^2 s^2, and s_b = 0.5 deg (core) or 1.0 deg (wide).
The drift likelihood is bilinear in the run A node surfaces (the per-impact export reproduces it). Then
LLR = ln[sum w L_a L_drift / sum w L_a] - ln[sum w L_drift / sum w], with each ocean model and the equal-weight likelihood mixture.
The reference reproduces the committed aus160-both.json ln Z to within 0.002 nat. Rows outside drift support (2-5 % of conditional weight)
are carried at their seed's weighted mean. The error is 1-sigma, from transport noise (100 mean-preserving node perturbations, split-half SD per 1-deg band;
these are shared by numerator and reference) and a seed bootstrap (100) combined in quadrature.

D0, core bearing sigma, by Australian option and ocean model (1-sigma):

| Branch | Australian non-recovery term | Mixture (headline) | GlobCurrent alone | GLORYS12 alone |
|---|---|---|---|---|
""" + "\n".join(tab) + f"""

'populated' = ABS RA 2021 major-city + inner-regional coasts only (Pete's ruling 15 Oct). It is reconstructed with the saturating law
Delta = -k ln(1 + lambda W/(cF)) from the 15-160 E pilot. 'current' is lambda = 1 (Australia at the find coasts' peak level, about 10 times their
pre-flaperon level). The rows at 1x, 3x and 5x the pre-flaperon level are the brief v2 alertness rows (Pete's call is open). B and C are the pre-registered
all-coast options. **Finds only** = no Australian term.

By 00:19 option (mixture; finds only and populated-current; core sigma, with the wide-sigma finds-only ratio in the last column):

| 00:19 option | ESS T / C | T, finds only | T, populated | C, finds only | C, populated | wide 1.0 deg, finds only T / C |
|---|---|---|---|---|---|---|
""" + "\n".join(tabD) + f"""

**Convergence.** The drift ratio is insensitive to where along the strip the selected rows lie (the surface varies by < 0.7 log units over 0-150 km),
so the ratios above are robust. The *composition* of the conditional is not: the ESS is 83 (T) and 19 (C) at D0, and 1-15 when the 00:19 BFO is used (D2-D5).
**The conditional for D2-D5 is unconverged as a sample**, and its family and position statistics are not reported as findings.

## 3. Point releases on the bearing (existing surfaces, release 00:19:37; D0 reference)

| Point | Finds only (mixture) | Finds + populated (mixture) | Finds only GLORYS12 / GlobCurrent |
|---|---|---|---|
""" + "\n".join(pt) + f"""

The strip points are 50/100/150/200 km inside the arc along the 306.18 deg geodesic from H01W. strip200 (24.50 S 99.92 E) is outside the run A
node support, so it is not computed here; the dedicated run covers it. **The Haixun row is a sensitivity case.** Errors are 1-sigma (corner-node noise plus reference noise).

## 4. Which trajectories the acoustic evidence selects (drift view; Q3 proper is the flight leg's)

D0: the selected rows impact at median 00:34:15 (T) and 00:37:15 (C) UTC. Their mean position is 25.68 S 101.33 E (T) and 25.89 S 101.62 E (C).
Their median range from H01W is 5 km beyond the arc (T) and 55 km short of it (C). The selected rows are 99.7 % waypoints-family (route stratum) and,
by end-of-flight family, A1 0.2 % / A2 24.8 % / B 75.1 % (T), against run J's 17.2 / 34.3 / 48.4 %. The low A1 share means that the impacts which fit the sound are
mostly B (and A2) descents that end late. A1 is barely sampled there: **coverage gap, see §7.** The full table is `selected-rows-character.csv`.

## 5. Forward drift L to 4-5 Apr 2014 (engine snapshot harness)

| Release (branch T; C identical within noise) | Median distance from Haixun at 03:15 UTC 5 Apr, GlobCurrent / GLORYS12 | Share in 70-110 km ring, GC / GL |
|---|---|---|
""" 
for name in ['crossing','strip50','strip100','strip150','strip200','haixun']:
    a=fwdf[(fwdf.point==name)&(fwdf.branch=='T')].set_index('model')
    md+=f"| {name}{' (sensitivity)' if name=='haixun' else ''} | {a.loc['globcurrent','med_dist_km']:.0f} / {a.loc['glorys12','med_dist_km']:.0f} km | {a.loc['globcurrent','frac_ring']:.1e} / {a.loc['glorys12','frac_ring']:.1e} |\n"
md += f"""
At the crossing, the GLORYS12 surface current from 8 to 22 Mar 2014 is 0.24-0.45 m/s westward (checked directly in the product). This is why the field moves about 450 km in the
first two weeks. The dedicated forward run for both branches uses 100,008 objects per release.
Hook: `ring_hook.py EXCHANGE LAT LON R_IN R_OUT [HOUR]` re-runs the forward and backward tests for a sighting position when the sources leg finds one.

## 6. Figures

- [fig-forward-drift-5apr.png]({{{{artifact:898b1595-edf7-4c12-aade-e3ef87a5f9af}}}}) — where floating debris from the bearing is at 03:15 UTC on 5 Apr.
- [fig-backward-origin-ring.png]({{{{artifact:42afca60-1149-424c-8b09-f2d823e74c7e}}}}) — where objects in the 70-110 km ring started on 8 Mar (provisional grid).
- [fig-drift-llr-kadri.png]({{{{artifact:e0253f08-2450-4378-9ac1-921ae3ef1c3d}}}}) — log-likelihood ratios along the arc and by 00:19 option.

## 7. COVERAGE

(a) **Feasible set** (drift view). Any impact point the 777-200ER can reach after 00:19 near the 7th arc, released as floating debris at its impact time.
The flight-side feasible set belongs to core and end of flight. (b) **Model's reach.** The run A node surfaces cover 41.2-21.2 S, 84-105.6 E, wherever all
four corner nodes were evaluated (h50 support). strip200 and 2-5 % of the conditional weight fall outside, and they are carried at the seed mean (brief v2 rule 4).
The snapshot harness covers 15-120 E with 28-day forcing; the backward origin grid covers 96-106.5 E, 31-21 S at 0.25 deg (extension to 96-113 E, 35-17 S
queued). The release time in the surfaces is 00:19:37, not the branch time; the dedicated run closes this. (c) **Proposal coverage.** Run J rows under H_K:
ESS 83 / 19 (D0, T / C), 135 / 17 (D1), 11 / 5 (D2), 1 / 2 (D3), 15 / 4 (D4), 4 / 2 (D5).

Gaps and status:
- G-K1: conditional ESS ≤ 15 for D2-D5. OPEN; the fix belongs to core and end of flight (a proposal aimed at the bearing, 00:32-00:38 impacts, with weights corrected).
  Drift ratios are robust to it (§2); the conditional composition is unconverged.
- G-K2: family A1 is barely present under H_K (0.2-0.4 %): drift ratios per family A1 are unconverged and are not quoted.
- G-K3: joined planned descents that start before 00:11 (run-j-joined-v2 J0011, J2241) are NOT included in the prior used here. Label: 'four route families only'.
- G-K4: backward grid edge mass 10-15 %. Queued fix (extension grid).
- G-K5: Indonesian non-recovery not assessed at this depth (provisional segments queued).
- G-K6: sighting position unknown; only the undirected ring is tested.
- Bounds and sources: windage classes from CSIRO Part II/III (flaperon 1.2 % + leeway 0.10 ± 0.03 m/s at -30 to 0 deg; exterior 1.2 ± 0.3 %; interior log-normal median 2.5 %);
  K log-uniform 100-1000 m2/s (PROVISIONAL, spans 100 and CSIRO's 248); ocean error from the GDP replay (sigma 0.115 / 0.087 m/s for GLORYS12 / GlobCurrent, L 100 km assumed);
  c = 1.48 km/s and s_b 0.5 / 1.0 deg from the pre-registration.

## 8. Caveats

The uncontrolled-descent physics is not calibrated. Surface search is not in this term: it is a separate module, and each evidence type enters once.
The populated-coast term is post hoc and reconstructed (brief v2 §5), so it is a labelled sensitivity until a dedicated run produces it. Ocean-model weights are equal and are not updated by the debris.
The drift ratio is the same for T and C within noise, so **drift cannot distinguish the two branches**.

## Files

Tables: drift-conditional-llr.csv (all D, branch, bearing sigma, model, Australian option, family), drift-point-llr-existing-surfaces.csv, forward-drift-L-to-5apr.csv,
backward-origin-ring-summary.csv, selected-rows-character.csv, drift-arc-profile-comparison.csv. Code: rowcond2.py (row-level accumulation), drift_eval.py
(node surfaces, Australian term), figs.py, ring_hook.py, jobs/ (deskstar job scripts and two sample configs). Large binaries (snapshots, row accumulators) are in
~/Downloads/mh370-exchange/debris-drift/kadri-haixun-2026-10-18/ with SHA256SUMS.
"""
open('out/README.md','w').write(md); print(len(md))
