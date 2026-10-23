
# restore the dropped duplicate (distinct window, distinct p)
C=pd.DataFrame(cand); C["key"]=C.rx+"|"+C.time_utc+"|"+C.det+"|"+C.band
C["eta_level_ref"]=[eta_level_ref(c) for _,c in C.iterrows()]
C["cid"]=[f"{k}|p{p:.6g}" for k,p in zip(C.key,C.p)]
assert not C.cid.duplicated().any()
missing=SG.set_index("key")
extra=C[~C.cid.isin([f"{k}|p{p:.6g}" for k,p in zip(SG.key,SG.p)])]
for _,c in extra.iterrows():
    c=c.to_dict(); s=score_set([c]); SG=pd.concat([SG,pd.DataFrame([{**c,**s}])],ignore_index=True)
SG["cid"]=[f"{k}|p{p:.6g}" for k,p in zip(SG.key,SG.p)]
SG["lnLR"]=SG.lnN-SG.lnB; SG["lnLR_pB"]=SG.lnN-SG.lnB_pB.fillna(SG.lnB)
for o in ["D2","D3","D4"]: SG[f"lnLR_{o}"]=SG[f"lnN_{o}"]-SG.lnB
SG["ln_f_amp_given_time"]=SG.lnN-SG.ln_ftime
print(len(SG), SG.cid.duplicated().sum())
CID=C.set_index("cid")
pr=pd.read_csv(f"{EX}/coincidence/pairs.csv",dtype={"rx_a":str,"rx_b":str})
def find(rx,tt,det,band,p):
    k=f"{rx}|{tt}|{det}|{band}"; m=C[(C.key==k)&np.isclose(C.p,p,rtol=1e-6)]
    return m.iloc[0].to_dict() if len(m) else None
kk=["rx_a","t_a","det_a","band_a","p_a","rx_b","t_b","det_b","band_b","p_b"]
pu=pr.groupby(kk,as_index=False).agg(family=("family",lambda x:"+".join(sorted(set(x)))),lag_s=("lag_s","first"),lag_lo_s=("lag_lo_s","first"),lag_hi_s=("lag_hi_s","first"),
      max_p=("max_p","first"),n_pairs_obs=("n_pairs_obs",lambda x:"/".join(map(str,sorted(set(x))))),p_perm=("p_perm",lambda x:"/".join(f"{v:.3g}" for v in sorted(set(x)))))
print(len(pu))
t0=time.time(); prow=[]; nf=0
for i,r in pu.iterrows():
    a=find(r.rx_a,r.t_a,r.det_a,r.band_a,r.p_a); b=find(r.rx_b,r.t_b,r.det_b,r.band_b,r.p_b)
    if a is None or b is None: nf+=1; continue
    s=score_set([a,b]); prow.append({**r.to_dict(),"cid_a":f"{a['key']}|p{a['p']:.6g}","cid_b":f"{b['key']}|p{b['p']:.6g}",**s,
        "eta_level_ref_a":a["eta_level_ref"],"eta_level_ref_b":b["eta_level_ref"],"src_a":a["source"],"src_b":b["source"],"pB_a":a["p_B"],"pB_b":b["p_B"],
        "kadri_a":a["kadri_label"],"kadri_b":b["kadri_label"]})
PRS=pd.DataFrame(prow); print("not found",nf, round(time.time()-t0,1))
PRS["lnLR"]=PRS.lnN-PRS.lnB; PRS["lnLR_pB"]=PRS.lnN-PRS.lnB_pB.fillna(PRS.lnB)
for o in ["D2","D3","D4"]: PRS[f"lnLR_{o}"]=PRS[f"lnN_{o}"]-PRS.lnB
PRS["ln_f_amp_given_time"]=PRS.lnN-PRS.ln_ftime
print(PRS.sort_values("lnLR",ascending=False)[["rx_a","t_a","det_a","band_a","p_a","rx_b","t_b","det_b","band_b","p_b","lag_s","lnLR","ln_ftime","ln_f_amp_given_time","lnB","n_rows"]].head(15).to_string())
