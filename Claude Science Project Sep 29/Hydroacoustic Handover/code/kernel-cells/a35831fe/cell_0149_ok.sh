cd "main/Claude Science Project Sep 29"
sed -n 50,64p results/hydroacoustics-references.md | cut -c1-400
echo ====; sed -n 765,776p coordination/architecture.md | cut -c1-400
echo ====; sed -n 2744,2751p coordination/architecture.md | cut -c1-400
echo ====; sed -n 50,58p results/hydroacoustics-calibration-events-stage1b.md | cut -c1-400
echo ====; grep -n "pick" results/hydroacoustics-methods-draft.md | head; grep -rn "10 s pick\|pick sd\|PICK_S" coordination/architecture.md | head -5 | cut -c1-400