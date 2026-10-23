E["CORE_STAGES.md"] = E["CORE_STAGES.md"].replace("Sabang and Lhokseumawe are 25-212 NM from these points.",
  "Sabang and Lhokseumawe are 25-212 NM from these points. The Indian positions are airfield reference points used as proxies, and the Indonesian positions are approximate town positions; no radar antenna site or height is published.")
for fn,txt in E.items():
    with open(f"repo/r/Claude Science Project Sep 29/coordination/{fn}","a") as f: f.write(txt)
print("ok")