
import json, numpy as np, pandas as pd
HY="hrepo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/"
j=json.load(open(HY+"results-data/blackman_noise/blackman_noise_summary.json"))
def keys(o,p='',d=0):
    if isinstance(o,dict) and d<3:
        for k,v in o.items():
            if not isinstance(v,dict): print(p+'/'+k, str(v)[:80])
            else: keys(v,p+'/'+k,d+1)
keys({k:v for k,v in j['stations']['H01W'].items() if not k.startswith('psd')})
print([k for k in j if k!='stations'])
print({k:j[k] for k in j if k not in ('stations','provenance')}.__repr__()[:800])
ks=json.load(open(HY+"results-data/kadri_northern/summary.json")); print(ks['median_shot_E_peak'], ks['h08s_predicted'].keys())
t=json.load(open(HY+"results-data/h08s_template/h08s_template.json")); print(t['injection_pd'][:3], len(t['injection_pd']))
