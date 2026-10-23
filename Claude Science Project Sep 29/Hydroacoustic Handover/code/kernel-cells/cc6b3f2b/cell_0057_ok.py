
cd = pd.read_csv("out/kadri/candidates.csv"); print(len(cd)); print(cd.groupby("label").size())
print(cd[cd.p_null<0.1].to_string(index=False))
bx = pd.read_csv("out/kadri/box_maxima.csv"); print(bx.pivot_table(index="box", columns="method", values="p_null").round(2).to_string())
m2 = pd.read_csv("out/kadri/m2_cross_station.csv"); print(m2.head(8).to_string(index=False)); print(json.load(open("out/kadri/summary.json")))
sc = pd.read_csv("out/h08s/surviving_candidates.csv"); print(sc.groupby(["panel","stage"]).size())
print(sc[sc.stage!="raw"].sort_values("z", ascending=False).to_string(index=False))
print(pd.read_csv("out/h08s/injection_pd.csv").round(2).to_string(index=False))
