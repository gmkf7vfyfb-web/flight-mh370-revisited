
rowh_km=np.diff(vc.ROW_EDGES)[:vc.NY]*111.2; iy=np.argmin(np.abs(yc_m+33)); sy=25/rowh_km[iy]; sx=25/(111.2*0.25*np.cos(np.radians(33)))
def smooth(M): M=M/M.sum(); return gaussian_filter(M,[sy,sx])
CS=smooth(core); DS_=smooth(dri)
TOP=top.reset_index(drop=True)
LOC_TXT={'A':'A · Table 1 00:49:58 (260.41°)\nimpact 00:26:47','B':'B · Table 1 00:53:31 (257.58°)\nimpact 00:29:13',
         'E':'E · CL 00:52:04 × DG 01:10:01\nimpact 00:28:36','F':'F · CL 00:54:27 × DG 01:12:49\nimpact 00:31:27',
         'D':"D · Kadri's preferred crossing, 306.18°\nimpact 00:34:03 (text time) / 00:36:30 (caption time)",
         'G':'G · CL 00:52:04 × DG 01:12:49 (this pair)\nimpact 00:31:41'}
LOC_OFF={'A':(70,-6),'B':(70,-36),'E':(-150,-30),'F':(-150,12),'D':(-200,22),'G':(40,30)}
def chart3():
    fig=plt.figure(figsize=(11,7.6)); axs=[fig.add_axes([0.06,0.36,0.43,0.58]),fig.add_axes([0.54,0.36,0.43,0.58])]
    ext=(84,106,-42,-20)
    for ax,M,ttl,raw in [(axs[0],CS,'Flight, fuel and final satellite contacts',core),(axs[1],DS_,'Same impacts, also weighted by the debris drift',dri)]:
        lv=hpd_levels(M,(0.99,0.9,0.5)); ax.contourf(xc_m,yc_m,M,levels=[lv[0],lv[1],lv[2],M.max()*1.01],colors=HPD_FILL,zorder=2)
        ax.contour(xc_m,yc_m,M,levels=lv,colors=['#4f79ad'],linewidths=[0.5,0.6,0.7],linestyles=[':','--','-'],zorder=2)
        land(ax,ext); ax.plot(ARC_LON,ARC_LAT,color=C_ARC,lw=0.9,ls='--',zorder=3)
        for k in ['A','B','E','F']:
            l=LOCI[k]; mk='o' if k in('A','B') else '^'
            ax.scatter(l['lon'],l['lat'],marker=mk,s=34,c='white',edgecolors=C_LOCI,lw=1.0,zorder=6)
            ax.annotate(LOC_TXT[k],(l['lon'],l['lat']),xytext=LOC_OFF[k],textcoords='offset points',fontsize=6,color=C_LOCI,arrowprops=dict(arrowstyle='-',color=C_LOCI,lw=0.5))
        ax.scatter(LOCI['D']['lon'],LOCI['D']['lat'],marker='*',s=150,c=C_D,edgecolors='white',lw=0.6,zorder=7)
        ax.annotate(LOC_TXT['D'],(LOCI['D']['lon'],LOCI['D']['lat']),xytext=LOC_OFF['D'],textcoords='offset points',fontsize=6,color=C_D,arrowprops=dict(arrowstyle='-',color=C_D,lw=0.5))
        for i,r in TOP.iterrows():
            ax.scatter(r.locus_lon,r.locus_lat,marker='D',s=16,facecolors='none',edgecolors=C_T1,lw=0.8,zorder=6)
        ax.annotate('ranked pairs 1-5\n(Diego Garcia South × Perth Canyon 3315)',(TOP.locus_lon.min(),TOP.locus_lat.max()),xytext=(-125,40),textcoords='offset points',fontsize=6,color=C_T1,arrowprops=dict(arrowstyle='-',color=C_T1,lw=0.5))
        ax.scatter(G['lon'],G['lat'],marker='*',s=230,c=C_G,edgecolors='white',lw=0.8,zorder=8)
        ax.annotate(LOC_TXT['G'],(G['lon'],G['lat']),xytext=LOC_OFF['G'],textcoords='offset points',fontsize=6.5,color=C_G,arrowprops=dict(arrowstyle='-',color=C_G,lw=0.6))
        n35=raw[yc_m>-35].sum()/raw.sum(); mG=(raw/raw.sum())[np.hypot((yc_m[:,None]-G['lat'])*111.2,(xc_m[None,:]-G['lon'])*111.2*np.cos(np.radians(G['lat'])))<150].sum()
        ax.text(0.02,0.02,f"{n35*100:.1f} % north of 35°S; {mG*100:.1f} % within 150 km of G",transform=ax.transAxes,fontsize=6.5)
        ax.set_xlim(ext[0],ext[1]); ax.set_ylim(ext[2],ext[3]); ax.set_aspect(1/np.cos(np.radians(31)))
        ax.set_title(ttl,loc='left',fontsize=8); ax.set_xlabel('Longitude (°E)')
    axs[0].set_ylabel('Latitude (°; south negative)'); axs[1].set_yticklabels([])
    fig.text(0.06,0.975,"The pair locus G is at the northern edge of the 99 % region without drift and inside the 90 % region with drift; it is not a strong candidate",fontsize=8,va='top')
    from matplotlib.patches import Patch
    H=[Patch(fc=HPD_FILL[2],label='50 % highest-density region'),Patch(fc=HPD_FILL[1],label='90 %'),Patch(fc=HPD_FILL[0],label='99 %'),Line2D([],[],color=C_ARC,ls='--',label='7th arc'),
       Line2D([],[],marker='o',ls='',mfc='white',mec=C_LOCI,label='arc crossing of a Table 1 bearing (A, B)'),Line2D([],[],marker='^',ls='',mfc='white',mec=C_LOCI,label='earlier two-station loci (E, F)'),
       Line2D([],[],marker='D',ls='',ms=4,mfc='none',mec=C_T1,label='top 5 pairs by likelihood ratio (ranking table)')]
    fig.legend(handles=H,loc='upper left',bbox_to_anchor=(0.06,0.335),ncol=4,frameon=False,fontsize=6.5)
    ste=("The maps show where the aircraft most probably is on the sea floor. Left: from the flight, fuel and satellite data. Right: the same, "
         "also with the debris drift. The blue star G is the point that the two sounds give. The letters show the earlier candidates. "
         "The five diamonds are the pairs with the highest likelihood ratio in the new ranking table; all five have a likelihood ratio below 1 and G is number 104. "+PAIR_STE)
    tech=(PAIR_TECH+" Maps: composer run-j-views-v3.2 maps-v3.npz, keys 'D0|core' (satcom + flight + end of flight, settled seabed) and 'D0|D' (core + debris drift, finds only, dedicated "
          "arc-latitude run), equal-area 769 km² grid (results/composer-views-run-j/views_common.py), each normalised to 1; HPD on cell mass after Gaussian display smoothing sigma 25 km. "
          f"Ranked pairs: graphics-2026-10-22/ranked/ranked_pairs.csv (parallel ranking track; ranks by lnLR; top 5 are H08S × 3315 secondary-family rows, lnLR -0.64 to -3.42, "
          f"loci 36.5-37.2°S 89.6-90.6°E); pair G is rank 104 by lnLR (-6.23) and rank 54 by p, bearing INCONSISTENT. Loci A, B from searches named/table1_verdicts.csv; E, F solved from "
          "the lag on the TL-grid arc; locus C of the earlier chart is not legible and is not redrawn; searched-area outlines of the earlier chart are not drawn. "+COMMON_TECH)
    footnotes(fig,ste,tech,width=215)
    return fig
fig=chart3(); save(fig,'chart3-hpd-maps-pair-g')
