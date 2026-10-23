import matplotlib as mpl, textwrap
apply_figure_style(sizes=(9,8,7))
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
win=sbox(99,-27.5,104,-23.0)
def fillgeom(ax,g,**kw):
    for q in getattr(g,'geoms',[g]):
        if q.geom_type=='Polygon' and not q.is_empty:
            ax.add_patch(mpl.patches.Polygon(np.array(q.exterior.coords),closed=True,**kw))
            for h_ in q.interiors: ax.add_patch(mpl.patches.Polygon(np.array(h_.coords),closed=True,fc='white',ec='none',zorder=kw.get('zorder',1)))
        elif hasattr(q,'geoms'): fillgeom(ax,q,**kw)
bline=[direct(306.18,s) for s in np.linspace(1400,1900,60)]
blo=[direct(305.18,s) for s in np.linspace(1400,1900,60)]; bhi=[direct(307.18,s) for s in np.linspace(1400,1900,60)]
fig,axs=plt.subplots(1,2,figsize=(10.5,6.2),sharey=True)
for ax,ak,ttl in [(axs[0],'Tcore','Sound received at 00:52:03 (paper text)'),(axs[1],'Ccore','Sound received at 00:54:30 (paper caption)')]:
    fillgeom(ax,bth.intersection(win),fc='#e8dcc4',ec='none',zorder=1)
    fillgeom(ax,bs.intersection(win),fc='#b89a63',ec='none',zorder=2)
    fillgeom(ax,poly_oi.intersection(win),fc='#9fd3b0',ec='#3b8a5a',lw=0.8,alpha=0.55,zorder=3)
    xe,ye,h,lev,_=hpd_grid(DF[ak])
    ax.contourf(0.5*(xe[1:]+xe[:-1]),0.5*(ye[1:]+ye[:-1]),h,levels=[lev[0],lev[1],lev[2],h.max()*1.01],colors=['#d0d0d0','#8c8c8c','#303030'],alpha=0.85,zorder=4)
    ax.plot(arc_lon,arc_lat,ls=':',c='k',lw=1.2,zorder=6)
    ax.plot(*zip(*bline),c='#1f4e9c',lw=1.1,zorder=6); ax.plot(*zip(*blo),c='#1f4e9c',lw=0.7,ls='--',zorder=6); ax.plot(*zip(*bhi),c='#1f4e9c',lw=0.7,ls='--',zorder=6)
    x_,y_=strip_poly.exterior.xy; ax.plot(x_,y_,c='#1f4e9c',lw=0.6,ls='-',alpha=0.6,zorder=6)
    ax.plot(101.369,-25.732,marker='*',ms=13,mfc='white',mec='k',zorder=8)
    ax.plot(101.461,-25.975,marker='o',ms=6,mfc='none',mec='#a3351f',mew=1.4,zorder=8)
    ax.set_xlim(99,104); ax.set_ylim(-27.5,-23.0); ax.set_aspect(1/np.cos(np.radians(25.5)))
    ax.set_title(ttl,loc='left'); ax.set_xlabel('longitude (deg E)')
    ess=res['D0'][ak]['ESS']; cv=res['D0'][ak]['covOI18']
    ax.text(99.1,-23.15,f'effective sample size {ess:.0f}\nmean inferred Ocean Infinity coverage {cv:.2f}',va='top',fontsize=7,zorder=9,bbox=dict(fc='white',ec='none',alpha=0.8))
axs[0].set_ylabel('latitude (deg)')
panel_letter(axs[0],'a'); panel_letter(axs[1],'b')
leg=[Patch(fc='#303030',label='impact region, 50 % HPD'),Patch(fc='#8c8c8c',label='90 % HPD'),Patch(fc='#d0d0d0',label='99 % HPD'),
     Patch(fc='#9fd3b0',ec='#3b8a5a',alpha=0.55,label='seabed searched by Ocean Infinity 2018 (inferred)'),
     Patch(fc='#e8dcc4',label='depth survey 2014-17, 150 m grid (not a search)'),Patch(fc='#b89a63',label='depth survey line along the arc (not a search)'),
     Line2D([],[],c='k',ls=':',label='7th arc (00:19:29, sea level)'),Line2D([],[],c='#1f4e9c',label='bearing 306.18 deg from Cape Leeuwin hydrophone; dashed = +/-1 deg'),
     Line2D([],[],ls='none',marker='*',ms=11,mfc='white',mec='k',label='bearing crosses the arc, 25.732 S 101.369 E'),
     Line2D([],[],ls='none',marker='o',mfc='none',mec='#a3351f',mew=1.4,label='Haixun 01 contact, 5 Apr 2014 (sensitivity only)')]
fig.legend(handles=leg,loc='lower center',ncol=2,frameon=False,bbox_to_anchor=(0.5,0.155),fontsize=7)
fig.suptitle('The inferred 2018 seabed search covers the bearing only within about 45 km of the 7th arc',x=0.06,ha='left',fontsize=10)
foot1=("Plain: Grey shows where the aircraft hit the sea if the sound came from the impact, for each of the two reception times. "
       "Green shows where Ocean Infinity searched the seabed in 2018; this area is taken from maps and ship tracks, not official data. "
       "Tan shows depth surveys only; they do not find wreckage. No ATSB sonar search reached this area. Haixun 01 is a sensitivity case.")
foot2=("Technical: run J impacts (4 strata by core P(family)), 00:19 data held out, cause q=1/3 (C2 silent); weights x pre-registered acoustic likelihood "
       "(c 1.48 km/s, sigma_b 0.5 deg core); end-of-flight physics not calibrated; impact point, no settling. OI 2018 = MH370-CAPTION tracing (grade C); "
       "Phase 1 bathymetry GA ga/100315 and 30 m backscatter ga/83922 coverage polygons (grade A). ATSB Phase 2 north limit 32.7 S; Bluefin-21 21 S; OI 2025-26 34-36 S.")
fig.text(0.06,0.085,'\n'.join(textwrap.wrap(foot1,175)),fontsize=7,va='top')
fig.text(0.06,0.04,'\n'.join(textwrap.wrap(foot2,185)),fontsize=6.5,va='top',color='#444')
fig.subplots_adjust(left=0.07,right=0.98,top=0.9,bottom=0.33,wspace=0.06)
fig.savefig('fig1-seabed-coverage-bearing.png',dpi=200); fig.savefig('fig1-seabed-coverage-bearing.pdf')
r=fig.canvas.get_renderer(); texts=[(t,t.get_window_extent(r)) for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
print(len([(a,b) for i,(a,ba) in enumerate(texts) for b,bb in texts[i+1:] if ba.overlaps(bb)]))