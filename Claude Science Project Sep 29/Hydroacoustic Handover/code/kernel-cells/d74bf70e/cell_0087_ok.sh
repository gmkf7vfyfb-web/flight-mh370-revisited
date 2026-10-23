cd repo && git sparse-checkout add "/ISO Sept 28 Status/inputs/recovered-v01/.sources/kadri-2024-hydroacoustics/data/kadri-table1-transients.csv" >/dev/null 2>&1; f="ISO Sept 28 Status/inputs/recovered-v01/.sources/kadri-2024-hydroacoustics/data/kadri-table1-transients.csv"; head -3 "$f"; echo; wc -l "$f"
python3 - "$f" <<'EOF'
import csv,sys
r=list(csv.DictReader(open(sys.argv[1])))
print(len(r), list(r[0].keys()))
EOF