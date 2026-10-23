import numpy as np
T=T0019B
def tab(nm):
    A=S[nm]; f4=A[:,ci["family_code"]]; t=A[:,ci["t_impact_s"]]; p=A[:,ci["peak_rate_w"]]
    vs=A[:,ci["latent:state_m0019b_vertical_speed_fpm"]]
    out=[]
    for k in np.unique(f4):
        m=f4==k
        out.append((int(k), m.mean(), ((t-T)[m]<180).mean(), (p[m]>LOUD).mean(),
                    float(np.nanmedian(vs[m]))))
    return out
print("family_code | share | dive<3min | loud | median 0019b fpm")
for nm in ["baseline","both/no-offset","r1200/no-offset","r600/no-offset"]:
    print("##", nm)
    for r in tab(nm):
        print(f"   {r[0]}  share={r[1]:.3f}  dive={r[2]:.3f}  loud={r[3]:.3f}  vs={r[4]:9.0f}")
