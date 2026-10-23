cd "audit/repo/Claude Science Project Sep 29/results/hydroacoustics-audit"; python3 - <<'EOF'
s=open('c3-source-models.md').read()
old="used as a proxy because the Ewing 20-gun geometry is not printed in Blackman (2004). Tolstoy et al. (2004) state that such arrays focus energy downwards |"
new="used as a proxy because the Ewing 20-gun geometry is not printed in Blackman (2004). That such arrays radiate less sound in near-horizontal directions is stated in the NMFS notice for the L-DEO Langseth surveys (Federal Register document 2012-07717, public-inspection copy) |"
assert old in s; s=s.replace(old,new)
s+="\n**Amendment 1 (same day, after a reviewer finding; no number changed).** The first version cited Tolstoy et al. (2004) for\nthe statement that airgun arrays focus energy downwards. The audit never obtained that paper's text from an authorised\nsource (the open-access fetch failed), so the citation is withdrawn and replaced with the public NMFS Federal Register\nnotice 2012-07717. M3 itself (geometry and formula) is unchanged.\n"
open('c3-source-models.md','w').write(s)
EOF
cd ../../..; git add -A "Claude Science Project Sep 29/results/hydroacoustics-audit/c3-source-models.md"; git commit -q -m "hydroacoustics audit: C3 amendment 1 - withdraw Tolstoy 2004 directivity citation (text not obtained from an authorised source); cite NMFS Federal Register 2012-07717" && git push -q https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git HEAD:claude-science-sep29 2>&1 | grep -v -e 'failed to store' -e ignore | tail -2; git log --oneline -1