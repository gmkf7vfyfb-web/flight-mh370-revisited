import matplotlib as mpl, matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
apply_figure_style(sizes=(8,7,6))
# arc contour grids
def arc_grid(lat0,lat1,lon0,lon1,n=400):
    la=np.linspace(lat0,lat1,n); lo=np.linspace(lon0,lon1,n); LO,LA=np.meshgrid(lo,la); return LO,LA,bto(LA,LO)
BL=bearing_line(306.18,1000,1950); BLm=bearing_line(305.18,1000,1950); BLp=bearing_line(307.18,1000,1950)
fig,axs=plt.subplots(1,2,figsize=(7.2,3.9),gridspec_kw=dict(width_ratios=[1.05,1],wspace=0.28))
# panel a regional
ax=axs[0]; LO,LA,B=arc_grid(-33,-17,91,109)
ax.contourf(LO,LA,B,levels=[18400-63,18400+63],colors=["0.88"])
ax.contour(LO,LA,B,levels=[18400],colors=["0.25"],linewidths=0.9)
ax.plot(BL[:,1],BL[:,0],color="0.45",lw=0.7,ls="--")
cmapd={"2014-03-29":"#1b9e77","2014-04-01":"#1b9e77","2014-04-05":"#7570b3","2014-04-09":"#7570b3","2014-04-10":"#7570b3"}
for _,r in df.drop_duplicates(["date","latmin","lonmin"]).iterrows():
    ax.add_patch(Rectangle((r.lonmin,r.latmin),r.lonmax-r.lonmin,r.latmax-r.latmin,fc="none",ec=cmapd[r.date],lw=0.6))
ax.add_patch(Rectangle((100,-26.5),2.5,1.5,fc="none",ec="k",lw=1.0))
ax.add_patch(Rectangle((101,-26),3,6,fc="none",ec="#d95f02",lw=0.8,ls=":"))
ax.plot(HX[1],HX[0],marker="*",ms=8,color="k",zorder=5)
ax.plot(104.1,-21.07,marker="s",ms=4,mfc="w",mec="k",zorder=5)
ax.text(102.7,-26.9,"study area",fontsize=7); ax.text(104.2,-20.6,"towed-pinger\ncontacts (approx.)",fontsize=6)
ax.text(96.9,-29.0,"archived high-resolution\nstrips 29 Mar, 1 Apr",fontsize=6,color="#1b9e77",ha="center")
ax.text(95.3,-18.4,"strips 5-10 Apr",fontsize=6,color="#7570b3")
ax.text(104.3,-24.9,"Chinese ships'\narea from 4 Apr",fontsize=6,color="#d95f02")
ax.text(93.2,-31.6,"7th arc (sea level)",fontsize=6,color="0.25",rotation=48)
ax.set_xlim(91,109); ax.set_ylim(-33,-17); ax.set_xlabel("Longitude (°E)"); ax.set_ylabel("Latitude (°)")
ax.set_title("Archived imagery strips did not reach the study area",loc="left")
panel_letter(ax,"a")
# panel b zoom
ax=axs[1]; LO,LA,B=arc_grid(-27.3,-24.2,99.8,103.0,500)
ax.contourf(LO,LA,B,levels=[18400-63,18400+63],colors=["0.88"])
ax.contour(LO,LA,B,levels=[18400],colors=["0.25"],linewidths=0.9)
for arr,ls in [(BL,"--"),(BLm,":"),(BLp,":")]: ax.plot(arr[:,1],arr[:,0],color="0.45",lw=0.7,ls=ls)
# 90 km ring around first contact
az=np.linspace(0,360,361); ring=np.array([[G.Direct(HX[0],HX[1],a,90e3)[k] for k in ("lat2","lon2")] for a in az])
ax.plot(ring[:,1],ring[:,0],color="#e7298a",lw=0.8)
ax.add_patch(Rectangle((100,-26.5),2.5,1.5,fc="none",ec="k",lw=1.0))
ax.plot(XC[1],XC[0],marker="o",ms=5,mfc="w",mec="k",zorder=6)
ax.plot(HX[1],HX[0],marker="*",ms=9,color="k",zorder=6)
ax.text(XC[1]-0.08,XC[0]+0.1,"bearing meets arc",fontsize=6,ha="right")
ax.text(HX[1]+0.08,HX[0]-0.12,"first contact\n(second 2-3 km W)",fontsize=6)
ax.text(101.5,-26.95,"objects reported\n'about 90 km' away\n(bearing not given)",fontsize=6,color="#e7298a")
ax.text(100.05,-24.45,"306.18° bearing\nfrom Cape Leeuwin\nhydrophones ±1°",fontsize=6,color="0.35")
ax.set_xlim(99.8,103.0); ax.set_ylim(-27.3,-24.2); ax.set_xlabel("Longitude (°E)")
ax.set_title("Contacts lie 28 km outside the arc",loc="left")
panel_letter(ax,"b")
for a in axs: a.set_aspect(1/np.cos(np.radians(25.5)))
foot1=("Plain: The map shows reported positions and the areas of saved satellite pictures. No flight model is used. "
       "The arc band shows the 1-sigma timing error.")
foot2=("Technical: 7th arc = sea-level BTO 18,400 µs (00:19 option m0019a, R600), band ±63 µs; bearing 306.18° ±1° from H01W centroid; "
       "contacts ATSB 2017 p.38; ring 90 km (JACC 5 Apr 2014, direction unpublished); strips = NASA CSDA Maxar L1B records, 29 Mar-10 Apr 2014; "
       "towed-pinger positions read from ATSB June 2014 Fig.12 (approx.). No posterior, ocean model or search case applied.")
fig.text(0.01,0.035,foot1,fontsize=6,wrap=True); fig.text(0.01,0.0,foot2,fontsize=5.5,wrap=True)
fig.subplots_adjust(bottom=0.24,top=0.92,left=0.08,right=0.98)
fig.savefig("out/fig-locality-sources-map.png",dpi=300)
r=fig.canvas.get_renderer()
texts_=[(t,t.get_window_extent(r)) for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
ov=[(a.get_text()[:25],b.get_text()[:25]) for i,(a,ba) in enumerate(texts_) for b,bb in texts_[i+1:] if ba.overlaps(bb)]
print(ov)