
print(cd.pivot_table(index="method", columns=["station","label"], values="utc", aggfunc="count", fill_value=0).to_string())
print("--- boxes: p_null by method"); print(bx.pivot_table(index="box", columns="method", values="p_null").round(2).to_string())
print("--- M2 top 5"); print(m2.head(5)[["utc_h01w","lag_s","utc_h08s","M2","p_null","label","box"]].to_string(index=False))
print("--- labelled candidates with p<0.1:"); print(cd[(cd.p_null<0.1)&(cd.box!="unlabelled")][["panel","method","utc","p_null","label","box"]].to_string(index=False))
print("--- H08S survivors"); print(sc.groupby(["panel","stage"]).size().to_string())
print(sc[sc.stage=="c1+c2"][["panel","utc","z","off_cadence","lag_consistent_with"]].to_string(index=False))
print(pd.read_csv("out/h08s/injection_pd.csv").round(2).to_string(index=False))
