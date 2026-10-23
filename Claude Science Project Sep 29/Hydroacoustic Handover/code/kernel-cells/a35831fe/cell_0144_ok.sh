cat hist2_233.txt; python - <<'E'
import json
F='/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/tool-results/a35831fe-107a-4961-bc9f-e6fd6d255601/compaction-history/a35831fe-107a-4961-bc9f-e6fd6d255601/compaction_0.txt'
L=open(F).readlines()
for i in (233,234):
    print('---',i, L[i][:2500])
E