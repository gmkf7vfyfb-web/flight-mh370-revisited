import json, pandas as pd, numpy as np
X="/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-metz-f35a"
f3=json.load(open(f"{X}/step3/step3_fits.json"))
rows=[]
for k,v in f3.items():
    rx,var,m,a=k.split("|")[0],"|".join(k.split("|")[1:-2]),k.split("|")[-2],k.split("|")[-1]
    rows.append(dict(rx=rx,var=var,method=m,alpha=a,L50=v['L50_re_noise_db']))
F=pd.DataFrame(rows)
print(F.pivot_table(index=['rx','alpha','var'],columns='method',values='L50').round(1).to_string())
s7=json.load(open("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection/run/summary.json"))
print({rx:{k:round(v,2) for k,v in s7['t_eff_s'][rx].items()} for rx in ('3376','H01W')})