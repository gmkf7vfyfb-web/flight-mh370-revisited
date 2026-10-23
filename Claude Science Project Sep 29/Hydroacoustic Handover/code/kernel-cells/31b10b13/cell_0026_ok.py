
fla=np.linspace(ARC_LA.min(),ARC_LA.max(),2001); flo=np.interp(fla,ARC_LA,ARC_LO)
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
        m=np.abs(lat-L_)<=1.0; mass_cache[k]=(float(wD0[m].sum()), np.where(m)[0])
    return mass_cache[k]
lg=np.linspace(-6,0,601)
def so_at(c, ti0):
    rx=c["rx"]
    if rx in R.RECEIVERS_GATED and np.isfinite(c["excess"]) and c["excess"]>0:
        return 10*(np.log10(c["excess"])+12-np.log10(M.teff[rx][ti0]))-M.bmed[rx]
    return bref[rx][0]+10*np.log10(c["eta_needed_searches"])
def eta_req(cs, L_):
    if any(c["rx"] not in R.RECEIVERS for c in cs): return np.inf, np.inf, np.nan
    ms,m=mass1(L_)
    if len(m)<20: return np.nan, np.nan, ms
    w=wD0[m]; Em=float(np.interp(0.5,np.cumsum(w[np.argsort(E[m])])/w.sum(),np.sort(E[m]))); tm=float(np.interp(0.5,np.cumsum(w[np.argsort(tau[m])])/w.sum(),np.sort(tau[m])))
    base,ti=M.level_base(np.array([L_]),np.array([Em]),np.array([tm])); both=np.ones_like(lg); lvl=[]
    for c in cs:
        par=pd_params(c["rx"],P.DETECTOR_METHOD[c["det"]],0.05)[ti[0]]
        both*=1/(1+np.exp(-(base[c["rx"]][0]+10*lg-par[0])/par[1]))
        lvl.append(10**((so_at(c,ti[0])-base[c["rx"]][0])/10))
    k=np.argmax(both>=0.5) if (both>=0.5).any() else None
    return (10**lg[k] if k is not None else np.inf), max(lvl), ms
a=[c for c in CID.index if c.startswith("H01W|00:52:04")][0]; b=[c for c in CID.index if c.startswith("H08S|01:12:49|M1b")][0]
A_=CID.loc[a].to_dict(); B_=CID.loc[b].to_dict(); A_["cid"]=a; B_["cid"]=b
lc=arc_loci("H01W",A_["t_unix"],"H08S",B_["t_unix"]); print(lc, [hms(x[2]) for x in lc])
print([eta_req([A_,B_],L_) for L_,_,_ in lc])
