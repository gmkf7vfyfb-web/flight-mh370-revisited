python -c "
import json;d=json.load(open('/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/geometry/run.json'))
s=json.dumps(d,indent=1); print(s[:3500])"