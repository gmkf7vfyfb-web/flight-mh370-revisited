
import matplotlib as mpl, matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
apply_figure_style(sizes=(8,7,6))
for lab,tg in [('c',18400),('p',18463),('m',18337)]:
    pts_=[KG['cross'](tg,0.0,'m0019a',az) for az in np.arange(299,313.01,0.25)]
    arcs[lab]=np.array([[p[1],p[2]] for p in pts_])
def hpd_levels(Hh,qs=(0.5,0.9,0.99)):
    v=np.sort(Hh.ravel())[::-1]; c=np.cumsum(v); c/=c[-1]
    return [v[np.searchsorted(c,q)] for q in qs]
fig,axs=plt.subplots(1,2,figsize=(7.2,4.3),gridspec_kw=dict(width_ratios=[1.15,1]))
ax=axs[0]
im=ax.pcolormesh(glon_m,glat_m,DEP,cmap='Blues',vmin=3000,vmax=6000,shading='auto',rasterized=True)
ax.contour(glon_m,glat_m,AUSM.astype(float),levels=[0.5],colors='0.35',linewidths=0.6,linestyles=':')
for daz,ls,lw in [(0,'-',0.9),(-0.5,'--',0.6),(0.5,'--',0.6),(-1,':',0.6),(1,':',0.6)]:
    s_=np.arange(R7-80,R7+260,2.0); la_,lo_,_=None,None,None
    lo_,la_,_=gw.fwd(np.full(len(s_),H01W[1]),np.full(len(s_),H01W[0]),np.full(len(s_),AZ+daz),s_*1e3)
    ax.plot(lo_,la_,color='k',ls=ls,lw=lw)
ax.plot(arcs['c'][:,1],arcs['c'][:,0],color='#b2182b',lw=1.0)
for k in 'pm': ax.plot(arcs[k][:,1],arcs[k][:,0],color='#b2182b',lw=0.6,ls='--')
for br,col in (('T','#e08214'),('C','#542788')):
    o=RES[f'kadri_{br}']['recorder-detached']; sel=np.random.default_rng(1).choice(N,1500,replace=False)
    ax.scatter(o['lon0'][sel],o['lat0'][sel],s=1.2,color=col,alpha=0.35,lw=0,rasterized=True)
ax.plot(CX[1],CX[0],marker='o',ms=4,mfc='white',mec='k',mew=0.8)
ax.plot(HX[1],HX[0],marker='*',ms=8,color='k')
ax.set_xlim(98.8,103.2); ax.set_ylim(-27.6,-23.4); ax.set_aspect(1/np.cos(np.radians(25.5)))
ax.set_xlabel('Longitude (°E)'); ax.set_ylabel('Latitude (°N)')
ax.set_title('Sea-floor depth along the 306.18° bearing',loc='left')
# direct labels
ax.text(101.55,-25.98,'Haixun 01 contact',fontsize=6,va='center')
ax.text(101.42,-25.62,'bearing × 7th arc',fontsize=6)
ax.text(99.0,-24.55,'impact, 00:52:03 reception',fontsize=6,color='#e08214')
ax.text(99.0,-24.30,'impact, 00:54:30 reception',fontsize=6,color='#542788')
ax.text(102.05,-24.75,'7th arc (sea level, ±63 µs)',fontsize=6,color='#b2182b',rotation=-58)
ax.text(100.35,-26.95,'bearing, ±0.5° (dashed), ±1° (dotted)',fontsize=6)
cb=fig.colorbar(im,ax=ax,shrink=0.7,pad=0.02); cb.set_label('Depth (m)'); cb.ax.invert_yaxis()
panel_letter(ax,'a')
# zoom panel
ax=axs[1]
im2=ax.pcolormesh(zlo,zla,ZD,cmap='Blues',vmin=4450,vmax=4700,shading='auto',rasterized=True)
kmx=1/(111.32*np.cos(np.radians(HX[0]))); kmy=1/110.57
for cls,style in (('recorder-detached','fill'),('fuselage-section','line')):
    I=INV[cls]; bx=np.arange(-20,20.01,0.1); Hh,_,_=np.histogram2d(I['ny'],I['ex'],bins=[bx,bx]); Hh=gaussian_filter(Hh,1.0)
    lv=hpd_levels(Hh); xc=HX[1]+0.5*(bx[1:]+bx[:-1])*kmx; yc=HX[0]+0.5*(bx[1:]+bx[:-1])*kmy
    if style=='fill':
        ax.contourf(xc,yc,Hh,levels=[lv[2],lv[1],lv[0],Hh.max()*1.01],colors=['0.85','0.6','0.3'],alpha=0.85)
    else:
        ax.contour(xc,yc,Hh,levels=[lv[2],lv[1],lv[0]],colors='k',linewidths=[0.5,0.8,1.1],linestyles=['--','-','-'])
