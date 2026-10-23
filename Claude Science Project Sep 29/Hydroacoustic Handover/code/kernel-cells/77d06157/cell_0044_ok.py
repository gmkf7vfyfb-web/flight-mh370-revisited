exec(open("gfx/charts_levels.py").read()); style()
for st,n in [("H01W","chart01-noise-vs-levels-H01W"),("H08S","chart02-noise-vs-levels-H08S")]+[(s,f"chart01-02-companion-noise-vs-levels-{s}") for s in ["H08N","3315","3376","3274","3275","3250"]]:
    r=chart_station(st,n); 
    if r!=([],[]): print(st,r)
print(chart_overview("chart01-02-companion-noise-vs-levels-overview"))
print(chart_maps("chart03-loudness-maps"))