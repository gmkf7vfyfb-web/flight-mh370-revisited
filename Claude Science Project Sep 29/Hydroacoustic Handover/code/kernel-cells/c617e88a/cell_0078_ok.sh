sleep 600; python -c "
import json; r=json.load(open('work/result/per_seed.json')); print(len(r)//3, [ (x['stratum'],x['seed']) for x in r[-1:]])"; ls work/power