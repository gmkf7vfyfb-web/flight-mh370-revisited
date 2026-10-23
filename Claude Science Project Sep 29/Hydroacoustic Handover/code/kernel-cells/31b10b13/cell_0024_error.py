
t0=time.time()
def nob(cs): return score_set(cs,bearing_override=[])["lnN"]
SG["lnLR_no_bearing"]=SG.lnLR
for i in SG.index[SG.rx=="H01W"]:
    SG.loc[i,"lnLR_no_bearing"]=nob([SG.loc[i].to_dict()])-SG.loc[i,"lnB"]
PRS["lnLR_no_bearing"]=PRS.lnLR
for i in PRS.index[(PRS.rx_a=="H01W")|(PRS.rx_b=="H01W")]:
    a=CID.loc[PRS.loc[i,"cid_a"]].to_dict(); b=CID.loc[PRS.loc[i,"cid_b"]].to_dict()
    if a["rx"] not in R.RECEIVERS or b["rx"] not in R.RECEIVERS: continue
    PRS.loc[i,"lnLR_no_bearing"]=nob([a,b])-PRS.loc[i,"lnB"]
print(round(time.time()-t0,1))
# arc loci (block 11 coincidence method, generalised) on a fine arc + eta for prod P_D = 0.5 at alpha 0.05
fla=np.linspace(ARC_LA.min(),ARC_LA.max(),2001); flo=np.interp(fla,ARC_LA,ARC_LO)
allrx=R.RECEIVERS+["3250"]
rxp=dict(M.rxpos); 
st=pd.read_csv(MOD+"/data/stations.csv") if os.path.exists(MOD+"/data/stations.csv") else None
import run_j_windows as Wm
rxall=Wm.receivers(); print(list(rxall))
DARC={}
for rx in rxall:
    rl_,ro_=rxall[rx]; _,_,dd=G.inv(flo,fla,np.full_like(flo,ro_),np.full_like(fla,rl_)); DARC[rx]=dd/1000
wD0=Wt["D0"]
def arc_loci(rxa,ta,rxb,tb):
    lagp=(DARC[rxb]-DARC[rxa])/R.C_SOFAR; target=tb-ta
    cr=np.where(np.diff(np.sign(lagp-target))!=0)[0]; out=[]
    for i in cr:
        L_=float(np.interp(target,[lagp[i],lagp[i+1]],[fla[i],fla[i+1]])) if lagp[i+1]!=lagp[i] else fla[i]
        lo_=float(np.interp(L_,fla,flo)); da=np.interp(L_,fla,DARC[rxa]); out.append((L_,lo_,ta-da/R.C_SOFAR))
    return out
mass_cache={}
def mass1(L_):
    k=round(L_,2)
    if k not in mass_cache:
        m=np.abs(lat-L_)<=1.0; mass_cache[k]=(float(wD0[m].sum()), m)
    return mass_cache[k]
lg=np.linspace(-6,0,601)
def eta_pd50(cs, L_, lo_):
    if any(c["rx"] not in R.RECEIVERS for c in cs): return np.inf, np.nan
    ms,m=mass1(L_); w=wD0[m]
    if m.sum()<20: return np.nan, np.nan
    Em=float(np.interp(0.5,np.cumsum(w[np.argsort(E[m])])/w.sum(),np.sort(E[m]))); tm=float(np.interp(0.5,np.cumsum(w[np.argsort(tau[m])])/w.sum(),np.sort(tau[m])))
    base,ti=M.level_base(np.array([L_]),np.array([Em]),np.array([tm]))
    both=np.ones_like(lg); lvl=[]
    for c in cs:
        l50,sl,ok=M.pd_par[(c["rx"],0.05)] if P.DETECTOR_METHOD[c["det"]]==R.METHOD else (None,None,None)
        par=pd_params(c["rx"],P.DETECTOR_METHOD[c["det"]],0.05)[ti[0]]
        snr=base[c["rx"]][0]+10*lg; both*=1/(1+np.exp(-(snr-par[0])/par[1]))
        so=snr_obs_rows(c,np.array([0]))[0] if not (c["rx"] in R.RECEIVERS_GATED) else 10*(np.log10(c["excess"])+12-np.log10(M.teff[c["rx"]][ti[0]]))-M.bmed[c["rx"]]
        lvl.append(10**((so-base[c["rx"]][0])/10))
    k=np.argmax(both>=0.5) if (both>=0.5).any() else None
    return (10**lg[k] if k is not None else np.inf), max(lvl)
# check vs composition
a=CID.loc["H01W|00:52:04|M1b|1-9 (plot)|p0.0428508"].to_dict() if "H01W|00:52:04|M1b|1-9 (plot)|p0.0428508" in CID.index else None
print([c for c in CID.index if c.startswith("H01W|00:52:04")], [c for c in CID.index if c.startswith("H08S|01:12:49|M1b")])
