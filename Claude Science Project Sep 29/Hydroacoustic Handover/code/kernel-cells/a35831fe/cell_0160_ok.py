rng=np.random.default_rng(7); half=rng.random(la.size)<0.5
for key in [('t3','arc_tdoa'),(0.4,'arc_tdoa'),(1.0,'arc_tdoa'),('t3','arc_time')]:
    W=res[key]['W']; v=[]
    for h in (half,~half):
        Wh=W*h; Wh=Wh/Wh.sum(); v.append(Wh[~srch].sum())
    print(key,'unsearched halves',np.round(v,3))
# ellipse from weighted covariance in local tangent km
def ell(W,q=0.5):
    mla=np.sum(W*la); mlo=np.sum(W*lo)
    x=(lo-mlo)*111.32*np.cos(np.radians(mla)); y=(la-mla)*110.95
    C=np.cov(np.vstack([x,y]),aweights=W); ev,evec=np.linalg.eigh(C)
    s=np.sqrt(stats.chi2.ppf(q,2)); th=np.linspace(0,2*np.pi,361)
    pts=evec@(np.sqrt(ev)[:,None]*s*np.vstack([np.cos(th),np.sin(th)]))
    elo=mlo+pts[0]/(111.32*np.cos(np.radians(mla))); ela=mla+pts[1]/110.95
    ang=np.degrees(np.arctan2(evec[0,1],evec[1,1]))%180  # azimuth of major axis
    return dict(lon=elo,lat=ela,semi=np.sqrt(ev)*s,az_major=ang,mla=mla,mlo=mlo)
E50=ell(res[('t3','arc_tdoa')]['W']); E50b=ell(res[(0.4,'arc_tdoa')]['W'])
print('t3 ellipse 50% semi-axes km',E50['semi'].round(0),'major az',round(E50['az_major']))
print('0.4 ellipse 50% semi-axes km',E50b['semi'].round(0),'major az',round(E50b['az_major']))
# HPD from smoothed hist
P_t3=hist_post(res[('t3','arc_tdoa')]['W'],1.0); P_04=hist_post(res[(0.4,'arc_tdoa')]['W'],1.0)
for nm,P in [('t3',P_t3),('0.4',P_04),('ac t3',AC['t3'])]:
    l50=hpd_lev(P,0.5); inside=P>=l50
    print(nm,'50% HPD lat',GLA[inside].min().round(2),GLA[inside].max().round(2),'lon',GLO[inside].min().round(2),GLO[inside].max().round(2),
          'area km2',round((inside*cellA).sum()*0.05*0.05*111.32*110.95),'unsearched share of 50% region mass',round(P[inside&~srG].sum()/P[inside].sum(),3))