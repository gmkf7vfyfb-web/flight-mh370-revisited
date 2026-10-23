import sys, importlib.util, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
M="repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
spec=importlib.util.spec_from_file_location("dg", M+"/prepare/digitise_duncan_fig3.py"); dg=importlib.util.module_from_spec(spec); spec.loader.exec_module(dg)
top, bot = dg.main(P, M+"/data")
# overlay check: digitised points drawn on the original pixel grid
fig, ax = plt.subplots(figsize=(6.5,6.1))
ax.imshow(np.array(Image.open(P).convert("RGB")))
px = lambda r: dg.X0 + r/3500*(dg.X1-dg.X0)
for p,c in [("MH370","cyan"),("F35","k")]:
    d=top[top.path==p]; ax.plot(px(d.range_km), dg.T0+(-80-d.power_mean_db)/100*(dg.T1-dg.T0), "-", color=c, lw=1.2)
    e=bot[bot.path==p]; ax.plot(px(e.range_km), dg.B0+e.water_depth_m/7000*(dg.B1-dg.B0), ".", color=c, ms=1)
    ax.plot(px(e.range_km), dg.B0+e.dsc_axis_depth_m/7000*(dg.B1-dg.B0), ".", color="magenta" if p=="F35" else "lime", ms=1)
ax.set_axis_off(); fig.savefig("hydro/duncan-fig3-digitisation-check.png", dpi=200, bbox_inches="tight")
