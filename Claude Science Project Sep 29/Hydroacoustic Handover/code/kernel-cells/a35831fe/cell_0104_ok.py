RXN={'H01W':'Cape Leeuwin\nH01W','H08S':'Diego Garcia S\nH08S','3315':'Perth Canyon\n3315','3376':'Perth Canyon\n3376','3274':'Portland\n3274','3275':'Portland\n3275'}
ecol={'1e-4':'#c6dbef','old value 2.1e-4 (wrong)':'#ffffff','1e-3':'#6baed6','F-35A 2.26e-3':'#08519c','1e-2':'#9ecae1'}
order_e=['1e-4','old value 2.1e-4 (wrong)','1e-3','F-35A 2.26e-3','1e-2']
def chart4(k):
    cd=CANDS[k]; lv=lev[k]
    fig,ax=plt.subplots(figsize=(7.2,4.2))
    wb=0.15; x0=np.arange(len(RX4))
    for j,lab in enumerate(order_e):
        eta=dict(ETAS)[lab]; q=np.array([np.quantile(lv['base'][r]+10*np.log10(eta),[.05,.5,.95]) for r in RX4])
        xs=x0+(j-2)*wb
        ax.bar(xs,q[:,1]+40,bottom=-40,width=wb*0.92,color=ecol[lab],edgecolor='#08306b' if 'F-35A' in lab else ('#a50f15' if 'old' in lab else '#6b6b6b'),
               lw=1.2 if ('F-35A' in lab or 'old' in lab) else 0.4,hatch='////' if 'old' in lab else None,label=('coupling '+lab),zorder=2)
        ax.errorbar(xs,q[:,1],yerr=[q[:,1]-q[:,0],q[:,2]-q[:,1]],fmt='none',ecolor='k',elinewidth=0.6,capsize=1.5,zorder=3)
    for i,r in enumerate(RX4):
        ax.plot([i-0.42,i+0.42],[L50[r]]*2,color='#e6550d',lw=1.2,zorder=4)
        ax.fill_between([i-0.42,i+0.42],[L50[r]+4.0]*2,[L50[r]+9.5]*2,color='#fdae6b',alpha=0.5,lw=0,zorder=1)
        if any(rr==r for rr,_ in cd['arr']): ax.text(i,52,'member',ha='center',fontsize=6,color='#2ca02c',fontweight='bold')
    ax.axhline(0,color='k',lw=0.8); ax.text(len(RX4)-0.45,0.8,'noise median',fontsize=6,ha='right')
    ax.set_xticks(x0); ax.set_xticklabels([RXN[r] for r in RX4],fontsize=6.5)
    ax.set_ylim(-40,56); ax.set_ylabel('predicted signal-to-noise ratio, dB\n(5-40 Hz; 0 = station noise median)')
    ax.set_title(f"Candidate {k}: predicted loudness at each station for an impact at {abs(cd['lat']):.2f} S {cd['lon']:.2f} E, {fmt(cd['t0'])[:8]}",loc='left',fontsize=7.5)
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    h,l=ax.get_legend_handles_labels()
    h+= [Line2D([0],[0],color='#e6550d',lw=1.2),Patch(color='#fdae6b',alpha=0.5)]
    l+= ['detector 50 % level, model signal','50 % level on a real arrival (+4 to +9.5 dB)']
    ax.legend(h,l,fontsize=5.6,frameon=False,ncol=4,loc='upper left',bbox_to_anchor=(0,-0.13))
    foot=(f"Plain words: Bars show how loud an impact at this place would be at each station, for five values of the share of impact energy that becomes sound. The dark bar is the F-35A value. "
          "The hatched bar is the old value used last night, which is wrong. Above the orange line the detector finds a model signal half the time; on a real arrival it needs the orange band.\n"
          f"Technical: run J impacts within 0.5 deg latitude and 10 min of the implied impact time ({lv['n']:,} rows, options averaged, 20,000 weighted draws; E q05/q50/q95 = {lv['Eq'][0]/1e9:.2f}/{lv['Eq'][1]/1e9:.2f}/{lv['Eq'][2]/1e9:.2f} GJ). "
          "Bars = median, whiskers = 5-95 %. Module chain (block 11 Machinery): TL grid offset 0, 10 m source, RAM-corrected IMOS table, IMS raw KRAKEN minus imp500 RAM delta, one-pole f^-2 source, tau90. "
          "H01W/H08S noise is a substitute (IMOS noise shaped to Blackman medians) and includes the 4.8 dB triad gain; H08S ignores the airgun survey. M1b L50 at alpha 0.05 from block 7 (model-matched); penalty from Metz F-35A test. C1, C2.")
    fig.text(0.01,-0.2,'\n'.join(textwrap.fill(p,170) for p in foot.split('\n')),fontsize=5.3,va='top')
    fn=f'cand/cand{k}_4_predicted_level_vs_noise.png'; fig.savefig(fn,dpi=220,bbox_inches='tight'); plt.close(fig); return fn
files4={k:chart4(k) for k in CANDS}
print(files4['A'])