th_=np.linspace(0,2*np.pi,200); ax.plot(HX[1]+2*np.cos(th_)*kmx,HX[0]+2*np.sin(th_)*kmy,color='#b2182b',lw=0.8)
ax.plot(HX[1],HX[0],marker='*',ms=8,color='k')
for k in (2,3):
    p_=dest(HX,270,k); ax.plot(p_[1],p_[0],marker='^',ms=4,mfc='white',mec='k',mew=0.7)
ax.set_xlim(zlo[0],zlo[-1]); ax.set_ylim(zla[0],zla[-1]); ax.set_aspect(1/np.cos(np.radians(HX[0])))
ax.set_xlabel('Longitude (°E)')
ax.set_title('Where the aircraft must hit the water',loc='left')
ax.text(HX[1]+0.015,HX[0]+0.03,'2 km from contact',fontsize=6,color='#b2182b')
ax.text(zlo[0]+0.005,zla[-1]-0.02,'grey fill: detached recorder\nblack lines: recorder kept in\nfloating aft fuselage\n(50 / 90 / 99 % HPD)',fontsize=6,va='top')
ax.text(HX[1]-0.06,HX[0]-0.02,'second contact,\n2–3 km west',fontsize=6,ha='center',va='top')
cb2=fig.colorbar(im2,ax=ax,shrink=0.7,pad=0.02); cb2.set_label('Depth (m)'); cb2.ax.invert_yaxis()
panel_letter(ax,'b')
fn1=("(i) The map shows the sea-floor depth. Panel b shows where the aircraft must hit the water if a recorder on the sea floor is within 2 km of the Haixun 01 contact. "
     "A recorder moves less than 1 km while it sinks. A recorder that stays in a floating fuselage part can move up to about 12 km. The Kadri impact points are more than 20 km from that area.")
fn2=("(ii) Depth: AusSeabed MH370 150 m where surveyed (dotted outline), GEBCO_2026 elsewhere. Settling: Python port of hypotheses/settling physics.rs (9330d4c), GLORYS12V1 8 Mar 2014 column, ERA5 wind, "
     "banded ocean error, PROVISIONAL element table + declared recorder class; impact conditions from run J rows in L (four route strata equal; 'weight' column, no 00:19 option term). "
     "Kadri impacts: eq. 4, sea-level arc 18,400 µs (m0019a), c = 1.48 km/s, v ~ U(0, 250) m/s, bearing sd 0.5°. No searched-area or drift evidence. Not a posterior.")
fig.text(0.01,0.035,fn1,fontsize=5.5,wrap=True,va='bottom'); fig.text(0.01,0.0,fn2,fontsize=5.5,wrap=True,va='bottom',color='0.25')
fig.subplots_adjust(left=0.08,right=0.97,top=0.93,bottom=0.25,wspace=0.28)
fig.savefig('out/fig_settling_haixun_map.png',dpi=300)
r_=fig.canvas.get_renderer()
texts=[(t,t.get_window_extent(r_)) for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
ov=[(a.get_text()[:25],b.get_text()[:25]) for i,(a,ba) in enumerate(texts) for b,bb in texts[i+1:] if ba.overlaps(bb)]
print(ov)
