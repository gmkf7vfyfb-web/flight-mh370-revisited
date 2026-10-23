python - <<'E'
import json
F='/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/tool-results/a35831fe-107a-4961-bc9f-e6fd6d255601/compaction-history/a35831fe-107a-4961-bc9f-e6fd6d255601/compaction_0.txt'
for i,l in enumerate(open(F)):
    try: m=json.loads(l)
    except: continue
    c=m.get('content')
    if not isinstance(c,list): continue
    for b in c:
        if b.get('type')=='tool_use':
            code=b['input'].get('code',b['input'].get('command',''))
            if isinstance(code,str) and ('CANDS=' in code or 'CANDS =' in code or 'arcline' in code.lower() or "'resid'" in code):
                open(f'hist2_{i}.txt','w').write(code); print(i,len(code))
E