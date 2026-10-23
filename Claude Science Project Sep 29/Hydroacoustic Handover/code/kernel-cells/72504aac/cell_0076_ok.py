
SEL=[('hw',C_HW,'-','highest weight within 150 km'),('tc',C_TC,'-','highest weight within 150 km and impact within 2 min of 00:31:41'),('cl',C_CL,(0,(4,2)),'closest to G (any non-zero weight)')]
def chart6():
    fig=plt.figure(figsize=(10.5,7.6)); a1=fig.add_axes([0.06,0.40,0.40,0.52]); a2=fig.add_axes([0.53,0.40,0.44,0.52])
    e1=(76,116,-42,10); land(a1,e1); a1.plot(ARC_LON,ARC_LAT,color=C_ARC,ls='--',lw=0.9,zorder=3)
    e2=(91.0,98.0,-36.6,-30.6); land(a2,e2); a2.plot(ARC_LON,ARC_LAT,color=C_ARC,ls='--',lw=0.9,zorder=3)
    cl_,co_=circle(G['lat'],G['lon'],150); a2.plot(co_,cl_,color=C_G,lw=0.7,ls=':',zorder=3)
    for key,c,ls,lab in SEL:
        draw_traj(a1,TJ[key],c,lw=1.3,ls=ls); draw_traj(a2,TJ[key],c,lw=1.3,ls=ls,zoom=True)
    for ax,s in [(a1,170),(a2,220)]:
        ax.scatter(G['lon'],G['lat'],marker='*',s=s,c=C_G,edgecolors='white',lw=0.8,zorder=8)
    a1.scatter(LOCI['D']['lon'],LOCI['D']['lat'],marker='*',s=90,c=C_D,edgecolors='white',lw=0.6,zorder=8); a1.annotate('D',(LOCI['D']['lon'],LOCI['D']['lat']),xytext=(6,-2),textcoords='offset points',color=C_D,fontsize=7)
    a1.annotate('G',(G['lon'],G['lat']),xytext=(8,-4),textcoords='offset points',color=C_G,fontsize=7)
    a2.annotate("G: pair locus, implied impact 00:31:41",(G['lon'],G['lat']),xytext=(25,45),textcoords='offset points',fontsize=6.5,color=C_G,arrowprops=dict(arrowstyle='-',color=C_G,lw=0.5))
    a1.set_xlim(e1[0],e1[1]); a1.set_ylim(e1[2],e1[3]); a1.set_aspect(1/np.cos(np.radians(15))); a2.set_xlim(e2[0],e2[1]); a2.set_ylim(e2[2],e2[3]); a2.set_aspect(1/np.cos(np.radians(33.5)))
    a1.set_title('Stored routes after 18:22 UTC',loc='left',fontsize=8); a2.set_title('Neighbourhood of the pair locus G',loc='left',fontsize=8)
    a1.set_xlabel('Longitude (°E)'); a2.set_xlabel('Longitude (°E)'); a1.set_ylabel('Latitude (°; south negative)')
    H=[Line2D([],[],color=c,ls=ls,lw=1.3,label=lab) for _,c,ls,lab in SEL]+[Line2D([],[],marker='o',ls='',ms=4,color='#555555',label='route at 00:10:59'),
       Line2D([],[],marker='s',ls='',ms=4,mfc='white',mec='#555555',label='start of the final descent'),Line2D([],[],marker='X',ls='',ms=6,color='#555555',label='simulated impact'),
       Line2D([],[],color=C_G,ls=':',lw=0.7,label='150 km from G')]
    fig.legend(handles=H,loc='upper left',bbox_to_anchor=(0.06,0.355),ncol=3,frameon=False,fontsize=6.5)
    lines=[]
    for key,c,ls,lab in SEL:
        T=TJ[key]; r=T['row']
        lines.append((c,f"{lab}: {r.d:.0f} km from G; impact {hms(T0+r.t_impact_s)} ({(r.t_impact_s-tG)/60:+.0f} min against 00:31:41); final descent from {hms(T0+r.t_takeover_s)}, "
                         f"max {r.max_descent_rate_fpm:,.0f} ft/min; family {FAMLAB[int(r.family4_code)].split(' (')[0]}; weight share {r.share:.1e}; seed {T['k']}, route {T['j']}"))
    y=0.29
    for c,s in lines: fig.text(0.06,y,s,fontsize=6.3,color=c); y-=0.022
    fig.text(0.06,0.985,"Near the pair locus the stored trajectories mostly hit the sea earlier than the pair implies; 18 % of the nearby weight falls within 2 min of 00:31:41",fontsize=8,va='top')
    ste=("Three stored flight paths from the simulation are shown. Orange has the highest weight within 150 km of G. Green has the highest weight among those that also hit the sea "
         "within 2 minutes of the time the pair gives. Purple is the closest to G, but its weight is almost zero. The flight paths and the impacts are linked by position at 00:11, not by a direct record. "
         "These are stored samples; they were not fitted to the sounds. "+PAIR_STE)
    tech=(PAIR_TECH+f" Within 150 km of G: {len(NR):,} end-of-flight rows (24 waypoints seeds), mass {W150TOT/WTOT:.3f} of the D0' p 0.5 waypoints-stratum total; weighted impact-time quantiles 5/50/95 % "
          "00:20:31 / 00:31:21 / 00:45:25; share with |t - 00:31:41| < 120 s = 0.181. Family shares within 150 km: A1 0.13, A2 0.28, B 0.59. Routes: core run J routes.npy (2,000 per seed, every 600 s from 18:01:49), "
          "joined to end-of-flight rows by POSITION at 00:10:59 (distances: "+', '.join(f"{TJ[k]['dd']:.1f}" for k,_,_,_ in SEL)+" km); the routes carry no row identity. "
          "Weights: run_j_windows.ln_weights(D0') x p_factor(0.5). "+COMMON_TECH)
    footnotes(fig,ste,tech,width=205)
    return fig
fig=chart6(); save(fig,'chart6-neighbourhood-pair-g')
