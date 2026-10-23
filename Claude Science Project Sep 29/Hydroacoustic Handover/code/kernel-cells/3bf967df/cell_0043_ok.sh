D="repo/Claude Science Project Sep 29/results/kadri-haixun-conditional-2026-10-18"; cp kadri-composed-terms.csv kadri-composed-combinations.csv "$D/"; cp kadri-crossing-impact-map.png "$D/"
cat > "$D/SYNTHESIS.md" <<'EOF'
# Kadri preferred signal and Haixun 01: synthesis of the pre-registered conditional (18 Oct 2026)

Pre-registration: `preregistration.md` (commit 207b332, before any statistic). Prior: run J end of flight, four route families,
74 seeds, headline cells `D{d} total q=0.333 (C2 silent)`; D0 = 00:19 data held out. Branches: T = Kadri text time 00:52:03,
C = caption/Table 1 time 00:54:30. Haixun 01 is a sensitivity line only (Pete, 18 Oct).

## 1. Geometry (coordinator, kadri_geom.py)
- 306.18 deg from the H01W triad centroid meets the sea-level 7th arc (corrected BTO 18,400 us) at **25.732 S 101.369 E, R7 = 1,591.3 km**
  (BTO +/-1 sigma: 1,578.9-1,603.7 km). Kadri's R7 = 1,586 km; Pete's 25.5-26 S agrees.
- The earlier project point 26.2 S 101.9 E (R about 1,517 km) was wrong by about 74 km; every window built on it was redone. The run I
  locality figures quoted at the start of this session (0.36/1.21/2.31 % within 100/200/400 km, median impact 00:36-00:38) were the
  **run I dive** draw around that wrong point and are superseded by the run J numbers below.
- Kadri eq. 4 errata: he uses 00:54:00; 1,586 km / 1.5 km/s = 17.62 min, not 17.45; '1450 m/s' must be 450 m/s.
- Haixun: az 305.68 deg (-0.50 deg, 13.6 km cross-track, about 1 sigma at 0.5 deg), 1,566 km, 28.5 km from the crossing, outside the arc.
- Run J time origin is run.json `T0_unix_s = 1394236800` (00:00 UTC); the EoF note's 1394232081 is wrong for these files.

## 2. Results by leg (each leg's report is in its sub-folder)
| Leg | Main result | Status |
|---|---|---|
| Flight (`flight/`, 513bbfd) | Model reaches the signal (about 209 k T / 222 k C rows within 6 sigma). Posterior mass: 0.06-0.11 % in the bearing strip, 0.55-0.79 % within 200 km. Selected trajectories: unpowered piloted glides of 15-20 min after flame-out at 00:16:30-00:18:30 (fuel-exhaustion log-on >= 0.99), family B about 0.7, A2 about 0.3, A1 negligible; under D3-D5 an arrested dive then glide; impacts straddle the arc. | UNCONVERGED (cond. ESS <= 278); targeted re-simulation built, not run (disk) |
| Hydro signals (`hydroacoustic-signals/`, 33b8f3e) | H08S corrected windows (T 01:14:33-01:16:08, C 01:17:00-01:18:35) had 0 % overlap with earlier searches; now searched: chance yields. Perth 3376 already covered. Royer: no event in L; his H01W picks match Kadri's times after +16 s; exploratory C recombination at 25.80 S 101.46 E, chance p 0.11. Kadri's H01W level needs coupling 0.24-0.9 (90-340x the F-35A anchor). | Amplitude terms PROVISIONAL (borrowed TL) |
| Beacon physics (`haixun-beacon-physics/`, be408a1) | Seabed 4,577 m; P(detect beacon overhead) 0.08 / 0.02 / 2e-4 by calibration; two contacts 2-3 km apart need 4.9-5.0 km slant range. B_H = 0.52 (ln -0.66), range 0.31-2.1. | Follow-up miss probabilities are judgement ranges |
| Search coverage (`searched-areas/`, 5a64797) | No ATSB sonar or OI 2025-26 here. Pete's +/-25 NM strip = OI 2018 northern extension (to 24.73 S, grade C; Malaysian update 12 grade B). OI covers Kadri's inside-arc line only for mean speed <= 49 (T) / 42 (C) m/s. No 2014 surface box on the strip. | OI northern extent grade C |
| Drift (`drift/`, c51f857) | Drift favours the 26-33 S plateau over 37 S generally, not the bearing specifically. Debris from the crossing is 190-1,140 km from Haixun on 5 Apr; ring share <= 6e-4. | Dedicated L-point run queued (deskstar 10b3068e) |
| Sources (`sources-sightings/`, aafae81) | White objects: PLA AF aircraft, from 03:05 UTC 5 Apr, about 90 km, position unpublished, checked and unrelated (JACC 7 Apr). Satellite coverage of L: none public at <= 30 m; 'not assessed'. | Commercial archives untested |
| Settling | Awaiting Pete's approval card | Open |

