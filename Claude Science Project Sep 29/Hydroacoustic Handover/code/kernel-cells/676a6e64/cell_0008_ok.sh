cd "repo/Claude Science Project Sep 29"
echo "=== work orders mentioning hydro"; grep -il hydro threads/work-orders/*.md
echo "=== overnight 19/20 hydro lines"; grep -n -i -B1 -A6 'hydro' threads/work-orders/overnight-2026-10-19.md threads/work-orders/overnight-2026-10-20.md | cut -c1-300 | head -80
echo "=== ARCHITECTURE.md module table hydro rows"; grep -n -i 'hydro' ARCHITECTURE.md | cut -c1-300 | head -30
echo "=== architecture.md entries dated 19-21 Oct mentioning hydro"; awk '/^## 2026-10-(19|20|21)/{h=$0} /[Hh]ydro/{if(h!=""){print h; h=""}}' coordination/architecture.md | cut -c1-200
echo "=== last 5 headers in architecture.md"; grep -n '^## ' coordination/architecture.md | tail -5 | cut -c1-200