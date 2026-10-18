"""Repo results note for settling on run J, from the published folders on the exchange (settling/run-j/)."""
import json, pathlib, re, sys, os
X = pathlib.Path('/Users/pete/Downloads/mh370-exchange/settling/run-j'); out = pathlib.Path(sys.argv[1]); stats = json.loads(pathlib.Path(sys.argv[3]).read_text())
ST = ['run-j-waypoints', 'run-j-free', 'run-j-descent-climb', 'run-j-repro-radar']; BB = 'run-j-both-burst-waypoints'
SHORTST = {'run-j-waypoints': 'waypoints', 'run-j-free': 'free', 'run-j-descent-climb': 'descent-climb', 'run-j-repro-radar': 'repro-radar', BB: 'both-burst (waypoints)'}
K = {'run-j-waypoints': 24, 'run-j-free': 18, 'run-j-descent-climb': 16, 'run-j-repro-radar': 16, BB: 8}
mix = json.loads((X / 'stratum-mixture-weights.json').read_text())['weights_per_cell']
R = {}
for st in ST + [BB]:
    for l in (X / st / 'README.txt').read_text().splitlines():
        if l.startswith('| P'):
            c = [x.strip() for x in l.strip('|').split('|')]; R[(st, c[1], c[2], c[3])] = c
D = []
for k in R:
    if k[1] not in D: D.append(k[1])
def cell(st, d, cause, fam):
    c = R.get((st, d, cause, fam))
    if c is None: return '-', '-', '-'
    a = c[7].split('->')[-1].strip() if '->' in c[7] else '-'
    return a + ('' if c[10] == 'yes' else ' (n.e.)'), c[5], c[6]
# run I primary areas for comparison (repo note, section 1)
RI = {}
ri = pathlib.Path(sys.argv[4]).read_text().split('## 2.')[0]
for l in ri.splitlines():
    if l.startswith('| 00:19'):
        c = [x.strip() for x in l.strip('|').split('|')]; RI[c[0]] = c[1].split(' ')[0]
L = ["# Ocean settling on end of flight's run J — seabed wreckage per stratum", '',
     "Settling `hypothesis/settling` 9330d4c (real ocean; unchanged since run I). End-of-flight tools 4605cc21 (`smoke/option_table_0019.py` as 31bb6211, which adds only the thinned-file normaliser), binary mh370-eof-rj1. "
     "Samples: `mh370-exchange/settling/run-j/<stratum>/` (README.txt with labels and COVERAGE, SHA256SUMS, READY); mixture weights `settling/run-j/stratum-mixture-weights.json`; top-level README and READY written last. "
     "Driver: `scripts/wf_runj.py` (from run I's `wf_runi.py`; diff in §Method).", '',
     "**Labels (carry on every result):** core run J split-half **accepted as a pass by project ruling, 16 Oct 2026** (free flight 0.840 single split, 0.873 all-partition mean; waypoints 0.934 all-partition); "
     "the thin northern detail north of 33 S is a tail-shape limitation (core prediction 5), not non-convergence. Piloted rapid descent to 40,000 ft/min with unloading; piloted-turn model and INTERIM pitch-down PROVISIONAL; "
     "in-flight structural outcome PROVISIONAL (no transonic drag rise); breakup rows settled from the intact impact point (gap G-bf); P(left) = 0.8 PROVISIONAL; D4/D5 \"Holland transient bias added\". "
     "**D0 is D0'**: 00:19 values held out, transmission imposed (every cell carries +alive: impact after 00:19:37.443). Each stratum is CONDITIONAL on itself.", '',
     "**Method.** As run I. Row mass = end of flight's 00:19 two-factor table (`seed_terms`): hand-off weight / (unthinned) weight total / K × (1 − P(breakup by 00:19:37)) × L(D) × L(cause). "
     "Primary cell: both log-on causes, q = 1/3 = prior odds C2:C1 (P(C1) = 0.75), C2 silent (W = 00:10:58–01:15:56). Each product is a systematic resample over all rows of all seeds of the stratum "
     "(24 / 18 / 16 / 16 seeds), one settling draw each: 40,000 per total, 10,000 per family, 20,000 per cause (same N as run I). Changes from `wf_runi.py`: run J labels; normaliser `thinning.weight_sum_in` (option_table_0019 31bb6211; "
     "identical for unthinned files); an assertion that no positive-mass row impacts at or before 00:19:37.443; optional D subset (`WF_DS`) used only for the both-burst folder.", '',
     "## Checks", ''] + [f"- {x}" for x in stats['checks']] + ['',
     "## 1. 90 % seabed area (thousand km²), primary cell (both causes), by stratum", '',
     "| 00:19 data treatment | " + " | ".join(SHORTST[s] for s in ST) + " | mixture weights (wp / free / d-c / r-r) | run I waypoints (for reference) |", "|---|" + "---|" * (len(ST) + 2)]
