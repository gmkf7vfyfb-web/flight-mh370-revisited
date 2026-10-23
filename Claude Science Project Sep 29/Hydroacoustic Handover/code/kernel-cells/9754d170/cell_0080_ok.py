
tl=pd.read_csv('audit/work/sus/sus_tl.csv')
b=pd.read_csv('audit/work/sus/paths/bathy_A11_H08S.csv')
sh=b[b.elevation_m>-500]; print(sh[['range_km','lat','lon','elevation_m']].iloc[[0,len(sh)//2,-1]] if len(sh) else 'none', b.range_km.iloc[-1])
pt=tl.pivot_table(index='fc_hz',columns=['site','station','src_depth_m'],values='tl_db').round(1)
print(pt.loc[:, (slice(None),slice(None),915.0)].to_string())
