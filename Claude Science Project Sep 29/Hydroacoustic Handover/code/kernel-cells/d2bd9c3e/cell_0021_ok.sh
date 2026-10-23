cd hydro; export GIT_CONFIG_GLOBAL=/dev/null
P="Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/data/kadri-figure-extraction/figure9-vector-traces"
mkdir -p ../kadri9
for p in a-H01W b-H01W c-H01W d-H08S e-H08S; do git show "origin/hypothesis/hydroacoustics:$P/kadri-2024-figure9-panel-$p.csv" > ../kadri9/panel-$p.csv 2>/dev/null; done
cd ../kadri9; wc -l *.csv; head -3 panel-a-H01W.csv; head -3 panel-d-H08S.csv
python - <<'EOF'
import csv,glob
for f in sorted(glob.glob('panel-*.csv')):
    rows=list(csv.reader(open(f))); hdr=rows[0]; body=[r for r in rows[1:] if r and not r[0].startswith('#')]
    print(f, hdr, body[0], body[-1], len(body))
EOF
# any README in that folder?
cd ../hydro; git ls-tree --name-only "origin/hypothesis/hydroacoustics:Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/data/kadri-figure-extraction/" 2>/dev/null