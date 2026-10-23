
g=pd.read_csv("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/raw/passA/tl_grid.csv")
g10=g[g.src_depth_m==10.0]
print(g10.groupby(['receiver','status']).size().unstack(fill_value=0))
ok=g10[g10.status=='ok'].groupby(['receiver'])['src_lat'].agg(['min','max'])
print(ok)
# median TL (over bands) per receiver at a few latitudes
for rx in ['3376','3274','H01W','H08S']:
    s=g10[(g10.receiver==rx)&(g10.status=='ok')].groupby('src_lat').tl_db.median()
    print(rx, {round(k,1):round(v,1) for k,v in s.iloc[::6].items()})
rc = pd.read_csv(f"{RD}/ram_check/imos_tl_ramcorr.csv", dtype={'logger':str}); tlk = pd.read_csv(f"{RD}/stageB/imos_tl.csv", dtype={'logger':str})
m = rc.merge(tlk, on=['quantile','logger','fc_hz','src_depth_m'], suffixes=('_ram','_kr'))
m['delta']=m.tl_db_ram-m.tl_db_kr
print(m[m.src_depth_m==10].groupby(['logger','quantile']).delta.median().unstack().round(1))
