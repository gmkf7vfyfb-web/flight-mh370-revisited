cd /Users/pete/Downloads/flight-mh370-revisited
H=origin/hypothesis/hydroacoustics; P='Claude Science Project Sep 29'
git grep -n -i -E "2019|san juan" $H -- "$P/engine/hypotheses/hydroacoustics/prepare/kadri_package/v2-2026-10-22/" | grep -v -i "predictions.csv" | sed "s|^$H:$P/engine/hypotheses/hydroacoustics/prepare/kadri_package/v2-2026-10-22/||" | cut -c1-360
echo "--- exchange copy"; grep -n -i -E "2019|san juan|closed access" /Users/pete/Downloads/mh370-exchange/hydroacoustics/kadri-package-v2/*.md 2>/dev/null | cut -c1-320 | head
echo "--- the same misattribution elsewhere on sep29 (Kadri + 2019 + San Juan/JASA):"
git grep -n -i -E "kadri[^|]{0,40}2019[^|]{0,60}(san juan|jasa)|(san juan|jasa)[^|]{0,60}kadri[^|]{0,20}2019|kadri ?\(?2019\)?[^.]{0,40}(san juan|ara)" origin/claude-science-sep29 -- "$P" | sed "s|^origin/claude-science-sep29:$P/||" | cut -c1-260 | head -20