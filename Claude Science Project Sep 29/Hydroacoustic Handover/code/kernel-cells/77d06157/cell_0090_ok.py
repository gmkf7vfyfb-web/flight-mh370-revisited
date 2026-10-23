exec(open("gfx/charts_levels.py").read()); style()
for st,n in [("H01W","chart01-noise-vs-levels-H01W"),("H08S","chart02-noise-vs-levels-H08S")]+[(s,f"chart01-02-companion-noise-vs-levels-{s}") for s in ["H08N","3315","3376","3274","3275","3250"]]:
    r=chart_station(st,n)
    if r!=([],[]): print(n,r)
print(chart_overview("chart01-02-companion-noise-vs-levels-overview"))
# contact sheet
from PIL import Image
order=["chart01-noise-vs-levels-H01W","chart02-noise-vs-levels-H08S","chart03-loudness-maps","chart04-kadri-poster-boxes-companion","chart05-arrivals-vs-published-traces",
       "chart06-publication-coverage","chart07-hypothesis-table","chart08-descents-not-redrawn","chart09-illustrative-traces","chart10-air9-predicted-vs-measured"]
fig,axs=plt.subplots(4,3,figsize=(18,22)); axs=axs.ravel()
for k,(ax,n) in enumerate(zip(axs,order)):
    im=Image.open(OUT/f"{n}.png"); ax.imshow(im); ax.set_axis_off(); ax.set_title(f"{k+1}", fontsize=14, loc="left", weight="bold")
for ax in axs[len(order):]: ax.set_axis_off()
fig.text(0.01,0.995,"Updated example charts 1–10 (22 Oct 2026): run J, corrected IMOS loss table. PREDICTIVE, NOT CALIBRATED (C1, C2). Chart 8 not redrawn (no run J descent traces).",fontsize=12,va="top")
fig.subplots_adjust(left=0.01,right=0.99,top=0.975,bottom=0.01,wspace=0.03,hspace=0.08)
fig.savefig(OUT/"contact-sheet-charts-01-10.png",dpi=110); plt.close(fig)
print(Image.open(OUT/"contact-sheet-charts-01-10.png").size)