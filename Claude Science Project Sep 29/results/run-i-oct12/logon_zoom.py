import sys, json, textwrap, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from PIL import Image
ENG="repo/Claude Science Project Sep 29/engine"; sys.path.insert(0, ENG+"/report"); import satcom_model as sm
EX="/Users/pete/Downloads/mh370-exchange/core/run-i"; out="repo/Claude Science Project Sep 29/results/run-i-oct12"
T0=1394216520.0  # 18:22:00 UTC, first trace point
EP={'18:25:34 BTO (log-on)':(1394216734.0,12600,43),'18:28:05 BTO+BFO':(1394216885.0,12500,29),'18:28:14 BTO+BFO':(1394216894.0,12480,29)}
fx=pd.read_csv("repo/Claude Science Project Sep 29/results/waypoints-2014-epoch-oct11/waypoints-2014-epoch.csv")
C2={r['name']:(r['lat_current'] if not np.isnan(r['lat_current']) else r['lat_deg'], r['lon_current'] if not np.isnan(r['lon_current']) else r['lon_deg']) for _,r in fx.iterrows()}
C2.update({'MEKAR':(6.503889,96.491111),'NILAM':(6.756389,95.976667)})
pix={'SAMAK':(215,47),'IGOGU':(215,175),'ANOKO':(215,278),'NOPEK':(215,425),'NILAM':(642,383),'MEKAR':(782,453),'IGEBO':(397,527),'SANOB':(557,430),'POVUS':(284,590),'ANSAX':(514,592),'BEDAX':(43,767),'BULVA':(101,985)}
Xa=np.array([[C2[n][1],C2[n][0],1] for n in pix]); Ya=np.array([pix[n] for n in pix],float); Aff=np.linalg.lstsq(Xa,Ya,rcond=None)[0]
toP=lambda lat,lon: np.c_[np.ravel(lon),np.ravel(lat),np.ones(np.size(lat))]@Aff
img=np.asarray(Image.open(CHART).convert('RGB'))
fam={'free flight':('next-i-free','#d95f02'),'waypoints':('next-i-waypoints','#08519c')}
def at(tr,t):  # position at time t, linear in the 40 s trace
    k=(t-T0)/40.0; i=int(np.floor(k)); f=k-i
    return (1-f)*tr[:,i,:]+f*tr[:,i+1,:]
apply_figure_style()
fig=plt.figure(figsize=(7.2,8.4)); ax=fig.add_axes([0.04,0.47,0.92,0.48]); bx=fig.add_axes([0.09,0.27,0.86,0.14])
lat0,lat1,lon0,lon1=6.30,7.05,95.65,96.62
c=toP(np.array([lat1,lat0]),np.array([lon0,lon1])); x0,y0=c[0]; x1,y1=c[1]
ax.imshow(img,alpha=0.5); ax.set_xlim(x0,x1); ax.set_ylim(y1,y0); ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values(): s.set_visible(True)
rng=np.random.default_rng(3); resid={}
for name,(d,colr) in fam.items():
    res=[]
    for k in range(1,9):
        tr=np.load(f"{EX}/{d}/bto-bfo/seed-{k}/trace.npy").astype(float)
        sel=rng.choice(len(tr),60,replace=False)
        for t_ in tr[sel,:14]:   # 18:22:00-18:30:40
            ok=~np.isnan(t_[:,0]); P_=toP(t_[ok,0],t_[ok,1]); ax.plot(P_[:,0],P_[:,1],color=colr,lw=0.5,alpha=0.12 if name=='free flight' else 0.18)
        p=at(tr,EP['18:25:34 BTO (log-on)'][0]); sat,_=sm.satstate(EP['18:25:34 BTO (log-on)'][0])
        res.append(np.array([sm.bto(sat,a,b,h) for a,b,h in p[:,:3]])-12600.0)
        q=toP(p[sel,0],p[sel,1]); ax.scatter(q[:,0],q[:,1],s=9 if name=='waypoints' else 4,color=colr,zorder=5 if name=='waypoints' else 4,edgecolors='white' if name=='waypoints' else 'none',linewidths=0.4)
    resid[name]=np.concatenate(res)
