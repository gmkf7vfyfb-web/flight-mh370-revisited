cd hydro/"Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/windows_run_j"
python - <<'EOF'
import csv
rows=list(csv.DictReader(open('windows.csv')))
for r in rows:
    if r['receiver']=='H01W' and r['branch']=='SOFAR': print(r['option'],r['p'],r['q0.5'],r['q99.5'])
EOF
N="../../../../../../../repo/Claude Science Project Sep 29/results/hydroacoustics-run-j-windows.md"
python - "$N" <<'EOF'
import sys,re
p=sys.argv[1]; s=open(p).read()
s=re.sub(r"\| -(\d+\.\d)°S \|", r"| \1°S |", s)
open(p,'w').write(s)
EOF
grep -n "°S |" "$N" | head -4