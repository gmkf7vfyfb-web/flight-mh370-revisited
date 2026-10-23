
PC=json.load(open(RUNO+"/proxy_check.json"))
for st in ("H01W","H08S"):
    b=PC[st]["bands"]; print(st, "offset",round(PC[st]["offset_db"],1), {k:(round(v["blackman_median"],1), round(v["shaped_median"],1), round(v["blackman_q90"]-v["blackman_q10"],1)) for k,v in b.items()})
print(PC["kadri_panel_b"])
ER=pd.read_csv(RUNO+"/errors.csv", dtype={"receiver":str})
e=ER[(ER.method=="M1b_mf_envelope")&(ER.alpha==0.01)]
print(e.groupby(["receiver","level_re_noise_db"])[["t_err_median_s","t_err_q05_s","t_err_q95_s","t_err_within_5s","amp_err_median_db","n_det"]].mean().loc[(slice(None),[0.0,5.0,10.0,15.0,20.0]),:].round(2).to_string())
