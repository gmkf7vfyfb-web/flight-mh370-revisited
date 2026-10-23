S=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated.staging; grep -c launch $S/topup.log; grep SKIP $S/topup.log | wc -l; grep -h "done\|Error\|Traceback" $S/_w_topup_*.log | head; python - <<'EOF'
import json,glob
n=0
for f in sorted(glob.glob("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated.staging/_parts/*.json")):
    d=json.load(open(f))
    if "columns_written" in d and len(d["columns_written"])<5: n+=1; print(f.split("/")[-1])
print("still short", n)
EOF
df -k /System/Volumes/Data | tail -1