O=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated-v2; tail -3 $O/driver.log | cut -c1-120; cat $O/READY; head -8 $O/README.txt | cut -c1-220; du -sh $O; df -k /System/Volumes/Data | tail -1 | awk '{print $4/1048576 " GiB free"}'
python - <<'EOF'
import json,glob,numpy as np
O="/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated-v2"
parts=[json.load(open(f)) for f in glob.glob(f"{O}/_parts/*.json") if not f.endswith("supplement.json")]
print("seeds", len(parts), "rows", sum(p["rows"] for p in parts), "nc", sum(p["not_computed"] for p in parts), "short", sum(len(p["columns_written"])<5 for p in parts), "imos_tl", set(p["imos_tl"] for p in parts))
q=np.array([p["quantiles"]["hydro-lnL-imos-margeta"] for p in parts]); print("marg quantiles median over seeds", np.round(np.median(q,0),3))
# consistency: v2 acc vs stats-ramgrid acc for one seed
a=np.load(f"{O}/run-j-free/seed-3/acc.npz"); b=np.load(f"{O.replace('-v2','')}/stats-ramgrid/run-j-free/seed-3/acc.npz")
print("acc equal (wL_a0.05):", np.allclose(a["wL_a0.05"], b["wL_a0.05"]), " sum_w equal:", np.allclose(a["sum_w"], b["sum_w"]))
EOF
cd $O && find . -name "*.npy" -o -name "README.txt" -o -name "COLUMNS.txt" | sort | xargs shasum -a 256 > SHA256SUMS.tmp && mv SHA256SUMS.tmp SHA256SUMS && wc -l SHA256SUMS