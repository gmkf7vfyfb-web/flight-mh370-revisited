cd "repo/Claude Science Project Sep 29"
ls threads/work-orders/ 2>/dev/null | tail; ls threads | head
WO="threads/work-orders/hydroacoustics-order-2026-10-21.md"
wc -l "$WO"; grep -n "^#" "$WO" | head -40