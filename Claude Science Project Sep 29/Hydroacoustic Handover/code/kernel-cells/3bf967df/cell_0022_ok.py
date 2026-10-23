T0=1394236800; tu=t.astype(np.float64)  # seconds after 00:00:00 UTC 8 Mar (run.json T0_unix_s)
print('impact time pct (min after 00:00):',np.percentile(tu/60,[1,5,50,95,99]))
fl=S[:,cols.index('t_realised_flameout_s')].astype(float); print('flameout pct:',np.nanpercentile(fl/60,[5,50,95]))
sc.set_array(tu[idx]/60); sc.set_clim(20,45); cb.update_normal(sc)
fig.savefig('kadri-crossing-impact-map.png',dpi=200,bbox_inches='tight')
def wq(x,ww,q): o=np.argsort(x); c=np.cumsum(ww[o]); return np.interp(np.array(q)*c[-1],c,x[o])
dist=np.array([G.Inverse(X[1],X[0],a,b)['s12'] for a,b in zip(la[::50],lo[::50])])/1e3  # subsample for speed check
dkm=np.hypot((lo-X[0])*np.cos(np.radians(25.7)),la-X[1])*111.2
for r in (50,100,200):
    m=dkm<r; print(f'<{r} km: rows {m.sum()}, share {w[m].sum():.5f}, weighted impact time p5/p50/p95 (min) {np.round(wq(tu[m]/60,w[m],[.05,.5,.95]),1)}')
# rows matching Kadri eq-4 timing along the bearing strip (cross-track < 1 deg ~ 27 km), time within +/-2 min of eq.4 time at that along-bearing range
inv=[G.Inverse(H01[0],H01[1],a,b) for a,b in zip(la,lo)] if False else None