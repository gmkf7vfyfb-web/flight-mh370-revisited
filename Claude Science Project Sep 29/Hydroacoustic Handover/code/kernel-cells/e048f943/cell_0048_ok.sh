cd hydro/"Claude Science Project Sep 29"/engine/hypotheses/hydroacoustics/prepare
export PYTHONPATH=.
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels
python - <<EOF
import numpy as np, pandas as pd, json, run_j_levels as RL
pd.set_option('display.width',250)
ex='$OUT'
d=pd.read_csv(f'{ex}/tables/detectable.csv',dtype={'receiver':str})
def frac(hist, eta, thr):
    x=thr-10*np.log10(eta); i=np.searchsorted(RL.SNR_GRID,x,side='left'); return float(hist[max(i-1,0):].sum())
def med(hist):
    c=np.cumsum(hist); 
    if c[-1]<=0: return np.nan
    return float(RL.SNR_GRID[np.searchsorted(c/c[-1],0.5)])
# Table A: matched-filter fraction at eta=2.1e-4 and 1e-3, per option (p=0.5), per receiver
rows=[]
for key in RL.KEYS:
    z=np.load(f'{ex}/levels/{key.replace("/","_")}.npz')
    for st in RL.RECEIVERS:
        h=z[f'{st}/snr1_hist']; r=dict(key=key, receiver=st, snr50_anchor=med(h)+10*np.log10(2.1e-4))
        for tag,hh in (('primary',h),('tau_k',z[f'{st}/snr1_hist_tau_k']),('tau_scenario',z[f'{st}/snr1_hist_tau_scenario'])):
            r[f'mf_anchor_{tag}']=frac(hh,2.1e-4,7); r[f'mf_1e-3_{tag}']=frac(hh,1e-3,7); r[f'base_1e-3_{tag}']=frac(hh,1e-3,15)
        if f'{st}/snr1_hist_kadri_chain' in z.files:
            hk=z[f'{st}/snr1_hist_kadri_chain']; r['snr50_anchor_kadri_chain']=med(hk)+10*np.log10(2.1e-4); r['mf_anchor_kadri_chain']=frac(hk,2.1e-4,7)
        rows.append(r)
T=pd.DataFrame(rows); T.to_csv(f'{ex}/tables/sensitivities.csv',index=False)
p5=T[T.key.str.endswith('/p0.5')]
print(p5.pivot(index='receiver',columns='key',values='mf_anchor_primary').round(3).to_string())
print(p5.pivot(index='receiver',columns='key',values='mf_1e-3_primary').round(3).to_string())
print(p5.pivot(index='receiver',columns='key',values='base_1e-3_primary').round(3).to_string())
print(T[T.key.str.startswith('D0/')].pivot(index='receiver',columns='key',values='mf_anchor_primary').round(3).to_string())
k=T[T.key=='D0/p0.5'][['receiver','snr50_anchor','mf_anchor_primary','mf_anchor_tau_k','mf_anchor_tau_scenario','mf_1e-3_primary','mf_1e-3_tau_k','mf_1e-3_tau_scenario','snr50_anchor_kadri_chain','mf_anchor_kadri_chain']].round(3); print(k.to_string(index=False))
run=json.load(open(f'{ex}/run.json')); print(run['noise_median_5_40_db'], run.get('noise_after_kadri_chain_db'), {k:round(v,3) for k,v in run['kadri_chain_band_weights'].items()})
n=pd.read_csv(f'{ex}/noise/imos_thirdoctave_percentiles.csv',dtype={'logger':str}); print(n[n.band=='5-40'][['logger','set','n_files','n_1s','p05','p10','p50','p90','p95']].to_string(index=False))
import shutil, pathlib
rd=pathlib.Path('../results-data/levels_run_j'); shutil.copy(f'{ex}/noise/imos_thirdoctave_percentiles.csv', rd/'imos_thirdoctave_percentiles.csv'); shutil.copy(f'{ex}/tables/math_check.json', rd/'math_check.json'); shutil.copy(f'{ex}/tables/sensitivities.csv', rd/'sensitivities.csv')
print(sorted(p.name for p in rd.iterdir()))
EOF
du -sh $OUT; du -sh ../results-data/levels_run_j