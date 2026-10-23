def context(ax, xl, yl):
    ax.plot(arc[:,1],arc[:,0],color='#1f4e9a',lw=1.0,zorder=3)
    ax.plot(bl[:,1],bl[:,0],color='#e08214',lw=0.9,zorder=3)
    ring(ax,HX,70,color='k',lw=0.6,zorder=4); ring(ax,HX,110,color='k',lw=0.6,zorder=4)
    ax.plot(pts[0][2],pts[0][1],marker='*',ms=9,color='#b2182b',mec='k',mew=0.4,zorder=6,ls='none')
    ax.plot([p[2] for p in pts[1:5]],[p[1] for p in pts[1:5]],marker='o',ms=3.5,color='#b2182b',mec='k',mew=0.3,ls='none',zorder=6)
    ax.plot(HX[1],HX[0],marker='^',ms=5,color='white',mec='k',mew=0.6,ls='none',zorder=6)
    ax.set_xlim(*xl); ax.set_ylim(*yl); ax.set_aspect(1/np.cos(np.radians(np.mean(yl))))
    ax.set_xlabel('longitude (deg E)')
xb=np.arange(86,107.01,0.1); yb=np.arange(-33,-16.99,0.1); XC=(xb[:-1]+xb[1:])/2; YC=(yb[:-1]+yb[1:])/2
fig,axs=plt.subplots(1,2,figsize=(7.2,4.2),sharey=True,gridspec_kw=dict(wspace=0.06))
for ax,(m,lab) in zip(axs,[('globcurrent','GlobCurrent currents + ERA5 wind'),('glorys12','GLORYS12 currents + ERA5 wind')]):
    a=SL[m]; s=a[a['rel']==0]; p=pos_at_0315(s['pos'],6,7); ok=np.isfinite(p[:,0])
    H,_,_=np.histogram2d(p[ok,1],p[ok,0],[yb,xb]); grey_hpd(ax,XC,YC,H)
    st=np.concatenate([a[a['rel']==ri]['pos'] for ri in (1,2,3,4)]); q=pos_at_0315(st,6,7); ok=np.isfinite(q[:,0])
    H2,_,_=np.histogram2d(q[ok,1],q[ok,0],[yb,xb]); ax.contour(XC,YC,H2,levels=[hpd_levels(H2)[1]],colors=['#b2182b'],linewidths=0.9,linestyles='--',zorder=2)
    sh=a[a['rel']==5]; h=pos_at_0315(sh['pos'],6,7); ok=np.isfinite(h[:,0])
    H3,_,_=np.histogram2d(h[ok,1],h[ok,0],[yb,xb]); ax.contour(XC,YC,H3,levels=[hpd_levels(H3)[1]],colors=['#555555'],linewidths=0.7,linestyles=':',zorder=2)
    context(ax,(86,106),(-33,-17)); ax.set_title(lab,loc='left')
axs[0].set_ylabel('latitude (deg)')
h=[mpl.patches.Patch(color='#404040',label='50 %'),mpl.patches.Patch(color='#969696',label='90 %'),mpl.patches.Patch(color='#d9d9d9',label='99 % HPD, objects from the arc crossing (star)'),
   mpl.lines.Line2D([],[],color='#b2182b',ls='--',lw=0.9,label='90 % HPD, objects from 50-200 km inside the arc (dots)'),
   mpl.lines.Line2D([],[],color='#555555',ls=':',lw=0.7,label='90 % HPD, objects from the Haixun 01 contact (sensitivity)'),
   mpl.lines.Line2D([],[],color='k',lw=0.6,label='70 and 110 km from the Haixun 01 contact (triangle)'),
   mpl.lines.Line2D([],[],color='#1f4e9a',lw=1,label='7th arc at sea level'),mpl.lines.Line2D([],[],color='#e08214',lw=0.9,label='306.18 deg bearing from H01W')]
fig.legend(handles=h,loc='upper left',ncol=2,frameon=False,bbox_to_anchor=(0.08,0.12),fontsize=6)
fig.suptitle('Floating debris from the bearing-arc crossing is 160-1,000 km from the Haixun 01 contact at 03:15 UTC on 5 April 2014',x=0.08,ha='left',fontsize=8,y=0.93)
fig.text(0.08,-0.06,"\n".join(textwrap.wrap(n1,170)),fontsize=6,va='top'); fig.text(0.08,-0.135,"\n".join(textwrap.wrap(n2,170)),fontsize=6,va='top')
fig.savefig('out/fig-forward-drift-5apr.png',dpi=300,bbox_inches='tight'); fig.savefig('out/fig-forward-drift-5apr.pdf',bbox_inches='tight'); plt.close(fig)
