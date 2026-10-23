cd "./.tmp/repo/ISO Sept 28 Status/results/worktree-hydroacoustics/hydroacoustics"; python3 - <<'EOF'
import json
def show(o,d=0,maxd=3,maxl=12):
    pad='  '*d
    if isinstance(o,dict):
        for i,(k,v) in enumerate(o.items()):
            if i>=maxl: print(pad+'...'); break
            if isinstance(v,(dict,list)) and d<maxd:
                print(pad+str(k)+':'); show(v,d+1,maxd,maxl)
            else:
                s=json.dumps(v); print(pad+f"{k}: {s[:220]}")
    elif isinstance(o,list):
        print(pad+f"[list len {len(o)}]")
        for v in o[:3]: show(v,d+1,maxd,maxl)
    else: print(pad+json.dumps(o)[:220])
for f in ['kadri-tests/kadri-tests.json','imos/earthquake-controls.json']:
    print('#####',f); show(json.load(open(f)),maxd=4,maxl=20)
EOF