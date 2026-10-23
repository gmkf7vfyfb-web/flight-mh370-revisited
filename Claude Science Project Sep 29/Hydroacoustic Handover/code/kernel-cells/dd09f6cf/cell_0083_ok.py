fig,axs=plt.subplots(1,2,figsize=(10.5,5.6),sharey=True)
DLAB=['00:19 data\nheld out','00:19:29\nBTO','00:19:29\nBTO + BFO','both 00:19\nBFOs','both BFOs,\nshared offset','00:19:37 BFO\nwith offset']
series=[('Tcore','00:52:03 reception','#1f4e9c',-0.2),('Ccore','00:54:30 reception','#b8621b',0.0),('strip','bearing strip (prior mass only)','#777777',0.2)]
for ax,term,ttl in [(axs[0],'seabed','Seabed search: the locality is less searched than the rest'),(axs[1],'surface','Surface search: debris near the crossing should have been seen')]:
    for key,lab,colr,off in series:
        for i,d in enumerate(DK):
            sub=T[(T.term==term)&(T.option==d)&(T.locality==key)]
            ref=sub[sub.case==('rho 05' if term=='seabed' else 'windage 0.5%, POD csiro, floor 0.0')].lnB.values[0]
            lo_,hi_=sub.lnB.min(),sub.lnB.max()
            sd=BOOT[d][key]['seabed_sd' if term=='seabed' else 'surface_sd']
            ess=res[d][key]['ESS']
            ax.plot([i+off,i+off],[lo_,hi_],c=colr,lw=0.8,alpha=0.6)
            ax.errorbar(i+off,ref,yerr=2*sd,fmt='o',ms=6,c=colr,mfc=colr if ess>=30 else 'white',mec=colr,capsize=0,lw=2)
    ax.axhline(0,c='k',lw=0.6)
    ax.set_xticks(range(6)); ax.set_xticklabels(DLAB,fontsize=7); ax.set_title(ttl,loc='left'); ax.margins(x=0.05)
axs[0].set_ylabel('ln likelihood ratio, locality vs rest of run J')
axs[0].text(5.4,1.95,'above 0 = favours the locality',ha='right',fontsize=7)
h_=[Line2D([],[],ls='none',marker='o',c=c_,label=l_) for k_,l_,c_,o_ in series]+[Line2D([],[],ls='none',marker='o',mfc='white',mec='k',label='effective sample size below 30 (not converged)'),
     Line2D([],[],c='k',lw=2,label='2 standard errors over seeds'),Line2D([],[],c='k',lw=0.8,alpha=0.6,label='range over sensitivity cases')]
fig.legend(handles=h_,loc='upper center',ncol=3,frameon=False,bbox_to_anchor=(0.52,0.235),fontsize=7)
panel_letter(axs[0],'a'); panel_letter(axs[1],'b')
f1=("Plain: Each point compares how well the searches agree with an impact near the bearing crossing and with an impact anywhere else in the result. "
    "Above zero, the search supports the crossing. The seabed search supports it because most other positions were searched and nothing was found. "
    "The surface search goes against it. Open points have too few samples to be reliable.")
f2=("Technical: run J, 4 strata by core P(family), q=1/3 (C2 silent). Locality rows weighted by the pre-registered acoustic likelihood (core sigma_b 0.5 deg); complement = run J outside the bearing strip. "
    "Seabed: L = rho + (1-rho) prod(1 - q c f), ATSB Phase 2 q 0.945, Bluefin-21 q 0.9, OI 2018 q 0.9 f 0.889 and OI 2025-26 q 0.9 f 0.7808 (inferred, grade C), impact point, reference rho 0.05; range rho 0-0.5 and ATSB only. "
    "Surface: CSIRO POD 1.0/0.15, windage 0.5 % on GlobCurrent 0 m, floor 0; range windage 0.5-2.5 %, POD field/item, floor 0-0.2. Physics not calibrated.")
fig.subplots_adjust(left=0.07,right=0.98,top=0.92,bottom=0.4,wspace=0.06)
fig.text(0.05,0.15,'\n'.join(textwrap.wrap(f1,185)),fontsize=7,va='top'); fig.text(0.05,0.085,'\n'.join(textwrap.wrap(f2,195)),fontsize=6.5,va='top',color='#444')
fig.savefig('fig3-search-likelihood-terms.png',dpi=200); fig.savefig('fig3-search-likelihood-terms.pdf'); print('ok')