
from scipy import stats
ic=pd.read_csv(f"{EX}/imos/imos_candidates.csv",dtype={"receiver":str}); pc=pd.read_csv(f"{EX}/panels/panel_candidates.csv")
t1=pd.read_csv(f"{EX}/named/table1_verdicts.csv")
T0=R.T0
def h2u(s): return Cm.hms_to_unix(s)
t1["t_unix"]=[h2u(s) for s in t1.time_utc]
cand=[]
for _,r in ic.iterrows():
    cand.append(dict(rx=r.receiver,time_utc=r.time_utc,t_unix=r.t_unix,det=r.detector,band=r.band_hz,p=r.p,p_B=np.nan,label=r.label,
        excess=r.excess_5_40_pa2s,eta_needed_searches=r.eta_needed,kadri_label=r.kadri_label,source="IMOS raw recording",panel="",
        in_window=r.in_window_sofar,tl_note=r.tl_note))
for _,r in pc.iterrows():
    cand.append(dict(rx=r.receiver,time_utc=r.time_utc,t_unix=r.t_unix,det=r.detector,band=r.band_hz,p=r.p,p_B=r.p_B,label=r.label,
        excess=np.nan,eta_needed_searches=r.eta_needed,kadri_label=r.kadri_label,source="digitised Kadri (2024) Fig. 9 panel "+r.panel,panel=r.panel,
        in_window=r.in_window_sofar,tl_note=r.tl_note))
C=pd.DataFrame(cand); C["key"]=C.rx+"|"+C.time_utc+"|"+C.det+"|"+C.band
print(len(C), C.key.duplicated().sum())
# reference impact
tpj=json.load(open(R.RD/"tl_grid_run_j"/"table_points.json")); arcpts=sorted([(v["lat"],v["lon"]) for v in tpj.values() if v["offset_nm"]==0])
ARC_LA=np.array([a for a,b in arcpts]); ARC_LO=np.array([b for a,b in arcpts])
ref_lon=float(np.interp(P.REF_LAT,ARC_LA,ARC_LO))
bref,tiref=M.level_base(np.array([P.REF_LAT]),np.array([P.REF_E_J]),np.array([P.REF_TAU_S]))
print("ref",P.REF_LAT,ref_lon,{k:round(float(v[0]),2) for k,v in bref.items()})
w0=Wt["D0"]
def snr_obs_rows(c, rows):
    rx=c["rx"]
    if rx in R.RECEIVERS_GATED and np.isfinite(c["excess"]) and c["excess"]>0:
        return 10*(np.log10(c["excess"])+12-np.log10(M.teff[rx][PP["ti"][rows]]))-M.bmed[rx]
    if np.isfinite(c["eta_needed_searches"]):
        return np.full(len(rows), bref[rx][0]+10*np.log10(c["eta_needed_searches"]))
    return np.full(len(rows), np.nan)
def eta_level_ref(c):
    rx=c["rx"]
    if rx not in R.RECEIVERS: return np.inf
    if rx in R.RECEIVERS_GATED and np.isfinite(c["excess"]) and c["excess"]>0:
        so=10*(np.log10(c["excess"])+12-np.log10(M.teff[rx][tiref[0]]))-M.bmed[rx]
        return float(10**((so-bref[rx][0])/10))
    return float(c["eta_needed_searches"])
C["eta_level_ref"]=[eta_level_ref(c) for _,c in C.iterrows()]
WIN=60.0
def rows_for(rx, tc):
    a=np.searchsorted(tps[rx],tc-WIN); b=np.searchsorted(tps[rx],tc+WIN); r=order[rx][a:b]
    return r[np.isfinite(PP["base"][rx][r])]
def factor(c, rows, bearing=None):
    """returns F [n,K] and K_t [n] for candidate c over row indices rows"""
    rx=c["rx"]; d=PP["d"][rx][rows]
    sig=np.sqrt((d*R.C_SOFAR_SD/R.C_SOFAR**2)**2+R.SIGMA_INJ_S**2+R.SIGMA_CLOCK_S**2)
    z=(PP["tp"][rx][rows]-c["t_unix"])/sig
    K=np.where(np.abs(z)<=R.KERNEL_TRUNC_SIGMA,np.exp(-0.5*z*z)/(np.sqrt(2*np.pi)*sig),0.0)
    par=pd_params(rx,P.DETECTOR_METHOD[c["det"]],c["p"]); ti=PP["ti"][rows]
    snr=PP["base"][rx][rows][:,None]+L10[None,:]+Lcal[rows][:,None]
    with np.errstate(over="ignore"):
        pdv=1/(1+np.exp(-(snr-par[ti,0][:,None])/par[ti,1][:,None]))
    pdv=np.nan_to_num(pdv,nan=0.0)
    so=snr_obs_rows(c,rows)
    A=np.exp(-0.5*((snr-so[:,None])/P.SIGMA_A_DB)**2) if np.isfinite(so).all() else np.ones_like(snr)
    Gb=np.ones(len(rows))
    brs=bearing if bearing is not None else (list(t1.bearing_deg[np.abs(t1.t_unix-c["t_unix"])<=P.BEARING_WINDOW_S]) if rx=="H01W" else [])
    if len(brs):
        Gb=np.mean([stats.t.pdf(((b-baz[rows]+180)%360-180)/P.BEARING_T3_SCALE_DEG,3)/P.BEARING_T3_SCALE_DEG*360 for b in brs],axis=0)
    return K[:,None]*pdv*A*Gb[:,None], K, brs
c0=C[C.key=="H01W|00:52:04|M1b|1-9 (plot)"].iloc[0]; r0=rows_for("H01W",c0.t_unix); F,K,brs=factor(c0,r0)
print(len(r0), brs, (w0[r0]*K).sum(), (w0[r0]*F.mean(1)).sum())
