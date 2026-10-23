
rs=pd.read_csv(f"{RDOUT}/ranked_singles_raw.csv",dtype={"rx":str}); rp=pd.read_csv(f"{RDOUT}/ranked_pairs_raw.csv"); rt=pd.read_csv(f"{RDOUT}/ranked_triples_raw.csv")
a=SG.set_index("cid").lnLR; b=rs.set_index("cid").lnLR.reindex(a.index)
fin=np.isfinite(a)
print("singles max|d|", np.nanmax(np.abs(a[fin]-b[fin])), (np.isfinite(b)==fin).all())
k=lambda d: d.cid_a+"&"+d.cid_b
a2=pd.Series(PRS.lnLR.values,index=k(PRS)); b2=pd.Series(rp.lnLR.values,index=k(rp)).reindex(a2.index); f2=np.isfinite(a2)
print("pairs max|d|", np.nanmax(np.abs(a2[f2]-b2[f2])), len(rp))
a3=pd.Series(TR.lnLR.values,index=TR.cids); b3=pd.Series(rt.lnLR.values,index=rt.cids).reindex(a3.index); f3=np.isfinite(a3)
print("triples max|d|", np.nanmax(np.abs(a3[f3]-b3[f3])), len(rt))
lc=pd.Series(PRS.eta_pd50_all_a005.values,index=k(PRS)); lr=pd.Series(rp.eta_pd50_all_a005.values,index=k(rp)).reindex(lc.index)
print("eta max rel", np.nanmax(np.abs(lc/lr-1)[np.isfinite(lc)]))
