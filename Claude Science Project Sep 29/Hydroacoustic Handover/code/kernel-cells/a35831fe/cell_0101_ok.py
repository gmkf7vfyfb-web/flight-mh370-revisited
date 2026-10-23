apply_figure_style(sizes=(8,7,6))
os.makedirs('cand',exist_ok=True)
RXP=[('H01W','Cape Leeuwin H01W (Kadri Fig. 9, digitised)','kadri'),('H08S','Diego Garcia South H08S (Kadri Fig. 9, digitised; airgun survey)','kadri'),
     ('3315','Perth Canyon 3315 (IMOS raw, 5-40 Hz)','imos'),('3376','Perth Canyon 3376 (IMOS raw, 5-40 Hz)','imos'),
     ('3274','Portland 3274 (IMOS raw, 5-40 Hz)','imos'),('3275','Portland 3275 (IMOS raw, 5-40 Hz)','imos'),
     ('H01W2','Cape Leeuwin H01W-2 (Royer strip, digitised spectrogram level)','royer'),('SSEIR','OHASISBIO SSEIR (Royer strip, digitised level)','royer'),('SWAMS3','OHASISBIO SWAMS3 (Royer strip, digitised level)','royer')]
def rx_ll(r): return rx_roy[r] if r in rx_roy else tuple(rx[r])
def land_on_path(la,lo,r):
    a,b=rx_ll(r); return path_land(la,lo,a,b)[0]
chart1_notes={}
def chart1(k):
    cd=CANDS[k]; L,Lo,t0=cd['lat'],cd['lon'],cd['t0']; W_=20.0
    fig,axs=plt.subplots(len(RXP),1,figsize=(7.2,10.5),sharex=True)
    notes=[]
    for ax,(r,lab,kind) in zip(axs,RXP):
        la,lo=rx_ll(r); d=G.inv(Lo,L,lo,la)[2]/1000; tt=d/c; sig=d*0.006/c**2
        nland=land_on_path(L,Lo,r)
        ax.axvspan(-sig,sig,color='#fde0c5',lw=0,zorder=0)
        ax.axvline(0,color='#e6550d',lw=0.8,zorder=1)
        lo_t,hi_t=t0+tt-W_,t0+tt+W_
        got=False
        if kind=='kadri':
            for tr,p in ktr[r]:
                mk=(tr>=lo_t)&(tr<=hi_t)
                if mk.any(): ax.plot(tr[mk]-tt-t0,p[mk],color='k',lw=0.4); got=True
            ax.set_ylabel('Pa',fontsize=6)
        elif kind=='imos':
            o=imos_rec(r,t0+tt)
            if o is None:
                for a_,b_ in held[r]:
                    if a_<=hi_t and b_>=lo_t: o=imos_rec(r,max(a_,lo_t)+1); break
            if o is not None:
                tr,p,fs=o; mk=(tr>=lo_t)&(tr<=hi_t)
                if mk.any(): ax.plot(tr[mk]-tt-t0,p[mk],color='k',lw=0.25); got=True
            ax.set_ylabel('Pa',fontsize=6)
        else:
            b=rstrip[r]; mk=(b.t_utc_s>=lo_t)&(b.t_utc_s<=hi_t)
            if mk.any():
                ref=b[(b.t_utc_s>=t0+tt-600)&(b.t_utc_s<=t0+tt+600)].psd_db_5_40.median()
                ax.plot(b.t_utc_s[mk]-tt-t0,b.psd_db_5_40[mk]-ref,color='#3182bd',lw=0.8,drawstyle='steps-mid'); got=True
                if r=='H01W2': ax.plot(b.t_utc_s[mk]-tt-t0-16,b.psd_db_5_40[mk]-ref,color='#9ecae1',lw=0.6,ls='--',drawstyle='steps-mid')
            ax.set_ylabel('dB re\nlocal median',fontsize=6)
        for rr,ts in cd['arr']:
            if rr==r: ax.axvline(hms(ts)-tt-t0,color='#2ca02c',lw=1.0,ls='--',zorder=2)
        nxt=''
        if not got:
            if kind=='imos':
                st=[a_ for a_,b_ in held[r] if a_>hi_t]; pr=[b_ for a_,b_ in held[r] if b_<lo_t]
                nxt=f" (records end {fmt(max(pr))[:8] if pr else '-'}, next starts {fmt(min(st))[:8] if st else '-'})"
            elif kind=='kadri': nxt=' (outside the published panels)'
            ax.text(0.5,0.5,'no data held at this time'+nxt,transform=ax.transAxes,ha='center',va='center',fontsize=6,color='#636363')
        flag=''
        if nland>0: flag=' - DIRECT PATH CROSSES LAND'
        if r=='H08S' and got: flag+=' - airgun shots every 10 s'
        ax.set_title(f"{lab}: arrival {fmt(t0+tt)[:8]} UTC, {d:,.0f} km{flag}",loc='left',fontsize=6.5,pad=2)
        ax.tick_params(labelsize=6)
        notes.append(dict(cand=k,rx=r,range_km=round(d),pred_arrival=fmt(t0+tt),sigma_s=round(sig,1),data=got,land_points=nland))
    axs[-1].set_xlim(-W_,W_)
    axs[-1].set_xticks(np.arange(-20,21,5)); axs[-1].set_xticklabels([fmt(t0+x)[:8] for x in np.arange(-20,21,5)],fontsize=6)
    axs[-1].set_xlabel(f'implied impact time, UTC 8 March 2014 (each record shifted back by its travel time at 1.482 km/s)')
    fig.suptitle(f"Candidate {k}: {cd['title']}\nimpact point {abs(L):.2f} S {Lo:.2f} E at {fmt(t0)[:8]} UTC - every panel aligned to that source time",x=0.01,ha='left',fontsize=8)
    foot=("Plain words: Each panel is one hydrophone. We moved each record back by the time sound needs to travel from the impact point, so a real impact would line up at the orange line in every panel. "
          "The orange band is the timing uncertainty. Green dashes are the detections that define this candidate. Grey text means we hold no data for that time.\n"
          f"Technical: arc line = run J D0' mean impact longitude per latitude; locus fitted by least squares to the member arrivals (residuals {', '.join(f'{x:+.0f}' for x in cd['resid'])} s). "
          "Band 0.006 km/s speed s.d.; IMOS 5-40 Hz 4th-order Butterworth, calibrated with the module gains and clock correction; Kadri traces are digitised plots (~14.5 points/s, his 5 Hz high-pass + 2-40 Hz band-pass), envelope only; "
          "Royer strips are digitised spectrogram 5-40 Hz levels (light dashes at H01W-2: shifted 16 s for the figure-table offset). Exploratory; C1, C2.")
    fig.text(0.01,0.005,'\n'.join(textwrap.fill(p,175) for p in foot.split('\n')),fontsize=5.3,va='top')
    fig.subplots_adjust(hspace=0.55,top=0.94,bottom=0.06)
    fn=f'cand/cand{k}_1_raw_records.png'; fig.savefig(fn,dpi=220,bbox_inches='tight'); plt.close(fig)
    chart1_notes[k]=notes; return fn
fnA=chart1('A'); print(fnA); print(pd.DataFrame(chart1_notes['A']).to_string())