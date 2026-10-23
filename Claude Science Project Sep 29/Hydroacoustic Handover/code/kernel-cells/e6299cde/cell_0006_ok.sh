cd "repo/Claude Science Project Sep 29"
echo "===== INBOX headers"; grep -n "^## \|^### " coordination/HYDROACOUSTICS.md | tail -8
n=$(grep -n "^## \|^### " coordination/HYDROACOUSTICS.md | tail -3 | head -1 | cut -d: -f1)
sed -n "${n},1690p" coordination/HYDROACOUSTICS.md | head -150
echo "===== WINDOWS NOTE"; cat results/hydroacoustics-run-j-windows.md