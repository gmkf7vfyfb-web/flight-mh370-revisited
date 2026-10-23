set -e
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/kadri_package/v2-2026-10-22"
for f in README REQUESTS COVER_NOTE_FOR_PETE; do git -c core.quotepath=off mv -f "$f.md" "$f.txt" 2>/dev/null || mv "$f.md" "$f.txt"; done
sed -i '' 's/`REQUESTS\.md`/`REQUESTS.txt` (REQUESTS.md in the zip)/g; s/`README\.md`/`README.txt`/g; s/`COVER_NOTE_FOR_PETE\.md`/`COVER_NOTE_FOR_PETE.txt`/g' README.txt COVER_NOTE_FOR_PETE.txt CALIBRATION_STATUS.txt REQUESTS.txt
sed -i '' 's/COVER_NOTE_FOR_PETE\.md/COVER_NOTE_FOR_PETE.txt/; ' ../README.txt
printf '\n  Note: inside engine/ the three prose files are .txt (project rule: no .md inside engine/); the zip-ready exchange copy carries them as .md.\n' >> ../README.txt
python - <<'EOF'
import pathlib,re,hashlib
m=pathlib.Path('MANIFEST.txt').read_text().replace('  README.md  ','  README.txt  ').replace('  REQUESTS.md  ','  REQUESTS.txt  ').replace('  COVER_NOTE_FOR_PETE.md  ','  COVER_NOTE_FOR_PETE.txt  ')
lines=m.splitlines(); out=[lines[0]]
for l in lines[1:]:
    h,rest=l.split('  ',1); size,name,_,prov=re.match(r'\s*(\d+)  (\S+)  (--)  (.*)',rest).groups()
    p=pathlib.Path(name) if not name.startswith('synthetic_triad/') else pathlib.Path('/Users/pete/Downloads/mh370-exchange/hydroacoustics/kadri-package-v2')/name
    out.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.stat().st_size:>9d}  {name}  --  {prov}")
out.append("# In the zip-ready exchange copy README/REQUESTS/COVER_NOTE are .md (same content); inside engine/ they are .txt by project rule.")
pathlib.Path('MANIFEST.txt').write_text('\n'.join(out)+'\n')
EOF
ls
# exchange copy: .md names
EXD=/Users/pete/Downloads/mh370-exchange/hydroacoustics/kadri-package-v2
rsync -a --exclude synthetic_triad --exclude '*.zip' --exclude SHA256SUMS --exclude 'README.txt' --exclude 'REQUESTS.txt' --exclude 'COVER_NOTE_FOR_PETE.txt' ./ $EXD/
cp README.txt $EXD/README.md; cp REQUESTS.txt $EXD/REQUESTS.md; cp COVER_NOTE_FOR_PETE.txt $EXD/COVER_NOTE_FOR_PETE.md
cd $EXD/.. && rm -f kadri-package-v2/*.zip && zip -qr kadri-package-v2/kadri-package-v2-2026-10-22.zip kadri-package-v2 -x 'kadri-package-v2/*.zip' 'kadri-package-v2/COVER_NOTE_FOR_PETE.md' 'kadri-package-v2/SHA256SUMS' && cd kadri-package-v2 && shasum -a 256 *.csv *.md *.txt *.json *.npz *.py *.zip synthetic_triad/*.npz > SHA256SUMS && ls *.zip && ls
cd /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/1814d527-d9b6-410a-a48a-1b497eabc73d/hydro
export GIT_CONFIG_GLOBAL=/dev/null; B=hypothesis/hydroacoustics
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
git fetch -q origin $B 2>/dev/null || true
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/$B
git rm -q --cached --sparse "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/kadri_package/v2-2026-10-22/README.md" "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/kadri_package/v2-2026-10-22/REQUESTS.md" "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/kadri_package/v2-2026-10-22/COVER_NOTE_FOR_PETE.md"
git add --sparse "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/kadri_package/v2-2026-10-22" "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/kadri_package/README.txt"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); echo "$OLD -> $NEW"; [ "$NEW" -ge "$OLD" ] || { echo "TREE SHRANK (expected: 3 .md renamed to .txt)"; }
git ls-tree -r $TREE --name-only | grep "v2-2026-10-22" 
C=$(git -c user.name="Hydroacoustic Module (kadri-package track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "Hydroacoustics block 12: Kadri package v2 prose files renamed .md -> .txt inside engine/ (project rule: no .md in engine/); manifest updated; exchange zip carries .md copies.")
git push -q "$URL" $C:refs/heads/$B && echo "PUSHED $C" || { git fetch -q origin $B; echo "RETRY needed"; }