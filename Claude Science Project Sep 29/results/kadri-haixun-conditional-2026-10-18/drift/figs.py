
def fig_forward(title, fn='out/fig-forward-drift-5apr'):
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
    hh=[mpl.patches.Patch(color='#404040',label='50 %'),mpl.patches.Patch(color='#969696',label='90 %'),mpl.patches.Patch(color='#d9d9d9',label='99 % HPD, objects from the arc crossing (star)'),
       mpl.lines.Line2D([],[],color='#b2182b',ls='--',lw=0.9,label='90 % HPD, objects from 50-200 km inside the arc (dots)'),
       mpl.lines.Line2D([],[],color='#555555',ls=':',lw=0.7,label='90 % HPD, objects from the Haixun 01 contact (sensitivity)'),
       mpl.lines.Line2D([],[],color='k',lw=0.6,label='70 and 110 km from the Haixun 01 contact (triangle)'),
       mpl.lines.Line2D([],[],color='#1f4e9a',lw=1,label='7th arc at sea level'),mpl.lines.Line2D([],[],color='#e08214',lw=0.9,label='306.18 deg bearing from H01W')]
    fig.legend(handles=hh,loc='upper left',ncol=2,frameon=False,bbox_to_anchor=(0.08,0.12),fontsize=6)
    fig.suptitle(title,x=0.08,ha='left',fontsize=8,y=0.93)
    fig.text(0.08,-0.06,"\n".join(textwrap.wrap(n1,170)),fontsize=6,va='top'); fig.text(0.08,-0.145,"\n".join(textwrap.wrap(n2,170)),fontsize=6,va='top')
    fig.savefig(fn+'.png',dpi=300,bbox_inches='tight'); fig.savefig(fn+'.pdf',bbox_inches='tight'); plt.close(fig)

def fig_backward(ODd, lons_, lats_, title, n1b, n2b, fn='out/fig-backward-origin-ring', xl=(95.5,107), yl=(-31.5,-20.5)):
    fig,axs=plt.subplots(1,2,figsize=(7.2,4.0),sharey=True,gridspec_kw=dict(wspace=0.06))
    dl=lons_[1]-lons_[0]
    for ax,(m,lab) in zip(axs,[('globcurrent','GlobCurrent currents + ERA5 wind'),('glorys12','GLORYS12 currents + ERA5 wind')]):
        od=ODd[m]; LLg,LOg=np.meshgrid(lats_,lons_,indexing='ij'); post=od*np.cos(np.radians(LLg))
        t50,t90,t99=hpd_levels(post)
        ax.contourf(lons_,lats_,post,levels=[t99,t90,t50,post.max()*1.0001],colors=['#d9d9d9','#969696','#404040'],zorder=1)
        ax.add_patch(mpl.patches.Rectangle((lons_[0]-dl/2,lats_[0]-dl/2),lons_[-1]-lons_[0]+dl,lats_[-1]-lats_[0]+dl,fill=False,ec='#777777',lw=0.6,ls='-.',zorder=2))
        context(ax,xl,yl); ax.set_title(lab,loc='left')
    axs[0].set_ylabel('latitude (deg)')
    hh=[mpl.patches.Patch(color='#404040',label='50 %'),mpl.patches.Patch(color='#969696',label='90 %'),mpl.patches.Patch(color='#d9d9d9',label='99 % HPD of start point on 8 Mar'),
        mpl.lines.Line2D([],[],color='#777777',ls='-.',lw=0.6,label='edge of the start-point grid'),
        mpl.lines.Line2D([],[],color='k',lw=0.6,label='70 and 110 km from the Haixun 01 contact (triangle)'),
        mpl.lines.Line2D([],[],marker='*',color='#b2182b',ls='none',mec='k',label='bearing-arc crossing; dots 50-200 km inside'),
        mpl.lines.Line2D([],[],color='#1f4e9a',lw=1,label='7th arc at sea level'),mpl.lines.Line2D([],[],color='#e08214',lw=0.9,label='306.18 deg bearing from H01W')]
    fig.legend(handles=hh,loc='upper left',ncol=2,frameon=False,bbox_to_anchor=(0.08,0.05),fontsize=6)
    fig.suptitle(title,x=0.08,ha='left',fontsize=8,y=0.95)
    fig.text(0.08,-0.13,"\n".join(textwrap.wrap(n1b,170)),fontsize=6,va='top'); fig.text(0.08,-0.235,"\n".join(textwrap.wrap(n2b,170)),fontsize=6,va='top')
    fig.savefig(fn+'.png',dpi=300,bbox_inches='tight'); fig.savefig(fn+'.pdf',bbox_inches='tight'); plt.close(fig)

