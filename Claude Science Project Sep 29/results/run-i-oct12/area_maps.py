"""Run I area maps at 00:11 and 00:19: all four families (equal prior, posterior-weighted), waypoints only, free flight only.
Same convention as report/epoch_map.py: 0.1 deg grid, 0.3 deg Gaussian smoothing, greyscale 50/90/99 % HPD bands, arcs."""
import json, textwrap, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator, FuncFormatter
from scipy.ndimage import gaussian_filter
EX="/Users/pete/Downloads/mh370-exchange/core/run-i"; out="repo/Claude Science Project Sep 29/results/run-i-oct12"
FAMS={'waypoints':'next-i-waypoints','free flight':'next-i-free','reproduction (Davey)':'next-i-repro-radar','descent-climb':'next-i-descent-climb'}
SHARE={'waypoints':0.998217,'free flight':0.001134,'reproduction (Davey)':0.000437,'descent-climb':0.000212}
GRID=0.1; SM=0.3; LEV=(0.99,0.90,0.50)
def routes_at(d, epoch):
    meta=json.load(open(f"{EX}/{d}/run.json")); t=next(e['unix_s'] for e in meta['epochs'] if e['id']==epoch)
    x=(t-meta['prior_unix_s'])/meta['route_interval_s']; lo=int(np.floor(x)); fr=x-lo; L=[];W=[]
    for k in range(1,9):
        r=np.load(f"{EX}/{d}/bto-bfo/seed-{k}/routes.npy").astype(float); p=r[:,lo]+fr*(r[:,lo+1]-r[:,lo]); ok=np.isfinite(p).all(1)
        L.append(p[ok]); W.append(np.full(ok.sum(),1.0/ok.sum()/8))
    return np.concatenate(L), np.concatenate(W), meta
def final_at(d, cap=1_500_000):
    meta=json.load(open(f"{EX}/{d}/run.json")); C=meta['final_columns']; iw,ila,ilo=(C.index(c) for c in ('weight','latitude_deg','longitude_deg')); L=[];W=[]
    for k in range(1,9):
        a=np.load(f"{EX}/{d}/bto-bfo/seed-{k}/final.npy",mmap_mode='r'); st=max(1,a.shape[0]//cap); ch=np.asarray(a[::st])
        w=ch[:,iw].astype(float); w/=w.sum()*8; L.append(ch[:,[ila,ilo]].astype(float)); W.append(w)
    return np.concatenate(L), np.concatenate(W), meta
def grid(ext): return np.arange(ext[0],ext[1]+GRID,GRID), np.arange(ext[2],ext[3]+GRID,GRID)
def dens(P,W,ext):
    le,oe=grid(ext); h,_,_=np.histogram2d(P[:,0],P[:,1],bins=[le,oe],weights=W); h=gaussian_filter(h,SM/GRID,mode='constant'); return 0.5*(le[1:]+le[:-1]),0.5*(oe[1:]+oe[:-1]),h/h.sum()
def levels(d):
    f=np.sort(d.ravel())[::-1]; s=np.cumsum(f); return [float(f[np.searchsorted(s,x)]) for x in LEV]
def area_km2(d,lat_c,lev):
    cell=(GRID*111.32)**2*np.cos(np.deg2rad(lat_c))[:,None]*np.ones_like(d); return float((cell*(d>=lev)).sum())
EXT={'m0011':(-40.5,-32.5,86.0,97.0),'m0019a':(-41.0,-33.0,84.5,96.5)}
data={}
for ep in ('m0011','m0019a'):
    per={}
    for f,d in FAMS.items():
        per[f]=routes_at(d,'m0011') if ep=='m0011' else final_at(d)
    allP=np.concatenate([per[f][0] for f in FAMS]); allW=np.concatenate([SHARE[f]*per[f][1] for f in FAMS])
    data[ep]={'all four families (posterior-weighted)':(allP,allW),'waypoints only':per['waypoints'][:2],'free flight only':per['free flight'][:2],'meta':per['waypoints'][2]}
apply_figure_style()
fig,axs=plt.subplots(2,3,figsize=(7.2,6.6))
shades=["#dcdcdc","#a8a8a8","#6a6a6a"]; rows=[]
for i,ep in enumerate(('m0011','m0019a')):
    meta=data[ep]['meta']; ext=EXT[ep]
    ref=None
    for j,name in enumerate(['all four families (posterior-weighted)','waypoints only','free flight only']):
        ax=axs[i,j]; P,W=data[ep][name]; la,lo,dn=dens(P,W,ext); lv=levels(dn)
        ax.contourf(lo,la,dn,levels=lv+[dn.max()],colors=shades); ax.contour(lo,la,dn,levels=lv,colors='#2b2b2b',linewidths=[0.4,0.6,0.8])
        if j==0: ref=(la,lo,dn,lv)
        else: ax.contour(ref[1],ref[0],ref[2],levels=[ref[3][1]],colors='#e7298a',linewidths=0.7,linestyles='--')
        for aid,sty in ((ep,dict(color='#b16286',lw=1.0)),('m0019a',dict(color='#4a6fa5',lw=0.8,ls='--'))):
            arc=next((a for a in meta['reference_arcs'] if a['epoch']==aid),None); pts=np.asarray(arc['lat_lon']); ax.plot(pts[:,1],pts[:,0],**sty)
        med=float(np.average(P[:,0],weights=W)) ; o=np.argsort(P[:,0]); cw=np.cumsum(W[o])/W.sum(); medl=float(P[o,0][np.searchsorted(cw,0.5)])
        a50,a90,a99=(area_km2(dn,la,lv[k]) for k in (2,1,0))
        rows.append(dict(epoch=('00:11' if ep=='m0011' else '00:19'),set=name,median_lat=round(medl,2),area_50_km2=round(a50),area_90_km2=round(a90),area_99_km2=round(a99),n_points=len(P)))
        ax.text(0.03,0.03,f"median {medl:.2f}°\n90 % area {a90/1000:.0f}k km²",transform=ax.transAxes,fontsize=6,va='bottom')
        ax.set_xlim(ext[2],ext[3]); ax.set_ylim(ext[0],ext[1]); ax.set_aspect(1/np.cos(np.deg2rad(0.5*(ext[0]+ext[1]))))
        ax.xaxis.set_major_locator(MultipleLocator(4)); ax.yaxis.set_major_locator(MultipleLocator(2))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_: f"{abs(v):.0f}°S")); ax.xaxis.set_major_formatter(FuncFormatter(lambda v,_: f"{v:.0f}°E"))
        ax.grid(True,color='#e3e3e3',lw=0.5); ax.set_axisbelow(True)
        if i==0: ax.set_title(name.replace(' (posterior-weighted)','\n(weighted by posterior)'),loc='left',fontsize=7)
        if j>0: ax.set_yticklabels([])
        if j==0: ax.set_ylabel("Position at 00:11 UTC" if ep=='m0011' else "Position at 00:19 UTC")
