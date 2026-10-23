import pandas as pd, re
tl = pd.read_csv("repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/data/blackman/blackman_transmission_loss.csv", comment="#")
print(tl.columns.tolist()); print(len(tl))
cols=[c for c in tl.columns if c not in ("notes",)]
print(tl[cols].to_string(max_colwidth=40))
t=open("repo/ISO Sept 28 Status/inputs/papers/hydroacoustics/ucrl-tr-207323.txt").read()
for m in re.finditer(r"Figure 23|Fig\. 23|transmission loss", t):
    print("...", t[max(0,m.start()-200):m.start()+700].replace("\n"," ")); print("====")