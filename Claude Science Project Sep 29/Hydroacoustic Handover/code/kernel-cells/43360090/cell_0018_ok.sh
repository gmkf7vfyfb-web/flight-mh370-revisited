cd "./.tmp/repo/Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/outputs"; python3 - <<'EOF'
import json
def flat(o,p=''):
    if isinstance(o,dict):
        for k,v in o.items(): yield from flat(v,p+'.'+k)
    elif isinstance(o,list):
        for i,v in enumerate(o[:6]): yield from flat(v,p+f'[{i}]')
    else: yield p,o
for f in ['oscar-boundary-audit-summary.json','event-pair-analysis-summary.json','aligned-detection-analysis-summary.json','impact-simulation-summary.json']:
    print('#####',f)
    for p,v in flat(json.load(open(f))):
        if any(s in p.lower() for s in ['p_','_p','status','null','conclusion','interpret','percentile','count','limit','surrog','threshold','sigma','false']):
            print(p, '=', str(v)[:240])
EOF