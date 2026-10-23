F=/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/tool-results/a35831fe-107a-4961-bc9f-e6fd6d255601/compaction-history/a35831fe-107a-4961-bc9f-e6fd6d255601/compaction_0.txt
python - <<'E'
import json,re
F='/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/tool-results/a35831fe-107a-4961-bc9f-e6fd6d255601/compaction-history/a35831fe-107a-4961-bc9f-e6fd6d255601/compaction_0.txt'
for i,l in enumerate(open(F)):
    try: m=json.loads(l)
    except: continue
    c=m.get('content')
    if not isinstance(c,list): continue
    for b in c:
        if b.get('type')=='tool_use':
            code=json.dumps(b.get('input',{}))
            if 'CANDS' in code and ("resid" in code or 't0' in code) and ('lstsq' in code or 'fit' in code or 'minimize' in code):
                open(f'hist_{i}.txt','w').write(b['input'].get('code',b['input'].get('command','')))
                print(i, len(code))
E