
t0=time.time()
def locus_cols(cs):
    out={}
    loc=arc_loci(cs[0]["rx"],cs[0]["t_unix"],cs[1]["rx"],cs[1]["t_unix"])
    if len(cs)==3:   # keep crossings of (a,b) consistent with c's lag within 60 s
        keep=[]
        for L_,lo_,ti_ in loc:
            dc=np.interp(L_,fla,DARC[cs[2]["rx"]]); 
            if abs(ti_+dc/R.C_SOFAR-cs[2]["t_unix"])<=60: keep.append((L_,lo_,ti_))
        loc=keep
    out["n_arc_loci"]=len(loc)
    if not loc: return out
    ms=[mass1(L_)[0] for L_,_,_ in loc]; j=int(np.argmax(ms)); L_,lo_,ti_=loc[j]
    e50,elv,_=eta_req(cs,L_)
    out.update(locus_lat=L_,locus_lon=lo_,implied_impact_utc=hms(ti_),implied_vs_0019="after" if ti_>R.T_0019_LOGON else "BEFORE 00:19:29",
               locus_D0_mass_within_1deg=ms[j],eta_pd50_all_a005=e50,eta_level_locus=elv,
               other_loci=";".join(f"{a:.2f}S {b:.2f}E {hms(c)}" for k,(a,b,c) in enumerate(loc) if k!=j))
    # bearing at H01W of locus vs Kadri bearings
    if any(c["rx"]=="H01W" for c in cs):
        az,_,_=G.inv(rxall["H01W"][1],rxall["H01W"][0],lo_,L_); out["locus_baz_H01W"]=az%360
    return out
lcs=[]
for i,r in PRS.iterrows():
    a=CID.loc[r.cid_a].to_dict(); b=CID.loc[r.cid_b].to_dict(); lcs.append(locus_cols([a,b]))
LC=pd.DataFrame(lcs,index=PRS.index); PRS=pd.concat([PRS.drop(columns=[c for c in LC.columns if c in PRS.columns]),LC],axis=1)
print(round(time.time()-t0,1), PRS.n_arc_loci.value_counts().to_dict())
