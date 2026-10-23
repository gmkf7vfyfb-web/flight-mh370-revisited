from scipy.ndimage import gaussian_filter
postn=gaussian_filter(post,2.0); postn/=postn.sum(); lvP=[hpd_level(postn,q) for q in (0.9,0.5)]
_orig_chart2=chart2
files2={k:chart2(k) for k in CANDS}
def cov_at(L,Lo):
    i=int((L-fs)/fst); j=int((Lo-fw)/fst)
    if 0<=i<p2.shape[0] and 0<=j<p2.shape[1]: return float(p2[i,j]), float(oi18[i,j]), float(oi25[i,j])
    return (np.nan,)*3
def plei_post_at(L,Lo,rad=1.0):
    mm=(np.abs(plat[:,None]-L)<=rad)&(np.abs(plon[None,:]-Lo)<=rad/np.cos(np.radians(L))); return float(postn[mm].sum()), float((pre/pre.sum())[mm].sum())
for k,cd in CANDS.items():
    print(k, 'search cover p2/oi18/oi25', np.round(cov_at(cd['lat'],cd['lon']),2), 'Pleiades-conditional mass within 1 deg (post, pre):', np.round(plei_post_at(cd['lat'],cd['lon']),3),
          'min dist to Pleiades object km', round(min(G.inv(plei.longitude_deg.values,plei.latitude_deg.values,np.full(len(plei),cd['lon']),np.full(len(plei),cd['lat']))[2])/1000))