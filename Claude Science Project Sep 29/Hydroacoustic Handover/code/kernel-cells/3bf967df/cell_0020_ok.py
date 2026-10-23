import numpy as np, matplotlib as mpl, matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from geographiclib.geodesic import Geodesic
apply_figure_style(sizes=(9,8,7))
G=Geodesic.WGS84
d=np.load('kadri_box.npz'); S=d['S']; cols=list(d['cols'])
T0=1394232081; t=S[:,cols.index('t_impact_s')]; la=S[:,cols.index('latitude_deg')]; lo=S[:,cols.index('longitude_deg')]
w=d['w_handoff_norm']*d['w_row_norm']/24
tu=(T0+t.astype(np.float64)) - 1394236800  # seconds after 00:00:00 UTC 8 Mar 2014 (1394236800)
# arcs
C=299792.458; GES=np.array([-2368.8,4881.1,-3342.0]); OFF=499962.0-4283.0
a_=6378.137; f=1/298.257223563; e2=f*(2-f)
def ecef(lat,lon,h=0):
    lat=np.radians(lat); lon=np.radians(lon); N=a_/np.sqrt(1-e2*np.sin(lat)**2)
    return np.stack([(N+h)*np.cos(lat)*np.cos(lon),(N+h)*np.cos(lat)*np.sin(lon),(N*(1-e2)+h)*np.sin(lat)],-1)
SAT={'7':np.array([18178.3537,38050.8487,393.0782]),'6':np.array([18177.5933,38051.6114,435.1660])}
def bto(lat,lon,s): return 2*(np.linalg.norm(s-ecef(lat,lon),axis=-1)+np.linalg.norm(s-GES))/C*1e6-OFF
def ring(target,s,lats):
    out=[]
    for L in lats:
        lo_,hi_=90.,110.
        f_=lambda x: bto(L,x,s)-target
        if f_(lo_)*f_(hi_)>0: out.append(np.nan); continue
        for _ in range(50):
            m=(lo_+hi_)/2
            if f_(lo_)*f_(m)<=0: hi_=m
            else: lo_=m
        out.append(m)
    return np.array(out)
lats=np.linspace(-29.5,-21.5,161)
arc7=ring(18400,SAT['7'],lats); arc7p=ring(18463,SAT['7'],lats); arc7m=ring(18337,SAT['7'],lats); arc6=ring(18040,SAT['6'],lats)
H01=(-34.8903,114.1426)
def bline(az,s0=1350,s1=1900):
    L=G.Line(H01[0],H01[1],az); P=[L.Position(s*1e3) for s in np.linspace(s0,s1,60)]
    return np.array([p['lon2'] for p in P]),np.array([p['lat2'] for p in P])
def pos(s,az=306.18):
    p=G.Line(H01[0],H01[1],az).Position(s*1e3); return p['lon2'],p['lat2']
R7=1591.3; X=pos(R7)
# Kadri eq.4 impact segments (c=1.48 km/s, along-bearing speed 0-250 m/s)
seg={}
for name,trec in [('T',52*60+3),('C',54*60+30)]:
    dt=(trec-(19*60+29))-R7/1.48; pts=[]
    for v in np.linspace(0,250,26):
        dT=dt/(1+v/1000/1.48); pts.append(pos(R7+v/1000*dT))
    seg[name]=np.array(pts)
hx=(101.461,-25.975)

fig,axs=plt.subplots(1,2,figsize=(11.5,6.4),sharey=True,gridspec_kw={'wspace':0.05})
ext=[97.5,104.5,-28.5,-22.5]
# panel a: scatter coloured by impact time
rng=np.random.default_rng(1); idx=rng.choice(len(S),min(len(S),150000),replace=False)
sc=axs[0].scatter(lo[idx],la[idx],c=tu[idx]/60,s=0.6,cmap='viridis',vmin=15,vmax=45,rasterized=True,lw=0)
cb=fig.colorbar(sc,ax=axs[0],orientation='horizontal',pad=0.09,fraction=0.045); cb.set_label('Impact time (minutes after 00:00 UTC, 8 Mar 2014)')
# panel b: weighted log density
hb=axs[1].hexbin(lo,la,C=w,reduce_C_function=np.sum,gridsize=(70,60),extent=ext,cmap='Greys',norm=LogNorm(vmin=max(w.sum()*1e-6,1e-12)),mincnt=1,linewidths=0)
cb2=fig.colorbar(hb,ax=axs[1],orientation='horizontal',pad=0.09,fraction=0.045); cb2.set_label('Posterior probability per cell (log scale)')
for ax in axs:
    for az,ls,al in [(305.18,':',0.9),(305.68,'--',0.9),(306.68,'--',0.9),(307.18,':',0.9)]:
        x,y=bline(az); ax.plot(x,y,ls,color='tab:red',lw=0.8,alpha=al)
    x,y=bline(306.18); ax.plot(x,y,'-',color='tab:red',lw=1.4)
    ax.fill_betweenx(lats,arc7m,arc7p,color='tab:blue',alpha=0.18,lw=0)
    ax.plot(arc7,lats,'-',color='tab:blue',lw=1.5); ax.plot(arc6,lats,'-',color='tab:cyan',lw=1.2)
    ax.plot(seg['T'][:,0],seg['T'][:,1],'-',color='darkorange',lw=3,solid_capstyle='butt')
    ax.plot(seg['C'][:,0],seg['C'][:,1],'-',color='magenta',lw=1.6)
    ax.plot(*X,'o',ms=8,mfc='white',mec='tab:red',mew=2)
    ax.plot(*hx,'*',ms=14,color='gold',mec='k',mew=0.8)
    ax.set_xlim(ext[0],ext[1]); ax.set_ylim(ext[2],ext[3]); ax.set_aspect(1/np.cos(np.radians(25.5)))
    ax.set_xlabel('Longitude (°E)')
