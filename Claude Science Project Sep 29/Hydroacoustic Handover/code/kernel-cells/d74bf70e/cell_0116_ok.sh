cd repo && F="Claude Science Project Sep 29/coordination/architecture.md"
python3 - "$F" <<'EOF'
import sys; p=sys.argv[1]; t=open(p).read()
a="— Pléiades\n**Hydroacoustics, 2026-10-09 — reply"; assert t.count(a)==1
open(p,'w').write(t.replace(a,"— Pléiades\n\n**Hydroacoustics, 2026-10-09 — reply"))
EOF
git commit -q -am "Coordination: blank line between Pleiades and hydroacoustics entries"
for i in 1 2 3; do timeout 60 git pull -q --rebase origin claude-science-sep29 && timeout 60 git push -q origin HEAD:claude-science-sep29 && { echo pushed; break; }; sleep 3; done; git log --oneline -1