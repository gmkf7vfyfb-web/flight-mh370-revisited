cd .tmp/standin; python - <<'EOF'
import pandas as pd, numpy as np, json
M="../hy/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/calibration_events/nielsen_fig5cd_bands.csv"
o=pd.read_csv(M); o=o[o.station=="H10N"].set_index("fc_hz")
t=pd.read_csv("tl/event_tl.csv"); t=t[t.path=="sanjuan-charge-H10N"]
rows=[]
for z in [33.0,30.0,10.0,2.0]:
    tt=t[np.isclose(t.src_depth_m,z)].set_index("fc_hz")
    for fc in o.index:
        s=o.loc[fc]; sig=10*np.log10(10**(s.signal_db/10)-10**(s.noise_db/10))
        rows.append(dict(src_depth_m=z,fc_hz=fc,rl_obs_db=s.signal_db,noise_db=s.noise_db,snr_db=s.snr_db,rl_signal_minus_noise_db=sig,tl_db=tt.loc[fc,"tl_db"],implied_sl_db=sig+tt.loc[fc,"tl_db"],n_modes_min=tt.loc[fc,"n_modes_min"]))
d=pd.DataFrame(rows); d.to_csv("sanjuan_h10n_implied_source.csv",index=False)
summ={}
for z,g in d.groupby("src_depth_m"):
    x=np.log2(g.fc_hz/25.0); y=g.implied_sl_db.values
    A=np.vstack([np.ones_like(x),x]).T; c,res,_,_=np.linalg.lstsq(A,y,rcond=None); r=y-A@c
    se=np.sqrt((r**2).sum()/(len(y)-2)/((x-x.mean())**2).sum())
    summ[str(z)]=dict(median_implied_sl_db=float(np.median(y)),slope_db_per_oct=float(c[1]),slope_se=float(se),detrended_rms_db=float(np.sqrt((r**2).mean())),range_db=[float(y.min()),float(y.max())])
json.dump(summ,open("sanjuan_h10n_implied_source_summary.json","w"),indent=1)
print(d[d.src_depth_m==33].round(1).to_string(index=False)); print(json.dumps(summ,indent=0))
EOF