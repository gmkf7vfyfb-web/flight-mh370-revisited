cd audit/lit; python3 -c "
import pypdfium2 as p; d=p.PdfDocument('fr2012-07717.pdf'); t=d[9].get_textpage().get_text_range(); print(repr(t[:120])); print(repr(t[-80:]))"; cd "../repo/Claude Science Project Sep 29/results/hydroacoustics-audit"; python3 - <<'EOF'
s=open('c3-source-models.md').read()
old="is stated in the NMFS notice for the L-DEO Langseth surveys (Federal Register document 2012-07717, public-inspection copy) |"
new="is stated in the NMFS notice for the L-DEO Langseth surveys (Federal Register document 2012-07717, public-inspection copy, p. 10: effective source levels for horizontal propagation \"are lower than those for downward propagation\"; text read in the audit) |"
assert old in s; s=s.replace(old,new)
s+="\n**Amendment 2 (same day).** Amendment 1's citation was first taken from a search listing. The notice was then\nretrieved (public-inspection PDF, 82 pages) and the statement was confirmed on its page 10. No number changed.\n"
open('c3-source-models.md','w').write(s)
EOF
cd ../../..; git add "Claude Science Project Sep 29/results/hydroacoustics-audit/c3-source-models.md"; git commit -q -m "hydroacoustics audit: C3 amendment 2 - NMFS FR 2012-07717 text retrieved and the directivity statement confirmed (p. 10)"; git push -q https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git HEAD:claude-science-sep29 2>&1 | grep -v -e 'failed to store' -e ignore | tail -2; git log --oneline -1