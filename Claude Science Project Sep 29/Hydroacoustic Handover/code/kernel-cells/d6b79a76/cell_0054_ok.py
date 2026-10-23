import pickle, pandas as pd, numpy as np, importlib, json
importlib.reload(A)
seeds=pickle.load(open('kh/out/seeds.pkl','rb')); print(len(seeds), pd.Series([s['stratum'] for s in seeds]).value_counts().to_dict())
print(open('kh/run.log').read().count('lock acquired'), [l for l in open('kh/run.log') if 'lock' in l])
REG=['all','strip','X50','X100','X200','X400','H50','H100','H200','H400']
q1m=pd.DataFrame(A.q1_table(seeds,'main',W.KEYS,REG)); q1j=pd.DataFrame(A.q1_table(seeds,'joined',[f'D{d} joined V2' for d in range(5)],REG))
# reproduce EoF mixture table
mix=json.load(open('/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/summary/table-0019-mixture.json'))
for k in W.KEYS[:6]+W.KEYS[6:8]:
    S=seeds; tot=A.L(r['prior'][k]['all']['l1'] for r in S if A.pool_of(r)=='main'); l2=A.L(r['prior'][k]['all']['l2'] for r in S if A.pool_of(r)=='main')
    c=mix['cells'][k]; print(k, round(tot,4), round(c['ln_Z'],4), round(np.exp(2*tot-l2)), round(c['eff_impacts']))
cols=['key','region','share','ess','eff_parents','parents_positive','A1_share_in_region','A2_share_in_region','B_share_in_region','C1_share_in_region','seed_share_se']
print(q1m[q1m.key.str.contains('total')&q1m.region.isin(['strip','X50','X100','X200','X400','H200'])][cols].round(5).to_string())