cd repo/"Claude Science Project Sep 29/results/evidence-sweep-2026-10-17"
grep -n -i "SWAMS\|NEAMS\|MAD\b\|WKER\|NCRO\|SSEIR\|°S\|Table 5\|GPS" research-radar-infrasound-ohasisbio.md | head -40
echo ==== kadri traces
cd ../../../..; export GIT_CONFIG_GLOBAL=/dev/null
cd hydro
P="Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/data/kadri-figure-extraction/figure9-vector-traces"
git ls-tree --name-only "origin/hypothesis/hydroacoustics:$P" 2>&1 | grep -v "failed to store"