def fig_llr(RC, prof, aus, ex, fn='out/fig-drift-llr-kadri', extra_pts=None):
    fig,axs=plt.subplots(1,2,figsize=(7.2,3.3),gridspec_kw=dict(width_ratios=[1.35,1],wspace=0.38))
    ax=axs[0]
    cols={'none':'#7f7f7f','populated':'#1f4e9a'}
    labs={'none':'debris finds only','populated':'finds and no finds on populated Australian coasts'}
    for o,po in (('none','off'),('populated','populated only (city+inner=1)')):
        pr=prof[(prof.model=='mean')&(prof.option==po)&(prof.position=='median impact')].sort_values('arc_lat')
        ref=aus['cells']['D0'][f"{OPT[o]}|mean"]['dlnZ_drift']
        ax.plot(pr.lat,pr.lnL-ref,color=cols[o],lw=1.2,label=labs[o]+' (7th arc, median impact track)')
        e=ex[(ex.model=='mean')&(ex.option==o)&(ex.D=='D0')&ex.LLR.notna()]
        ax.plot(e.lat,e.LLR,marker='o',ms=3.5,ls='none',mfc='white',mec=cols[o],mew=0.8)
        for br,mk in (('T_core','D'),('C_core','s')):
            r=RC[(RC.D=='D0')&(RC.model=='mean')&(RC.option==o)&(RC.variant==br)].iloc[0]
            pc=P[('D0',br)]; w=pc['sum']; la=float((pc['lat_mean']*w).sum()/w.sum())
            ax.errorbar(la,r.LLR,yerr=2*r.sd_total,marker=mk,ms=4.5,color=cols[o],mec='k',mew=0.4,capsize=2,lw=0.8,zorder=5)
    ax.axhline(0,color='k',lw=0.5); ax.set_xlabel('latitude (deg)'); ax.set_ylabel('log-likelihood ratio vs run J reference')
    ax.set_title('Debris evidence near the bearing exceeds run J',loc='left')
    hh=[mpl.lines.Line2D([],[],color=cols['populated'],lw=1.2,label=labs['populated']),mpl.lines.Line2D([],[],color=cols['none'],lw=1.2,label=labs['none']),
        mpl.lines.Line2D([],[],marker='o',ls='none',mfc='white',mec='k',ms=3.5,label='release points on the bearing (0-150 km inside)'),
        mpl.lines.Line2D([],[],marker='D',ls='none',color='w',mec='k',ms=4.5,label='impacts selected by the sound, text time (2-sigma)'),
        mpl.lines.Line2D([],[],marker='s',ls='none',color='w',mec='k',ms=4.5,label='impacts selected by the sound, caption time (2-sigma)')]
    ax.legend(handles=hh,frameon=False,fontsize=6,loc='lower left'); ax.set_xlim(-41.5,-21.5); ax.margins(y=0.08)
    ax=axs[1]
    for o,off in (('populated',0.0),('none',0.0)):
        for br,mk,dx in (('T_core','D',-0.2),('C_core','s',0.2)):
            r=RC[(RC.model=='mean')&(RC.option==o)&(RC.variant==br)].set_index('D').loc[[f'D{d}' for d in range(6)]]
            x=np.arange(6)+dx
            ax.errorbar(x,r.LLR,yerr=2*r.sd_total,marker=mk,ms=4,ls='none',color=cols[o],mec='k',mew=0.4,capsize=2,lw=0.8)
            if o=='none':
                for xi,ei in zip(x,r.ESS): ax.text(xi,-0.45,f'{ei:.0f}',ha='center',fontsize=5.5,color='#444444')
    ax.axhline(0,color='k',lw=0.5); ax.set_xticks(range(6)); ax.set_xticklabels(['held out','R600 BTO','+R600 BFO','+both BFOs','+both, offset','+R1200 offset'],rotation=30,ha='right')
    ax.set_xlabel('00:19 data used'); ax.set_ylabel('log-likelihood ratio vs run J reference')
    ax.set_title('Stable across 00:19 options',loc='left'); ax.set_ylim(-0.6,4.4)
    ax.text(0.02,0.075,'effective sample size (diamond, square):',transform=ax.transAxes,ha='left',fontsize=5.5,color='#444444'); ax.set_ylim(-0.6,None)
    panel_letter(axs[0],'a'); panel_letter(axs[1],'b')
    fig.text(0.06,-0.2,"\n".join(textwrap.wrap(N3a,175)),fontsize=6,va='top'); fig.text(0.06,-0.33,"\n".join(textwrap.wrap(N3b,175)),fontsize=6,va='top')
    fig.savefig(fn+'.png',dpi=300,bbox_inches='tight'); fig.savefig(fn+'.pdf',bbox_inches='tight'); plt.close(fig)
