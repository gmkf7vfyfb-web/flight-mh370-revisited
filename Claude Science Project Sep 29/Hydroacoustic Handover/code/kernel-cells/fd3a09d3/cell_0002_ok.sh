cd "hydro/Claude Science Project Sep 29"
WO="threads/work-orders/hydroacoustics-order-2026-10-21.md"
wc -l "$WO" threads/master-prompts/hydroacoustics.md coordination/HYDROACOUSTICS.md
echo ==== WORK ORDER
grep -n "^#" "$WO" | head -40
echo
awk '/[Bb]lock 2/{f=1} f' "$WO" | head -80