
sup = pd.read_csv("out/h08s/suppression.csv"); print(sup.round(2).to_string(index=False))
sc = pd.read_csv("out/h08s/surviving_candidates.csv"); print(sc.groupby(["panel","stage"]).size())
print(sc[sc.stage=="c1+c2"].sort_values("z", ascending=False).head(20).to_string(index=False))
print(pd.read_csv("out/h08s/injection_pd.csv").round(2).to_string(index=False))
