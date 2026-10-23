cd audit/repo; F="Claude Science Project Sep 29/results/hydroacoustics-audit-architecture.md"; python3 - "$F" <<'EOF'
import sys
p=sys.argv[1]; t=open(p).read()
a="- **Scored:** 8 shots detected at both H01W and H08S were traced; 13 shot-station spectra gave a usable 50 Hz signal."
b="- **Scored:** 8 shots were detected at both H01W and H08S. Both panels were traced for 6 of them (A6sus3 at H01W and A7sus2 at H08S failed panel detection; A11sus has no model TL to H08S). 13 shot-station spectra gave a usable 50 Hz signal."
assert a in t; t=t.replace(a,b)
a2="2012-07717, p. 10, says horizontal effective source levels are lower than downward ones."
b2="2012-07717, p. 10 (text retrieved and read; C3 amendment 2), says horizontal effective source levels are lower than downward ones."
assert a2 in t; t=t.replace(a2,b2)
open(p,'w').write(t)
EOF
cp "$F" ../../hydroacoustics-audit-architecture.md; git add "$F"; git commit -q -m "hydroacoustics audit report: correct SUS traced-shot count (6 of 8 at both stations); note FR 2012-07717 text was retrieved"; git pull -q --rebase origin claude-science-sep29 2>&1 | grep -v ignore | tail -1; git push -q https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git HEAD:claude-science-sep29 2>&1 | grep -v -e 'failed to store' -e ignore | tail -1; git log --oneline -1