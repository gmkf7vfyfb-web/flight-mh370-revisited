z=np.load('ocean/test_drift.npz')
cells=z['cells']; la=GLAT0=-46.0
lat_c=-46+ (cells//136+0.5)*0.25; lon_c=78+(cells%136+0.5)*0.25
import pandas as pd
df=pd.DataFrame({'lat':lat_c,'lon':lon_c,'csiro':z['L|csiro'],'field':z['L|field'],'item':z['L|item'],'ever':z['frac_ever_in_box']})
print(df.pivot_table(index='lat',columns='lon',values='csiro').round(2).iloc[::2, ::2].to_string())
dd=z['days']; print({int(d):round(float(z[f'inbox|{d}'].mean()),3) for d in dd if z[f'inbox|{d}'].mean()>0.005})