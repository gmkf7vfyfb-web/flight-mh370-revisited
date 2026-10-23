set -e
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/kadri_package/v2-2026-10-22"
python - <<'EOF'
import hashlib, pathlib, re
lines=pathlib.Path('MANIFEST.txt').read_text().splitlines()
out=[lines[0]]
for l in lines[1:]:
    h,rest=l.split('  ',1); size,name,_,prov=re.match(r'\s*(\d+)  (\S+)  (--)  (.*)',rest).groups()
    p=pathlib.Path(name) if not name.startswith('synthetic_triad/') else pathlib.Path('/Users/pete/Downloads/mh370-exchange/hydroacoustics/kadri-package-v2')/name
    out.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.stat().st_size:>9d}  {name}  --  {prov}")
pathlib.Path('MANIFEST.txt').write_text('\n'.join(out)+'\n'); print(len(out)-1,'files')
EOF
EXD=/Users/pete/Downloads/mh370-exchange/hydroacoustics/kadri-package-v2
rsync -a --exclude synthetic_triad --exclude '*.zip' --exclude SHA256SUMS ./ $EXD/
cd $EXD/.. && rm -f kadri-package-v2/*.zip && zip -qr kadri-package-v2/kadri-package-v2-2026-10-22.zip kadri-package-v2 -x 'kadri-package-v2/*.zip' 'kadri-package-v2/COVER_NOTE_FOR_PETE.md' 'kadri-package-v2/SHA256SUMS' && cd kadri-package-v2 && shasum -a 256 *.csv *.md *.txt *.json *.npz *.py *.zip synthetic_triad/*.npz > SHA256SUMS && ls -la *.zip && du -sh .
# commit module branch
cd /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/1814d527-d9b6-410a-a48a-1b497eabc73d/hydro
export GIT_CONFIG_GLOBAL=/dev/null; B=hypothesis/hydroacoustics
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
git fetch -q origin $B 2>/dev/null || true
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/kadri_package/v2-2026-10-22" "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/kadri_package/README.txt"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); echo "$OLD -> $NEW"; [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (kadri-package track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "Hydroacoustics block 12: Kadri collaboration package v2 (PREPARE ONLY, nothing sent). predictions.csv on the whole-arc grid (run J 74 seeds + supplement; D0'/D2/D3/D4; both branches; TL per band with flags; levels for five eta), windows.csv with both Kadri times as reference rows, reference_measure.py + M1b templates, run J pulse model synthetic triad set + self-test, REQUESTS.md (incl. Royer draft), CALIBRATION_STATUS.txt rewritten with the block 7 gate verdict, cover note for Pete. PREDICTIVE, NOT CALIBRATED; C1, C2.")
git push -q "$URL" $C:refs/heads/$B && echo "PUSHED $C" || { git fetch -q origin $B; echo "RETRY needed"; }