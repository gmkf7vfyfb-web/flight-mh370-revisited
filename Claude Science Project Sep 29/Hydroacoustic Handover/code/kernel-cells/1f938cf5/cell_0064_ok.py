
import textwrap
def render_map(fname):
    fig,axs=plt.subplots(1,2,figsize=(7.2,4.6),gridspec_kw=dict(width_ratios=[1.15,1]))
    ax=axs[0]
    im=ax.pcolormesh(glon_m,glat_m,DEP,cmap='Blues',vmin=3000,vmax=6000,shading='auto',rasterized=True)
    ax.contour(glon_m,glat_m,gaussian_filter(AUSM.astype(float),2),levels=[0.5],colors='0.35',linewidths=0.6,linestyles=':')
    for br,col in (('T','#e08214'),('C','#542788')):
        o=RES[f'kadri_{br}']['recorder-detached']; sel=np.random.default_rng(1).choice(N,1500,replace=False)
        ax.scatter(o['lon0'][sel],o['lat0'][sel],s=1.2,color=col,alpha=0.35,lw=0,rasterized=True)
    for daz,ls,lw in [(0,'-',0.9),(-0.5,'--',0.6),(0.5,'--',0.6),(-1,':',0.7),(1,':',0.7)]:
        s_=np.arange(R7-80,R7+260,2.0)
        lo_,la_,_=gw.fwd(np.full(len(s_),H01W[1]),np.full(len(s_),H01W[0]),np.full(len(s_),AZ+daz),s_*1e3)
        ax.plot(lo_,la_,color='k',ls=ls,lw=lw)
    ax.plot(arcs['c'][:,1],arcs['c'][:,0],color='#b2182b',lw=1.0)
    for k in 'pm': ax.plot(arcs[k][:,1],arcs[k][:,0],color='#b2182b',lw=0.6,ls='--')
    ax.plot(CX[1],CX[0],marker='o',ms=4,mfc='white',mec='k',mew=0.8)
    ax.plot(HX[1],HX[0],marker='*',ms=8,color='k')
    ax.set_xlim(98.8,103.2); ax.set_ylim(-27.6,-23.4); ax.set_aspect(1/np.cos(np.radians(25.5)))
    ax.set_xlabel('Longitude (°E)'); ax.set_ylabel('Latitude (°N)')
    ax.set_title('Sea-floor depth along the 306.18° bearing',loc='left')
    bb=dict(boxstyle='square,pad=0.15',fc='white',ec='none',alpha=0.8)
    ax.text(101.58,-26.02,'Haixun 01 contact',fontsize=6,va='center',bbox=bb)
    ax.text(101.47,-25.66,'bearing × 7th arc',fontsize=6,bbox=bb)
    ax.text(98.9,-23.62,'impact, 00:52:03 reception',fontsize=6,color='#e08214',bbox=bb)
    ax.text(98.9,-23.82,'impact, 00:54:30 reception',fontsize=6,color='#542788',bbox=bb)
    ax.text(101.75,-24.35,'7th arc\n(sea level,\n±63 µs dashed)',fontsize=6,color='#b2182b',bbox=bb)
    ax.text(99.0,-27.45,'bearing: centre, ±0.5° dashed, ±1° dotted\nAusSeabed 150 m coverage: grey dotted',fontsize=6,bbox=bb)
    cb=fig.colorbar(im,ax=ax,shrink=0.7,pad=0.02); cb.set_label('Depth (m)'); cb.ax.invert_yaxis()
    panel_letter(ax,'a')
    ax=axs[1]
    im2=ax.pcolormesh(zlo,zla,ZD,cmap='Blues',vmin=4450,vmax=4700,shading='auto',rasterized=True)
    for cls,style in (('recorder-detached','fill'),('fuselage-section','line')):
        I=INV[cls]; bx=np.arange(-20,20.01,0.1); Hh,_,_=np.histogram2d(I['ny'],I['ex'],bins=[bx,bx]); Hh=gaussian_filter(Hh,1.0 if style=='fill' else 4.0)
        lv=hpd_levels(Hh); xc=HX[1]+0.5*(bx[1:]+bx[:-1])*kmx; yc=HX[0]+0.5*(bx[1:]+bx[:-1])*kmy
        if style=='fill':
            ax.contourf(xc,yc,Hh,levels=[lv[2],lv[1],lv[0],Hh.max()*1.01],colors=['0.85','0.6','0.3'],alpha=0.85)
        else:
            ax.contour(xc,yc,Hh,levels=[lv[2],lv[1],lv[0]],colors='k',linewidths=[0.5,0.8,1.1],linestyles=[':','--','-'])
    ax.plot(HX[1]+2*np.cos(th_)*kmx,HX[0]+2*np.sin(th_)*kmy,color='#b2182b',lw=0.8)
    ax.plot(HX[1],HX[0],marker='*',ms=8,color='k')
    for k in (2,3):
        p_=dest(HX,270,k); ax.plot(p_[1],p_[0],marker='^',ms=4,mfc='white',mec='k',mew=0.7)
    ax.set_xlim(zlo[0],zlo[-1]); ax.set_ylim(zla[0],zla[-1]); ax.set_aspect(1/np.cos(np.radians(HX[0])))
    ax.set_xlabel('Longitude (°E)')
    ax.set_title('Where the aircraft must hit the water',loc='left')
    ax.text(HX[1]+0.012,HX[0]+0.026,'2 km from contact',fontsize=6,color='#b2182b',bbox=bb)
    ax.text(zlo[0]+0.005,zla[-1]-0.008,'grey fill: detached recorder\nblack lines: recorder kept in aft fuselage\n50 / 90 / 99 % HPD: solid / dashed / dotted',fontsize=6,va='top',bbox=bb)
    ax.text(HX[1]-0.07,HX[0]-0.015,'second contact,\n2–3 km west',fontsize=6,ha='center',va='top',bbox=bb)
    cb2=fig.colorbar(im2,ax=ax,shrink=0.7,pad=0.02); cb2.set_label('Depth (m)'); cb2.ax.invert_yaxis()
    panel_letter(ax,'b')
    fig.subplots_adjust(left=0.08,right=0.97,top=0.94,bottom=0.27,wspace=0.28)
    fig.text(0.01,0.135,textwrap.fill(fn1,200),fontsize=5.5,va='top')
    fig.text(0.01,0.07,textwrap.fill(fn2,215),fontsize=5.5,va='top',color='0.25')
    fig.savefig(fname,dpi=300); return fig
fig=render_map('out/fig_settling_haixun_map.png')
r_=fig.canvas.get_renderer()
texts=[(t,t.get_window_extent(r_)) for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
print([(a.get_text()[:25],b.get_text()[:25]) for i,(a,ba) in enumerate(texts) for b,bb in texts[i+1:] if ba.overlaps(bb)])
