import json, numpy as np, pathlib
X=pathlib.Path("/Users/pete/Downloads/mh370-exchange/settling/run-j-supplement/a1-stratified")
z=np.load("/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j-supplement/reduced/impacts-ruleB.npz", mmap_mode="r")
A=json.load(open("/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j-supplement/summary-oct20/a1-strata.json"))
info=json.load(open(X/"rjsa_info.json")); p0=info["pass0"]
f4=np.asarray(z["family4_code"]); om,cr,ra=(np.asarray(z[k]) for k in ("latent:onset_mechanism","latent:control_realised","latent:recovery_attempted"))
br=np.select([(om==2)&(cr==2),(om==2)&(ra==1)],[1,2],0); rest=~((br==1)|((br==2)&(f4==1)))
out={}
for d,c in p0["check"].items():
    w=np.exp(np.asarray(z["lnw:comb/"+d],float)); R=float(w[rest].sum()); RA1=float(w[rest&(f4==1)].sum())
    strat=c["branch1_share"]+c["outside_share"]; a1=strat+RA1
    s=(1-a1)/(R-RA1)   # EoF convention: A1 share = strata + A1 rows outside the strata; other families rescaled to 1 - A1
    out[d]={"rest_mass_reduced":R,"rest_A1_mass":RA1,"strata_A1":strat,"A1_share_eof_convention":a1,"eof_A1_share_stratified":A["cells"].get(d,{}).get("A1_share_stratified"),
            "mixture_A1_share":(strat+RA1)/(R+strat),"outcome_weight_for_rest_rows_nonA1":s,"outcome_weight_for_rest_rows_A1":1.0,"outcome_weight_for_strata_rows":1.0}
    print(d, {k:round(v,5) if isinstance(v,float) else v for k,v in out[d].items()})
json.dump(out,open("eof-convention-weights.json","w"),indent=1)
