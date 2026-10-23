cd /Users/pete/Downloads/flight-mh370-revisited
echo "=== bibliography CSV Kadri rows (sep29 branch)"; git show origin/claude-science-sep29:"Claude Science Project Sep 29/results/hydroacoustics-bibliography.csv" | tr -d '\r' | grep -i "^Kadri" | cut -c1-330
echo; echo "=== repo: papers held, hydroacoustics (ISO Sept 28 Status/inputs/papers)"; git ls-tree -r --name-only origin/claude-science-sep29 -- "ISO Sept 28 Status/inputs/papers/hydroacoustics/" | head -40
echo; echo "=== any file in any branch with kadri in the path"; for b in origin/claude-science-sep29 origin/hypothesis/hydroacoustics origin/main; do git ls-tree -r --name-only $b | grep -i kadri | grep -i -E "\.(pdf|txt)$" | sed "s|^|$b: |"; done | sort -u | head -40
echo; echo "=== Usama Kadri Sep 11.pdf"; python3 - <<'EOF'
import pypdf
p='/Users/pete/Downloads/Usama Kadri Sep 11.pdf'
r=pypdf.PdfReader(p); print(len(r.pages),'pp'); print((r.pages[0].extract_text() or '')[:500])
EOF
ls -la "/Users/pete/Downloads/Usama Kadri Sep 11.pdf"
echo; echo "=== Kadri 2019 mentions: lit review vs summary"; git show origin/claude-science-sep29:"Claude Science Project Sep 29/results/hydroacoustics-literature-review.md" | grep -n -i "kadri2019\|Kadri 2019\|Kadri (2019" | cut -c1-300 | head -8