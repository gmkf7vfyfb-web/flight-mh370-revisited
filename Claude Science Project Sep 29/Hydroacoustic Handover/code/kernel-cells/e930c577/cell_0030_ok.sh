cd ~/Downloads/mh370-exchange/end-of-flight/run-j; python - <<'E'
import json
j=json.load(open('summary/table-0019-mixture.json'))
def walk(o,p='',d=0):
    if d>3: return
    if isinstance(o,dict):
        for k,v in list(o.items())[:12]:
            print('  '*d+str(k), type(v).__name__, (str(v)[:100] if not isinstance(v,(dict,list)) else len(v)))
            walk(v,p+'/'+k,d+1)
    elif isinstance(o,list) and o and isinstance(o[0],(dict,list)):
        walk(o[0],p,d+1)
walk(j)
E
cat run-j-waypoints/seed-1/run.json | head -c 1500; echo; ls -la run-j-waypoints/seed-1/