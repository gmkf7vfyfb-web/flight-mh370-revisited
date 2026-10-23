cd "hydro/Claude Science Project Sep 29"
R=results/evidence-sweep-2026-10-17
ls $R; echo; find . -name 'royer_table5.json' | head
echo "== infrasound numbers"; grep -n -i "infrasound\|IS06\|33\|2,500\|2500" $R/research-radar-infrasound-ohasisbio.md | head -30
echo "== Royer in note"; grep -n -i "royer\|event B\|D1\|D2\|35.224\|27.856\|table 5" $R/research-radar-infrasound-ohasisbio.md | head -40
echo "== bearing error"; grep -n -i "bearing" results/hydroacoustics-kadri-table1-test.md | head -20
echo "== kadri geometry"; head -3 engine/hypotheses/hydroacoustics/results-data/kadri2a/kadri_table1_geometry.csv
echo "== table1"; cat engine/hypotheses/hydroacoustics/data/kadri_fig9_digitised/kadri-table1-transients.csv
echo "== imos_tl"; head -5 engine/hypotheses/hydroacoustics/results-data/stageB/imos_tl.csv; wc -l engine/hypotheses/hydroacoustics/results-data/stageB/imos_tl.csv
echo "== tl grid raw"; ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/raw | head