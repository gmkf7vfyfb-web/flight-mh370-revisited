
FAMLAB={1:'A1 (descent at fuel exhaustion, no control)',2:'A2 (descent at fuel exhaustion, controlled phase)',3:'B (descent begun before fuel exhaustion)',6:'outside B'}
def traj(row):
    k,j,dd=match_route(row); r=ROUTES[k-1][j]; p=r[36]+(r[37]-r[36])*frac
    rl=np.r_[r[2:37,0],p[0]]; ro=np.r_[r[2:37,1],p[1]]
    return dict(k=k,j=j,dd=dd,rl=rl,ro=ro,h=(row.h_lat,row.h_lon),to=(row.takeover_latitude_deg,row.takeover_longitude_deg),imp=(row.lat,row.lon),row=row)
TJ={'hw':traj(hw),'cl':traj(cl),'tc':traj(tc)}
def draw_traj(ax,T,c,lw=1.6,ls='-',zoom=False):
    ax.plot(T['ro'],T['rl'],color=c,lw=lw,ls=ls,zorder=5)
    ax.scatter(T['ro'][-1],T['rl'][-1],s=18,c=c,zorder=6)              # 00:10:59 on the route
    ax.plot([T['ro'][-1],T['h'][1],T['to'][1],T['imp'][1]],[T['rl'][-1],T['h'][0],T['to'][0],T['imp'][0]],color=c,lw=lw*0.7,ls=ls,zorder=5)
    if zoom: ax.scatter(T['to'][1],T['to'][0],s=22,marker='s',facecolors='white',edgecolors=c,zorder=6)
    ax.scatter(T['imp'][1],T['imp'][0],s=50,marker='X',c=c,edgecolors='white',lw=0.5,zorder=7)
def circle(lat,lon,rkm,n=200):
    lo,la,_=G84.fwd(np.full(n,lon),np.full(n,lat),np.linspace(0,360,n),np.full(n,rkm*1000)); return la,lo
C_HW='#c2501b'; C_CL='#6a51a3'; C_TC='#1a9850'
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
    a2.annotate("G: pair locus, implied impact 00:31:41\n(Cape Leeuwin 00:52:04 × Diego Garcia 01:12:49)",(G['lon'],G['lat']),xytext=(15,-40),textcoords='offset points',fontsize=6.5,color=C_G,arrowprops=dict(arrowstyle='-',color=C_G,lw=0.5))
    r=T['row']; a2.annotate(f"simulated impact {hms(T0+r.t_impact_s)}, {r.d:.0f} km from G",(r.lon,r.lat),xytext=(-10,22),textcoords='offset points',fontsize=6.5,color=C_HW,ha='right',arrowprops=dict(arrowstyle='-',color=C_HW,lw=0.5))
    a2.annotate(f"start of the final descent {hms(T0+r.takeover_s if False else T0+r.t_takeover_s)}",(r.takeover_longitude_deg,r.takeover_latitude_deg),xytext=(10,-18),textcoords='offset points',fontsize=6.5,color=C_HW,arrowprops=dict(arrowstyle='-',color=C_HW,lw=0.5))
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
          f"at {r.lat:.2f}°S {r.lon:.2f}°E; family {FAMLAB[int(r.family4_code)]}; max descent rate {r.max_descent_rate_fpm:,.0f} ft/min; share of the D0' p 0.5 waypoints-stratum mass {r.share:.1e} "
          f"(mass within 150 km of G {W150TOT/WTOT:.3f}). Weights: run_j_windows.ln_weights(D0') x p_factor(0.5), seeds pooled equally (24 seeds). "+COMMON_TECH)
    footnotes(fig,ste,tech,width=205)
    return fig
fig=chart2(); save(fig,'chart2-trajectory-pair-g')
