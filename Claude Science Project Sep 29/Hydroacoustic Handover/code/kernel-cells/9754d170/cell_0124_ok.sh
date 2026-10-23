cd audit/repo; git log --oneline -1 adaf1ab; git branch -r --contains adaf1ab | head -2; shasum -a 256 ../lit/fr2012-07717.pdf; F="Claude Science Project Sep 29/results/hydroacoustics-audit-architecture.md"; python3 - "$F" <<'EOF'
import sys
p=sys.argv[1]; t=open(p).read()
a="Both panels were traced for 6 of them (A6sus3 at H01W and A7sus2 at H08S failed panel detection; A11sus has no model TL to H08S)."
b="Both panels were traced for 6 of them: all but A6sus3 (H01W panel) and A7sus2 (H08S panel), which failed panel detection. Separately, A11sus was traced at both stations but has no model TL to H08S (path blocked), so it is scored at H01W only. A6sus2 was traced at both stations but was detected only at H08S."
assert a in t; t=t.replace(a,b)
a2="(text retrieved and read; C3 amendment 2)"
b2="(public-inspection PDF retrieved in the audit session, sha256 recorded in C3 amendment 2)"
assert a2 in t; t=t.replace(a2,b2)
open(p,'w').write(t)
EOF
SHA=$(shasum -a 256 ../lit/fr2012-07717.pdf | cut -d' ' -f1); C3="Claude Science Project Sep 29/results/hydroacoustics-audit/c3-source-models.md"; printf '\nRetrieved file: public-inspection.federalregister.gov/2012-07717.pdf, sha256 %s; statement on its page 10.\n' "$SHA" >> "$C3"
cp "$F" ../../hydroacoustics-audit-architecture.md; git add "$F" "$C3"; git commit -q -m "hydroacoustics audit: clarify SUS tracing wording (A11sus blocked TL is not a tracing failure); record sha256 of retrieved FR 2012-07717"; git pull -q --rebase origin claude-science-sep29 2>&1 | grep -v ignore | tail -1; git push -q https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git HEAD:claude-science-sep29 2>&1 | grep -v -e 'failed to store' -e ignore | tail -1; git log --oneline -1