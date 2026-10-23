from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
cm_post=LinearSegmentedColormap.from_list('pg',['#ffffff','#bdbdbd','#525252','#000000'])
yc=0.5*(ROW_E[1:]+ROW_E[:-1]); xc=LON0+(np.arange(NX)+0.5)*STEP
Sn=mapS/mapS.sum(); Cn=mapC/mapC.sum()
lvS=[hpd_level(Sn,q) for q in (0.9,0.5)]; lvC=hpd_level(Cn,0.9)
postn=post/post.sum(); lvP=[hpd_level(postn,q) for q in (0.9,0.5)]
def gc_line(lat0,lon0,az,dist_km=2600,n=200):
    lo_,la_,_=G.fwd(np.full(n,lon0),np.full(n,lat0),np.full(n,az),np.linspace(0,dist_km*1000,n)); return la_,lo_
def chart2(k):
    cd=CANDS[k]; L,Lo=cd['lat'],cd['lon']; dlat,dlon=2.7,3.4
    fig,ax=plt.subplots(figsize=(7.2,6.2))
    ext=[Lo-dlon,Lo+dlon,L-dlat,L+dlat]
    pcm=ax.pcolormesh(LON_E,ROW_E,np.ma.masked_less_equal(Sn,0)/ (np.diff(ROW_E)[:,None]*0+1),cmap=cm_post,shading='flat',vmin=0,vmax=np.nanmax(Sn[(yc>L-dlat)[:,None]&(yc<L+dlat)[:,None]&((xc>Lo-dlon)&(xc<Lo+dlon))[None,:]])*1.0,rasterized=True,alpha=0.85)
    ax.contour(xc,yc,Sn,levels=sorted(lvS),colors=['k','k'],linewidths=[0.8,1.6])
    ax.contour(xc,yc,Cn,levels=[lvC],colors=['#636363'],linewidths=0.8,linestyles=[(0,(3,2))])
    # searched seabed
    sl=(flat>=L-dlat-0.1)&(flat<=L+dlat+0.1); sc=(flon>=Lo-dlon-0.1)&(flon<=Lo+dlon+0.1)
    if sl.any() and sc.any():
        X_,Y_=flon[sc][::4],flat[sl][::4]
        ax.contourf(X_,Y_,p2[np.ix_(sl,sc)][::4,::4],levels=[0.5,1.01],colors=['#d9b98c'],alpha=0.55)
        oi=np.maximum(oi18,oi25)[np.ix_(sl,sc)][::4,::4]
        ax.contourf(X_,Y_,oi,levels=[0.5,1.01],colors=['#74c476'],alpha=0.45)
        ax.contour(X_,Y_,oi,levels=[0.5],colors=['#238b45'],linewidths=0.5)
    # pleiades conditional source PDF
    ax.contour(plon,plat,postn,levels=sorted(lvP),colors=['#7b3294','#7b3294'],linewidths=[0.9,1.6],linestyles=['--','-'])
    ip=(plei.latitude_deg.between(L-dlat,L+dlat))&(plei.longitude_deg.between(Lo-dlon,Lo+dlon))
    ax.scatter(plei.longitude_deg[ip],plei.latitude_deg[ip],marker='P',s=28,color='#7b3294',edgecolor='white',lw=0.4,zorder=6)
    ic=(cosmo.latitude.between(L-dlat,L+dlat))&(cosmo.longitude.between(Lo-dlon,Lo+dlon))
    ax.scatter(cosmo.longitude[ic],cosmo.latitude[ic],marker='^',s=26,color='#c51b7d',edgecolor='white',lw=0.4,zorder=6)
    for _,r_ in cosmo[ic].iterrows(): ax.text(r_.longitude+0.05,r_.latitude+0.05,r_.id,fontsize=5.5,color='#c51b7d')
    ax.plot(flo,fla,color='#2171b5',lw=1.0,ls=(0,(5,2)))
    # bearing lines for Kadri members
    for rr,ts in cd['arr']:
        if rr=='H01W':
            row=t1[t1.time_utc==ts]
            if len(row): la_,lo_=gc_line(rx['H01W'][0],rx['H01W'][1],float(row.bearing_deg.iloc[0])); ax.plot(lo_,la_,color='#e6550d',lw=0.9); ax.text(Lo+dlon*0.55,L+dlat*0.85,f"Kadri bearing {float(row.bearing_deg.iloc[0]):.2f} deg",color='#e6550d',fontsize=6)
    if 'bearing' in cd:
        la_,lo_=gc_line(rx['H01W'][0],rx['H01W'][1],cd['bearing']); ax.plot(lo_,la_,color='#e6550d',lw=0.9); ax.text(Lo+dlon*0.55,L+dlat*0.85,f"Kadri bearing {cd['bearing']:.2f} deg",color='#e6550d',fontsize=6)
    ax.scatter([Lo],[L],marker='*',s=180,color='#e6550d',edgecolor='k',lw=0.6,zorder=7)
    ax.text(Lo+0.12,L-0.18,f"candidate {k}\n{abs(L):.2f} S {Lo:.2f} E\nimpact {fmt(cd['t0'])[:8]} UTC",fontsize=6.5,zorder=7,bbox=dict(fc='white',ec='none',alpha=0.7,pad=1))
    ax.set_xlim(ext[0],ext[1]); ax.set_ylim(ext[2],ext[3]); ax.set_aspect(1/np.cos(np.radians(L)))
    ax.set_xlabel('longitude (deg E)'); ax.set_ylabel('latitude (deg)')
    ax.set_title(f"Candidate {k}: impact point, searched seabed and sea-floor PDF (00:19 data held out)",loc='left',fontsize=7.5)
    h=[Patch(color='#525252',alpha=0.8,label='sea-floor PDF, core + searched areas (shading)'),Line2D([0],[0],color='k',lw=1.6,label='same, 50 % HPD (thick) / 90 % (thin)'),
       Line2D([0],[0],color='#636363',lw=0.8,ls=(0,(3,2)),label='core only, 90 % HPD'),Patch(color='#d9b98c',alpha=0.6,label='searched seabed, ATSB Phase 2'),
       Patch(color='#74c476',alpha=0.5,label='searched seabed, Ocean Infinity 2018 + 2025-26 (inferred)'),
       Line2D([0],[0],color='#7b3294',lw=1.6,label='impact PDF if the Pleiades objects are debris, 50 % / 90 % (dashed)'),
       Line2D([0],[0],marker='P',ls='',color='#7b3294',label='Pleiades rating-5 objects (23 Mar 2014 positions)'),Line2D([0],[0],marker='^',ls='',color='#c51b7d',label='COSMO-SkyMed contacts'),
       Line2D([0],[0],color='#2171b5',ls=(0,(5,2)),label='mean impact line (run J)'),Line2D([0],[0],marker='*',ls='',ms=10,color='#e6550d',label='candidate impact point')]
    ax.legend(handles=h,fontsize=5.5,frameon=True,framealpha=0.85,loc='lower right')
    foot=("Plain words: The star is where this candidate puts the impact. Grey is the computed sea-floor position of the aircraft after the searched areas are taken into account. Tan and green are sea floor already searched. "
          "Purple shows where the impact would be if the Pleiades objects were aircraft debris (a conditional result, not evidence that they are). Pleiades objects are where they floated 15 days later.\n"
          "Technical: composer views v3.2 maps (equal-area 0.25 deg grid), product S = core x searched areas, D0' (00:19 held out), 4-stratum mixture; core-only 90 % HPD dashed. Search fields: searched-areas spatial-fields-v2 "
          "(Phase 2 coverage p2 > 0.5; OI 2018/2025-26 > 0.5, grade C inferred). Pleiades: run J map-D0 'post' (flight-only cell mass conditional on H, q = 1/3, C2 silent, 0.05 deg). "
          "The S map is a sea-floor PDF; the candidate is an impact point (surface). Sea-floor maps do not use any hydroacoustic result. C1, C2.")
    fig.text(0.01,0.0,'\n'.join(textwrap.fill(p,170) for p in foot.split('\n')),fontsize=5.3,va='top')
    fn=f'cand/cand{k}_2_closeup_map.png'; fig.savefig(fn,dpi=220,bbox_inches='tight'); plt.close(fig); return fn
files2={'A':chart2('A')}