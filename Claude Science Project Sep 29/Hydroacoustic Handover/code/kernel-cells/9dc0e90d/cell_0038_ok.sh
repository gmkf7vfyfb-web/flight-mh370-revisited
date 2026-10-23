cd repo/r && F="Claude Science Project Sep 29/coordination/architecture.md" && python - "$F" <<'EOF'
import sys,re
p=sys.argv[1]; s=open(p).read()
pat=re.compile(r'<<<<<<< [^\n]*\n(.*?)=======\n(.*?)>>>>>>> [^\n]*\n', re.S)
n=len(pat.findall(s)); s=pat.sub(lambda m: m.group(1).rstrip('\n')+'\n'+m.group(2), s)
assert '<<<<<<<' not in s and '>>>>>>>' not in s
open(p,'w').write(s); print('blocks resolved', n)
EOF
grep -c "evidence sweep (Pete's request" "$F"
git add "$F" && GIT_EDITOR=true git -c user.name="Claude Science" -c user.email="noreply@example.com" rebase --continue 2>&1 | tail -1
git push -q origin claude-science-sep29 2>&1 | tail -2; git log --oneline -2; git status -sb | head -1