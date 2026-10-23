def hist_norm(pool,k,reg,which):
    h,_=A.pooled_hist(seeds,pool,k,reg,which); return h/h.sum() if h is not None else None
fig,axs=plt.subplots(2,3,figsize=(7.2,4.4),sharex='col',gridspec_kw=dict(hspace=0.3,wspace=0.25))
TBm=W.TB[:-1]/60+0.5; FBm=W.FB[:-1]/60+0.5; ABm=W.AB[:-1]/60+0.5
series=[('all','whole posterior','0.6','-'),('strip','impacts in the bearing strip','k','-'),('cond_T1.0','given arrival 00:52:03','#e66101','-'),('cond_C1.0','given arrival 00:54:30','#5e3c99','--')]
for i,d in enumerate((0,2)):
    k=f'D{d} total q=0.333 (C2 silent)'
    for reg,lab,c,ls in series:
        for j,(which,xm,n) in enumerate((('t',TBm,len(TBm)),('fo',FBm,len(FBm)),('aloft',ABm,len(ABm)))):
            h=hist_norm('main',k,reg,which); axs[i,j].plot(xm,h[:n],color=c,ls=ls,lw=1.0,label=lab if (i==0 and j==0) else None)
            if which=='aloft' and reg!='all' or (which=='aloft' and reg=='all'):
                pass
    axs[i,0].set_ylabel(f"{OPT[d].replace(chr(10),' ')}\nprobability per minute")
for i in range(2):
    axs[i,0].set_xlim(15,60); axs[i,1].set_xlim(10,40); axs[i,2].set_xlim(0,40)
    for j in range(3): axs[i,j].axvline({0:34.1,1:None,2:None}.get(j) or -99,color='#e66101',lw=0.5,ls=':')
axs[1,0].set_xlabel('impact time (min after 00:00 UTC)'); axs[1,1].set_xlabel('final flame-out (min after 00:00 UTC)'); axs[1,2].set_xlabel('minutes aloft after final flame-out')
axs[0,0].legend(frameon=False,fontsize=5.5,loc='upper right')
fig.suptitle('Flights that fit the H01W sound end in a 15-20 min glide after fuel exhaustion at about 00:17-00:18',x=0.06,ha='left',y=0.99)
fig.text(0.06,-0.02,('(i) Plain: Lines show how often each time occurs. Grey: all flights that agree with the satellite data. Black: flights that end in the strip along the bearing. '
 'Coloured: flights weighted by agreement with the sound. The dotted line at 00:34 is the impact time for an impact on the arc at the bearing (text reading). Flights still powered at impact are not in the right-hand panels. Searches, drift and other evidence are not used.'),fontsize=5.5,wrap=True,va='top')
fig.text(0.06,-0.10,('(ii) Technical: end-of-flight run J, cells "D0/D2 total q=0.333 (C2 silent)", four strata mixed by core P(family); strip = 1,531-1,841 km from H01W, |cross-track| <= range tan 1 deg; '
 'conditional = w_i L_i with s_b = 1.0 deg (pre-registration Q2); 1-min bins; times from compact T0 = 1394236800 (00:00:00 UTC). Conditional effective samples 166 / 14 (D0) and 24 / 14 (D2): NOT ESTIMABLE as shapes. Physics PROVISIONAL; no search, drift or ocean model.'),fontsize=5.5,wrap=True,va='top')
fig.savefig('kh/fig/fig-timing-distributions.png',dpi=300,bbox_inches='tight'); fig.savefig('kh/fig/fig-timing-distributions.pdf',bbox_inches='tight'); plt.close(fig)
# check cond aloft share none/powered
for d in (0,2):
    k=f'D{d} total q=0.333 (C2 silent)'; h=hist_norm('main',k,'cond_T1.0','aloft'); print(d, 'aloft>=60',h[-2].round(4),'no flameout before impact',h[-1].round(4))