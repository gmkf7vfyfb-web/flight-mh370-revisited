
from scipy.ndimage import gaussian_filter
def hpd_grid(lat,lon,w,ext,step=0.1,sig_km=25):
    lo0,lo1,la0,la1=ext; xe=np.arange(lo0,lo1+step,step); ye=np.arange(la0,la1+step,step)
    H,_,_=np.histogram2d(lat,lon,bins=[ye,xe],weights=w); H=gaussian_filter(H,[sig_km/111/step, sig_km/111/step/np.cos(np.radians(33))])
    return 0.5*(xe[1:]+xe[:-1]),0.5*(ye[1:]+ye[:-1]),H
def hpd_levels(H,ps):
    v=np.sort(H.ravel())[::-1]; c=np.cumsum(v)/v.sum(); return [v[np.searchsorted(c,p)] for p in ps]
HPD_FILL=['#dbe6f2','#9fbbd9','#4f79ad']
def draw_hpd(ax,xc,yc,H,ps=(0.99,0.9,0.5),alpha=1):
    lv=hpd_levels(H,ps); ax.contourf(xc,yc,H,levels=[lv[0],lv[1],lv[2],H.max()*1.01],colors=HPD_FILL,alpha=alpha,zorder=2)
    ax.contour(xc,yc,H,levels=lv,colors=['#4f79ad'],linewidths=[0.5,0.6,0.7],linestyles=[':','--','-'],zorder=2)
ext4=(82,117,-43,-15)
xc4,yc4,H4=hpd_grid(slat,slon,sw,ext4)
RAYS=[('Pair locus bearing (time difference)',G_AZ_H01W,C_G,'-',2.0),('Table 1, 00:52:50',274.84,C_T1,'-',1.2),
      ("Kadri's 00:52 bearing, Table 1 caption",306.18,C_KADRI,'--',1.4),('Table 1, 00:39:02',268.24,'#8c8c8c','-',0.9),
      ('A: Table 1, 00:49:58',260.41,'#8c8c8c','-',0.9),('B: Table 1, 00:53:31',257.58,'#8c8c8c','-',0.9)]
def chart4():
    fig=plt.figure(figsize=(9.5,8.0)); ax=fig.add_axes([0.08,0.36,0.86,0.58])
    land(ax,ext4); draw_hpd(ax,xc4,yc4,H4)
    ax.plot(ARC_LON,ARC_LAT,color=C_ARC,lw=1.0,ls='--',zorder=3)
    rl,ro=RX['H01W']
    for lab,b,c,ls,lw in RAYS:
        la,lo,dk,R=ray_arc_cross('H01W',b); L,O=ray('H01W',b,2600); ax.plot(O,L,color=c,ls=ls,lw=lw,zorder=4)
        ax.scatter(lo,la,s=22,c=c,edgecolors='white',lw=0.5,zorder=6)
        off={'Pair':(-20,-26),'Table 1, 00:52:50':(-10,12),"Kadri's":(-14,10),'Table 1, 00:39:02':(-80,14),'A:':(-95,-14),'B:':(-60,-30)}
        k=[kk for kk in off if lab.startswith(kk)][0]
        ax.annotate(f"{lab}\n{b:.2f}°, R = {R:,.0f} km",(lo,la),xytext=off[k],textcoords='offset points',fontsize=6.5,color=c,ha='right' if off[k][0]<-30 else 'center',
                    arrowprops=dict(arrowstyle='-',color=c,lw=0.5))
    L,O=ray('H01W',57.0,900); ax.plot(O,L,color=C_KADRI,lw=1.4,zorder=4)
    ax.annotate("Kadri's 00:52 bearing, text p. 9: 57°\n(points to land; never meets the arc)",(O[-1],L[-1]),xytext=(-6,4),textcoords='offset points',fontsize=6.5,color=C_KADRI,ha='right')
    L8,O8=path('H08S',G['lat'],G['lon']); ax.plot(O8,L8,color=C_G,lw=1.2,ls=(0,(6,2)),zorder=4)
    ax.annotate(f"from Diego Garcia South H08S\n{G_AZ_H08S:.1f}°, {G_D_H08S:,.0f} km",(O8[np.argmin(np.abs(L8+18))],-18),xytext=(8,0),textcoords='offset points',fontsize=6.5,color=C_G)
    ax.scatter(G['lon'],G['lat'],marker='*',s=200,c=C_G,edgecolors='white',lw=0.8,zorder=8)
    ax.scatter(ro,rl,marker='^',s=60,c=C_G,zorder=8); ax.annotate('Cape Leeuwin H01W',(ro,rl),xytext=(-4,-14),textcoords='offset points',fontsize=7,ha='right',color=C_G)
    ax.scatter(LOCI['D']['lon'],LOCI['D']['lat'],marker='*',s=100,c=C_D,edgecolors='white',lw=0.6,zorder=7)
    ax.annotate("D: Kadri's preferred crossing",(LOCI['D']['lon'],LOCI['D']['lat']),xytext=(8,-4),textcoords='offset points',fontsize=6.5,color=C_D)
    ax.set_xlim(ext4[0],ext4[1]); ax.set_ylim(ext4[2],ext4[3]); ax.set_aspect(1/np.cos(np.radians(30)))
    ax.set_xlabel('Longitude (°E)'); ax.set_ylabel('Latitude (°; south negative)')
    ax.set_title("Only the bearing from the time difference reaches 33.6°S; the bearings Kadri gives for 00:52 cross the arc 900 km further north or not at all",loc='left',fontsize=8)
    from matplotlib.patches import Patch
    H=[Patch(fc=HPD_FILL[2],label='50 % highest-density region, simulated impacts'),Patch(fc=HPD_FILL[1],label='90 %'),Patch(fc=HPD_FILL[0],label='99 %'),
       Line2D([],[],color=C_ARC,ls='--',label='7th arc'),Line2D([],[],marker='*',ls='',ms=10,mfc=C_G,mec='white',label='pair locus 33.6°S 94.5°E (implied impact 00:31:41)'),
       Line2D([],[],marker='o',ls='',ms=4,mfc='#8c8c8c',mec='white',label='arc crossing of a bearing; R = range from Cape Leeuwin')]
    ax.legend(handles=H,loc='lower right',frameon=False,fontsize=6.5)
    ste=("Each line is a sound direction from Cape Leeuwin. The dot is where the line meets the arc, and R is the distance. The thick blue line goes "
         "to the place that the time difference of the pair gives. Kadri's two published directions for the 00:52 signal (57° and 306.18°) do not "
         "go there. The grey lines are other Table 1 directions that the earlier chart used. "+PAIR_STE)
    tech=(PAIR_TECH+" Rays are WGS84 geodesics from the H01W triad centroid; R is the geodesic range to the nearest approach to the drawn arc "
          "(composer small-circle fit to run J 00:19:29 positions). Table 1 rows from searches named/table1_verdicts.csv (bearings DIGITISED from Kadri 2024 "
          "Table 1). HPD: run J impacts (geometry/sample.npz, waypoints seeds 1-8 stride 6 + northern supplement, Kish ESS 110k), D0', 0.1° bins, "
          "Gaussian display smoothing sigma 25 km. "+COMMON_TECH)
    footnotes(fig,ste,tech,width=185)
    return fig
fig=chart4(); save(fig,'chart4-bearings-pair-g')
for lab,b,*_ in RAYS: print(lab,b,ray_arc_cross('H01W',b))
