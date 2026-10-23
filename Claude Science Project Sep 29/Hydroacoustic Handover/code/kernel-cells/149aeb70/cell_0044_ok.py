import numpy as np
def q(v, p): v=v[np.isfinite(v)]; return np.percentile(v,p)
rows=[]
for nm in ["baseline"]+[n for n in names if n!="baseline"]:
    A=S[nm]
    g=lambda c: A[:,ci[c]]
    pr=g("peak_rate_w")
    rows.append((nm, q(g("t_impact_s"),50)/60, q(g("velocity_up_mps"),50), q(g("velocity_up_mps"),5),
                 q(g("flight_path_angle_deg"),50), q(g("flight_path_angle_deg"),95),
                 q(g("latent:state_m0019b_vertical_speed_fpm"),50), q(g("latent:max_descent_rate_fpm"),50),
                 q(g("latent:state_m0019b_altitude_ft"),50),
                 q(pr,50), q(pr,90), q(g("tau90_s"),50), (pr>4.678e10).mean()))
hdr=["option","t_imp med (min)","v_up med","v_up p5","fpa med","fpa p95","0019b vs med fpm","max desc med fpm","0019b alt ft","peak med W","peak p90 W","tau90 med","frac loud"]
print(" | ".join(h[:16].ljust(16) for h in hdr))
for r in rows:
    print(" | ".join([str(r[0])[:16].ljust(16)]+[f"{x:16.4g}" for x in r[1:]]))
