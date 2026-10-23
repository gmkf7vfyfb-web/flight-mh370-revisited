import matplotlib as mpl, matplotlib.pyplot as plt, textwrap
apply_figure_style(sizes=(8,7,6))
def hpd_levels(H, levels=(0.5,0.9,0.99)):
    f=np.sort(H.ravel())[::-1]; c=np.cumsum(f)/f.sum()
    return [f[min(np.searchsorted(c,l),len(f)-1)] for l in levels]
def grey_hpd(ax, X, Y, H, alpha=1.0):
    t50,t90,t99=hpd_levels(H)
    ax.contourf(X,Y,H,levels=[t99,t90,t50,H.max()*1.0001],colors=['#d9d9d9','#969696','#404040'],alpha=alpha,zorder=1)
def ring(ax, c, r, **kw):
    az_=np.linspace(0,360,181); g=[Gd.Direct(c[0],c[1],a,r*1e3) for a in az_]
    ax.plot([q['lon2'] for q in g],[q['lat2'] for q in g],**kw)
def context(ax, xl, yl):
    ax.plot(arc[:,1],arc[:,0],color='#1f4e9a',lw=1.0,zorder=3)
    ax.plot(bl[:,1],bl[:,0],color='#b2182b',lw=0.8,ls='--',zorder=3)
    ring(ax,HX,70,color='k',lw=0.6,zorder=4); ring(ax,HX,110,color='k',lw=0.6,zorder=4)
    ax.plot(pts[0][2],pts[0][1],marker='*',ms=9,color='#b2182b',mec='k',mew=0.4,zorder=6,ls='none')
    ax.plot([p[2] for p in pts[1:5]],[p[1] for p in pts[1:5]],marker='o',ms=3.5,color='#b2182b',mec='k',mew=0.3,ls='none',zorder=6)
    ax.plot(HX[1],HX[0],marker='^',ms=5,color='white',mec='k',mew=0.6,ls='none',zorder=6)
    ax.set_xlim(*xl); ax.set_ylim(*yl); ax.set_aspect(1/np.cos(np.radians(np.mean(yl))))
    ax.set_xlabel('longitude (deg E)')
# ---- Figure 1: forward
xb=np.arange(86,107.01,0.1); yb=np.arange(-33,-19.99,0.1); XC=(xb[:-1]+xb[1:])/2; YC=(yb[:-1]+yb[1:])/2
fig,axs=plt.subplots(1,2,figsize=(7.2,3.9),sharey=True,gridspec_kw=dict(wspace=0.06))
for ax,(m,lab) in zip(axs,[('globcurrent','GlobCurrent currents + ERA5 wind'),('glorys12','GLORYS12 currents + ERA5 wind')]):
    a=SL[m]
    s=a[a['rel']==0]; p=pos_at_0315(s['pos'],6,7)
    H,_,_=np.histogram2d(p[:,1][np.isfinite(p[:,1])],p[:,0][np.isfinite(p[:,0])],[yb,xb]); grey_hpd(ax,XC,YC,H)
    st=np.concatenate([a[a['rel']==ri]['pos'] for ri in (1,2,3,4)]); q=pos_at_0315(st,6,7); ok=np.isfinite(q[:,0])
    H2,_,_=np.histogram2d(q[ok,1],q[ok,0],[yb,xb]); ax.contour(XC,YC,H2,levels=[hpd_levels(H2)[1]],colors=['#b2182b'],linewidths=0.9,linestyles='--',zorder=2)
    sh=a[a['rel']==5]; h=pos_at_0315(sh['pos'],6,7); ok=np.isfinite(h[:,0])
    H3,_,_=np.histogram2d(h[ok,1],h[ok,0],[yb,xb]); ax.contour(XC,YC,H3,levels=[hpd_levels(H3)[1]],colors=['#555555'],linewidths=0.7,linestyles=':',zorder=2)
    context(ax,(86,106),(-33,-20)); ax.set_title(lab,loc='left')
axs[0].set_ylabel('latitude (deg)')
fr=fwdf[(fwdf.branch=='T')]
h=[mpl.patches.Patch(color='#404040',label='50 %'),mpl.patches.Patch(color='#969696',label='90 %'),mpl.patches.Patch(color='#d9d9d9',label='99 % (from arc crossing)'),
   mpl.lines.Line2D([],[],color='#b2182b',ls='--',lw=0.9,label='90 %, from 50-200 km inside the arc'),
   mpl.lines.Line2D([],[],color='#555555',ls=':',lw=0.7,label='90 %, from the Haixun 01 contact (sensitivity)'),
   mpl.lines.Line2D([],[],color='k',lw=0.6,label='70 and 110 km from the Haixun 01 contact'),
   mpl.lines.Line2D([],[],color='#1f4e9a',lw=1,label='7th arc at sea level'),mpl.lines.Line2D([],[],color='#b2182b',lw=0.8,ls='--',label='306.18 deg bearing from H01W')]
fig.legend(handles=h,loc='lower center',ncol=3,frameon=False,bbox_to_anchor=(0.5,-0.02),fontsize=6)
fig.suptitle('Floating debris from the bearing-arc crossing is 300-1,000 km west of the Haixun 01 contact on 5 April 2014',x=0.06,ha='left',fontsize=8,y=0.99)
n1=("Plain: We put 100,000 floating objects at the point where the 306.18 deg bearing meets the 7th arc, and at points 50-200 km inside the arc, on 8 Mar 2014 "
    "at the impact time from the sound. The shading shows where the objects are at 03:15 UTC on 5 Apr 2014, when white objects were seen about 90 km from the Haixun 01 contact. "
    "Almost no objects come within 110 km of the contact. Two ocean models are shown. This is a forward drift only; it does not use the flight-path calculation.")
n2=("Technical: debris-drift engine snapshot harness (drift d51d80a, untracked stand-in test `snapshots`), aus160 configs with 28-day forcing (GLORYS12V1 0.494 m or GlobCurrent 0 m, ERA5 U10; "
    "GlobCurrent product-relative windage U(-0.75,-0.60) % U10), 3 object classes x 4 ocean-error/diffusivity realisations (K log-uniform 100-1000 m2/s), 8,334 per class, refloat off, 6 h step. "
    "Release at branch T impact times (00:31:52-00:34:24 UTC; branch C +2 min 27 s gives the same map within Monte Carlo noise). Positions linearly interpolated 00Z-12Z 5 Apr. HPD of object density, 0.1 deg bins. "
    "No flight-path posterior, no 00:19 option, no search case, no exclusions. Sighting: JACC 5-6 Apr 2014 (grade A), position not published.")
fig.text(0.06,-0.13,"\n".join(textwrap.wrap(n1,180)),fontsize=6,va='top'); fig.text(0.06,-0.22,"\n".join(textwrap.wrap(n2,180)),fontsize=6,va='top')
os.makedirs('out',exist_ok=True)
fig.savefig('out/fig-forward-drift-5apr.png',dpi=300,bbox_inches='tight'); fig.savefig('out/fig-forward-drift-5apr.pdf',bbox_inches='tight')
plt.close(fig)
