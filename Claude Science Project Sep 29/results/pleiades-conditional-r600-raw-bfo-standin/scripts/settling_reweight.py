"""Settling reweighting under H (stand-in, 10 Oct 2026): settling core-set (b) samples, field/nrb*, read-only."""
def sm(H): d=gaussian_filter(H,0.1/G,mode='constant'); return d/d.sum()

def areas3(H): d=sm(H); lv=hpd_levels(d,(0.99,0.9,0.5)); return [float(cellkm[d>=l].sum()) for l in lv]

def seabed_w(rows,draws,v):
    st=EL[:,4]==0
    key=EL[st,0].astype(np.int64)*1048576+EL[st,1].astype(np.int64)
    o=np.argsort(key,kind='stable'); key,lat_,lon_,mass=key[o],EL[st,5][o],EL[st,6][o],EL[st,7][o]
    uk,start=np.unique(key,return_index=True); stop=np.r_[start[1:],len(key)]
    tot=np.add.reduceat(mass,start); share=mass/np.repeat(tot,stop-start)
    want=rows.astype(np.int64)*1048576+draws.astype(np.int64)
    pos=np.minimum(np.searchsorted(uk,want),len(uk)-1); ok=uk[pos]==want
    n_el=(stop-start)[pos[ok]]; idx=np.concatenate([np.arange(a,b) for a,b in zip(start[pos[ok]],stop[pos[ok]])])
    vv=np.repeat(v[ok],n_el); w=share[idx]*vv/v.sum()
    Hw=np.histogram2d(lat_[idx],lon_[idx],bins=[le,oe],weights=w)[0]
    imp=TB_[rows,1:3]; Hs=np.histogram2d(imp[:,0],imp[:,1],bins=[le,oe],weights=v)[0]
    il,io=np.repeat(imp[ok,0],n_el),np.repeat(imp[ok,1],n_el)
    off=np.hypot((lat_[idx]-il)*111.2,(lon_[idx]-io)*111.2*np.cos(np.radians(il))); oo=np.argsort(off); c=np.cumsum(w[oo])/w.sum()
    return Hw,Hs,dict(offset_p50_p90_p99=[float(off[oo][np.searchsorted(c,q)]) for q in (0.5,0.9,0.99)],not_computed=int((~ok).sum()),mass_gt5km=float(w[off>5].sum()/w.sum()))

# row matching: (stratum, seed, parent, latitude) -> end-of-flight row -> L_H = mean_m exp(lnL_both_<m>), NaN -> 0
