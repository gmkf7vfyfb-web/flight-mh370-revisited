E=/Users/pete/Downloads/mh370-exchange/hydroacoustics
ls $E/run-j-windows/ | grep -v '^_w_'
echo ===
for f in $E/run-j-windows/*.csv; do echo "## $f"; head -4 "$f"; wc -l "$f"; done 2>/dev/null | head -80
echo ===
cat $E/run-j-windows/README.md 2>/dev/null | head -60
echo === evidence
head -3 $E/run-j-tl-grid/evidence/evidence_alone.csv; wc -l $E/run-j-tl-grid/evidence/*.csv; cat $E/run-j-tl-grid/evidence/noise_levels.json | head -50