for d in D:
    w = mix.get(f"{d} | total", {})
    L.append(f"| {d} | " + " | ".join(f"{cell(st, d, 'total', 'all')[0]} (ESS {cell(st, d, 'total', 'all')[1]})" for st in ST) + " | " + " / ".join(f"{w.get(st, 0):.4f}" for st in ST) + f" | {RI.get(d, '-')} |")
L += ['', f"Both-burst supplement (`{BB}`, waypoints only, 8 thinned seeds, D2–D5 only; use beside, not pooled with, run-j-waypoints, as searched areas did):", '',
      "| 00:19 data treatment | both-burst 90 % area (row ESS) | run-j-waypoints 90 % area (row ESS) |", "|---|---|---|"]
for d in D[2:]:
    L.append(f"| {d} | {cell(BB, d, 'total', 'all')[0]} (ESS {cell(BB, d, 'total', 'all')[1]}) | {cell('run-j-waypoints', d, 'total', 'all')[0]} (ESS {cell('run-j-waypoints', d, 'total', 'all')[1]}) |")
L += ['', stats['area_sentence'], "n.e. = not estimable (row Kish ESS < 1,000). Mixture weights = core share × Z_s(cell), normalised (core shares: waypoints 0.9982, free 0.0013, repro-radar 0.0003, descent-climb 0.0002).", '',
      "## 2. Log-on cause (posterior share within the treatment = prior p × Z ratio; 90 % area)", '',
      "| 00:19 data treatment | stratum | C1 fuel-exhaustion share | C1 area | C2 silent share | C2 silent area |", "|---|---|---|---|---|---|"]
for d in D:
    for st in ST + ([BB] if d in D[2:] else []):
        a1, e1, s1 = cell(st, d, 'C1', 'all'); a2, e2, s2 = cell(st, d, 'C2 silent', 'all')
        L.append(f"| {d} | {SHORTST[st]} | {s1} | {a1} | {s2} (ESS {e2}) | {a2} |")
L += ['', "## 3. Flight-end family (share within the treatment; 90 % area)", '',
      "| 00:19 data treatment | stratum | A1 | A2 | B |", "|---|---|---|---|---|"]
for d in D:
    for st in ST + ([BB] if d in D[2:] else []):
        L.append(f"| {d} | {SHORTST[st]} | " + " | ".join(f"{cell(st, d, 'total', f)[2]}, {cell(st, d, 'total', f)[0]} (ESS {cell(st, d, 'total', f)[1]})" for f in ('A1', 'A2', 'B')) + " |")
gaps = [f"{SHORTST[k[0]]}: {k[1]} × {k[2]} × {k[3]} (row ESS {c[5]})" for k, c in R.items() if c[10] != 'yes']
L += ['', '## COVERAGE', '',
      "**(a) Feasible set.** As end of flight's run J note: piloted dives to about 40,000 ft/min with unloading to −1.0 g, speeds past VMO/MMO, piloted turns, in-flight structural damage or breakup; four strata (waypoint routes, free flight, descent-climb, Davey dynamics with radar). Core shares: waypoints 0.9982, free 0.0013, repro-radar 0.0003, descent-climb 0.0002.", '',
      "**(b) Settling's reach.** Every row that reaches the water is settled as an intact impact through the real ocean (GLORYS12V1 75–115 E, 45–10 S; TEOS-10; AusSeabed then GEBCO_2026); settling bounds and sources as `results/settling-run-c/README.md` §COVERAGE (unchanged in 9330d4c). Reach gaps: **G-bf** (in-flight breakup rows are settled from the intact impact point; the fragment field along the descent is not modelled); attitude-dependent breakup (declared); impact pitch is not used (flight-path angle stand-in, gap G6). " + stats['reach_sentence'], '',
      "**(c) Proposal coverage.** Row Kish ESS per product in each stratum README; gate 1,000. Products below the gate (stamped 'Not yet estimable' in the figures; NOT ASSESSED at this depth):", ''] + ([f"- {g}" for g in gaps] or ['- none']) + ['', stats['coverage_status'], '',
      "**Settling's parameter bounds.** Unchanged from run I (9330d4c); element classes, sink rates and breakup table with sources in `results/settling-run-c/README.md` §COVERAGE. Breakup table PROVISIONAL.", '',
      "## Figures", ''] + [f"- `{SHORTST[st]}`: `settling-seabed-wreckage-{st}-{{core,cause,family}}.png`" for st in ST + [BB]] + ['',
      "## Deviations", ''] + [f"- {x}" for x in stats['deviations']] + ['', '- Ocean Settling, ' + sys.argv[2]]
out.mkdir(parents=True, exist_ok=True); (out / 'README.md').write_text('\n'.join(L) + '\n'); print(len(L), 'lines;', len(gaps), 'gaps')
