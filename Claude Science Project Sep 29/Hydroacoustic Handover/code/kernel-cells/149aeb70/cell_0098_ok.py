import numpy as np, pandas as pd
H08S = RX["H08S Diego Garcia S"]
lats = np.arange(-45, -18, 0.1); lons = np.polyval(cf, lats)
dt = (gc_km(lats, lons, *H08S) - gc_km(lats, lons, *H01W))/1.48
tested = (dt>=856) & (dt<=1347)
print("pre-registered pair span 856-1347 s covers arc latitudes "
      f"{lats[tested].min():.1f} to {lats[tested].max():.1f} deg")
print(f"dt required for the bearing-implied crossing at 26.19 S = "
      f"{float(np.interp(-26.19, lats, dt)):.0f} s")
print("implied_lat range in the module's pair table:", round(kp.implied_lat.min(),2), "to", round(kp.implied_lat.max(),2))
print("dt range tested:", round(kp.dt_s.min()), "to", round(kp.dt_s.max()), "s")
for L in (-38,-36,-34,-32,-30,-28,-26.19,-24,-22):
    print(f"  arc lat {L:7.2f}  lon {np.polyval(cf,L):6.2f}  H01W {gc_km(L,np.polyval(cf,L),*H01W):6.0f} km"
          f"  H08S {gc_km(L,np.polyval(cf,L),*H08S):6.0f} km  dt {float(np.interp(L,lats,dt)):6.0f} s"
          f"  {'TESTED' if 856<=float(np.interp(L,lats,dt))<=1347 else 'outside tested span'}")
