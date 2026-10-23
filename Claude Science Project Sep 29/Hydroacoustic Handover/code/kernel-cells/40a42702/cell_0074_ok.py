
import eta_map as EM; importlib.reload(EM)
S0=np.load(OUT+"/inputs/subsample.npz"); Sx={k:S0[k][::400] for k in S0.files}
lat=Sx["lat"].astype(float); E=Sx["E_j"].astype(float); tau=Sx["tau90_s"].astype(float)
lats,tab,delta=EM.tl_tables()
print("E median GJ", np.nanmedian(E)/1e9, "lat q", np.nanpercentile(lat,[5,50,95]))
for rx in ["3376","H01W","3274"]:
    TL=EM.tl_for_rows(lat,rx,lats,tab,delta); print(rx, "TL med per band", np.nanmedian(TL,0).round(1), "blocked", (~np.isfinite(TL).any(1)).mean())
tg=np.logspace(np.log10(0.02),np.log10(30),60); SB=np.vstack([EM.band_fraction(fc,1.0/tg,2.0) for fc in R.BANDS_HZ]).T if False else None
from imos_stageB_map import band_fraction
SB=np.vstack([band_fraction(fc,1.0/tg,2.0) for fc in EM.R.BANDS_HZ]).T; print("Sb sum 5-40 at tau 0.1/3.3/10:", [round(SB[np.abs(tg-t).argmin()].sum(),4) for t in (0.1,3.3,10)])
summ=json.load(open(RUNO+"/summary.json")); print({rx: {k:round(v,2) for k,v in summ["t_eff_s"][rx].items()} for rx in ["3376","H01W"]})
# manual SPL at eta 1e-4 for median row at 3376
TL=EM.tl_for_rows(lat,"3376",lats,tab,delta); i=np.argsort(lat)[len(lat)//2]
sb=SB[np.abs(tg-tau[i]).argmin()]; se=1e-4*E[i]*EM.R.RHO_C/(2*np.pi)*np.nansum(sb*10**(-TL[i]/10))/1.2
print("row lat",lat[i],"E",E[i]/1e9,"tau",tau[i],"TL",TL[i].round(1),"SPL",10*np.log10(se/1e-12),"bmed",summ["bg_median_level_db"]["3376"])
