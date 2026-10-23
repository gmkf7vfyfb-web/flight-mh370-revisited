res={}
for f in ["charts_levels","charts_time","charts_kadri","charts_table","charts_traces","charts_air9"]:
    exec(open(f"gfx/{f}.py").read())
style()
for st,n in [("H01W","chart01-noise-vs-levels-H01W"),("H08S","chart02-noise-vs-levels-H08S")]+[(s,f"chart01-02-companion-noise-vs-levels-{s}") for s in ["H08N","3315","3376","3274","3275","3250"]]:
    res[n]=chart_station(st,n)
res["ov"]=chart_overview("chart01-02-companion-noise-vs-levels-overview")
res["c3"]=chart_maps("chart03-loudness-maps")
res["c4"]=chart4("chart04-kadri-poster-boxes-companion")
res["c5"]=chart5("chart05-arrivals-vs-published-traces")
res["c6"]=chart6("chart06-publication-coverage")
res["c7"]=chart7("chart07-hypothesis-table","chart07-hypothesis-table.csv")[0]
res["c9"]=chart9("chart09-illustrative-traces")
res["c10"]=chart10("chart10-air9-predicted-vs-measured")
fig=plt.figure(figsize=(10,4)); 
fig.text(0.04,0.85,"Simulated descents (end-of-flight chart): not redrawn on run J",fontsize=11,va="top")
fig.text(0.04,0.7,textwrap.fill("No run J descent time series exist. The run J products under mh370-exchange/end-of-flight/run-j/ hold one row per impact "
  "(impacts32.npy with COLUMNS.txt, tau90_v1.npz, attitude_v1.npz, parents32.npy, terminal.json): impact state, take-over altitude, flame-out time, "
  "altitude and vertical speed at 00:19:29 and 00:19:37, maximum descent rate and time descending, but no altitude-against-time traces. No script for the "
  "original chart was found in results/ on the work branch. Redrawing the chart from these summary columns would be a reconstruction, not the simulated "
  "trajectories, so it was not done. The original chart (21 Oct) stays as it is; it is from an earlier ensemble, not run J.",110),fontsize=8.5,va="top")
fig.text(0.04,0.12,"Gap: run J descent traces were not saved by the end-of-flight module (request: save altitude-time traces for selected examples).",fontsize=8,va="top",color="#8a1c1c")
fig.savefig(OUT/"chart08-descents-not-redrawn.png"); fig.savefig(OUT/"chart08-descents-not-redrawn.pdf"); plt.close(fig)
for k,v in res.items():
    if v!=([],[]): print(k,v)