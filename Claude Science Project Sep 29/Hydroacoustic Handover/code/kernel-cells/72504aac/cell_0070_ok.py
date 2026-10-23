
LOC_OFF3['G']=(-20,40); fig=chart3(); save(fig,'chart3-hpd-maps-pair-g'); plt.close('all')
NR['share']=NR.w/WTOT
hw=NR.loc[NR.w.idxmax()]; pos=NR[NR.w>0]; cl=pos.loc[pos.d.idxmin()]
print('n within150', len(NR), 'positive', len(pos), 'mass', NR.w.sum()/WTOT)
def match_route(row):
    k=int(row.seed); r=ROUTES[k-1]; p=r[:,36]+(r[:,37]-r[:,36])*frac
    d=hav(p[:,0],p[:,1],row.h_lat,row.h_lon); j=int(np.argmin(d)); return k,j,float(d[j])
for nm,row in [('highest',hw),('closest',cl)]:
    k,j,dd=match_route(row)
    print(nm, dict(seed=k,parent=int(row.parent),share=row.share,d=row.d,lat=row.lat,lon=row.lon,t=hms(T0+row.t_impact_s),takeover=hms(T0+row.t_takeover_s),
                    onset=hms(T0+row.t_onset_s) if np.isfinite(row.t_onset_s) else None, flameout=hms(T0+row.t_realised_flameout_s) if np.isfinite(row.t_realised_flameout_s) else None,
                    fam=row.family4_code, maxrate=row.max_descent_rate_fpm, route=j, route_d_km=dd, f150=RI[(RI.seed==k)&(RI.route==j)].f150.iloc[0]))
