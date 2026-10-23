t=open(p).read()
ids={"3f52be83-f18b-48b7-b587-8a74a9794c66":"haixun-water-column.png","fc455a0f-8dad-4537-bebf-402670d1f354":"haixun-detection-vs-offset.png","8c8336b5-383c-4e5f-a57b-da1703b82209":"haixun-bayes-factor-sensitivity.png"}
L="{"+"{artifact:art_"; R="}"+"}"
repo_t=t; art_t=t
for aid,fn in ids.items():
    m="../../../../"+L+aid+R
    assert m in t
    repo_t=repo_t.replace(m,fn); art_t=art_t.replace(m,L+aid+R)
open(p,"w").write(repo_t); open("haixun-beacon-physics-results.md","w").write(art_t)
print(repo_t.count(L), art_t.count(L), art_t.count("../../../../"))