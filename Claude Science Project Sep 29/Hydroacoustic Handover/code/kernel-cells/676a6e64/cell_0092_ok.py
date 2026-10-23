import pandas as pd, json, os
S='/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches'
pairs=pd.read_csv(f'{S}/coincidence/pairs.csv'); cs=pd.read_csv(f'{S}/coincidence/coincidence_summary.csv')
imos=pd.read_csv(f'{S}/imos/imos_candidates.csv')
print(pairs.shape, list(pairs.columns)); print(pairs.head(3).T.to_string()[:2500])
print(cs.shape, list(cs.columns)); print(cs.head(40).to_string()[:3500])
print(imos.shape, list(imos.columns))
H='hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/searches_run_j'
print(os.listdir(H+'/panels'), os.listdir(H+'/imos'), os.listdir(H+'/null'))