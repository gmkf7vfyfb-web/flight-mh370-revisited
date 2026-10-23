python - <<'EOF'
import pathlib
p=pathlib.Path("repo/Claude Science Project Sep 29/results/hydroacoustics-imos-ram-grid.md"); s=p.read_text()
rep={
"218 of 253 planned paths complete in all three bands (647 path × band jobs, 0 failed;\n  about 19.7 CPU-hours;":"212 of 253 planned paths complete in all three bands, 6 more partial (647 path × band jobs, 0 failed;\n  about 23 CPU-hours;",
"−30 NM 66 of 84 (3315 18/22, 3376 18/22, 3274 8/13, 3275\n  8/13, 3250 14/16); +30 NM 61 of 84 (17/22, 17/22, 7/13, 7/13, 13/15).":"−30 NM 66 of 86 (3315 18/22, 3376 18/22, 3274 8/13, 3275\n  8/13, 3250 14/16); +30 NM 61 of 82 (17/22, 17/22, 7/12, 7/12, 13/14).",
"35 paths not reached at the 03:35 soft deadline (all at ±30 NM; mask\n  `imos_tl_ram_coverage.csv`)":"35 paths not reached and 6 partial at the 03:35 soft deadline (all at ±30 NM; mask\n  `imos_tl_ram_coverage.csv`)",
"`imos_ram_minus_kraken_arc.csv` (654 node × band rows)":"`imos_ram_minus_kraken_arc.csv` (647 node × band rows)",
"(bathymetry, sound speed, info per path: 218 + 35 built)":"(bathymetry, sound speed, info per path: 253 built)",
"A node counts only when all three bands are done (3 partial nodes at the deadline are 'not covered')":"A node counts only when all three bands are done (6 partial nodes at the deadline are 'not covered')",
"112 of 667 queued jobs (35 paths, all ±30 NM) were not reached.":"112 of 667 queued jobs (35 paths and 6 partial ones, all ±30 NM) were not reached.",
"the 35\n±30 NM paths (G-TL1a)":"the 41\n±30 NM paths not complete (G-TL1a)",
"plus the 35 missing ±30 NM paths":"plus the 41 incomplete ±30 NM paths",
"and the 35 missing ±30 NM paths;":"and the 41 incomplete ±30 NM paths;",
"and on 70–82 % of the ±30 NM lines":"and on 74–77 % of the ±30 NM lines",
"Offsets ±30 NM are 70–82 % covered;":"Offsets ±30 NM are 74–77 % covered;",
"**closed on the offset-0 line and 73 % of the ±30 NM lines**":"**closed on the offset-0 line and 76 % of the ±30 NM paths**",
"and on 73 % of the ±30 NM lines; acceptance":"and on 76 % of the ±30 NM paths; acceptance",
}
for a,b in rep.items():
    assert a in s, a[:50]; s=s.replace(a,b)
p.write_text(s); print("ok")
EOF