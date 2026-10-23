import pandas as pd, re
M="repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/"
tl = pd.read_csv(M+"data/blackman/blackman_transmission_loss.csv", comment="#")
print(tl.columns.tolist(), len(tl))
print(tl.drop(columns=[c for c in tl.columns if c in ("notes",)]).to_string(max_colwidth=45))
t=open("repo/ISO Sept 28 Status/inputs/papers/hydroacoustics/ucrl-tr-207323.txt").read()
for m in re.finditer(r"Figure 23|Fig\.? ?23", t):
    print("...", t[max(0,m.start()-300):m.start()+900].replace("\n"," ")); print("====")