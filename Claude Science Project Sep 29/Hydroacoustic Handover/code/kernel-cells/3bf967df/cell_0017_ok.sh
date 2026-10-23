cd ~/Downloads/mh370-exchange/end-of-flight/run-j/run-j-waypoints/seed-1; python - <<'EOF'
import json
r=json.load(open('run.json'))
def walk(o,p=''):
    if isinstance(o,dict):
        for k,v in o.items(): walk(v,p+'/'+k)
    elif isinstance(o,list):
        if o and not isinstance(o[0],(dict,list)): 
            s=str(o)[:150]
            if any(w in (p+s).lower() for w in ('weight','column','loglik')): print(p,s)
        else:
            for i,v in enumerate(o[:3]): walk(v,f'{p}[{i}]')
    else:
        if any(w in (p+str(o)).lower() for w in ('weight','loglik','prior')): print(p,str(o)[:200])
walk(r)
EOF
sed -n '60,111p' COLUMNS.txt | tr '\n' ' '