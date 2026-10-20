"""Results note for the joined V2 production run: tables from R/joined-v2-summary.json and R/gate4-sK.json, written to OUT/README.md
with the COVERAGE section the contract requires. Numbers are copied from the JSON; prose that interprets them is in the TEMPLATE
blocks and must be re-read against the numbers before the note is committed.
    python joined_v2_note.py R OUT_DIR"""
import json, sys, pathlib
import numpy as np

R = pathlib.Path(sys.argv[1]); OUT = pathlib.Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
S = json.load(open(R / "joined-v2-summary.json")); seeds = S["seeds"]
G = {k: json.load(open(R / f"gate4-s{k}.json")) for k in seeds if (R / f"gate4-s{k}.json").exists()}
FAMS = ("A1", "A2", "B", "outside B (6)")
CELLS = {"D0": "D0: 23:15 and 00:11 only (no 00:19 data)", "D1": "D1: R600 BTO", "D2": "D2: R600 BTO + BFO",
         "D3": "D3: both BFOs, raw", "D4": "D4: both BFOs, start-up offset (Holland H1)"}
L = []
L.append("# Joined V2 at 00:11 — production run, core run I, waypoints stratum (14 Oct 2026)\n")
L.append(f"**Label for every figure below:** {S['label']}.\n")
L.append("Binary mh370-eof-o13d (sha256 bf18d786…). Core run I, stratum `next-i-waypoints` (core P(family) 0.9982). "
         f"Seeds {seeds[0]}–{seeds[-1]}: each is an independent replicate of the whole pipeline, core included. "
         "00:11 arm: run-i-dive recipe + exact fuel-cue truncation + all four deliberate control outcomes, N = 8 children × 4 descents per parent. "
         "22:41 arm: the same recipe, deliberate onsets only (mechanism weights [1, 1, 0]; the V2 prior's factor 2/3 applied exactly in the join), "
         "scored candidate selection aimed at m0011 (K = 8, defensive share 0.2; test 6 passed at pilot scale), N = 8 × 4. "
         "Join (smoke/joined_v2.py; Pete's ruling 14 Oct): deliberate onsets before 00:11 scored in-stage from the 22:41 arm, everything else "
         "from the 00:11 arm with the filter's 22:41→00:11 increment; families A1/A2 entirely from the 00:11 arm.\n")
L.append("## Results by 00:19 data treatment (cause total, q = 1/3, C2 silent)\n")
L.append("| treatment | ln Z (log-mean-exp over seeds) | seed s.d. of ln Z | ESS, smallest seed | A1 share | A2 share | B share | outside B (code 6) | B ESS, smallest seed | share from onsets before 00:11 |")
L.append("|---|---|---|---|---|---|---|---|---|---|")
for c, d in S["cells"].items():
    L.append(f"| {CELLS.get(c, c)} | {d['lnZ_combined']:.3f} | {d['lnZ_seed_sd']:.3f} | {d['ess_min']:.0f} | {d['A1']['share']:.3f} ± {d['A1']['share_seed_sd']:.3f} | "
             f"{d['A2']['share']:.3f} ± {d['A2']['share_seed_sd']:.3f} | {d['B']['share']:.3f} ± {d['B']['share_seed_sd']:.3f} | "
             f"{d['outside B (6)']['share']:.3f} | {d['B']['ess_min']:.0f} | {d['S1_share']:.3f} |")
L.append("\nShares are the seed posteriors pooled with weights Z_k; ± is the seed standard deviation. ESS is Kish's, per seed, never pooled.\n")
J = {k: json.load(open(R / f"joined-s{k}.json")) for k in seeds}
L.append("### Per seed (ln Z; B share; B ESS)\n")
L.append("| treatment | " + " | ".join(f"seed {k}" for k in seeds) + " |"); L.append("|---|" + "---|" * len(seeds))
for c in S["cells"]:
    L.append(f"| {c} | " + " | ".join(f"{J[k]['cells'][c]['lnZ']:.2f}; {J[k]['cells'][c]['B']['share']:.3f}; {J[k]['cells'][c]['B']['ess']:.0f}" for k in seeds) + " |")
L.append("\nFilter increment 22:41→00:11 by seed: " + ", ".join(f"{J[k]['dlnZ_filter']:.3f}" for k in seeds) + " nat.\n")
L.append("## Onset-boundary statistic (22:41 arm: weight within 60 s of the 22:41 hand-off), largest over seeds\n")
L.append("| cell | all | B | outside B (6) |"); L.append("|---|---|---|---|")
for c, v in S["onset_boundary_fraction_max_over_seeds"].items():
    if "sampled" not in c: continue
    f = lambda k: "—" if v.get(k) is None else f"{100 * v[k]:.2f} %"
    L.append(f"| {c.split('| ')[-1]} | {f('all')} | {f('B')} | {f('outside B (6)')} |")
L.append("\nContract threshold 5 %. Support truncation is populated (finite fraction per seed: " +
         ", ".join(f"{v:.3f}" for v in S["truncation_finite_fraction"].values()) + ").\n")
L.append("## COVERAGE\n")
L.append("TEMPLATE — check every line against the tables before committing.\n")
L.append("**(a) Feasible set.** A 777-200ER from the core's 22:41/00:11 states to the sea: descent onset anticipatory, fuel-cue or "
         "flame-out-associated; 0, 1 or 2 engines thrusting; control ditching, maintained-then-lost, no intervention or upset; rates up to "
         "the structural limits (VMO/MMO 330 kt / M0.87, TCDS T00001SE); piloted turns; single-engine flight with or without thrust-asymmetry "
         "compensation.\n")
L.append("**(b) Model reach.** Gaps, each named in the label: (1) single-engine flight is a symmetric point mass in this run (item 1 code "
         "landed after, off here); (2) the uncontrolled-arm dynamics are not calibrated (item 2 gate open; smoke shows a glide-phugoid and a "
         "dive-chord misfit against Boeing); (3) deliberate onsets earlier than 22:41 are not reachable — measured boundary statistic above; "
         "(4) A-family flame-out timing differs by about 2.6 min between the 22:41- and 00:11-based hand-offs (V1a/V1b effect, ~0.36 nat), "
         "carried by taking A from the 00:11 arm.\n")
L.append("**(c) Proposal coverage.** ESS per treatment and family in the table above (smallest seed). D5 (R600 BTO + R600 BFO + R1200 BFO "
         "with offset) is NOT estimable from this sample set at 22:41: the bias variance after the in-stage updates is not emitted — a coverage "
         "gap, fix proposed (emit it, or its own log-likelihood column). The 22:41 arm carries 648 rows per seed-1 of flame-out mechanism with "
         "prior 0 (no deliberate support after 22:41), excluded from the join by construction (weight share 6e-5).\n")
L.append("**Parameter bounds with sources:** as in the run-i-dive recipe (hypotheses/end-of-flight/full/*.toml, each with its source line).\n")
(OUT / "README.md").write_text("\n".join(L) + "\n")
print(f"wrote {OUT / 'README.md'}")
