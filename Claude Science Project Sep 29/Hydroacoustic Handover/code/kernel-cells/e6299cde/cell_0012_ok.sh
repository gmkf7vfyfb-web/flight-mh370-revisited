cd "repo/Claude Science Project Sep 29"
R=results/evidence-sweep-2026-10-17
ls $R | head -20; echo
echo "== royer json"; cat $R/royer_table5.json 2>/dev/null | head -80 || find . -name 'royer_table5.json'
echo "== infrasound numbers"; grep -n -i "infrasound\|IS06\|times below\|2,500" $R/research-radar-infrasound-ohasisbio.md | head -25
echo "== bearing error"; grep -n -i "bearing" results/hydroacoustics-kadri-table1-test.md | head -25