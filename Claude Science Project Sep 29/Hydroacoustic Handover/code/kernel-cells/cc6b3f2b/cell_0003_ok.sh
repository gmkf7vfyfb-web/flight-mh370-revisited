cd "repo/Claude Science Project Sep 29"
echo "=== WORK ORDER block 8 ==="; grep -n "^#" threads/work-orders/hydroacoustics-order-2026-10-21.md | head -40
echo; awk '/[Bb]lock 8|^## 8|^### 8/{f=1} f{print; n++} n>60{exit}' threads/work-orders/hydroacoustics-order-2026-10-21.md
echo "=== BRIEF Refresh v2 headers ==="; grep -n "Refresh v2\|^## \|^### " threads/master-prompts/hydroacoustics.md | tail -40