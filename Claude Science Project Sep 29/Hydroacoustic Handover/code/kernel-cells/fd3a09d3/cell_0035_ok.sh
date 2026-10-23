cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
python - <<'EOF'
import pathlib; p=pathlib.Path('tl_grid_run_j.py'); s=p.read_text()
s=s.replace("        # Validated in the timing run (arc020.0S_+0-3250: KRAKEN no_modes in all 10 bands, 7 m minimum).",
"        # Validated before the grid run with --no-prescreen: arc036.0S_+0-3250 (1.5 m), arc026.0S_+0-H08N (2.5 m) and\n        # arc036.0S_+0-H08N (10.5 m) all gave KRAKEN no_modes in all 10 bands; arc030.0S_+0-3250 (104 m) was open from 12.5 Hz.")
s=s.replace("BLOCKAGE RULE (the module's existing rule, nx2d.py step 3 and imos_stageB_tl.py; no new threshold): a path whose\non-track GEBCO elevation is >= 0 m anywhere is BLOCKED 'land' and not run; a (path, band) for which KRAKEN finds no\npropagating mode on some 5-km profile (fatal \"No modes\") is BLOCKED 'no_modes' for that band, contributing zero\nreceived energy.",
"BLOCKAGE RULE (the module's existing rule, nx2d.py step 3 and imos_stageB_tl.py; no new threshold): a path whose\non-track GEBCO elevation is >= 0 m anywhere is BLOCKED 'land' and not run; a (path, band) for which KRAKEN finds no\npropagating mode on some 5-km profile (fatal \"No modes\") is BLOCKED 'no_modes' for that band, contributing zero\nreceived energy. A path with a 5-km profile shallower than 15 m is marked 'no_modes_shallow' in every band without\nrunning KRAKEN (validated equivalent of the same rule, see run_path; --no-prescreen disables it).")
p.write_text(s)
EOF
python -c "import ast,sys; ast.parse(open('tl_grid_run_j.py').read()); print('syntax ok')"
cd ../../../../..   # hydro clone root
export GIT_CONFIG_GLOBAL=/dev/null; B=hypothesis/hydroacoustics
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
git fetch -q origin $B 2>&1 | grep -v "failed to store"
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/tl_grid_run_j.py"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); echo "$OLD -> $NEW"; [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (tl-grid)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "Hydroacoustics block 2: pre-register the whole-arc TL grid method (tl_grid_run_j.py; 41-20 S, offsets -60..+60 NM, 8 receivers, module's KRAKEN settings and blockage rule) before the grid run")
git push -q "$URL" $C:refs/heads/$B 2>&1 | grep -v "failed to store"; echo "commit $C"; git fetch -q origin $B 2>&1 | grep -v "failed to store"; git log --oneline -1 origin/$B