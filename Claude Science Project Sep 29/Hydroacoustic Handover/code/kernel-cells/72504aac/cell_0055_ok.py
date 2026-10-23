
def chart4():
    fig=plt.figure(figsize=(8.2,8.6)); ax=fig.add_axes([0.09,0.37,0.88,0.57])
    land(ax,ext4); draw_hpd(ax,xc4,yc4,H4)
    ax.plot(ARC_LON,ARC_LAT,color=C_ARC,lw=1.0,ls='--',zorder=3)
    rl,ro=RX['H01W']
    off={'Pair':(-45,45,'right'),'Table 1, 00:52:50':(10,22,'left'),"Kadri's":(-14,12,'center'),'Table 1, 00:39:02':(45,-48,'left'),'A:':(-60,-6,'right'),'B:':(-45,-28,'right')}
    for lab,b,c,ls,lw in RAYS:
        if lab.startswith('Pair'): la,lo,R=G['lat'],G['lon'],G_D_H01W
        else: la,lo,_,R=ray_arc_cross('H01W',b)
        L,O=ray('H01W',b,2600); ax.plot(O,L,color=c,ls=ls,lw=lw,zorder=4)
        ax.scatter(lo,la,s=22,c=c,edgecolors='white',lw=0.5,zorder=6)
        k=[kk for kk in off if lab.startswith(kk)][0]; dx,dy,ha=off[k]
        ax.annotate(f"{lab}\n{b:.2f}°, R = {R:,.0f} km" if not lab.startswith('Pair') else f"{lab}\n{b:.1f}°, R = {R:,.0f} km",(lo,la),xytext=(dx,dy),textcoords='offset points',fontsize=6.5,color=c,ha=ha,
                    arrowprops=dict(arrowstyle='-',color=c,lw=0.5))
    L,O=ray('H01W',57.0,420); ax.plot(O,L,color=C_KADRI,lw=1.4,zorder=5)
    ax.annotate("Kadri's 00:52 bearing, text p. 9: 57°\n(towards land; never meets the arc)",(O[len(O)//3],L[len(L)//3]),xytext=(-40,-40),textcoords='offset points',fontsize=6.5,color=C_KADRI,ha='right',
                arrowprops=dict(arrowstyle='-',color=C_KADRI,lw=0.5))
    L8,O8=path('H08S',G['lat'],G['lon']); ax.plot(O8,L8,color=C_G,lw=1.2,ls=(0,(6,2)),zorder=4)
    j=np.argmin(np.abs(L8+22)); ax.annotate(f"from Diego Garcia South H08S\n{G_AZ_H08S:.1f}°, {G_D_H08S:,.0f} km",(O8[j],L8[j]),xytext=(8,0),textcoords='offset points',fontsize=6.5,color=C_G)
    ax.scatter(G['lon'],G['lat'],marker='*',s=200,c=C_G,edgecolors='white',lw=0.8,zorder=8)
    ax.scatter(ro,rl,marker='^',s=60,c=C_G,zorder=8); ax.annotate('Cape Leeuwin H01W',(ro,rl),xytext=(-4,-14),textcoords='offset points',fontsize=7,ha='right',color=C_G)
    ax.scatter(LOCI['D']['lon'],LOCI['D']['lat'],marker='*',s=100,c=C_D,edgecolors='white',lw=0.6,zorder=7)
    ax.annotate("D: Kadri's preferred crossing",(LOCI['D']['lon'],LOCI['D']['lat']),xytext=(8,-4),textcoords='offset points',fontsize=6.5,color=C_D)
    ax.set_xlim(ext4[0],ext4[1]); ax.set_ylim(ext4[2],ext4[3]); ax.set_aspect(1/np.cos(np.radians(30)))
    ax.set_xlabel('Longitude (°E)'); ax.set_ylabel('Latitude (°; south negative)')
    ax.set_title("Only the bearing from the time difference reaches 33.6°S;\nKadri's two bearings for 00:52 cross the arc near 25.8°S or not at all",loc='left',fontsize=8)
    from matplotlib.patches import Patch
    H=[Patch(fc=HPD_FILL[2],label='50 % highest-density region, simulated impacts'),Patch(fc=HPD_FILL[1],label='90 %'),Patch(fc=HPD_FILL[0],label='99 %'),
       Line2D([],[],color=C_ARC,ls='--',label='7th arc'),Line2D([],[],marker='*',ls='',ms=10,mfc=C_G,mec='white',label='pair locus 33.6°S 94.5°E (implied impact 00:31:41)'),
       Line2D([],[],marker='o',ls='',ms=4,mfc='#8c8c8c',mec='white',label='arc crossing of a bearing; R = range from Cape Leeuwin')]
    ax.legend(handles=H,loc='lower right',frameon=False,fontsize=6.5)
    ste=("Each line is a sound direction from Cape Leeuwin. The dot is where the line meets the arc, and R is the distance. The thick blue line goes "
         "to the place that the time difference of the pair gives. Kadri's two published directions for the 00:52 signal (57° and 306.18°) do not "
         "go there. The grey lines are other Table 1 directions that the earlier chart used; the 00:39:02 direction meets the arc 0.2° from the star, 13 minutes earlier. "+PAIR_STE)
    tech=(PAIR_TECH+" Rays are WGS84 geodesics from the H01W triad centroid; R is the geodesic range to the nearest approach to the drawn arc "
          "(composer small-circle fit to run J 00:19:29 positions); for the pair, R is the range to the locus on the module's TL-grid arc. Table 1 rows from searches named/table1_verdicts.csv (bearings DIGITISED from Kadri 2024 "
          "Table 1). HPD: run J impacts (geometry/sample.npz, waypoints seeds 1-8 stride 6 + northern supplement, Kish ESS 110k), D0', 0.1° bins, "
          "Gaussian display smoothing sigma 25 km. Locus C of the earlier chart is not legible in the original and is not redrawn. "+COMMON_TECH)
    footnotes(fig,ste,tech,width=160)
    return fig
fig=chart4(); save(fig,'chart4-bearings-pair-g')
