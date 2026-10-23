exec(open("gfx/charts_levels.py").read()); style()
rep={}
for st,n in [("H01W","chart01-noise-vs-levels-H01W"),("H08S","chart02-noise-vs-levels-H08S")]+[(s,f"chart01-02-companion-noise-vs-levels-{s}") for s in ["H08N","3315","3376","3274","3275","3250"]]:
    rep[st]=chart_station(st,n)
rep["ov"]=chart_overview("chart01-02-companion-noise-vs-levels-overview")
print(rep)