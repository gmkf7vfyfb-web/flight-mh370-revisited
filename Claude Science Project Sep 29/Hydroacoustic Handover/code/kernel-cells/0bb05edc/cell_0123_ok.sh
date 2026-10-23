cd fix-metz && export GIT_CONFIG_GLOBAL=/dev/null
P='Claude Science Project Sep 29'; B=origin/claude-science-sep29
for x in results/hydroacoustics-bibliography.csv results/hydroacoustics-literature-review.md results/hydroacoustics-prior-work-critique.md; do git show $B:"$P/$x" > "$P/$x"; done
python3 - <<'EOF'
import re
P='Claude Science Project Sep 29/'
f=P+'threads/master-prompts/hydroacoustics.md'
t=open(f,encoding='utf-8',newline='').read()
old="ask Metz's group for the F-35 paper and waveforms"
assert t.count(old)==1
t=t.replace(old,"ask Metz's group for the H11 waveforms (the paper is held, artifact 7e4d336f)")
MARK="STANDING RULE ON LABELS (Pete, 22 Oct 2026)"
import subprocess
blk=subprocess.run(['git','show','origin/claude-science-sep29:'+P+'threads/master-prompts/hydroacoustics.md'],capture_output=True,text=True).stdout
i=blk.index('> **'+MARK); j=blk.index('\n\n',i)+2
block=blk[i:j]
if MARK not in t:
    lines=t.split('\n'); k=next(n for n,l in enumerate(lines[:15]) if l.startswith('# '))
    t='\n'.join(lines[:k+1])+'\n'+block+'\n'.join(lines[k+1:])
open(f,'w',encoding='utf-8',newline='').write(t)
print('master prompt on module branch: Metz fixed, rule present =', MARK in t)
EOF
git add --sparse -A . 2>&1 | grep -v ignore || true
git diff --cached --name-only | sed "s|$P/||"
git commit -q -m "hydroacoustics: sync corrected bibliography/critique/literature review and the brief (Metz held; standing rule on labels) from claude-science-sep29" 2>&1 | grep -v ignore || true
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git"
for i in 1 2 3 4; do
  git -c credential.helper= pull -q --rebase "$URL" hypothesis/hydroacoustics 2>&1 | sed "s/${GITHUB_TOKEN}/***/g" | grep -v ignore || true
  git -c credential.helper= push -q "$URL" fix-hydro:hypothesis/hydroacoustics 2>&1 | sed "s/${GITHUB_TOKEN}/***/g" | grep -v ignore || true
  R=$(git -c credential.helper= ls-remote "$URL" refs/heads/hypothesis/hydroacoustics 2>/dev/null | cut -f1)
  if [ "$(git rev-parse HEAD)" = "$R" ]; then echo "PUSHED: $(git rev-parse --short HEAD)"; break; fi
  sleep 4
done