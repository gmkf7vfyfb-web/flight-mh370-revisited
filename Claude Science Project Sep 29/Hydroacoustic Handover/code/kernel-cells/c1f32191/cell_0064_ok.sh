sleep 60; S=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated.staging; tail -3 $S/driver.log 2>/dev/null; tail -3 $S/driver.out 2>/dev/null; ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/ | grep gated; ls $S/_parts 2>/dev/null | wc -l
python - <<'EOF'
import json,glob
n=0
for f in sorted(glob.glob("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated*/_parts/*.json")):
    d=json.load(open(f))
    if "columns_written" in d and len(d["columns_written"])<5: n+=1; print(f.split("/")[-1], len(d["columns_written"]), round(d["free_gib_at_write"],1))
print("short", n)
EOF
df -k /System/Volumes/Data | tail -1