cd .tmp/standin; python - <<'EOF'
import json
s=json.load(open("q1/af447_q1_summary.json"))
for c in ("total KE","vertical KE"):
    print(c, {k:{a:round(b,1) for a,b in v.items()} for k,v in s[c].items() if k!="by_src_depth_ratio_mean"})
    print("  by z", {z:{a:round(b,1) for a,b in v.items()} for z,v in s[c]["by_src_depth_ratio_mean"].items()})
print(s["inputs"])
EOF