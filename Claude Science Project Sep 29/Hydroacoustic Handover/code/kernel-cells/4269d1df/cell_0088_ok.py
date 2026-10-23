figsrc3 = r'''
def fig_llr(RC, prof, aus, ex, fn='out/fig-drift-llr-kadri', extra_pts=None):
    fig,axs=plt.subplots(1,2,figsize=(7.2,3.3),gridspec_kw=dict(width_ratios=[1.35,1],wspace=0.32))
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
    ax.set_title('Debris evidence favours the bearing locality over the run J posterior',loc='left')
    hh=[mpl.lines.Line2D([],[],color=cols['populated'],lw=1.2,label=labs['populated']),mpl.lines.Line2D([],[],color=cols['none'],lw=1.2,label=labs['none']),
        mpl.lines.Line2D([],[],marker='o',ls='none',mfc='white',mec='k',ms=3.5,label='release points on the bearing (0-150 km inside)'),
        mpl.lines.Line2D([],[],marker='D',ls='none',color='w',mec='k',ms=4.5,label='impacts selected by the sound, text time (2-sigma)'),
        mpl.lines.Line2D([],[],marker='s',ls='none',color='w',mec='k',ms=4.5,label='impacts selected by the sound, caption time (2-sigma)')]
    ax.legend(handles=hh,frameon=False,fontsize=6,loc='lower left'); ax.set_xlim(-41.5,-21.5); ax.margins(y=0.08)
    ax=axs[1]
    for o,off in (('populated',0.0),('none',0.0)):
        for br,mk,dx in (('T_core','D',-0.12),('C_core','s',0.12)):
            r=RC[(RC.model=='mean')&(RC.option==o)&(RC.variant==br)].set_index('D').loc[[f'D{d}' for d in range(6)]]
            x=np.arange(6)+dx
            ax.errorbar(x,r.LLR,yerr=2*r.sd_total,marker=mk,ms=4,ls='none',color=cols[o],mec='k',mew=0.4,capsize=2,lw=0.8)
            if o=='populated':
                for xi,(yi,ei) in zip(x,zip(r.LLR,r.ESS)): ax.text(xi,yi+2*r.sd_total.max()+0.12,f'{ei:.0f}',ha='center',fontsize=5.5,color='#444444')
    ax.axhline(0,color='k',lw=0.5); ax.set_xticks(range(6)); ax.set_xticklabels(['held out','R600 BTO','+R600 BFO','+both BFOs','+both, offset','+R1200 offset'],rotation=30,ha='right')
    ax.set_xlabel('00:19 data used'); ax.set_ylabel('log-likelihood ratio vs run J reference')
    ax.set_title('The ratio is stable across the 00:19 options',loc='left'); ax.margins(y=0.12)
    ax.text(0.98,0.02,'numbers: effective sample size (finds + populated)',transform=ax.transAxes,ha='right',fontsize=5.5,color='#444444')
    panel_letter(axs[0],'a'); panel_letter(axs[1],'b')
    fig.text(0.06,-0.2,"\n".join(textwrap.wrap(N3a,175)),fontsize=6,va='top'); fig.text(0.06,-0.31,"\n".join(textwrap.wrap(N3b,175)),fontsize=6,va='top')
    fig.savefig(fn+'.png',dpi=300,bbox_inches='tight'); fig.savefig(fn+'.pdf',bbox_inches='tight'); plt.close(fig)
'''
open('figs.py','a').write(figsrc3); exec(figsrc3)
N3a=("Plain: The debris model gives a number for how well each impact place explains the debris that was found (flaperon and eight other items, with the dates they were found) and the absence of finds on Australian coasts where people live. "
     "We compare the impact places that agree with the sound from H01W (bearing 306.18 deg; arrival 00:52:03 or 00:54:30) with all impacts from the flight-path calculation. A positive number means the debris favours the place near the bearing. "
     "The two ocean models have equal weight. The selected impacts are few, so the effective sample size is small.")
N3b=("Technical: drift surfaces run A (rebuilt, h50 kernel, GLORYS12V1 + ERA5 and GlobCurrent + ERA5, equal-weight likelihood mixture), Australian populated-coast term reconstructed with the saturating law from the 15-160 E pilot (k,c fitted per model), "
     "release 00:19:37 UTC in these surfaces (dedicated L-point run at the branch impact times queued). Prior: run J four families (waypoints 0.9982, free, repro-radar, descent-climb), cell 'D{d} total q=0.333 (C2 silent)', 74 seeds. "
     "Acoustic weight: pre-registered Q2 likelihood, c = 1.48 km/s, s_b = 0.5 deg (core). Bars: 2-sigma = transport noise (200 node perturbations) and seed bootstrap combined. Uncontrolled-descent physics not calibrated. "
     "No search-area term (separate module); joined planned descents J0011/J2241 not included. Rows outside drift support (2-5 % of weight) carried at the mean.")
fig_llr(RC,prof,aus,ex)
