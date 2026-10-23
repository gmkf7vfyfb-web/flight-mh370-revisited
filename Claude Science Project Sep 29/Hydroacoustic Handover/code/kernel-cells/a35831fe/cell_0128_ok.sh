cd cand && python - <<'E'
f='candidates-A-F-charts-note-2026-10-22.md'; t=open(f).read()
reps=[
("*22 October 2026. Exploratory, not pre-registered.","**Version 2 (22 Oct 2026, later the same evening):** version 1 drew the Pleiades layer from the module's flight-only map (its README says `pre = post: no search`) and labelled it conditional on the Pleiades objects. The maps and every Pleiades statement below are corrected. The true conditional PDF has mean 35.44 S 92.20 E and its 50 % region spans 34.8-35.9 S, 91.7-93.2 E; this agrees with the module README (35.38-35.60 S, 92.20-92.62 E) and the composer core x Pleiades product (35.43 S 92.19 E).\n\n*22 October 2026. Exploratory, not pre-registered."),
("| A | 35.81 S 91.58 E, 00:26:46 | +9 / −6 / −3 s | 11.4 % | yes, ATSB Phase 2 | 0.12 |","| A | 35.81 S 91.58 E, 00:26:46 | +9 / −6 / −3 s | 11.4 % | yes, ATSB Phase 2 | 0.63 |"),
("| B | 32.62 S 95.10 E, 00:28:35 | −15 / +7 / +8 s (poor) | 1.1 % | yes, Ocean Infinity 2018 | 0.01 |","| B | 32.62 S 95.10 E, 00:28:35 | −15 / +7 / +8 s (poor) | 1.1 % | yes, Ocean Infinity 2018 | 0.002 |"),
("| C | 36.74 S 90.16 E, 00:29:05 | single site | 74.4 % | yes, ATSB Phase 2 | 0.56 |","| C | 36.74 S 90.16 E, 00:29:05 | single site | 74.4 % | yes, ATSB Phase 2 | 0.09 |"),
("| D | 36.85 S 90.09 E, 00:25:43 | exact (2 sites) | 75.5 % | yes, ATSB Phase 2 | 0.59 |","| D | 36.85 S 90.09 E, 00:25:43 | exact (2 sites) | 75.5 % | yes, ATSB Phase 2 | 0.08 |"),
("| E | 33.46 S 94.18 E, 00:32:58 | exact (2 sites) | 3.7 % | yes, Ocean Infinity 2018 | 0.03 |","| E | 33.46 S 94.18 E, 00:32:58 | exact (2 sites) | 3.7 % | yes, Ocean Infinity 2018 | 0.02 |"),
("| F | 37.21 S 89.88 E, 00:33:52 | exact (2 sites) | 75.9 % | yes, ATSB Phase 2 | 0.65 |","| F | 37.21 S 89.88 E, 00:33:52 | exact (2 sites) | 75.9 % | yes, ATSB Phase 2 | 0.06 |"),
("- The impact point lies on ATSB Phase 2 searched sea floor. It is 122 km from the nearest Pleiades object.","- The impact point lies on ATSB Phase 2 searched sea floor. It is 122 km from the nearest Pleiades object. It sits just outside the south-west edge of the Pleiades-conditional 50 % region and inside the 90 % region."),
("- The place is in the prior core, inside the Pleiades-conditional 50 % region, and on Phase 2 searched sea floor.","- The place is in the prior core and on Phase 2 searched sea floor. It is outside the Pleiades-conditional 50 % region."),
("- The place is in the prior core, on Phase 2 searched sea floor, and inside the Pleiades-conditional 50 % region.","- The place is in the prior core and on Phase 2 searched sea floor. It is outside the Pleiades-conditional 50 % region."),
("- C and D sit in the prior core and in the Pleiades-conditional 50 % region. There the impact model","- C and D sit in the prior core. A is the only candidate near the Pleiades-conditional region (0.63 of its mass within 1 degree). At C and D the impact model"),
]
for a,b in reps:
    assert t.count(a)==1, a[:60]; t=t.replace(a,b)
open(f,'w').write(t); print('ok')
E
grep -n "Pleiades-conditional\|0.56\|0.59" cand/candidates-A-F-charts-note-2026-10-22.md 2>/dev/null | head; grep -c "" candidates-A-F-charts-note-2026-10-22.md 2>/dev/null; cd .. ; grep -n "Pleiades-conditional" cand/candidates-A-F-charts-note-2026-10-22.md