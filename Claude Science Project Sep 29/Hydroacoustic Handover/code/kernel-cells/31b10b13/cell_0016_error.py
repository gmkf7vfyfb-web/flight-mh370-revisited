
from pyproj import Geod
G=Geod(ellps="WGS84")
idx=np.where(anyw)[0]
lat,lon,t,E,tau=[S[k][idx] for k in ["lat","lon","t_unix","E_j","tau90_s"]]
Wt={o:S[f"w_{o}"][idx] for o in ["D0","D2","D3","D4"]}
t0=time.time()
PP=M.prep(t,lat,lon,E,tau)
rng=np.random.default_rng(P.SEED); Lcal=rng.normal(0,R.CAL_L_SD_DB,len(t))
rl,ro=M.rxpos["H01W"]; baz,_,_=G.inv(np.full_like(lon,ro),np.full_like(lat,rl),lon,lat); baz=np.mod(baz,360)
print(round(time.time()-t0,1), {rx:(np.isfinite(PP['base'][rx]).mean().round(3), np.nanmedian(PP['base'][rx][np.isfinite(PP['base'][rx])]).round(1)) for rx in R.RECEIVERS})
# sorted arrival index per receiver for fast windowing
order={rx:np.argsort(PP["tp"][rx]) for rx in R.RECEIVERS}; tps={rx:PP["tp"][rx][order[rx]] for rx in R.RECEIVERS}
# eta grid
ETA=np.logspace(np.log10(P.ETA_LO),np.log10(P.ETA_HI),P.N_ETA); L10=10*np.log10(ETA)
# P_D params with alpha interpolation
ALS=[0.001,0.01,0.05,0.1,0.3]
def pd_params(rx, method, alpha):
    a=np.clip(alpha,*P.ALPHA_CLIP); la=np.log10(a); out=[]
    for tt in M.taus:
        L=[];Sl=[];A=[]
        for al in ALS:
            f=M.fits.get(f"{rx}|{method}|{al}|{tt}",{})
            if f.get("L50_re_noise_db") is not None and f.get("slope_db") is not None:
                L.append(f["L50_re_noise_db"]);Sl.append(f["slope_db"]);A.append(np.log10(al))
        if len(A)==0: out.append((np.nan,np.nan)); continue
        out.append((np.interp(la,A,L),np.interp(la,A,Sl)))
    return np.array(out)  # [tau,2]
print(pd_params("H01W","M1b_mf_envelope",0.043), pd_params("3275","M0b_bandenergy",0.008))
