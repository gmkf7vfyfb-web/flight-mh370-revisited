H2,xe,ye=np.histogram2d(RT[:,:,1].ravel(),RT[:,:,0].ravel(),bins=[np.arange(70,121,0.5),np.arange(-46,8,0.5)])
def chart3(k):
    cd=CANDS[k]; S_=sel[k]; rng_=np.random.default_rng(11); pick=rng_.choice(S_,size=min(300,len(S_)),replace=False)
    fig,ax=plt.subplots(figsize=(7.2,7.0))
    ax.pcolormesh(xe,ye,np.ma.masked_equal(H2.T,0),cmap='Greys',norm=mpl.colors.LogNorm(vmin=1,vmax=H2.max()),alpha=0.35,rasterized=True)
    ax.contourf(cl_lon,cl_lat,ELV,levels=[0,10000],colors=['#d9d9d9']); ax.contour(cl_lon,cl_lat,ELV,levels=[0],colors=['#737373'],linewidths=0.4)
    for i in pick:
        ax.plot(RT[i,:,1],RT[i,:,0],color='#2171b5',lw=0.35,alpha=0.25)
        ax.plot([RT[i,-1,1],EXT[i,1]],[RT[i,-1,0],EXT[i,0]],color='#2171b5',lw=0.35,alpha=0.25,ls=':')
    ax.plot(flo,fla,color='#e6550d',lw=0.8,ls=(0,(5,2)))
    ax.scatter([cd['lon']],[cd['lat']],marker='*',s=200,color='#e6550d',edgecolor='k',zorder=6)
    for r_,lab_ in [('H01W','Cape Leeuwin'),('3315','Perth Canyon'),('H08S','Diego Garcia')]:
        ax.scatter([rx[r_][1]],[rx[r_][0]],marker='v',s=22,color='k',zorder=6); ax.text(rx[r_][1]+0.4,rx[r_][0],lab_,fontsize=6)
    ax.set_xlim(80,118); ax.set_ylim(-42,0); ax.set_aspect(1/np.cos(np.radians(21)))
    ax.set_xlabel('longitude (deg E)'); ax.set_ylabel('latitude (deg)')
    ax.set_title(f"Candidate {k}: posterior flight routes that reach within 120 km of {abs(cd['lat']):.2f} S {cd['lon']:.2f} E by 00:19:29\n"
                 f"{len(S_):,} of {len(RT):,} routes ({100*len(S_)/len(RT):.1f} %); 300 drawn",loc='left',fontsize=7.5)
    h=[Line2D([0],[0],color='#2171b5',lw=1,label='route 18:01:49-00:11:49 (core posterior sample)'),Line2D([0],[0],color='#2171b5',lw=1,ls=':',label='straight extension 00:11:49-00:19:29 (this chart only)'),
       Patch(color='#969696',alpha=0.5,label='density of all 48,000 routes'),Line2D([0],[0],color='#e6550d',ls=(0,(5,2)),label='mean impact line (run J)'),
       Line2D([0],[0],marker='*',ls='',ms=10,color='#e6550d',label='candidate impact point'),Line2D([0],[0],marker='v',ls='',color='k',label='hydrophone sites')]
    ax.legend(handles=h,fontsize=5.8,loc='lower left',framealpha=0.85)
    foot=("Plain words: Each blue line is one possible flight path from the satellite-data analysis. We show only the paths that end near this candidate. The dotted end is a straight-line guess for the last 8 minutes.\n"
          "Technical: core run J, waypoints stratum (core share 0.998), 24 seeds x 2,000 routes systematically resampled by weight (filter.rs) at 600 s steps from 18:01:49; routes are conditioned on BTO/BFO only, "
          "not on the end of flight, 00:19 data, drift, searched areas or Pleiades. Selection: last leg extended 460 s at its own speed, end within 120 km of the candidate point. Other strata (0.002) not drawn.")
    fig.text(0.01,0.02,'\n'.join(textwrap.fill(p,170) for p in foot.split('\n')),fontsize=5.3,va='top')
    fn=f'cand/cand{k}_3_routes_map.png'; fig.savefig(fn,dpi=200,bbox_inches='tight'); plt.close(fig); return fn
files3={k:chart3(k) for k in CANDS}; print(files3['B'])