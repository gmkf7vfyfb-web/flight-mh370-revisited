cd repo && timeout 60 git ls-remote origin hypothesis/hydroacoustics; git rev-parse HEAD
python3 - <<'EOF'
import json,csv
J=json.load(open("../hydro/bmr/bearing-mixture-rerun.json"))
with open("../hydro/bmr/bearing-mixture-rerun.csv","w",newline="") as f:
    w=csv.DictWriter(f, fieldnames=list(J["rows"][0].keys())); w.writeheader(); w.writerows(J["rows"])
print(len(J["rows"]))
EOF