cd "./.tmp/repo/Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/outputs"; python3 - <<'EOF'
import json
def flat(o,p=''):
    if isinstance(o,dict):
        for k,v in o.items(): yield from flat(v,p+'.'+k)
    elif isinstance(o,list):
        for i,v in enumerate(o[:8]): yield from flat(v,p+f'[{i}]')
    else: yield p,o
for f in ['summary.json','conditional-geometry-summary.json']:
    print('#####',f)
    for p,v in flat(json.load(open(f))):
        if isinstance(v,(int,float)) and ('p' in p.split('.')[-1].split('_') or p.endswith('_p') or 'p_' in p.split('.')[-1]) or 'status' in p or 'conclusion' in p or 'interpret' in p:
            print(p,'=',str(v)[:200])
EOF
grep -rl "0\.0025" . ../data 2>/dev/null | grep -v "\.md$" | head