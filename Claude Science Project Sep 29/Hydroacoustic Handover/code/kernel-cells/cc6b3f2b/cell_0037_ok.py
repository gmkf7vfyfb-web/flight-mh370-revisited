
import numpy as np, json, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy import signal
T = np.load("out/templates/templates_raw.npz"); print(json.load(open("out/templates/template_build.json"))["n_modes_min"], T["n_modes"].max(), T["H"].shape)
fs=float(T["fs"]); Tn=float(T["T"]); t=np.arange(int(Tn*fs))/fs
H=T["H"]; print("TL at 2200 km, 5/10/20/40 Hz:", [round(-20*np.log10(abs(H[np.argmin(abs(T['freqs']-f)),1])),1) for f in (5,10,20,40)])
fig,ax=plt.subplots(3,2,figsize=(12,8))
for j,r in enumerate(T["ranges_km"]):
    a=ax.flat[j]
    for key,c in (("h","C0"),("h2","C1")):
        h=T[f"{key}_{r:.1f}"]; e=np.convolve(h**2,np.ones(64)/64,"same"); a.plot(t,10*np.log10(e/e.max()+1e-9),c,lw=0.7,label=key)
    a.set_title(f"{r:.0f} km"); a.set_ylim(-40,2); a.legend()
fig.tight_layout(); fig.savefig("out/templates/template_check.png",dpi=80)
# energy centroid / spread
for key in ("h","h2"):
    h=T[f"{key}_2200.0"]; e=h**2; c=np.sum(t*e)/e.sum(); cs=np.cumsum(e)/e.sum(); print(key, "centroid %.1f s, 5-95%% span %.1f-%.1f s"%(c, t[np.searchsorted(cs,0.05)], t[np.searchsorted(cs,0.95)]))
