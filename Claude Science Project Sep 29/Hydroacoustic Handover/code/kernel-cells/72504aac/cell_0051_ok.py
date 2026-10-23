
from matplotlib.lines import Line2D
def chart1():
    fig=plt.figure(figsize=(10.5,8.4)); ax=fig.add_axes([0.065,0.385,0.92,0.565])
    ext=(48,146,-50,2); land(ax,ext)
    ax.scatter(slon[ci],slat[ci],s=0.6,c=C_CLOUD,alpha=0.25,lw=0,zorder=2,rasterized=True)
    m=(ARC_LAT>-41)&(ARC_LAT<-20); ax.plot(ARC_LON[m],ARC_LAT[m],color=C_ARC,lw=3.0,alpha=0.45,zorder=3,solid_capstyle='butt')
    ax.plot(ARC_LON,ARC_LAT,color=C_ARC,lw=0.8,ls='--',zorder=3)
    for r,(stt,lab) in STATUS.items():
        la,lo=path(r,G['lat'],G['lon'])
        if stt=='open': ax.plot(lo,la,color=C_OPEN if r not in('H01W','H08S') else C_G,lw=1.6 if r in('H01W','H08S') else 0.9,zorder=4)
        else: ax.plot(lo,la,color=C_BLOCK,lw=0.9,ls=(0,(4,3)),zorder=4)
        rl,ro=RX[r]; mk='^' if r.startswith('H') else 's'
        ax.scatter(ro,rl,marker=mk,s=46 if r.startswith('H') else 26,c=(C_G if r in('H01W','H08S') else (C_OPEN if stt=='open' else 'white')),
                   edgecolors=C_OPEN if stt=='open' else C_BLOCK,lw=1,zorder=6)
    for r in OHA:
        rl,ro=RX[r]; ax.scatter(ro,rl,marker='D',s=20,facecolors='white',edgecolors='#555555',lw=0.9,zorder=6)
        ax.annotate(r,(ro,rl),xytext=(4,-8),textcoords='offset points',fontsize=6,color='#555555')
    for b,c,ls,lw,dmax in [(57.0,C_KADRI,'-',1.4,1500),(306.18,C_KADRI,(0,(5,2)),1.4,2400),(274.84,C_T1,(0,(1,1.5)),1.4,2300)]:
        la,lo=ray('H01W',b,dmax); ax.plot(lo,la,color=c,ls=ls,lw=lw,zorder=5)
    ax.scatter(G['lon'],G['lat'],marker='*',s=220,c=C_G,edgecolors='white',lw=0.8,zorder=8)
    ax.annotate("Pair locus 33.6°S 94.5°E\nimpact 00:31:41 (implied)",(G['lon'],G['lat']),xytext=(-175,-12),textcoords='offset points',fontsize=7,color=C_G,
                arrowprops=dict(arrowstyle='-',color=C_G,lw=0.6))
    ax.scatter(LOCI['D']['lon'],LOCI['D']['lat'],marker='*',s=110,c=C_D,edgecolors='white',lw=0.6,zorder=7)
    ax.annotate("Kadri's preferred crossing\n25.8°S 101.4°E",(LOCI['D']['lon'],LOCI['D']['lat']),xytext=(-150,-2),textcoords='offset points',fontsize=7,color=C_D,
                arrowprops=dict(arrowstyle='-',color=C_D,lw=0.6))
    rl,ro=RX['H01W']; ax.annotate(f"Cape Leeuwin H01W, 00:52:04\nlocus at {G_AZ_H01W:.1f}°, {G_D_H01W:,.0f} km",(ro,rl),xytext=(-4,-26),textcoords='offset points',fontsize=7,color=C_G,ha='center')
    rl,ro=RX['H08S']; ax.annotate(f"Diego Garcia South H08S, 01:12:49\nlocus at {G_AZ_H08S:.1f}°, {G_D_H08S:,.0f} km",(ro,rl),xytext=(8,4),textcoords='offset points',fontsize=7,color=C_G)
    rl,ro=RX['H08N']; ax.annotate("H08N (blocked)",(ro,rl),xytext=(-6,6),textcoords='offset points',fontsize=6,color=C_BLOCK,ha='right')
    for r,dx,dy,ha in [('3315',6,6,'left'),('3376',6,-9,'left'),('3274',-4,8,'right'),('3275',-4,-11,'right'),('3250',6,3,'left')]:
        rl,ro=RX[r]; stt,lab=STATUS[r]; ax.annotate(lab+(' (blocked)' if stt=='blocked' else ''),(ro,rl),xytext=(dx,dy),textcoords='offset points',fontsize=6,color=C_OPEN if stt=='open' else C_BLOCK,ha=ha)
    la,lo=ray('H01W',57.0,1500); ax.annotate("57° (Kadri text, p. 9)",(lo[-1],la[-1]),xytext=(3,2),textcoords='offset points',fontsize=6.5,color=C_KADRI)
    la,lo=ray('H01W',306.18,2400); ax.annotate("306.18° (Kadri Table 1 caption)",(lo[-1],la[-1]),xytext=(4,2),textcoords='offset points',fontsize=6.5,color=C_KADRI,ha='left')
    la,lo=ray('H01W',274.84,2300); ax.annotate("274.84° (Table 1, 00:52:50)",(lo[-1],la[-1]),xytext=(-4,5),textcoords='offset points',fontsize=6.5,color=C_T1,ha='right')
    ax.set_xlim(ext[0],ext[1]); ax.set_ylim(ext[2],ext[3]); ax.set_aspect(1/np.cos(np.radians(25)))
    ax.set_xlabel('Longitude (°E)'); ax.set_ylabel('Latitude (°; south negative)')
    ax.set_title("The time difference between the two sounds points to 33.6°S, but no bearing Kadri published for 00:52 points there",loc='left',fontsize=8)
    H=[Line2D([],[],color=C_G,lw=1.6,label='path to the locus, the two stations of the pair'),Line2D([],[],color=C_OPEN,lw=0.9,label='path open (sound can reach the recorder)'),
       Line2D([],[],color=C_BLOCK,lw=0.9,ls=(0,(4,3)),label='path blocked (shallow ridge or shelf)'),
       Line2D([],[],color=C_KADRI,lw=1.4,label="Kadri's bearings for the 00:52 signal"),Line2D([],[],color=C_T1,lw=1.4,ls=(0,(1,1.5)),label='nearest Table 1 bearing (00:52:50)'),
       Line2D([],[],color=C_ARC,lw=3,alpha=0.45,label='7th arc; thick: span searched by the pair test, 41-20°S'),
       Line2D([],[],marker='o',ls='',ms=3,color=C_CLOUD,alpha=0.6,label='simulated impacts (25,000 weighted draws)'),
       Line2D([],[],marker='^',ls='',ms=6,mfc=C_OPEN,mec=C_OPEN,label='IMS hydrophone station'),Line2D([],[],marker='s',ls='',ms=5,mfc=C_OPEN,mec=C_OPEN,label='IMOS recorder (open symbol = blocked)'),
       Line2D([],[],marker='D',ls='',ms=4,mfc='white',mec='#555555',label='OHASISBIO site (not modelled; no recordings held)'),
       Line2D([],[],marker='*',ls='',ms=9,mfc=C_G,mec='white',label='arc point from the time difference of the pair')]
    fig.legend(handles=H,loc='upper left',bbox_to_anchor=(0.06,0.355),frameon=False,fontsize=6.5,ncol=3,columnspacing=1.5)
    ste=("The star is the point on the arc that the time difference of the two sounds gives. The lines show where sound can travel from that "
         "point to each recorder. Grey dashed lines are blocked by shallow sea floor. The orange and purple lines are the directions Kadri "
         "published from Cape Leeuwin; none goes to the star. "+PAIR_STE)
    tech=(PAIR_TECH+" Path status at the 33.5°S node (offset 0, 10 m source): IMS from the KRAKEN arc grid (run-j-tl-grid/tl_grid.csv.gz; H08N no propagating modes, "
          "track min depth 6 m); IMOS from the RAM-corrected table imos_tl_ram_arc.csv (3274/3275 open at 130-136 dB for 6.3-40 Hz, KRAKEN gives no modes; 3250 "
          "TL > 440 dB, shelf 12 m). OHASISBIO positions from Royer LDO-201608 Table 1. Impact cloud: run J waypoints stratum seeds 1-8 stride 6 + northern supplement "
          "(searches geometry/sample.npz, Kish ESS 110k), weights D0'. Bearings are WGS84 geodesics from the H01W triad centroid. Land: GEBCO 2026 at 0.05°. "+COMMON_TECH)
    footnotes(fig,ste,tech,width=205)
    return fig
fig=chart1(); save(fig,'chart1-geometry-pair-g'); print(bbox_check(fig))
