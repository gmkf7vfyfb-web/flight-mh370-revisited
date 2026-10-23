plt.close('all')
fig=plt.figure(figsize=(7.2,7.4))
gs=fig.add_gridspec(2,2,height_ratios=[1.35,1],width_ratios=[1,0.42],hspace=0.42,wspace=0.05)
ax=fig.add_subplot(gs[0,0]); lax=fig.add_subplot(gs[0,1]); lax.axis('off')
pc_=ax.pcolormesh(tb/60,lb,np.log10(Hm.T),cmap='Greys',vmin=-6,vmax=-1.5,shading='flat',rasterized=True)
handles=[]
for v,(mk,c,lab) in styles.items():
    g=plotted[plotted.verdict==v]; pub=g.id.str.startswith('K-')
    if (~pub).any(): handles.append(ax.scatter(g.tm[~pub],g.implied_lat[~pub],marker=mk,s=24,facecolor=c,edgecolor='k',lw=0.3,label=lab+'\n(module search, two or three sites)',zorder=3))
    if pub.any(): handles.append(ax.scatter(g.tm[pub],g.implied_lat[pub],marker=mk,s=28,facecolor='white',edgecolor=c,lw=1.1,label=lab+'\n(Kadri Table 1 time and bearing)',zorder=3))
ax.axvline(hms('00:19:29')/60,color='k',lw=0.6,ls=':'); ax.text(hms('00:19:50')/60,-20.4,'last log-on 00:19:29',fontsize=6,va='top')
ax.set_xlim(19,50); ax.set_ylim(-41,-20)
ax.set_xticks([20,25,30,35,40,45,50]); ax.set_xticklabels(['00:20','00:25','00:30','00:35','00:40','00:45','00:50'])
ax.set_xlabel('implied impact time, UTC 8 March 2014'); ax.set_ylabel('implied impact latitude on the 7th arc (deg)')
ax.set_title('Where and when each candidate puts the impact (grey = impact prior)',loc='left')
lax.legend(handles=handles,loc='upper left',fontsize=6,frameon=False,labelspacing=0.9)
cax=lax.inset_axes([0.05,0.06,0.8,0.04]); cb=fig.colorbar(pc_,cax=cax,orientation='horizontal'); cb.set_label('impact prior, log10 share per cell',fontsize=6); cb.ax.tick_params(labelsize=6)
ax=fig.add_subplot(gs[1,:])
for i,v in enumerate(order):
    g=B[B.verdict==v]; mk,c,_=styles[v]
    ax.scatter(g.x, np.full(len(g),i)+(np.linspace(-0.18,0.18,len(g)) if len(g)>1 else 0), marker=mk,s=22,facecolor=c,edgecolor='k',lw=0.3,zorder=3)
ax.scatter(h8x, np.full(len(h8x),3)+np.random.default_rng(1).uniform(-0.18,0.18,len(h8x)),marker='^',s=13,facecolor='#c7c7c7',edgecolor='k',lw=0.2,zorder=3)
ax.set_yticks(range(4)); ax.set_yticklabels(['feasible module sets','sets with a known other event','overnight headline pairs (airgun)','Diego Garcia single detections (airgun)'],fontsize=6)
ax.set_xscale('log'); ax.set_xlim(0.3,3e3); ax.set_ylim(3.6,-0.9)
ax.axvspan(0.3,10,color='#d9ead3',alpha=0.6,lw=0); ax.axvspan(10,100,color='#fff2cc',alpha=0.7,lw=0); ax.axvspan(100,3e3,color='#f4cccc',alpha=0.6,lw=0)
ax.axvline(1,color='k',lw=0.7); ax.axvline(1/ANCH,color='k',lw=0.7,ls='--')
for x,t in [(2.5,'feasible (up to 10x)'),(31,'strained (10-100x)'),(250,'not feasible'),]: ax.text(x,-0.6,t,fontsize=6,ha='center')
ax.text(1.07,3.45,'F-35A value',fontsize=6); ax.text(1/ANCH*1.08,3.45,'all impact energy\nbecomes sound',fontsize=6,va='bottom')
ax.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v,p: f"{v:g}"))
ax.set_xlabel('coupling needed to match the recorded level (multiple of the F-35A value, at 12 GJ impact energy)')
ax.set_title('How much of the impact energy each signal needs to become sound',loc='left')
panel_letter(fig.axes[0],'a'); panel_letter(ax,'b')
fig.savefig('candidates_location_time_coupling.png',dpi=300,bbox_inches='tight')
r_=fig.canvas.get_renderer()
texts=[(t,t.get_window_extent(r_)) for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
tick=set(); [tick.update(a.get_xticklabels()+a.get_yticklabels()) for a in fig.axes]
ov=[(a.get_text()[:25],b.get_text()[:25]) for i,(a,ba) in enumerate(texts) for b,bb in texts[i+1:] if ba.overlaps(bb) and not (a in tick and b in tick)]
print(ov)