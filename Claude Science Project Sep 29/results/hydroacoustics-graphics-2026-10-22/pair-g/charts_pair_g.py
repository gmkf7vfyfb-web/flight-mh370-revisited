"""Chart functions for the pair-G updates (22 Oct 2026). Run after exec(open('common.py').read()) and the data cells; see README.txt."""
def hpd_grid(lat,lon,w,ext,step=0.1,sig_km=25):
    lo0,lo1,la0,la1=ext; xe=np.arange(lo0,lo1+step,step); ye=np.arange(la0,la1+step,step)
    H,_,_=np.histogram2d(lat,lon,bins=[ye,xe],weights=w); H=gaussian_filter(H,[sig_km/111/step, sig_km/111/step/np.cos(np.radians(33))])
    return 0.5*(xe[1:]+xe[:-1]),0.5*(ye[1:]+ye[:-1]),H


def hpd_levels(H,ps):
    v=np.sort(H.ravel())[::-1]; c=np.cumsum(v)/v.sum(); return [v[np.searchsorted(c,p)] for p in ps]


def draw_hpd(ax,xc,yc,H,ps=(0.99,0.9,0.5),alpha=1):
    lv=hpd_levels(H,ps); ax.contourf(xc,yc,H,levels=[lv[0],lv[1],lv[2],H.max()*1.01],colors=HPD_FILL,alpha=alpha,zorder=2)
    ax.contour(xc,yc,H,levels=lv,colors=['#4f79ad'],linewidths=[0.5,0.6,0.7],linestyles=[':','--','-'],zorder=2)


def traj(row):
    k,j,dd=match_route(row); r=ROUTES[k-1][j]; p=r[36]+(r[37]-r[36])*frac
    rl=np.r_[r[2:37,0],p[0]]; ro=np.r_[r[2:37,1],p[1]]
    return dict(k=k,j=j,dd=dd,rl=rl,ro=ro,h=(row.h_lat,row.h_lon),to=(row.takeover_latitude_deg,row.takeover_longitude_deg),imp=(row.lat,row.lon),row=row)


def draw_traj(ax,T,c,lw=1.6,ls='-',zoom=False):
    ax.plot(T['ro'],T['rl'],color=c,lw=lw,ls=ls,zorder=5)
    ax.scatter(T['ro'][-1],T['rl'][-1],s=18,c=c,zorder=6)              # 00:10:59 on the route
    ax.plot([T['ro'][-1],T['h'][1],T['to'][1],T['imp'][1]],[T['rl'][-1],T['h'][0],T['to'][0],T['imp'][0]],color=c,lw=lw*0.7,ls=ls,zorder=5)
    if zoom: ax.scatter(T['to'][1],T['to'][0],s=22,marker='s',facecolors='white',edgecolors=c,zorder=6)
    ax.scatter(T['imp'][1],T['imp'][0],s=50,marker='X',c=c,edgecolors='white',lw=0.5,zorder=7)


def circle(lat,lon,rkm,n=200):
    lo,la,_=G84.fwd(np.full(n,lon),np.full(n,lat),np.linspace(0,360,n),np.full(n,rkm*1000)); return la,lo


