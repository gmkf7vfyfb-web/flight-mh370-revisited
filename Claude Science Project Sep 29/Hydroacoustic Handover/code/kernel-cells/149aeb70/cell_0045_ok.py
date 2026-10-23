import numpy as np
T0019B = 19*60+37  # 00:19:37 UTC in seconds after 00:00
LOUD = 4.678e10
out=[]
for nm in ["baseline"]+[n for n in names if n!="baseline"]:
    A=S[nm]; g=lambda c: A[:,ci[c]]
    t=g("t_impact_s"); alt=g("latent:state_m0019b_altitude_ft"); vs=g("latent:state_m0019b_vertical_speed_fpm")
    pr=g("peak_rate_w"); ta=g("tau90_s")
    dt=np.clip(t-T0019B,1,None)
    implied = alt/(dt/60.0)                      # mean fpm needed from 00:19:37 to impact
    arrest = np.isfinite(vs)&(vs<-8000)
    cont = dt<180                                 # impact within 3 min of 00:19:37
    loud_short = (pr>LOUD)&(ta<2.0)
    out.append((nm, float(np.nanmedian(implied)), float(np.nanmedian(-vs[arrest])) if arrest.any() else np.nan,
                float(arrest.mean()), float(cont.mean()),
                float((pr[cont]>LOUD).mean()) if cont.any() else np.nan,
                float(loud_short.mean()), float(np.median(t[loud_short])/60) if loud_short.any() else np.nan,
                float(np.median(ta[pr>LOUD]))))
h=["option","implied mean fpm","0019 rate fpm","frac >8000fpm","frac impact<3min","loud|<3min","frac loud&short","t med loud&short","tau90 med loud"]
print(" | ".join(x[:17].ljust(17) for x in h))
for r in out:
    print(" | ".join([str(r[0])[:17].ljust(17)]+[f"{x:17.4g}" for x in r[1:]]))
