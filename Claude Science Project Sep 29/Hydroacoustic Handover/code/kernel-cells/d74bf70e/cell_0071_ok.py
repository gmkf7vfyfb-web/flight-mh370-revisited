import pandas as pd
WHITE=np.array([255,255,255.]); BLUE=np.array([0,114,189.]); ORNG=np.array([217,83,25.])
def alpha(c):
    d = c - WHITE; v = im - WHITE
    a = (v @ d) / (d @ d)
    res = np.linalg.norm(v - a[...,None]*d, axis=2)
    return np.where(res < 18, a, 0.0)
aB, aO = alpha(BLUE), alpha(ORNG)
X0,X1 = 119, 824; KM = lambda x: (x-X0)/(X1-X0)*3500
# --- top panel: dB = -80 at y=64, -180 at y=409
T0,T1 = 64, 409; DB = lambda y: -80 - (y-T0)/(T1-T0)*100
mask_leg_top = np.zeros((H,W),bool); mask_leg_top[66:120, 688:800] = True
def series_top(a):
    m = (a >= 0.5) & ~mask_leg_top
    m[:T0+1] = False; m[T1:] = False; m[:, :X0+1] = False; m[:, X1:] = False
    ys, xs = np.nonzero(m); return KM(xs), DB(ys)
rows=[]
for name,a in [("MH370",aB),("F35",aO)]:
    km, db = series_top(a)
    bins = np.arange(0, 3500+25, 25.0)
    idx = np.digitize(km, bins)-1
    for i in range(len(bins)-1):
        v = db[idx==i]
        if len(v)==0: rows.append((name,bins[i]+12.5,0,*([np.nan]*6))); continue
        rows.append((name, bins[i]+12.5, len(v), np.median(v), np.quantile(v,.1), np.quantile(v,.9), v.min(), v.max(),
                     10*np.log10(np.mean(10**(v/10)))))
top = pd.DataFrame(rows, columns=["path","range_km","n_pixels","median_db","p10_db","p90_db","min_db","max_db","power_mean_db"])
print(top.groupby("path").apply(lambda d: d.iloc[[0,4,20,40,60,80,100,120,128,130,135]][["range_km","n_pixels","median_db","power_mean_db"]]).to_string())
