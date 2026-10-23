p="repo/Claude Science Project Sep 29/results/kadri-haixun-conditional-2026-10-18/haixun-beacon-physics/README.md"
t=open(p).read()
rep={"| 0.081 | 0.038 / 0.012 |":"| 0.081 | 0.037 / 0.011 |",
     "| 0.023 | 0.006 / 0.0009 |":"| 0.023 | 0.0059 / 0.00082 |",
     "| 2.4 x 10^-4 | 3 x 10^-5 / 2 x 10^-6 |":"| 2.4 x 10^-4 | 3.1 x 10^-5 / 2.2 x 10^-6 |",
     "(Values at 2 and 3 km are read from `pdet_vs_offset.csv` at the nearest 100 m grid point.)":"(Values at 2 and 3 km are read from `pdet_vs_offset.csv`.)"}
for a,b in rep.items():
    assert a in t,a; t=t.replace(a,b)
repo_t=t.replace("../../../../{{artifact:art_3f52be83-f18b-48b7-b587-8a74a9794c66}}","haixun-water-column.png")\
 .replace("../../../../{{artifact:art_fc455a0f-8dad-4537-bebf-402670d1f354}}","haixun-detection-vs-offset.png")\
 .replace("../../../../{{artifact:art_8c8336b5-383c-4e5f-a57b-da1703b82209}}","haixun-bayes-factor-sensitivity.png")
art_t=t.replace("../../../../{{artifact:","{{artifact:")
open(p,"w").write(repo_t)
open("haixun-beacon-physics-results.md","w").write(art_t)
print(repo_t.count("{{artifact"), art_t.count("{{artifact:art_"))