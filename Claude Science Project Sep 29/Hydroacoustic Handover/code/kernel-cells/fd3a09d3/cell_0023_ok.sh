cd "repo/Claude Science Project Sep 29"
sed -n 136,178p threads/master-prompts/hydroacoustics.md | grep -n -i "3315\|3376\|3250\|3274\|3275\|Perth\|Portland\|Scott" | head
cd "../../hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
grep -n "def parse_meta" -A25 imos_preregistration.py | grep -n "lat\|lon\|depth" | head; grep -n "3315\|3376\|3250\|3274\|3275" imos_preregistration.py | head -12