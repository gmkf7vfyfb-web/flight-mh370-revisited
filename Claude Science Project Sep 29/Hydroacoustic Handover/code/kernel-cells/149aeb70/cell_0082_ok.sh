cd /Users/pete/Downloads/mh370-exchange/end-of-flight/run-i && python3 - <<'PY'
import numpy as np, json
cols=json.load(open("next-i-free/seed-1/run.json"))["impact_columns"]; ix={c:i for i,c in enumerate(cols)}
a=np.load("next-i-free/seed-1/impacts32.npy",mmap_mode="r")[:600000]
z=np.load("next-i-free/seed-1/tau90_v1.npz")
n=600000
tau=z["tau90_s"][:n]; en=z["energy_transferred_j"][:n]; pk=z["peak_rate_w"][:n]
ws=z["w_steep"][:n]; dg=z["decel_g"][:n]; le=z["l_eff_m"][:n]
vu=np.asarray(a[:,ix["velocity_up_mps"]]); ve=np.asarray(a[:,ix["velocity_east_mps"]]); vn=np.asarray(a[:,ix["velocity_north_mps"]])
sp=np.sqrt(ve**2+vn**2+vu**2); fpa=np.asarray(a[:,ix["flight_path_angle_deg"]])
print("w_steep: unique-ish", np.round(np.quantile(ws,[0,.05,.25,.5,.75,.95,1]),4))
print("tau90   quantiles", np.round(np.quantile(tau,[0,.05,.25,.5,.75,.95,1]),3))
short = tau<1.0
print(f"\nfraction tau90<1s = {short.mean():.3f}")
for nm,v in [("speed m/s",sp),("v_up m/s",vu),("fpa deg",fpa),("energy GJ",en/1e9),("decel_g",dg),("l_eff_m",le),("w_steep",ws)]:
    print(f"  {nm:10s} short: med={np.median(v[short]):9.3f}  long: med={np.median(v[~short]):9.3f}")
print("\ntau vs speed check: median l_eff/speed for short =", np.median(le[short]/sp[short]), " for long =", np.median(le[~short]/sp[~short]))
print("corr(log tau, log speed) =", np.corrcoef(np.log(tau),np.log(sp))[0,1])
print("\nbins of speed -> median tau90")
bs=np.quantile(sp,np.linspace(0,1,11))
for i in range(10):
    m=(sp>=bs[i])&(sp<bs[i+1])
    print(f"  speed {bs[i]:7.1f}-{bs[i+1]:7.1f}  n={m.sum():6d}  tau med={np.median(tau[m]):8.3f}  w_steep med={np.median(ws[m]):.3f}  fpa med={np.median(fpa[m]):6.2f}")
PY