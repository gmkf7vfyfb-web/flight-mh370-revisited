cd hydro/"Claude Science Project Sep 29"/engine/hypotheses/hydroacoustics/prepare
python - <<'EOF'
import pathlib
p=pathlib.Path('run_j_levels.py'); s=p.read_text()
s=s.replace('''bs[str(fc).rstrip("0").rstrip(".") if str(fc).endswith(".0") else str(fc)]["median"]''','''bs[f"{fc:g}"]["median"]''')
p.write_text(s)
EOF
cd ../../../../../..
cd hydro; export GIT_CONFIG_GLOBAL=/dev/null; B=hypothesis/hydroacoustics
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
git fetch -q origin $B 2>&1 | grep -v config/git
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/run_j_levels.py"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); echo "$OLD -> $NEW"; [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (levels track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "hydroacoustics: PRE-REGISTRATION run_j_levels.py — block 3 level half + power screen on run J (subsample design, source model, eta grid, TL grid, noise models, Kadri chain, thresholds 7/15 dB, eta_50, charts, math check); committed before any run")
git push -q "$URL" $C:refs/heads/$B 2>&1 | grep -v config/git; echo "commit $C"; git fetch -q origin $B 2>&1 | grep -v config/git; git rev-parse --short origin/$B