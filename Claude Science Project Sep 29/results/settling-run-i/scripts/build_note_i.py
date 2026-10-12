"""Repo results note for settling on run I, from the four published strata (exchange settling/run-i/)."""
import json, pathlib, re, sys
X = pathlib.Path('/Users/pete/Downloads/mh370-exchange/settling/run-i'); out = pathlib.Path(sys.argv[1])
ST = ['next-i-waypoints', 'next-i-free', 'next-i-descent-climb', 'next-i-repro-radar']
SH = {'next-i-waypoints': 0.9982, 'next-i-free': 0.0011, 'next-i-descent-climb': 0.0002, 'next-i-repro-radar': 0.0004}
mix = json.loads((X / 'stratum-mixture-weights.json').read_text())['weights_per_cell']
R = {}
for st in ST:
    for l in (X / st / 'README.txt').read_text().splitlines():
        if l.startswith('| P'):
            c = [x.strip() for x in l.strip('|').split('|')]; R[(st, c[1], c[2], c[3])] = c
D = []
for k in R:
    if k[1] not in D: D.append(k[1])
def cell(st, d, cause, fam):
    c = R[(st, d, cause, fam)]; a = c[7].split('->')[-1].strip() if '->' in c[7] else '-'
    return a + ('' if c[10] == 'yes' else ' (n.e.)'), c[5], c[6]
L = ["# Ocean settling on end of flight's run I — seabed wreckage per stratum (PROVISIONAL, NOT CONVERGED)", '',
     f"Settling `hypothesis/settling` 9330d4c (real ocean). End-of-flight tools f7f54dd0 (`smoke/option_table_0019.py`), binary mh370-eof-ri1. Samples: `mh370-exchange/settling/run-i/<stratum>/` (README.txt with COVERAGE, SHA256SUMS, READY); mixture weights `settling/run-i/stratum-mixture-weights.json`.", '',
     "**Labels (carry on every result):** core run I split-half NOT converged (waypoints 0.916 against floor 0.924); piloted-turn model and INTERIM pitch-down PROVISIONAL; in-flight structural outcome PROVISIONAL; breakup rows settled from the intact impact point (gap G-bf); P(left) = 0.8 PROVISIONAL; D4/D5 \"Holland transient bias added\". Each stratum is CONDITIONAL on itself.", '',
     "**Method.** Row mass = end of flight's 00:19 two-factor table (`seed_terms`): hand-off weight / sum / K × (1 − P(breakup by 00:19:37)) × L(D) × L(cause). Primary cell: both log-on causes, q = 1/3 = prior odds C2:C1, so P(C1) = 0.75, P(C2) = 0.25, C2 silent (W = 00:10:58–01:15:56). Per-cell per-seed ln Z equals `seed_terms` to ≤ 7e-15 in every seed of every stratum. Each product is a systematic resample over all rows of 8 seeds, one settling draw each (40,000 per total, 10,000 per family, 20,000 per cause).", '',
     "## 1. 90 % seabed area (thousand km²), primary cell, by stratum", '',
     "| 00:19 data treatment | " + " | ".join(ST) + " | core-share mixture weights (wp / free / d-c / r-r) |", "|---|" + "---|" * (len(ST) + 1)]
for d in D:
    w = mix.get(f"{d} | total", {})
    L.append(f"| {d} | " + " | ".join(f"{cell(st, d, 'total', 'all')[0]} (ESS {cell(st, d, 'total', 'all')[1]})" for st in ST) + " | " + " / ".join(f"{w.get(st, 0):.4f}" for st in ST) + " |")
L += ['', "Settling adds 0.1–1.5 % to the 90 % area in every estimable product (up to 1.9 % in products below the gate); settled-offset p90 1.9–4.7 km (README tables). n.e. = not estimable (row Kish ESS < 1,000). Mixture weights = core share × Z_s(cell), normalised; core shares are themselves NOT converged.", '',
      "## 2. Log-on cause (posterior share within the treatment = prior p × Z ratio; 90 % area)", '',
      "| 00:19 data treatment | stratum | C1 fuel-exhaustion share | C1 area | C2 silent share | C2 silent area |", "|---|---|---|---|---|---|"]
for d in D:
    for st in ST:
        a1, e1, s1 = cell(st, d, 'C1', 'all'); a2, e2, s2 = cell(st, d, 'C2 silent', 'all')
        L.append(f"| {d} | {st} | {s1} | {a1} | {s2} (ESS {e2}) | {a2} |")
L += ['', "## 3. Flight-end family (share within the treatment; 90 % area)", '',
      "| 00:19 data treatment | stratum | A1 | A2 | B |", "|---|---|---|---|---|"]
for d in D:
    for st in ST:
        L.append(f"| {d} | {st} | " + " | ".join(f"{cell(st, d, 'total', f)[2]}, {cell(st, d, 'total', f)[0]} (ESS {cell(st, d, 'total', f)[1]})" for f in ('A1', 'A2', 'B')) + " |")
gaps = [f"{st}: {k[1]} × {k[2]} × {k[3]} (row ESS {c[5]})" for (st, *_), c in zip(R.keys(), R.values()) for k in [(st,) + tuple(c[1:4])] if c[10] != 'yes']
L += ['', '## COVERAGE', '',
      "**(a) Feasible set.** As end of flight's run I note: piloted dives to about 40,000 ft/min, unloading, speeds past VMO/MMO, piloted turns, in-flight structural damage or breakup; four strata (waypoint routes, free flight, descent-climb, Davey dynamics with radar). Core shares (equal prior): waypoints 0.9982, free 0.0011, descent-climb 0.0002, repro-radar 0.0004.", '',
      "**(b) Settling's reach.** Every row that reaches the water is settled as an intact impact through the real ocean (GLORYS12V1 75–115 E, 45–10 S; TEOS-10; AusSeabed then GEBCO_2026); settling bounds and sources as `results/settling-run-c/README.md` §COVERAGE (unchanged in 9330d4c). Reach gaps: **G-bf** (in-flight breakup rows are settled from the intact impact point; the fragment field along the descent is not modelled; waits for end of flight's 1(B) columns); attitude-dependent breakup (declared). No impact was refused by the ocean window in any stratum (column 'not computed' = 0).", '',
      "**(c) Proposal coverage.** Row Kish ESS per product in each stratum README; gate 1,000. Products below the gate (stamped 'Not yet estimable' in the figures; NOT ASSESSED at this depth):", ''] + [f"- {g}" for g in gaps] + ['',
      "Status: the primary cell (both causes) of every 00:19 treatment is estimable in every stratum (lowest row ESS 1,276: R600 BTO + both BFOs as recorded, repro-radar). The gaps sit in the two-BFO treatments: under both BFOs as recorded (Holland H2 data) the C2-silent cell and the A1 and B families fall below the gate in all four strata, and A2 also in descent-climb and repro-radar; under D5 the A1 family and the C2-silent cell fall below it in all four strata (and B in repro-radar); under both BFOs with Holland transient bias added (Holland H1 data) A1 falls below it in descent-climb and repro-radar. These are proposal-coverage gaps of end of flight (more A1 / C2-silent mass under the two-BFO likelihoods); settling cannot close them. They are reported, not dropped.", '',
      "## Figures", ''] + [f"- `{st}`: `settling-seabed-wreckage-run-i-{st[7:]}-{{core,cause,family}}.png`" for st in ST] + ['', '- Ocean Settling, ' + sys.argv[2]]
out.mkdir(parents=True, exist_ok=True); (out / 'README.md').write_text('\n'.join(L) + '\n'); print(len(L), 'lines;', len(gaps), 'gaps')
