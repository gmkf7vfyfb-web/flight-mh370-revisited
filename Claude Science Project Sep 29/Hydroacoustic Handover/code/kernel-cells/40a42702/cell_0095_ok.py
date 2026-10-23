
e=ER[(ER.method=="M1b_mf_envelope")&(ER.alpha==0.01)&np.isclose(ER.tau_s,taus[1])]
for lev in (5.0,10.0):
    g=e[e.level_re_noise_db==lev]; print(lev, g[["receiver","t_err_q05_s","t_err_q95_s","t_err_within_5s"]].round(2).to_string(index=False))
