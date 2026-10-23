
rng2=np.random.default_rng([P.SEED,5])
lgE=np.linspace(-6,-1,101)
res50={}
for o in ["D0","D2","D3","D4"]:
    w=Wt[o]; pk=rng2.choice(len(w),200_000,p=w/w.sum())
    for a in (0.01,0.05):
        pnd=np.ones((len(pk),len(lgE)))
        for rx in R.RECEIVERS:
            b=PP["base"][rx][pk]; ok=np.isfinite(b)
            par=M.pd_par[(rx,a)]; L50=par[0][PP["ti"][pk]]; sl=par[1][PP["ti"][pk]]
            snr=b[:,None]+10*lgE[None,:]+Lcal[pk][:,None]
            pdv=np.where(ok[:,None],1/(1+np.exp(-(np.nan_to_num(snr,nan=-999)-L50[:,None])/sl[:,None])),0.0)
            pnd*=1-pdv
        pany=1-pnd.mean(0)
        e50=10**np.interp(0.5,pany,lgE); res50[(o,a)]=(e50,float(np.interp(np.log10(ANCH),lgE,pany)))
print({k:(f"{v[0]:.2e}",round(v[1],3)) for k,v in res50.items()})
# energies per option
Eq={}
for o in ["D0","D2","D3","D4"]:
    w=Wt[o]; srt=np.argsort(E); cw=np.cumsum(w[srt])/w.sum(); Eq[o]={q:float(np.interp(q,cw,E[srt])) for q in (0.05,0.25,0.5,0.75,0.95)}
print({o:{q:f"{v:.3g}" for q,v in d.items()} for o,d in Eq.items()})
