sleep 240; S=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated.staging; df -k /System/Volumes/Data | tail -1; tail -2 $S/driver.log; ls $S/_parts | wc -l; python - <<'EOF'
import json,glob
for f in sorted(glob.glob("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated.staging/_parts/*.json")):
    d=json.load(open(f)); 
    if "columns_written" in d and len(d["columns_written"])<5: print(f.split("/")[-1], len(d["columns_written"]), round(d["free_gib_at_write"],1))
EOF