axs[0].set_ylabel('Latitude (°; south is negative)')
axs[0].set_title('Simulated impacts near the bearing-arc crossing, by impact time',loc='left')
axs[1].set_title('Same impacts weighted by the flight-path posterior',loc='left')
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
h=[Line2D([],[],color='tab:blue',lw=1.5,label='7th arc, 00:19:29, sea level'),Patch(color='tab:blue',alpha=0.18,label='7th arc ±1σ timing (±63 µs)'),
   Line2D([],[],color='tab:cyan',lw=1.2,label='6th arc, 00:10:59, sea level'),
   Line2D([],[],color='tab:red',lw=1.4,label='Kadri bearing 306.18° from Cape Leeuwin'),Line2D([],[],color='tab:red',ls='--',lw=0.8,label='bearing ±0.5°'),Line2D([],[],color='tab:red',ls=':',lw=0.8,label='bearing ±1.0°'),
   Line2D([],[],marker='o',ls='',ms=8,mfc='white',mec='tab:red',mew=2,label='bearing meets 7th arc (25.73 S, 101.37 E)'),
   Line2D([],[],color='darkorange',lw=3,label='Kadri impact, text time 00:52:03 (0–250 m/s)'),Line2D([],[],color='magenta',lw=1.6,label='Kadri impact, caption time 00:54:30 (0–250 m/s)'),
   Line2D([],[],marker='*',ls='',ms=13,color='gold',mec='k',label='Haixun 01 contact, 4 Apr 2014 (sensitivity only)')]
fig.legend(handles=h,loc='upper center',bbox_to_anchor=(0.5,0.035),ncol=3,frameon=False,fontsize=7.5)
foot=("Note (plain): Dots are simulated impact points from the flight model. Left: the colour shows the impact time. Right: darker cells have more probability. "
 "The red line is the direction of Kadri's sound from Cape Leeuwin. The orange and pink lines show where his equation puts the impact for his two printed times. "
 "The star is the Haixun 01 sound contact. It is shown only for comparison.\n"
 "Note (technical): Run J end of flight, waypoints family (P = 0.998), 24 seeds pooled at equal weight; 3.08 M of 153.6 M rows in 22–29 S, 97–105 E. Left: unweighted, random 150 k subsample. "
 "Right: hand-off weight × within-parent weight; 00:19 BTO/BFO likelihood, log-on cause factor and D5 NOT applied (00:19 data held out); share in box 1.6 %. "
 "Arcs: corrected BTO 18,400 µs (00:19:29) and 18,040 µs (00:10:59), Inmarsat ephemeris, Perth GES, WGS84, h = 0. Bearing: WGS84 geodesic from the H01W triad centroid (34.8903 S, 114.1426 E). "
 "Kadri eq. 4 with c = 1.48 km/s, along-bearing speed 0–250 m/s. Haixun: ATSB 2017 p. 38. Physics provisional; no search, drift or acoustic evidence applied.")
fig.text(0.06,-0.16,foot,ha='left',va='top',fontsize=7,wrap=True)
fig.subplots_adjust(bottom=0.2)
fig.savefig('kadri-crossing-impact-map.png',dpi=200,bbox_inches='tight')
print(len(S), w.sum(), tu.min()/60, np.percentile(tu/60,[5,50,95]))
m=np.hypot((lo-X[0])*np.cos(np.radians(25.7)),la-X[1])*111.2<100
print('within 100 km of crossing: rows',m.sum(),'weighted share',w[m].sum(),'impact-time pct (min after 00:00)',np.percentile(tu[m]/60,[5,50,95]) if m.any() else None)
print('weighted median impact time in 100 km', np.interp(0.5,np.cumsum(w[m][np.argsort(tu[m])])/w[m].sum(),np.sort(tu[m]))/60)