def chart1():
    fig=plt.figure(figsize=(10.5,7.2)); ax=fig.add_axes([0.065,0.44,0.92,0.53])
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
    ax.annotate("Pair locus 33.6°S 94.5°E\nimpact 00:31:41 (implied)",(G['lon'],G['lat']),xytext=(30,-80),textcoords='offset points',fontsize=7,color=C_G,
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
    fig.legend(handles=H,loc='upper left',bbox_to_anchor=(0.06,0.41),frameon=False,fontsize=6.5,ncol=3,columnspacing=1.5)
    ste=("The star is the point on the arc that the time difference of the two sounds gives. The lines show where sound can travel from that "
         "point to each recorder. Grey dashed lines are blocked by shallow sea floor. The orange and purple lines are the directions Kadri "
         "published from Cape Leeuwin; none goes to the star. "+PAIR_STE)
    tech=(PAIR_TECH+" Path status at the 33.5°S node (offset 0, 10 m source): IMS from the KRAKEN arc grid (run-j-tl-grid/tl_grid.csv.gz; H08N no propagating modes, "
          "track min depth 6 m); IMOS from the RAM-corrected table imos_tl_ram_arc.csv (3274/3275 open at 130-136 dB for 6.3-40 Hz, KRAKEN gives no modes; 3250 "
          "TL > 440 dB, shelf 12 m). OHASISBIO positions from Royer LDO-201608 Table 1. Impact cloud: run J waypoints stratum seeds 1-8 stride 6 + northern supplement "
          "(searches geometry/sample.npz, Kish ESS 110k), weights D0'. Bearings are WGS84 geodesics from the H01W triad centroid. Land: GEBCO 2026 at 0.05°. "+COMMON_TECH)
    footnotes(fig,ste,tech,width=205)
    return fig


def chart2():
    fig=plt.figure(figsize=(10.5,7.0)); a1=fig.add_axes([0.06,0.36,0.40,0.56]); a2=fig.add_axes([0.53,0.36,0.44,0.56])
    e1=(76,116,-42,10); land(a1,e1); a1.plot(ARC_LON,ARC_LAT,color=C_ARC,ls='--',lw=0.9,zorder=3)
    T=TJ['hw']; draw_traj(a1,T,C_HW)
    a1.scatter(G['lon'],G['lat'],marker='*',s=170,c=C_G,edgecolors='white',lw=0.7,zorder=8); a1.scatter(LOCI['D']['lon'],LOCI['D']['lat'],marker='*',s=90,c=C_D,edgecolors='white',lw=0.6,zorder=8)
    a1.annotate('G',(G['lon'],G['lat']),xytext=(-14,-4),textcoords='offset points',color=C_G,fontsize=7); a1.annotate('D',(LOCI['D']['lon'],LOCI['D']['lat']),xytext=(6,-2),textcoords='offset points',color=C_D,fontsize=7)
    a1.set_xlim(e1[0],e1[1]); a1.set_ylim(e1[2],e1[3]); a1.set_aspect(1/np.cos(np.radians(15)))
    a1.set_title('Stored route after 18:22 UTC, highest-weight impact near G',loc='left',fontsize=8); a1.set_xlabel('Longitude (°E)'); a1.set_ylabel('Latitude (°; south negative)')
    e2=(91.0,98.0,-36.6,-30.6); land(a2,e2); a2.plot(ARC_LON,ARC_LAT,color=C_ARC,ls='--',lw=0.9,zorder=3)
    cl_,co_=circle(G['lat'],G['lon'],150); a2.plot(co_,cl_,color=C_G,lw=0.7,ls=':',zorder=3)
    draw_traj(a2,T,C_HW,zoom=True)
    a2.scatter(G['lon'],G['lat'],marker='*',s=220,c=C_G,edgecolors='white',lw=0.8,zorder=8)
    a2.annotate("G: pair locus, implied impact 00:31:41\n(Cape Leeuwin 00:52:04 × Diego Garcia 01:12:49)",(G['lon'],G['lat']),xytext=(25,45),textcoords='offset points',fontsize=6.5,color=C_G,arrowprops=dict(arrowstyle='-',color=C_G,lw=0.5))
    r=T['row']; a2.annotate(f"simulated impact {hms(T0+r.t_impact_s)}, {r.d:.0f} km from G",(r.lon,r.lat),xytext=(-10,22),textcoords='offset points',fontsize=6.5,color=C_HW,ha='right',arrowprops=dict(arrowstyle='-',color=C_HW,lw=0.5))
    a2.annotate(f"start of the final descent {hms(T0+r.takeover_s if False else T0+r.t_takeover_s)}",(r.takeover_longitude_deg,r.takeover_latitude_deg),xytext=(-12,-30),textcoords='offset points',fontsize=6.5,color=C_HW,ha='right',arrowprops=dict(arrowstyle='-',color=C_HW,lw=0.5))
    a2.annotate("route at 00:10:59",(T['ro'][-1],T['rl'][-1]),xytext=(8,6),textcoords='offset points',fontsize=6.5,color=C_HW)
    a2.text(0.02,0.02,'dotted circle: 150 km from G',transform=a2.transAxes,fontsize=6.5,color=C_G)
    a2.set_xlim(e2[0],e2[1]); a2.set_ylim(e2[2],e2[3]); a2.set_aspect(1/np.cos(np.radians(33.5)))
    a2.set_title('Neighbourhood of the pair locus and the modelled impact',loc='left',fontsize=8); a2.set_xlabel('Longitude (°E)')
    fig.text(0.06,0.985,f"The highest-weight simulated impact within 150 km of the pair locus G hits at {hms(T0+r.t_impact_s)}, {(tG-r.t_impact_s)/60:.0f} min before the time the pair implies",fontsize=8,va='top')
    ste=(f"The orange line is one stored flight path from the simulation. Its impact is the one with the highest weight within 150 km of the pair point G. "
         f"It hits the sea {(tG-r.t_impact_s)/60:.0f} minutes before the time that the pair of sounds gives. The flight path and the impact are linked by position at 00:11, not by a direct record. "+PAIR_STE)
    tech=(PAIR_TECH+f" Trajectory: core run J waypoints stratum, seed {T['k']}, stored route sample {T['j']} (routes.npy, lat/lon every 600 s from 18:01:49; drawn from 18:21:49 to 00:01:49 "
          f"and interpolated to 00:10:59); joined to end-of-flight row (seed {T['k']}, parent hand-off row {int(r.parent)}) by POSITION at 00:10:59 (route-to-parent distance {T['dd']:.1f} km): the stored "
          f"routes carry no row identity, so the join is an association, not a link. End-of-flight segment: hand-off position 00:10:59 -> start of final descent (takeover, {hms(T0+r.t_takeover_s)}) -> impact {hms(T0+r.t_impact_s)} "
          f"at {-r.lat:.2f}°S {r.lon:.2f}°E; family {FAMLAB[int(r.family4_code)]}; max descent rate {r.max_descent_rate_fpm:,.0f} ft/min; share of the D0' p 0.5 waypoints-stratum mass {r.share:.1e} "
          f"(mass within 150 km of G {W150TOT/WTOT:.3f}). Weights: run_j_windows.ln_weights(D0') x p_factor(0.5), seeds pooled equally (24 seeds). "+COMMON_TECH)
    footnotes(fig,ste,tech,width=205)
    return fig


def chart3():
    fig=plt.figure(figsize=(11,7.9)); axs=[fig.add_axes([0.06,0.36,0.43,0.57]),fig.add_axes([0.54,0.36,0.43,0.57])]
    ext=(84,106,-42,-20)
    for ax,M,ttl,raw in [(axs[0],CS,'Flight, fuel and final satellite contacts',core),(axs[1],DS_,'Same impacts, also weighted by the debris drift',dri)]:
        lv=hpd_levels(M,(0.99,0.9,0.5)); ax.contourf(xc_m,yc_m,M,levels=[lv[0],lv[1],lv[2],M.max()*1.01],colors=HPD_FILL,zorder=2)
        ax.contour(xc_m,yc_m,M,levels=lv,colors=['#4f79ad'],linewidths=[0.5,0.6,0.7],linestyles=[':','--','-'],zorder=2)
        land(ax,ext); ax.plot(ARC_LON,ARC_LAT,color=C_ARC,lw=0.9,ls='--',zorder=3)
        for k in ['A','B','E','F']:
            l=LOCI[k]; mk='o' if k in('A','B') else '^'
            ax.scatter(l['lon'],l['lat'],marker=mk,s=34,c='white',edgecolors=C_LOCI,lw=1.0,zorder=6)
            ax.annotate(LOC_TXT[k],(l['lon'],l['lat']),xytext=LOC_OFF3[k],textcoords='offset points',fontsize=6,color=C_LOCI,arrowprops=dict(arrowstyle='-',color=C_LOCI,lw=0.5))
        ax.scatter(LOCI['D']['lon'],LOCI['D']['lat'],marker='*',s=150,c=C_D,edgecolors='white',lw=0.6,zorder=7)
        ax.annotate(LOC_TXT['D'],(LOCI['D']['lon'],LOCI['D']['lat']),xytext=LOC_OFF3['D'],textcoords='offset points',fontsize=6,color=C_D,arrowprops=dict(arrowstyle='-',color=C_D,lw=0.5))
        for i,r in TOP.iterrows():
            ax.scatter(r.locus_lon,r.locus_lat,marker='D',s=16,facecolors='none',edgecolors=C_T1,lw=0.8,zorder=6)
        ax.annotate('ranked pairs 1-5\n(Diego Garcia South × Perth Canyon 3315)',(TOP.locus_lon.min(),TOP.locus_lat.max()),xytext=(30,-62),textcoords='offset points',fontsize=6,color=C_T1,arrowprops=dict(arrowstyle='-',color=C_T1,lw=0.5))
        ax.scatter(G['lon'],G['lat'],marker='*',s=230,c=C_G,edgecolors='white',lw=0.8,zorder=8)
        ax.annotate(LOC_TXT['G'],(G['lon'],G['lat']),xytext=LOC_OFF3['G'],textcoords='offset points',fontsize=6.5,color=C_G,arrowprops=dict(arrowstyle='-',color=C_G,lw=0.6))
        n35=raw[yc_m>-35].sum()/raw.sum(); mG=(raw/raw.sum())[np.hypot((yc_m[:,None]-G['lat'])*111.2,(xc_m[None,:]-G['lon'])*111.2*np.cos(np.radians(G['lat'])))<150].sum()
        ax.text(0.02,0.98,f"{n35*100:.1f} % north of 35°S; {mG*100:.1f} % within 150 km of G\nHPD level at G {hpd_at(M,G['lat'],G['lon']):.2f}; at D {hpd_at(M,LOCI['D']['lat'],LOCI['D']['lon']):.2f}",transform=ax.transAxes,fontsize=6.5,va='top')
        ax.set_xlim(ext[0],ext[1]); ax.set_ylim(ext[2],ext[3]); ax.set_aspect(1/np.cos(np.radians(31)))
        ax.set_title(ttl,loc='left',fontsize=8); ax.set_xlabel('Longitude (°E)')
    axs[0].set_ylabel('Latitude (°; south negative)'); axs[1].set_yticklabels([])
    fig.text(0.06,0.99,"The pair locus G lies on the edge of the 90 % region without drift and inside it with drift; the five highest-ranked pairs all point further south, near 37°S",fontsize=8,va='top')
    from matplotlib.patches import Patch
    H=[Patch(fc=HPD_FILL[2],label='50 % highest-density region'),Patch(fc=HPD_FILL[1],label='90 %'),Patch(fc=HPD_FILL[0],label='99 %'),Line2D([],[],color=C_ARC,ls='--',label='7th arc'),
       Line2D([],[],marker='o',ls='',mfc='white',mec=C_LOCI,label='arc crossing of a Table 1 bearing (A, B)'),Line2D([],[],marker='^',ls='',mfc='white',mec=C_LOCI,label='earlier two-station loci (E, F)'),
       Line2D([],[],marker='D',ls='',ms=4,mfc='none',mec=C_T1,label='top 5 pairs by likelihood ratio (ranking table)')]
    fig.legend(handles=H,loc='upper left',bbox_to_anchor=(0.06,0.30),ncol=4,frameon=False,fontsize=6.5)
    ste=("The maps show where the aircraft most probably is on the sea floor. Left: from the flight, fuel and satellite data. Right: the same, "
         "also with the debris drift. The blue star G is the point that the two sounds give. The letters show the earlier candidates. "
         "The five diamonds are the pairs with the highest likelihood ratio in the new ranking table; all five have a likelihood ratio below 1 and G is number 104. "+PAIR_STE)
    tech=(PAIR_TECH+" Maps: composer run-j-views-v3.2 maps-v3.npz, keys 'D0|core' (satcom + flight + end of flight, settled seabed) and 'D0|D' (core + debris drift, finds only, dedicated "
          "arc-latitude run), equal-area 769 km² grid (results/composer-views-run-j/views_common.py), each normalised to 1; HPD level at a point = mass of cells at least as dense as the point's cell (smoothed); HPD on cell mass after Gaussian display smoothing sigma 25 km. "
          f"Ranked pairs: graphics-2026-10-22/ranked/ranked_pairs.csv (parallel ranking track; ranks by lnLR; top 5 are H08S × 3315 secondary-family rows, lnLR -0.64 to -3.42, "
          f"loci 36.5-37.2°S 89.6-90.6°E); pair G is rank 104 by lnLR (-6.23) and rank 54 by p, bearing INCONSISTENT. Loci A, B from searches named/table1_verdicts.csv; E, F solved from "
          "the lag on the TL-grid arc; locus C of the earlier chart is not legible and is not redrawn; searched-area outlines of the earlier chart are not drawn. "+COMMON_TECH)
    footnotes(fig,ste,tech,width=215)
    return fig


def chart4():
    fig=plt.figure(figsize=(8.2,8.0)); ax=fig.add_axes([0.09,0.385,0.88,0.565])
    land(ax,ext4); draw_hpd(ax,xc4,yc4,H4)
    ax.plot(ARC_LON,ARC_LAT,color=C_ARC,lw=1.0,ls='--',zorder=3)
    rl,ro=RX['H01W']
    off={'Pair':(-75,45,'center'),'Table 1, 00:52:50':(10,22,'left'),"Kadri's":(-14,12,'center'),'Table 1, 00:39:02':(-45,-100,'right'),'A:':(-60,-6,'right'),'B:':(-45,-28,'right')}
    for lab,b,c,ls,lw in RAYS:
        if lab.startswith('Pair'): la,lo,R=G['lat'],G['lon'],G_D_H01W
        else: la,lo,_,R=ray_arc_cross('H01W',b)
        L,O=ray('H01W',b,2600); ax.plot(O,L,color=c,ls=ls,lw=lw,zorder=4)
        ax.scatter(lo,la,s=22,c=c,edgecolors='white',lw=0.5,zorder=6)
        k=[kk for kk in off if lab.startswith(kk)][0]; dx,dy,ha=off[k]
        ax.annotate(f"{lab}\n{b:.2f}°, R = {R:,.0f} km" if not lab.startswith('Pair') else f"{lab}\n{b:.1f}°, R = {R:,.0f} km",(lo,la),xytext=(dx,dy),textcoords='offset points',fontsize=6.5,color=c,ha=ha,
                    arrowprops=dict(arrowstyle='-',color=c,lw=0.5))
    L,O=ray('H01W',57.0,420); ax.plot(O,L,color=C_KADRI,lw=1.4,zorder=5)
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
       Line2D([],[],color=C_ARC,ls='--',label='7th arc'),Line2D([],[],color=C_KADRI,lw=1.4,label="Kadri's 00:52 bearing, text p. 9: 57° (towards land; never meets the arc)"),Line2D([],[],marker='*',ls='',ms=10,mfc=C_G,mec='white',label='pair locus 33.6°S 94.5°E (implied impact 00:31:41)'),
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


def chart5():
    fig=plt.figure(figsize=(8.6,6.4)); ax=fig.add_axes([0.08,0.40,0.62,0.53])
    ax.fill_between(xc,pdf,color=HPD_FILL[1],alpha=0.8,lw=0); ax.plot(xc,pdf,color=HPD_FILL[2],lw=1.2,label='simulated impacts, latitude density')
    ax.plot(dv.latitude_deg,dv.density_per_deg,color='#444444',lw=1.0,ls='--',label='Davey et al. (2016), Fig. 10.3')
    ymax=max(pdf.max(),dv.density_per_deg.max())*1.12
    rows=[]
    for k,lab,l,c,ls,lw in VL:
        ax.axvline(l,color=c,ls=ls,lw=lw,zorder=3); ax.scatter([l],[dens(l)],s=18,c=c,zorder=5,edgecolors='white',lw=0.5)
        rows.append((k,lab,l,dens(l),massband(l)))
    for k,y in [('G',0.93),('00:52:50',0.80),('D',0.93),('00:39:02',0.67)]:
        l=[r for r in VL if r[0]==k][0][2]; c=[r for r in VL if r[0]==k][0][3]
        ax.text(l+(0.15 if k!='00:39:02' else -0.15),ymax*y,{'G':'pair locus\n33.6°S','00:52:50':'Table 1\n00:52:50','D':"Kadri 306.18°\n(D), 25.7°S",'00:39:02':'Table 1\n00:39:02'}[k],color=c,fontsize=6.5,va='top',ha='left' if k!='00:39:02' else 'right')
    for (k,l),dy in zip([('A',LOCI['A']['lat']),('B',LOCI['B']['lat']),('E',LOCI['E']['lat']),('F',LOCI['F']['lat'])],[0.012,0.012,0.012,0.05]):
        ax.text(l+(0.12 if k in('A','F') else -0.12),-ymax*dy,k,color='#5e5e5e',fontsize=6.5,ha='left' if k in('A','F') else 'right',va='top')
    ax.set_xlim(-42,-20); ax.set_ylim(-ymax*0.09,ymax); ax.axhline(0,color='#999999',lw=0.5)
    ax.set_xlabel('Latitude of the arc crossing (°; south negative)'); ax.set_ylabel('Probability density per degree')
    ax.set_title('The pair locus lies in the thin northern tail of the impact density (about 5 % of the peak); Kadri\'s 306.18° crossing lies further out',loc='left',fontsize=8)
    ax.legend(loc='upper left',frameon=False,fontsize=6.5)
    # table on the right
    tx=fig.add_axes([0.72,0.40,0.27,0.53]); tx.axis('off')
    lines=[f"{'crossing':<10}{'lat °S':>7}{'density':>9}{'±0.5°':>8}"]
    for k,lab,l,d,m in rows: lines.append(f"{k:<10}{-l:7.2f}{d:9.3f}{m:8.3f}")
    tx.text(0,1,'\n'.join(lines),family='monospace',fontsize=6.3,va='top')
    tx.text(0,0.55,"A, B: Table 1 bearings 00:49:58, 00:53:31\nE: Cape Leeuwin 00:52:04 x Diego Garcia 01:10:01\nF: Cape Leeuwin 00:54:27 x Diego Garcia 01:12:49\nmass ±0.5°: share of simulated impacts\nwithin 0.5° of latitude",fontsize=6.3,va='top',color='#333333')
    ste=("The blue curve shows where the simulated impacts are along the arc. The vertical lines show where each sound gives a point on the arc. "
         "At the pair point (33.6°S) the curve is about 5 % of its peak height, and 3 % of the simulated impacts are within 0.5° of it. Kadri's direction 306.18° gives 25.7°S, where there are few simulated impacts. "+PAIR_STE)
    tech=(PAIR_TECH+" Density: run J impact latitudes (geometry/sample.npz, waypoints seeds 1-8 stride 6 + northern supplement, Kish ESS 110k), D0', 0.1° bins, "
          "Gaussian smoothing sigma 0.1°. The x-axis is the latitude of the impact for the density and of the arc crossing for the lines. Davey et al. (2016), Fig. 10.3, recovered "
          "from the PDF vector paths (BTO + BFO). Loci E, F, G solved from the lag on the module TL-grid arc at c = 1.482 km/s. Locus C of the earlier chart is not legible and is not redrawn. "+COMMON_TECH)
    footnotes(fig,ste,tech,width=170)
    return fig, rows


def chart6():
    fig=plt.figure(figsize=(10.5,7.6)); a1=fig.add_axes([0.06,0.44,0.40,0.49]); a2=fig.add_axes([0.53,0.44,0.44,0.49])
    e1=(76,116,-42,10); land(a1,e1); a1.plot(ARC_LON,ARC_LAT,color=C_ARC,ls='--',lw=0.9,zorder=3)
    e2=(91.0,98.0,-36.6,-30.6); land(a2,e2); a2.plot(ARC_LON,ARC_LAT,color=C_ARC,ls='--',lw=0.9,zorder=3)
    cl_,co_=circle(G['lat'],G['lon'],150); a2.plot(co_,cl_,color=C_G,lw=0.7,ls=':',zorder=3)
    for key,c,ls,lab in SEL:
        draw_traj(a1,TJ[key],c,lw=1.3,ls=ls); draw_traj(a2,TJ[key],c,lw=1.3,ls=ls,zoom=True)
    for ax,s in [(a1,170),(a2,220)]:
        ax.scatter(G['lon'],G['lat'],marker='*',s=s,c=C_G,edgecolors='white',lw=0.8,zorder=8)
    a1.scatter(LOCI['D']['lon'],LOCI['D']['lat'],marker='*',s=90,c=C_D,edgecolors='white',lw=0.6,zorder=8); a1.annotate('D',(LOCI['D']['lon'],LOCI['D']['lat']),xytext=(6,-2),textcoords='offset points',color=C_D,fontsize=7)
    a1.annotate('G',(G['lon'],G['lat']),xytext=(8,-4),textcoords='offset points',color=C_G,fontsize=7)
    a2.annotate("G: pair locus, implied impact 00:31:41",(G['lon'],G['lat']),xytext=(50,-60),textcoords='offset points',fontsize=6.5,color=C_G,ha='left',arrowprops=dict(arrowstyle='-',color=C_G,lw=0.5))
    a1.set_xlim(e1[0],e1[1]); a1.set_ylim(e1[2],e1[3]); a1.set_aspect(1/np.cos(np.radians(15))); a2.set_xlim(e2[0],e2[1]); a2.set_ylim(e2[2],e2[3]); a2.set_aspect(1/np.cos(np.radians(33.5)))
    a1.set_title('Stored routes after 18:22 UTC',loc='left',fontsize=8); a2.set_title('Neighbourhood of the pair locus G',loc='left',fontsize=8)
    a1.set_xlabel('Longitude (°E)'); a2.set_xlabel('Longitude (°E)'); a1.set_ylabel('Latitude (°; south negative)')
    H=[Line2D([],[],color=c,ls=ls,lw=1.3,label=lab) for _,c,ls,lab in SEL]+[Line2D([],[],marker='o',ls='',ms=4,color='#555555',label='route at 00:10:59'),
       Line2D([],[],marker='s',ls='',ms=4,mfc='white',mec='#555555',label='start of the final descent'),Line2D([],[],marker='X',ls='',ms=6,color='#555555',label='simulated impact'),
       Line2D([],[],color=C_G,ls=':',lw=0.7,label='150 km from G')]
    fig.legend(handles=H,loc='upper left',bbox_to_anchor=(0.06,0.385),ncol=4,frameon=False,fontsize=6.5)
    lines=[]
    for key,c,ls,lab in SEL:
        T=TJ[key]; r=T['row']
        lines.append((c,f"{lab}: {r.d:.0f} km from G; impact {hms(T0+r.t_impact_s)} ({(r.t_impact_s-tG)/60:+.0f} min against 00:31:41); final descent from {hms(T0+r.t_takeover_s)}, "
                         f"max {r.max_descent_rate_fpm:,.0f} ft/min; family {FAMLAB[int(r.family4_code)].split(' (')[0]}; weight share {r.share:.1e}"))
    y=0.305
    for c,s in lines: fig.text(0.06,y,s,fontsize=6.3,color=c); y-=0.02
    fig.text(0.06,0.985,"Near the pair locus the simulated impacts span 00:20-00:45 UTC (median 00:31:21); 18 % of the nearby weight falls within 2 min of the implied 00:31:41",fontsize=8,va='top')
    ste=("Three stored flight paths from the simulation are shown. Orange has the highest weight within 150 km of G. Green has the highest weight among those that also hit the sea "
         "within 2 minutes of the time the pair gives. Purple is the closest to G, but its weight is almost zero. The flight paths and the impacts are linked by position at 00:11, not by a direct record. "
         "These are stored samples; they were not fitted to the sounds. "+PAIR_STE)
    tech=(PAIR_TECH+f" Within 150 km of G: {len(NR):,} end-of-flight rows (24 waypoints seeds), mass {W150TOT/WTOT:.3f} of the D0' p 0.5 waypoints-stratum total; weighted impact-time quantiles 5/50/95 % "
          "00:20:31 / 00:31:21 / 00:45:25; share with |t - 00:31:41| < 120 s = 0.181. Family shares within 150 km: A1 0.13, A2 0.28, B 0.59. Routes: core run J routes.npy (2,000 per seed, every 600 s from 18:01:49), "
          "joined to end-of-flight rows by POSITION at 00:10:59 (seed/route/distance: "+'; '.join(f"{TJ[k]['k']}/{TJ[k]['j']}/{TJ[k]['dd']:.1f} km" for k,_,_,_ in SEL)+"); the routes carry no row identity. "
          "Weights: run_j_windows.ln_weights(D0') x p_factor(0.5). "+COMMON_TECH)
    footnotes(fig,ste,tech,width=205)
    return fig


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
    b1.text(1.0,0.02,' 22:41 handshake',transform=b1.get_xaxis_transform(),fontsize=6.5,color='#555555',va='bottom',ha='left')
    b2.legend(handles=[Line2D([],[],color=C_NEAR,lw=1.6,marker='o',ms=2.5,label='impact within 150 km of G'),Line2D([],[],color=C_REST,lw=1.2,marker='o',ms=2.5,label='all other paths')],loc='lower left',frameon=False,fontsize=6.5)
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


