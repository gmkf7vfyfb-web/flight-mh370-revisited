import json, textwrap, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from PIL import Image
R_NM=3440.065
EX="/Users/pete/Downloads/mh370-exchange/core/run-i"
OUT="repo/Claude Science Project Sep 29/results/run-i-oct12"
fx=pd.read_csv("repo/Claude Science Project Sep 29/results/waypoints-2014-epoch-oct11/waypoints-2014-epoch.csv")
C2={r['name']:(r['lat_current'] if not np.isnan(r['lat_current']) else r['lat_deg'], r['lon_current'] if not np.isnan(r['lon_current']) else r['lon_deg']) for _,r in fx.iterrows()}
C2.update({'MEKAR':(6.503889,96.491111),'NILAM':(6.756389,95.976667)})
pix={'SAMAK':(215,47),'IGOGU':(215,175),'ANOKO':(215,278),'NOPEK':(215,425),'NILAM':(642,383),'MEKAR':(782,453),
     'IGEBO':(397,527),'SANOB':(557,430),'POVUS':(284,590),'ANSAX':(514,592),'BEDAX':(43,767),'BULVA':(101,985)}
nm=list(pix); Xa=np.array([[C2[n][1],C2[n][0],1] for n in nm]); Ya=np.array([pix[n] for n in nm],float)
Aff=np.linalg.lstsq(Xa,Ya,rcond=None)[0]
def toP(lat,lon): return np.c_[np.ravel(lon),np.ravel(lat),np.ones(np.size(lat))]@Aff
img=np.asarray(Image.open(CHART).convert('RGB'))
TF=[np.load(f"{EX}/next-i-free/bto-bfo/seed-{k}/trace.npy") for k in range(1,9)]
TW=[np.load(f"{EX}/next-i-waypoints/bto-bfo/seed-{k}/trace.npy") for k in range(1,9)]
def group_of(tr):
    m=np.nanmax(tr[:,:,0],1); return np.where(m>=7.55,0,np.where(m>=7.2,1,2))
GN=['turn north of 7.55°N (towards SAMAK)','turn 7.2–7.55°N (near IGOGU)','turn south of 7.2°N (ANOKO or earlier)']
gsh={f:(np.array([[np.mean(group_of(t)==g) for g in range(3)] for t in TT]).mean(0),np.array([[np.mean(group_of(t)==g) for g in range(3)] for t in TT]).std(0,ddof=1)) for f,TT in (('free',TF),('waypoints',TW))}
apply_figure_style()
y1=720; x1=img.shape[1]
fig,ax=plt.subplots(figsize=(7.2,7.4)); ax.imshow(img[:y1],alpha=0.5)
colW=['#08519c','#4292c6','#9ecae1']; colF='#d95f02'; rng=np.random.default_rng(7)
for tr in TF:
    for t_ in tr[rng.choice(len(tr),150,replace=False)]:
        ok=~np.isnan(t_[:,0]); P_=toP(t_[ok,0],t_[ok,1]); ax.plot(P_[:,0],P_[:,1],color=colF,lw=0.4,alpha=0.07)
for tr in TW:
    sel=rng.choice(len(tr),150,replace=False); g=group_of(tr[sel])
    for t_,gg in sorted(zip(tr[sel],g),key=lambda z:-z[1]):
        ok=~np.isnan(t_[:,0]); P_=toP(t_[ok,0],t_[ok,1]); ax.plot(P_[:,0],P_[:,1],color=colW[gg],lw=0.5,alpha=0.18 if gg else 0.12)
for n in pix:
    p_=toP(*C2[n])[0]
    if 0<=p_[0]<x1 and 0<=p_[1]<y1: ax.plot(*p_,'k^',ms=4); ax.text(p_[0]+7,p_[1]-7,n,fontsize=6,weight='bold')
ax.set_xlim(0,x1); ax.set_ylim(y1,0); ax.set_xticks([]); ax.set_yticks([])
fm,fs=gsh['free']; wm,ws=gsh['waypoints']
hand=[Line2D([],[],color=colW[i],lw=2,label=f"Waypoint paths, {GN[i]}: {100*wm[i]:.0f} % ± {100*ws[i]:.0f}") for i in range(3)]
hand.append(Line2D([],[],color=colF,lw=2,label=f"Free-flight paths: north of 7.55°N {100*fm[0]:.0f} %, 7.2–7.55°N {100*fm[1]:.0f} %, south of 7.2°N {100*fm[2]:.0f} %"))
leg=ax.legend(handles=hand,loc='lower right',frameon=True,framealpha=0.92,fontsize=6,title="Posterior probability: waypoints 99.8 % (split-half 0.92), free flight 0.11 % (split-half 0.83)",title_fontsize=6)
leg._legend_box.align='left'
ax.set_title("Paths that follow waypoints, which the data favour, turn south between IGOGU and SAMAK at 18:37–18:39 UTC",loc='left',fontsize=7)
fig.subplots_adjust(left=0.03,right=0.97,top=0.955,bottom=0.215)
fig.text(0.03,0.20,'\n'.join(textwrap.wrap(STE,150)),fontsize=6,va='top')
fig.text(0.03,0.125,'\n'.join(textwrap.wrap(TECH,150)),fontsize=6,va='top',color=META_GREY)
fig.canvas.draw()
r=fig.canvas.get_renderer()
texts=[t for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
ov=[(a.get_text()[:25],b.get_text()[:25]) for i,a in enumerate(texts) for b in texts[i+1:] if a.get_window_extent(r).overlaps(b.get_window_extent(r))]
leg_bb=leg.get_window_extent(r); tech_bb=[t for t in texts if t.get_text().startswith('Technical')][0].get_window_extent(r); ste_bb=[t for t in texts if t.get_text().startswith('Simple')][0].get_window_extent(r)
print('overlaps after draw:', ov)
print('legend bottom y', round(leg_bb.y0), '| simple-text top y', round(ste_bb.y1), '| technical top y', round(tech_bb.y1))
fig.savefig(f"{OUT}/run-i-turn-zoom.png",dpi=300); fig.savefig(f"{OUT}/run-i-turn-zoom.pdf")
