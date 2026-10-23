cd /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches
python - <<'EOF'
import pandas as pd, json, numpy as np
pd.set_option('display.width',250)
P=pd.read_csv('coincidence/pairs.csv'); p=P[(P.rx_a=='H01W')&(P.rx_b=='3376')]; print(p[['family','t_a','det_a','p_a','t_b','det_b','band_b','p_b','lag_s','max_p','p_perm']].to_string(index=False))
W=pd.read_csv('imos/imos_windows.csv'); r=W[(W.receiver==3376)&(W.t_unix>=1394239900)&(W.t_unix<=1394240000)]; print(r[['time_utc','detector','band_hz','statistic','p','eta_needed']].to_string(index=False))
s=json.load(open('imos/imos_summary.json')); print({k:(v['n_records'],v['n_windows_scored'],v['n_null_windows']) for k,v in s.items() if k in ('3315','3376','3274','3275','3250')})
print(json.load(open('named/named_summary.json')))
PB=pd.read_csv('named/poster_boxes.csv'); print(PB[['box','H01W_arrival_mass_D0','H01W_arrival_mass_D2','H01W_arrival_mass_D3','H01W_arrival_mass_D4','minutes_before_earliest','verdict_timing','min_p_M1b','min_p_D1','min_p_BE_2-5','min_p_BE_5-9']].round(4).to_string(index=False))
e=json.load(open('geometry/energy.json')); print({o:(round(e[o]['ess']), e[o]['lat_q']['q99.5']) for o in e})
g=json.load(open('geometry/run.json')); print(g['n_strata_rows'], g['n_supp_rows'])
EOF
sha256sum_cmd=$(command -v sha256sum || echo "shasum -a 256"); cd /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches && find . -type f ! -name SHA256SUMS -exec $sha256sum_cmd {} + > SHA256SUMS; wc -l SHA256SUMS