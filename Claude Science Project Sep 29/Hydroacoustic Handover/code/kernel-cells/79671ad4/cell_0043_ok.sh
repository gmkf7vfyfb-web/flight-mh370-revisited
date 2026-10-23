D="repo/Claude Science Project Sep 29/results/kadri-haixun-conditional-2026-10-18/haixun-beacon-physics"; mkdir -p "$D/inputs"
cp haixun_beacon.py out/*.csv out/*.json out/*.png "$D/"; cp src/woa23_*.asc src/gebco_otd.json src/era5_haixun_2014-04-03_06.csv "$D/inputs/"
ls -la "$D" | awk '{print $5,$9}'; du -sh "$D"
python - <<'EOF'
import json;s=json.load(open("out/bh_summary.json"));g=json.load(open("out/geometry_test.json"))
for c in "ABC":
  r=s["per_calibration"][c]; print(c,{k:(round(v,4) if isinstance(v,float) else v) for k,v in r.items() if k!="sensitivity_f1"})
print(s["headline_mix_A_B"]); print(s["sonobuoy_check"]); print(g["P_overhead_margin_ge_Mreq"])
EOF