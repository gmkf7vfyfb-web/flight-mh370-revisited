import numpy as np, pandas as pd
KAD = (-26.19, 101.88)
src_times = {"text 00:52:03": "00:34:55", "caption 00:54:30": "00:37:22"}
WIN = {"3250": (2909.2,4754.0), "3274": (3831.7,5098.6), "3275": (3830.4,5097.2), "3315": (2234.0,3704.9), "3376": (2234.5,3706.3)}
ALL = dict(RX); ALL["Perth Canyon 3315"] = (-(31+52.033/60), 115+0.068/60); ALL["Portland 3275"]=(-(38+32.546/60),141+13.535/60)
rows=[]
for nm,(rla,rlo) in ALL.items():
    d = float(gc_km(KAD[0], KAD[1], rla, rlo))
    blk = blocked(KAD[0], KAD[1], (rla,rlo))
    r = {"receiver": nm, "range_km": round(d,0), "land_blocked": blk, "travel_s": round(d/1.48)}
    for lbl,t in src_times.items():
        ts = int(t[:2])*3600+int(t[3:5])*60+int(t[6:])
        arr = ts + d/1.48
        r[f"arrival {lbl}"] = f"{int(arr//3600):02d}:{int(arr%3600//60):02d}:{int(arr%60):02d}"
        key = nm.split()[-1]
        if key in WIN:
            r[f"in window {lbl}"] = WIN[key][0] <= arr <= WIN[key][1]
    rows.append(r)
print(pd.DataFrame(rows).to_string(index=False))
for nm,A in [("run I", S), ("run I dive", np.load("/Users/pete/Downloads/mh370-exchange/end-of-flight/run-i-dive/run-i-dive-subsample.npz", allow_pickle=True))]:
    cc = {str(n):i for i,n in enumerate(A["columns"])}; b=A["baseline"]
    d = gc_km(b[:,cc["latitude_deg"]], b[:,cc["longitude_deg"]], *KAD)
    t = b[:,cc["t_impact_s"]]
    for rad in (100,200,400):
        m = d<rad
        tt = f"{np.median(t[m])/3600:.4f}" if m.sum() else "-"
        hhmm = (f"{int(np.median(t[m])//3600):02d}:{int(np.median(t[m])%3600//60):02d}" if m.sum() else "-")
        print(f"{nm:11s} within {rad:4d} km of Kadri crossing: {m.sum():5d}/20000 draws ({m.mean()*100:5.2f}%)  median impact time {hhmm}")
