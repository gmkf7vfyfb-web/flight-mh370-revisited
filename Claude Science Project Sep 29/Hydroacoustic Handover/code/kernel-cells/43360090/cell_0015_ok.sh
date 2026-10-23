cd "./.tmp/repo/Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics"; cat data/two-station-correlation-config.json | head -c 5700; echo; echo =====; python3 - <<'EOF'
import json
s=json.load(open('outputs/two-station-correlation-summary.json'))
def show(o,d=0,maxd=3,maxl=25):
    pad='  '*d
    if isinstance(o,dict):
        for i,(k,v) in enumerate(o.items()):
            if i>=maxl: print(pad+f'... ({len(o)} keys)'); break
            if isinstance(v,(dict,list)) and d<maxd:
                print(pad+str(k)+':'); show(v,d+1,maxd,maxl)
            else: print(pad+f"{k}: {json.dumps(v)[:260]}")
    elif isinstance(o,list):
        print(pad+f"[list len {len(o)}]")
        for v in o[:2]: show(v,d+1,maxd,maxl)
    else: print(pad+json.dumps(o)[:260])
show(s)
EOF