
C_NEAR=C_G; C_REST='#9a9a9a'
def chart7():
    fig=plt.figure(figsize=(10.5,7.2)); a=fig.add_axes([0.06,0.36,0.50,0.57]); b1=fig.add_axes([0.65,0.66,0.33,0.27]); b2=fig.add_axes([0.65,0.36,0.33,0.25])
    ext=(84,106,-42,-12); land(a,ext)
    rest_idx=np.nonzero(~near)[0][::30]; near_idx=np.nonzero(near)[0]
    for i in rest_idx: a.plot(lo[i,k0:],la[i,k0:],color=C_REST,lw=0.3,alpha=0.35,zorder=2)
    for i in near_idx[::2]: a.plot(lo[i,k0:],la[i,k0:],color=C_NEAR,lw=0.35,alpha=0.35,zorder=3)
    a.plot(ARC_LON,ARC_LAT,color=C_ARC,ls='--',lw=0.9,zorder=4)
    a.scatter(G['lon'],G['lat'],marker='*',s=200,c=C_G,edgecolors='white',lw=0.8,zorder=8)
    cl_,co_=circle(G['lat'],G['lon'],150); a.plot(co_,cl_,color=C_G,lw=0.8,ls=':',zorder=6)
    a.scatter(LOCI['D']['lon'],LOCI['D']['lat'],marker='*',s=100,c=C_D,edgecolors='white',lw=0.6,zorder=8)
    a.annotate('G: pair locus',(G['lon'],G['lat']),xytext=(25,-25),textcoords='offset points',fontsize=6.5,color=C_G,arrowprops=dict(arrowstyle='-',color=C_G,lw=0.5))
    a.annotate("D: Kadri's preferred crossing",(LOCI['D']['lon'],LOCI['D']['lat']),xytext=(8,-3),textcoords='offset points',fontsize=6.5,color=C_D)
    a.set_xlim(ext[0],ext[1]); a.set_ylim(ext[2],ext[3]); a.set_aspect(1/np.cos(np.radians(27)))
    a.set_xlabel('Longitude (°E)'); a.set_ylabel('Latitude (°; south negative)')
    a.set_title('Stored paths 22:11-00:11 UTC',loc='left',fontsize=8)
    H=[Line2D([],[],color=C_NEAR,lw=1,label=f'impact within 150 km of G ({near.sum():,} paths; 1 in 2 shown)'),Line2D([],[],color=C_REST,lw=1,label=f'all other paths (1 in 30 shown)'),
       Line2D([],[],color=C_ARC,ls='--',label='7th arc'),Line2D([],[],color=C_G,ls=':',label='150 km from G')]
    a.legend(handles=H,loc='upper left',frameon=False,fontsize=6.5)
    x=tmid[ix]
    for ax,v,yl in [(b1,'trk','Ground track (°, true)'),(b2,'gs','Ground speed (kt)')]:
        for nm,c in [('rest',C_REST),('near',C_NEAR)]:
            B=band[nm][v]; ax.fill_between(x,B[:,0],B[:,2],color=c,alpha=0.25,lw=0); ax.plot(x,B[:,1],color=c,lw=1.6 if nm=='near' else 1.2,marker='o',ms=2.5)
        ax.axvline(0,color='#555555',lw=0.6,ls='--'); ax.set_ylabel(yl); ax.margins(x=0.03)
    b1.text(0.5,0.97,'22:41 handshake',transform=b1.get_xaxis_transform(),fontsize=6.5,color='#555555',va='top',ha='left')
    b1.text(x[-1],band['near']['trk'][-1,1]-5,'impact within\n150 km of G',color=C_NEAR,fontsize=6.5,ha='right',va='top'); b1.text(x[-1],band['rest']['trk'][-1,1]+2,'all others',color='#666666',fontsize=6.5,ha='right',va='bottom')
    b1.set_xticklabels([]); b2.set_xlabel('Minutes after the 22:41 handshake')
    b1.set_title('Track and speed, 10-minute chords (median, 10-90 %)',loc='left',fontsize=8)
    fig.text(0.06,0.985,"Paths that end near the pair locus fly about 10° further east of south and 30-50 kt slower after 22:41 than the other paths",fontsize=8,va='top')
    ste=("Left: blue lines are stored flight paths whose simulated impact is within 150 km of the pair point G; grey lines are the other paths. "
         "Right: the direction and the speed of the paths after the 22:41 satellite contact. The paths that end near G go more to the east of south and fly slower. "
         "The paths and the impacts are linked by position at 00:11, not by a direct record. "+PAIR_STE)
    tech=(PAIR_TECH+f" Paths: core run J waypoints stratum, 24 seeds x 2,000 stored route samples (routes.npy, every 600 s from 18:01:49; drawn 22:11:49-00:11:49). Each route is joined to the "
          f"end-of-flight hand-off rows within 10 km of its position at 00:10:59 (POSITION association; the routes carry no row identity); f = share of those rows' D0' p 0.5 impact weight within 150 km of G. "
          f"Blue: f >= 0.5 ({near.sum():,} of {len(f):,}); bands weight each route by f (near) or 1 - f (others), sum f = {f.sum():,.0f}. Track and speed from WGS84 chords between consecutive 600 s points "
          "(not instantaneous; a turn inside a chord is smoothed). 5th/6th-arc contours of the earlier chart are not drawn. "+COMMON_TECH)
    footnotes(fig,ste,tech,width=205)
    return fig
fig=chart7(); save(fig,'chart7-paths-track-speed-pair-g')
