
tG=hms2s('00:31:41'); tt=NR.t_impact_s.values
inwin=np.abs(tt-tG)<120
print('share of within-150 mass with |dt|<120 s', NR.w[inwin].sum()/NR.w.sum(), ' of total', NR.w[inwin].sum()/WTOT)
tc=NR[inwin].loc[NR[inwin].w.idxmax()]
k,j,dd=match_route(tc); print(dict(seed=k,share=tc.share,d=tc.d,t=hms(T0+tc.t_impact_s),fam=tc.family4_code,route=j,route_d=dd,lat=tc.lat,lon=tc.lon, takeover=hms(T0+tc.t_takeover_s), maxrate=tc.max_descent_rate_fpm))
# weighted impact-time quantiles within 150 km
o=np.argsort(tt); c=np.cumsum(NR.w.values[o]); c/=c[-1]; print([hms(T0+tt[o][np.searchsorted(c,q)]) for q in (0.05,0.25,0.5,0.75,0.95)])
print(NR.groupby('family4_code').w.sum()/NR.w.sum())
