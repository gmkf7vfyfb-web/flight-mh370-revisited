cd repo && M="Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
cp ../hydro/stub8/bathy_air8_*.csv ../hydro/stub8/ssp_air8_*.csv ../hydro/stub8/stub-manifest_air8.json "$M/data/stub/"
sed -i '' 's|item 5). Two paths only: air9 -> H01W and air9 -> H08S.|item 5; extended to air8 by ruling H3). Four paths only: air9 and air8 -> H01W and -> H08S.|' "$M/data/stub/PROVISIONAL.txt"; head -2 "$M/data/stub/PROVISIONAL.txt"
git add "$M/data/stub" "$M/prepare/build_path_stub.py" "$M/prepare/air8_negative_control.py"
git diff --cached --name-only | grep -v 'engine/hypotheses/hydroacoustics/'; du -sh "$M/data/stub"
git commit -q -m "Hydroacoustics: air8 path stub (ruling H3) and the pre-registered air8 negative control (H01) with H08S positive control" && timeout 60 git push -q origin hypothesis/hydroacoustics && git log --oneline -1