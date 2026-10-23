cd "repo/Claude Science Project Sep 29"
R=results/evidence-sweep-2026-10-17
grep -n -i "event B\|event D\|D1\|D2\|35.224\|27.856\|Table 5\|origin\|located\|NEAMS" $R/research-radar-infrasound-ohasisbio.md | head -40
echo "== kadri note bearing model"; sed -n 50,60p results/hydroacoustics-kadri-table1-test.md
echo "== stations"; cat "../../hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/data/stations.csv" | head -20
echo "== brief §4 IMOS positions"; grep -n "3315\|3376\|3274\|3275\|3250" threads/master-prompts/hydroacoustics.md | head -12