## 3. Combined evidence for H_K (ln Bayes factor, D0, bearing sd 1.0 deg)
Each non-acoustic term is the ratio of the acoustically weighted run J expectation to the run J reference, so it adds to the
acoustic ln B; adding the terms assumes they are independent given the impact (approximation). Table: `kadri-composed-terms.csv`.

| Combination | T, rate background | C, rate background | T, one-arrival background | C, one-arrival background |
|---|---|---|---|---|
| A timing + bearing only | -5.59 | -5.58 | -2.70 | -2.69 |
| B A + drift finds + both searches | -4.68 | -4.46 | -1.79 | -1.57 |
| C B + Australian non-recovery (current setting) | -2.65 | -2.45 | +0.24 | +0.44 |
| D C + Perth amplitude + H08S given level (provisional) | -7.69 | -5.21 | -4.80 | -2.32 |

Reading: the acoustic timing and bearing alone disfavour 'this transient is MH370' against a chance transient by about 5.6 nats
under the pre-registered rate background (2.7 nats under a one-arrival background), because only about 0.1 % of the run J posterior
predicts an arrival from that direction at that time. Drift and the searches recover 1-3 nats, but drift's gain is not specific to the
bearing (it favours 26-33 S over 37 S generally) and the Australian term is post hoc. The provisional amplitude test disfavours the signal
further, more strongly for T than C. **Net: disfavoured to indeterminate; no combination favours H_K except C with the one-arrival
background (+0.2 to +0.4, not material).** All values are unconverged until the targeted re-simulation runs; conditional maps are
'not estimable'. Joint V2 (pre-00:11 planned descents, seeds 1-21, D0-D4): acoustic ln B -5.0 to -9.6 at sd 1.0 deg (-4.5 at sd 0.5 deg).
H_H (Haixun beacon, sensitivity): B_H 0.52, so the contacts cannot move the site odds by more than about 2-3x either way.

## 4. Open items
1. Free disk to >= 30 GiB and run the Flight targeted re-simulation (about 1.5 h); then recompute every ln B and the conditional maps.
2. Real-path transmission loss (L to H01W, Perth 3376, H08S) before the amplitude term enters composition; validate on a common event.
3. Drift dedicated L-point release at the branch times and origin-grid extension (deskstar 10b3068e, queued).
4. Settling leg (awaiting approval).
5. Data requests: raw H01W via the Kadri package (confirm text vs caption time); Royer raw 2014 OHASISBIO and the 16 s correction;
   ATSB 2017 Table 17 from the PDF; Malaysian weekly update 12 (OI 2018 northern extension).
6. Reconcile the two Haixun dossiers so the Echo/submarine non-reacquisition enters once.
7. Reviewer notes carried: Flight worker refactor showed one npar mismatch (781 vs 780, D3xC1 X200) with identical statistics -
   recheck; Sources timeline Maxar label should read 0.3-2 m; Search coverage Fig. 1 Haixun label should read 4 Apr.
EOF
cd repo; export HOME=$PWD/../h XDG_CONFIG_HOME=$PWD/../h/.config
git checkout -q -B claude-science-sep29 origin/claude-science-sep29 2>/dev/null; git pull -q --rebase origin claude-science-sep29 2>&1|tail -1
git add --sparse "Claude Science Project Sep 29/results/kadri-haixun-conditional-2026-10-18/SYNTHESIS.md" "Claude Science Project Sep 29/results/kadri-haixun-conditional-2026-10-18/kadri-composed-terms.csv" "Claude Science Project Sep 29/results/kadri-haixun-conditional-2026-10-18/kadri-composed-combinations.csv" "Claude Science Project Sep 29/results/kadri-haixun-conditional-2026-10-18/kadri-crossing-impact-map.png"
git -c user.name="Claude Science" -c user.email="noreply@example.com" commit -qm "Kadri-Haixun conditional: synthesis of six legs and combined evidence table" && git push -q origin claude-science-sep29 2>&1|tail -1; git log -1 --format='%h %s'