# arcs from the run (engine geometry)
rjw=json.load(open(f"{EX}/next-i-waypoints/run.json")); arcs={a['epoch']:np.array(a['lat_lon']) for a in rjw['reference_arcs']}
for ep,ls,lab,yl in (('m1825','-','18:25:34 arc (BTO 12,600 µs)',6.42),('m1828a','--','18:28:05 arc (BTO 12,500 µs)',6.97)):
    ll=arcs[ep]; m=(ll[:,0]>5)&(ll[:,0]<8); P_=toP(ll[m,0],ll[m,1]); ax.plot(P_[:,0],P_[:,1],color='k',ls=ls,lw=0.9)
    j=np.argmin(np.abs(ll[m,0]-yl)); ax.text(P_[j,0]+5,P_[j,1],lab,fontsize=6,backgroundcolor=(1,1,1,0.7))
rp=toP(6.5779,96.3410)[0]; ax.plot(*rp,'s',color='#b2182b',ms=4); ax.text(rp[0]-4,rp[1]-8,"18:22:12 radar (sd 5 NM)",fontsize=6,color='#b2182b',ha='right')
for n in ('MEKAR','NILAM','SANOB'):
    p_=toP(*C2[n])[0]; ax.plot(*p_,'k^',ms=4); ax.text(p_[0]+6,p_[1]-6,n,fontsize=6,weight='bold')
ax.legend(handles=[Line2D([],[],color='#08519c',lw=2,label='Waypoint paths, 18:22–18:31 (dots: position at 18:25:34)'),
                   Line2D([],[],color='#d95f02',lw=2,label='Free-flight paths, 18:22–18:31 (dots: position at 18:25:34)')],loc='lower left',frameon=True,framealpha=0.9,fontsize=6)
ax.set_title("At the 18:25 log-on most waypoint paths are a little past the timing arc; free-flight paths spread across it",loc='left')
b=np.linspace(-150,150,61)
for name,(d,colr) in fam.items():
    r=resid[name]; bx.hist(r,bins=b,density=True,histtype='step',color=colr,lw=1.4,label=f"{name}: median {np.median(r):+.0f} µs, middle 90 % {np.percentile(r,5):+.0f} to {np.percentile(r,95):+.0f} µs")
x=np.linspace(-150,150,301); bx.plot(x,np.exp(-0.5*(x/43)**2)/(43*np.sqrt(2*np.pi)),color='k',lw=0.8,ls=':',label='measurement error model (sd 43 µs)')
bx.axvline(0,color='k',lw=0.5); bx.set_xlabel("Predicted minus measured BTO at 18:25:34 (µs; positive = further from the satellite)"); bx.set_ylabel("Density")
bx.legend(frameon=False,fontsize=6,loc='upper left'); bx.set_title("Fit to the 18:25:34 timing measurement, all 16,000 posterior draws per family",loc='left')
mpl_t=lambda s,w=158: '\n'.join(textwrap.wrap(s,w))
ste=("Simple version (ASD-STE100): The top map shows possible flight paths from 18:22 to 18:31 UTC near MEKAR and NILAM. The dots show where each path is "
     "at 18:25:34, when the satellite system logged on again. The black lines show where the timing measurements put the aircraft. The bottom chart shows the "
     "difference between each path and the 18:25:34 measurement. The waypoint paths agree a little less well at 18:25:34 than the free paths, because they are all "
     "on one line and most of them are a little too far west at that time. This costs the waypoint paths 0.3 of evidence. They gain much more later.")
tech=("Technical version: Core run I, 8 seeds × 2,000 posterior route draws per family; 40 s trace from 18:22:00, linearly interpolated to 18:25:34; 60 draws per "
      "seed shown on the map. BTO predicted with report/satcom_model.py (Inmarsat ephemeris, terminal altitude from the trace) against the logged 12,600 µs; "
      "sd 43 µs at 18:25:34 (log-on, BFO excluded), 29 µs at 18:28. Arcs drawn from the engine's reference_arcs (run.json). Evidence increments at 18:25:34 "
      "(waypoints minus free) −0.27 nats; 18:22:12 radar −0.16; 18:28 −0.10 and +0.14. Chart background supplied by Pete, affine fit to 12 fixes.")
fig.text(0.04,0.20,mpl_t(ste),fontsize=6,va='top'); fig.text(0.04,0.105,mpl_t(tech),fontsize=6,va='top',color=META_GREY)
fig.canvas.draw(); r=fig.canvas.get_renderer(); texts=[t for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
print('overlaps',[(a.get_text()[:20],b.get_text()[:20]) for i,a in enumerate(texts) for b in texts[i+1:] if a.get_window_extent(r).overlaps(b.get_window_extent(r))])
print({k:(round(float(np.median(v)),1),round(float(np.std(v)),1)) for k,v in resid.items()})
fig.savefig(f"{out}/run-i-logon-1825-zoom.png",dpi=300); fig.savefig(f"{out}/run-i-logon-1825-zoom.pdf")