bands=[Patch(facecolor=c,edgecolor='#2b2b2b',lw=0.5,label=f"{int(f*100)} % of probability") for c,f in zip(shades[::-1],(0.5,0.9,0.99))]
from matplotlib.lines import Line2D
hand=bands+[Line2D([],[],color='#e7298a',ls='--',lw=0.8,label='90 % region of all four families'),Line2D([],[],color='#b16286',lw=1,label='arc of that time'),Line2D([],[],color='#4a6fa5',ls='--',lw=0.8,label='7th arc, 00:19')]
fig.legend(handles=hand,loc='upper center',bbox_to_anchor=(0.5,0.315),ncol=3,frameon=False,fontsize=6)
fig.suptitle("Where the aircraft was at 00:11 and 00:19: waypoint paths give a smaller area than free flight",x=0.02,ha='left',fontsize=8,y=0.985)
fig.subplots_adjust(left=0.1,right=0.98,top=0.90,bottom=0.33,wspace=0.06,hspace=0.14)
ste=("Simple version (ASD-STE100): The grey areas show where the aircraft probably was at 00:11 UTC (top) and 00:19 UTC (bottom). Darker grey has more probability. "
     "The left column uses all four groups of early flights, each with its share of probability from the data. The middle column uses only the waypoint paths. "
     "The right column uses only the free paths. The dashed pink line is the 90 % area of the left column, for comparison.")
tech=("Technical version: Core run I, 8 seeds per family. 00:11: positions interpolated from the 2,000 posterior route draws per seed (smoothing distribution); "
      "00:19: final.npy states, thinned to 1.5M rows per seed, with their weights. Family weights at equal prior from pooled log-evidence (waypoints 0.9982, free 0.0011, "
      "reproduction 0.0004, descent-climb 0.0002); seeds equally weighted within a family. 0.1° grid, 0.3° Gaussian smoothing, highest-density regions at 50/90/99 % "
      "(report/epoch_map.py convention). Areas on the smoothed grid. 00:19 treatment: core, Davey both-BTO, no BFO. One-engine phase provisional.")
fig.text(0.02,0.24,'\n'.join(textwrap.wrap(ste,165)),fontsize=6,va='top'); fig.text(0.02,0.165,'\n'.join(textwrap.wrap(tech,165)),fontsize=6,va='top',color=META_GREY)
fig.canvas.draw(); r=fig.canvas.get_renderer(); texts=[t for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
print('overlaps',[(a.get_text()[:18],b.get_text()[:18]) for i_,a in enumerate(texts) for b in texts[i_+1:] if a.get_window_extent(r).overlaps(b.get_window_extent(r))])
fig.savefig(f"{out}/run-i-area-maps.png",dpi=300); fig.savefig(f"{out}/run-i-area-maps.pdf")
AREA=pd.DataFrame(rows); AREA.to_csv(f"{out}/run-i-area-summary.csv",index=False); print(AREA.to_string())
