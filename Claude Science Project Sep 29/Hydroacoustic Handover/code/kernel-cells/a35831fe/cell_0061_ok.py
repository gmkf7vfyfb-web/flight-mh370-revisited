import matplotlib as mpl, matplotlib.pyplot as plt
apply_figure_style(sizes=(8,7,6))
fig,axs=plt.subplots(1,2,figsize=(7.2,3.6),gridspec_kw=dict(width_ratios=[1.35,1],wspace=0.32))
ax=axs[0]
tb=np.arange(hms('00:19:00'),hms('00:50:00'),30); lb=np.arange(-41,-19.5,0.25)
Hh,_,_=np.histogram2d(tu[m],lat[m],bins=[tb,lb],weights=wall[m]); Hh=Hh/Hh.sum()
Hm=np.ma.masked_where(Hh<=0,Hh)
pc_=ax.pcolormesh((tb-hms('00:00:00'))/60,lb,np.log10(Hm.T),cmap='Greys',vmin=-6,vmax=-1.5,shading='flat',rasterized=True)
def tmin(x): return hms(x)/60 if isinstance(x,str) and x[:2].isdigit() else np.nan
styles={'FEASIBLE (not supported above chance)':('o','#1f77b4','feasible, not above chance'),
        'WEAK: location at north edge of prior':('s','#9467bd','feasible time, place at north edge of prior'),
        'LIKELY KNOWN OTHER EVENT':('X','#ff7f0e','time matches a Royer-located event'),
        'NOT MH370: airgun artefact':('^','#7f7f7f','Diego Garcia airgun shot')}
plotted=R[R.implied_lat.notna()&R.verdict.isin(styles)].copy()
plotted['tm']=plotted.implied_impact.map(lambda x: tmin(str(x)[:8]))
for v,(mk,c,lab) in styles.items():
    g=plotted[plotted.verdict==v]
    pub=g.id.str.startswith('K-')
    ax.scatter(g.tm[~pub],g.implied_lat[~pub],marker=mk,s=22,facecolor=c,edgecolor='k',lw=0.3,label=lab+' (module search)' if (~pub).any() else None,zorder=3)
    ax.scatter(g.tm[pub],g.implied_lat[pub],marker=mk,s=26,facecolor='white',edgecolor=c,lw=1.1,label=lab+' (Kadri Table 1, bearing)' if pub.any() else None,zorder=3)
ax.axvline(hms('00:19:29')/60,color='k',lw=0.6,ls=':'); ax.text(hms('00:19:45')/60,-20.6,'last log-on 00:19:29',fontsize=6,va='top')
ax.set_xlim(19,50); ax.set_ylim(-41,-20)
ax.set_xticks([20,25,30,35,40,45,50]); ax.set_xticklabels(['00:20','00:25','00:30','00:35','00:40','00:45','00:50'])
ax.set_xlabel('implied impact time, UTC 8 March 2014'); ax.set_ylabel('implied impact latitude on the 7th arc (deg)')
ax.set_title('Where and when each candidate puts the impact',loc='left')
cb=fig.colorbar(pc_,ax=ax,fraction=0.04,pad=0.02); cb.set_label('impact prior, log10 share per cell',fontsize=6); cb.ax.tick_params(labelsize=6)
ax.legend(loc='lower right',fontsize=5.2,frameon=False,handletextpad=0.3,borderaxespad=0.2)
# panel b: coupling
ax=axs[1]
rowsb=[]
for _,r in R.iterrows():
    et=str(r.energy_test)
    if 'x F-35A' in et: rowsb.append((r.id, float(et.split('x')[0]), r.verdict))
B=pd.DataFrame(rowsb,columns=['id','x','verdict'])
# add H01W singles (text/caption) already in R; add H08S singles as group
h8x=s[s.rx=='H08S'].eta_min_xF35A.values
order=['FEASIBLE (not supported above chance)','LIKELY KNOWN OTHER EVENT','NOT MH370: airgun artefact']
ylab={'FEASIBLE (not supported above chance)':'feasible module pairs\nand triple','LIKELY KNOWN OTHER EVENT':'known other\nevents','NOT MH370: airgun artefact':'overnight headline\npairs (airgun)'}
for i,v in enumerate(order):
    g=B[B.verdict==v]; mk,c,_=styles[v]
    ax.scatter(g.x, np.full(len(g),i)+np.linspace(-0.15,0.15,len(g)) if len(g)>1 else [i], marker=mk,s=20,facecolor=c,edgecolor='k',lw=0.3,zorder=3)
ax.scatter(h8x, np.full(len(h8x),3)+np.random.default_rng(1).uniform(-0.15,0.15,len(h8x)),marker='^',s=12,facecolor='#c7c7c7',edgecolor='k',lw=0.2,zorder=3)
ax.set_yticks(range(4)); ax.set_yticklabels([ylab[v] for v in order]+['Diego Garcia single\ndetections (airgun)'],fontsize=6)
ax.set_xscale('log'); ax.set_xlim(0.3,3e3)
ax.axvspan(0.3,10,color='#d9ead3',alpha=0.6,lw=0); ax.axvspan(10,100,color='#fff2cc',alpha=0.7,lw=0); ax.axvspan(100,3e3,color='#f4cccc',alpha=0.6,lw=0)
ax.axvline(1,color='k',lw=0.7); ax.text(1.08,3.45,'F-35A',fontsize=6)
ax.axvline(1/ANCH,color='k',lw=0.7,ls='--'); ax.text(1/ANCH*0.55,3.45,'all\nenergy',fontsize=6,ha='right',va='center')
for x,t in [(2.2,'feasible'),(30,'strained'),(400,'not feasible')]: ax.text(x,-0.62,t,fontsize=6,ha='center')
ax.set_ylim(-0.8,3.7); ax.invert_yaxis()
ax.set_xlabel('coupling needed to match the recorded level\n(multiple of the F-35A value, at 12 GJ impact energy)')
ax.set_title('Loudness each signal needs',loc='left')
ax.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v,p: f"{v:g}"))
panel_letter(axs[0],'a'); panel_letter(axs[1],'b')
fig.savefig('candidates_location_time_coupling.png',dpi=300,bbox_inches='tight')
r_=fig.canvas.get_renderer()
texts=[(t,t.get_window_extent(r_)) for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
ov=[(a.get_text()[:20],b.get_text()[:20]) for i,(a,ba) in enumerate(texts) for b,bb in texts[i+1:] if ba.overlaps(bb)]
print(ov[:10]); print(B.verdict.value_counts())