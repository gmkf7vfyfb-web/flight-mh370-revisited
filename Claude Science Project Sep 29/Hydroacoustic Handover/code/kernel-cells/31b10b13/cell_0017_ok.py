
spec=importlib.util.spec_from_file_location("rprereg", MOD+"/prepare/ranked_candidates/prereg.py"); P=importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
rng=np.random.default_rng(P.SEED); Lcal=rng.normal(0,R.CAL_L_SD_DB,len(t))
rl,ro=M.rxpos["H01W"]; baz,_,_=G.inv(np.full_like(lon,ro),np.full_like(lat,rl),lon,lat); baz=np.mod(baz,360)
print({rx:(np.isfinite(PP['base'][rx]).mean().round(3), np.nanmedian(PP['base'][rx][np.isfinite(PP['base'][rx])]).round(1)) for rx in R.RECEIVERS})
order={rx:np.argsort(PP["tp"][rx]) for rx in R.RECEIVERS}; tps={rx:PP["tp"][rx][order[rx]] for rx in R.RECEIVERS}
ETA=np.logspace(np.log10(P.ETA_LO),np.log10(P.ETA_HI),P.N_ETA); L10=10*np.log10(ETA)
ALS=[0.001,0.01,0.05,0.1,0.3]
def pd_params(rx, method, alpha):
    a=np.clip(alpha,*P.ALPHA_CLIP); la=np.log10(a); out=[]
    for tt in M.taus:
        L=[];Sl=[];A=[]
        for al in ALS:
            f=M.fits.get(f"{rx}|{method}|{al}|{tt}",{})
            if f.get("L50_re_noise_db") is not None and f.get("slope_db") is not None:
                L.append(f["L50_re_noise_db"]);Sl.append(f["slope_db"]);A.append(np.log10(al))
        out.append((np.interp(la,A,L),np.interp(la,A,Sl)) if A else (np.nan,np.nan))
    return np.array(out)
print(pd_params("H01W","M1b_mf_envelope",0.043).round(2).tolist(), pd_params("3275","M0b_bandenergy",0.008).round(2).tolist())
