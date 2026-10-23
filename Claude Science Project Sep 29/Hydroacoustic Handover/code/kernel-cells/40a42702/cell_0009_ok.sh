cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
python - <<'EOF'
import json
m=json.load(open('data/imos_background/MANIFEST.json'))
print(m['source'], m['days'], m['held_at'])
for k,v in m['loggers'].items():
    print(k, type(v), (list(v)[:6] if isinstance(v,dict) else len(v)))
    if isinstance(v,dict):
        for kk in list(v)[:6]:
            vv=v[kk]; print('  ',kk, (vv if not isinstance(vv,(list,dict)) else (len(vv), (vv[0] if isinstance(vv,list) else list(vv)[:3]))))
EOF
ls /Users/pete/Downloads/mh370-inputs/hydroacoustics/imos/background/ ; for d in /Users/pete/Downloads/mh370-inputs/hydroacoustics/imos/background/*/; do echo "$d $(ls $d | wc -l) $(du -sh $d | cut -f1)"; done
echo --- weak_signal common/template/bank/methods
sed -n 1,80p prepare/weak_signal/common.py