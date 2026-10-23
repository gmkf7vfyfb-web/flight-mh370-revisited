R=/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j
sed -n 1,200p $R/run-j-waypoints/README.md | cut -c1-400
echo ==== mixture json keys
python - <<'EOF'
import json
d=json.load(open('/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/summary/table-0019-mixture.json'))
print(list(d.keys()))
for k,v in d.items():
    s=json.dumps(v); print(k, s[:600])
EOF