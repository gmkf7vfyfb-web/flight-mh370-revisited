p1=RT[:,-2,:]; p2=RT[:,-1,:]
az,baz_,dd=G.inv(p1[:,1],p1[:,0],p2[:,1],p2[:,0])
ext_lo,ext_la,_=G.fwd(p2[:,1],p2[:,0],az,dd*(460/600))   # 00:11:49 -> 00:19:29 = 460 s at the last leg speed
EXT=np.c_[ext_la,ext_lo]
sel={}
for k,cd in CANDS.items():
    d=G.inv(np.full(len(EXT),cd['lon']),np.full(len(EXT),cd['lat']),ext_lo,ext_la)[2]/1000
    sel[k]=np.where(d<=120)[0]
    print(k, len(sel[k]), f"{len(sel[k])/len(RT):.4f}")