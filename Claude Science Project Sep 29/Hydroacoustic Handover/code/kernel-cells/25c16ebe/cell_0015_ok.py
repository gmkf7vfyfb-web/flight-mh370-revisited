rj = json.load(open(f"{S}/run.json"))
print(list(rj.keys()))
txt = json.dumps(rj)
import re
# find onset / descent config blocks
for k in ["onset","descent","profile","level","dive","pushover","checkpoint","handoff","families","family"]:
    hits = [m.start() for m in re.finditer(k, txt)][:3]
    for h in hits[:1]:
        print(f"\n--- '{k}' @{h}:", txt[max(0,h-300):h+500].replace("\\n","\n")[:800])
