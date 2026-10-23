cd /Users/pete/Downloads/mh370-exchange/end-of-flight && python3 - <<'PY'
import json
a=json.load(open("run-i/next-i-free/seed-1/run.json"))["config"]
b=json.load(open("run-i-dive/next-i-free/seed-1/run.json"))["config"]
def flat(d,p=""):
    out={}
    for k,v in d.items():
        kk=f"{p}.{k}" if p else k
        if isinstance(v,dict): out.update(flat(v,kk))
        else: out[kk]=v
    return out
fa,fb=flat(a),flat(b)
for k in sorted(set(fa)|set(fb)):
    if fa.get(k,"<absent>")!=fb.get(k,"<absent>"):
        print(f"{k}\n   run-i     : {str(fa.get(k,'<absent>'))[:300]}\n   run-i-dive: {str(fb.get(k,'<absent>'))[:300]}")
print("\n--- terminal (run-i) ---"); print(json.dumps(a["terminal"],indent=1)[:1500])
PY