import json,re
T=json.load(open("handoff/atsb_texts.json"))
a=T["atsb2017"]; b=T["atsb2014jun"]
for name,txt in [("2017",a),("2014",b)]:
    for m in re.finditer(r"Haixun",txt):
        pass
i=a.find("Haixun"); print([m.start() for m in re.finditer("Haixun",a)][:20])
print([m.start() for m in re.finditer("Haixun",b)][:20])