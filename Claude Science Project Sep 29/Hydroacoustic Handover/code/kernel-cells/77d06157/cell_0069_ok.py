exec(open("gfx/charts_table.py").read()); style()
df=build_rows(); print(df[["row","implied_position","implied_impact_utc","p_H01W","p_H08S"]].to_string())
W7=[("hypothesis",34),("implied_position",26),("implied_impact_utc",20),("arrivals_utc",20),("trace_assessment",44),("eta_needed",20),("bearing",31)]
nl=[max(textwrap.fill(str(r[k]),n).count("\n")+1 for k,n in W7)+1 for _,r in df.iterrows()]; print(nl, sum(nl))