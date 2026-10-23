l50=hpd_lev(P_t3,0.5); l90=hpd_lev(P_t3,0.9); l50b=hpd_lev(P_04,0.5)
GL=dict(P_t3=P_t3,P_04=P_04,l50=l50,l90=l90,l50b=l50b,E50=E50,glo=glo,gla=gla,PM=(res[('t3','arc_tdoa')]['mla'],res[('t3','arc_tdoa')]['mlo']))
ov=("    if k=='A':\n"
"        ax.contourf(glo,gla,P_t3,levels=[l50,1],colors=['#cb181d'],alpha=0.18,zorder=5)\n"
"        ax.contour(glo,gla,P_t3,levels=[l50],colors=['#a50f15'],linewidths=1.4,zorder=6)\n"
"        ax.contour(glo,gla,P_t3,levels=[l90],colors=['#a50f15'],linewidths=0.9,linestyles=[(0,(4,2))],zorder=6)\n"
"        ax.contour(glo,gla,P_04,levels=[l50b],colors=['#a50f15'],linewidths=0.8,linestyles=[(0,(1,1.5))],zorder=6)\n"
"        ax.plot(E50['lon'],E50['lat'],color='k',lw=0.9,ls=(0,(6,1.5,1,1.5)),zorder=6)\n"
"        ax.plot(PM[1],PM[0],marker='X',ms=7,color='#a50f15',mec='white',mew=0.6,ls='',zorder=8)\n")
hA=("    if k=='A':\n"
"        h+= [Patch(fc='#cb181d',alpha=0.3,ec='#a50f15',label='impact location, 50 % region (bearing + timing + arc uncertainty)'),\n"
"             Line2D([0],[0],color='#a50f15',lw=0.9,ls=(0,(4,2)),label='same, 90 % region'),\n"
"             Line2D([0],[0],color='k',lw=0.9,ls=(0,(6,1.5,1,1.5)),label='same, 50 % ellipse (Gaussian approximation)'),\n"
"             Line2D([0],[0],color='#a50f15',lw=0.8,ls=(0,(1,1.5)),label='50 % region if bearing error is 0.4 deg (Kadri claim)'),\n"
"             Line2D([0],[0],marker='X',ls='',ms=7,color='#a50f15',label='mean impact location')]\n")
footA=("    if k=='A':\n"
"        foot=(\"Plain words: The star is where the Kadri bearing line crosses the mean impact line. The red areas show where the impact can be when the errors in bearing, arrival time and sound speed are included. \"\n"
"              \"About one third of the 50 % red area mass is not on searched sea floor; in total 33 % of the impact probability is on sea floor that is not searched (49 % if the bearing error is 0.4 deg). \"\n"
"              \"Tan and green are sea floor already searched. Grey is the computed sea-floor position after the searches. Purple shows where the impact would be if the Pleiades objects were aircraft debris.\\n\"\n"
"              \"Technical: members Kadri 2024 Table 1 H01W 00:49:58 UTC, bearing 260.41 deg, and IMOS Portland 3274 01:15:51 UTC (Perth Canyon 3376 00:51:30 removed: 2-5 Hz, below the 8 Hz high-pass; the earlier point 35.81 S 91.58 E used it). \"\n"
"              \"Posterior = run J impact sample (D0', 00:19 held out; w_D0; impact positions, flight only) x bearing likelihood (Student-t, 3 dof, sd 3.3 deg, Kadri's demonstrated Sinabang deviation; dotted: Gaussian 0.4 deg, his claim) \"\n"
"              \"x H01W-3274 arrival-time-difference likelihood (pick sd 10 s each, IMOS clock sd 2 s, group speed 1.482 +/- 0.006 km/s common to both paths; impact time free). \"\n"
"              \"Mean 36.31 S 90.85 E; 50 % ellipse semi-axes 59 x 138 km, major axis 73 deg; effective sample size 20,191; split-half off-searched share 0.337 / 0.326. \"\n"
"              \"Searched = coverage > 0.5 (Phase 2 p2, OI 2018, OI 2025-26 grade C inferred); detection probability inside searched areas not applied; impact-to-seabed offset not applied; straight geodesic paths, no horizontal refraction. Pleiades layer as in the other maps.\")\n")
src2d=src2c.replace("    h=[",ov+"    h=[",1)
src2d=src2d.replace("    ax.legend(handles=h",hA+"    ax.legend(handles=h",1)
src2d=src2d.replace("    fig.text(0.01,0.0",footA+"    fig.text(0.01,0.0",1)
src2d=src2d.replace("fn=f'cand/cand{k}_2_closeup_map.png'","fn=f'cand/cand{k}_2_closeup_map_uncertainty.png' if k=='A' else f'cand/cand{k}_2_closeup_map.png'")
assert src2d.count("if k=='A'")==3
globals().update(GL)
import copy
CANDS_bak=copy.deepcopy(CANDS['A'])
CANDS['A'].update(lat=float(fla[i_b]),lon=float(flo[i_b]),t0=float(t0b-nT0),title='Kadri 00:49:58 (bearing 260.41 deg) + Portland 3274 01:15:51')
exec(src2d); fnA=chart2('A'); plt.close('all'); print(fnA, CANDS['A']['lat'],CANDS['A']['lon'],fmt(CANDS['A']['t0']))