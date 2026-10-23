cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/kadri_package/v2-2026-10-22" && python - <<'EOF'
import pandas as pd, numpy as np, json
d=pd.read_csv('predictions.csv'); m=json.load(open('predictions_meta.json'))
print(d.shape, m['seeds_used'], m['mass']['D0/p0.5'], m['pooled_medians'])
w=d[d.receiver=='H01W']
print('mass by offset', w.groupby('offset_nm')['weight_D0_p0.5'].sum().round(3).to_dict())
lat=w.groupby('lat')['weight_D0_p0.5'].sum(); c=lat.sort_index(ascending=False).cumsum()
print('lat mass top:', lat.sort_values(ascending=False).head(8).round(3).to_dict())
# mass-weighted core cells: top cells by weight
top=w.sort_values('weight_D0_p0.5',ascending=False).head(6)
print(top[['lat','offset_nm','weight_D0_p0.5','weight_D2_p0.5','weight_D3_p0.5','weight_D4_p0.5','impact_q05','impact_q50','impact_q95','ke_q50_j','tau90_q50_s']].to_string())
for rx in ['H01W','H08S']:
    r=d[(d.receiver==rx)]
    # mass-weighted mean SPL at anchor over cells with mass
    mm=r['weight_D0_p0.5']>0
    for eta in ['0.01','0.001','0.00021','0.0001','1e-05']:
        col=f'spl_1s_db_5-40hz_eta{eta}'
        v=r.loc[mm,col]; wgt=r.loc[mm,'weight_D0_p0.5']
        ok=np.isfinite(v)
        q=np.quantile(np.repeat(v[ok].values, np.maximum(1,(wgt[ok]*1e5).astype(int))),[0.05,0.5,0.95])
        print(rx, eta, 'mass-weighted SPL q05/50/95', q.round(1), 'noise', r.noise_median_db.iloc[0] if 'noise_median_db' in r else r['noise_median_db_5-40hz'].iloc[0])
    core=r[(r.lat==-37.0)&(r.offset_nm==0)].iloc[0]
    print(rx,'core 37.0S/0:', {k:core[k] for k in ['range_km','back_azimuth_deg','sofar_start_q05','sofar_end_q95','tl_db_10hz','tl_db_40hz','spl_1s_db_5-40hz_eta0.00021','snr_db_eta2.1e-4','eta_for_snr0','adiabatic_suspect']})
print(d.groupby('receiver').blockage.value_counts().unstack(fill_value=0))
print(d.energy_source.value_counts())
EOF