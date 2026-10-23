fm=pd.read_csv(H+'digitised/royer-2016/royer_figure_marks.csv')
print(fm.columns.tolist()); print(fm[fm.astype(str).apply(lambda c: c.str.contains('H01W')).any(axis=1)].to_string()[:3000])
la,lo=rx['H01W']
for i in [1,2,3,4,5,6,9,10,14,15]:
    e=ev[ev['index']==i].iloc[0]; az=G.inv(lo,la,e.lon_deg,e.lat_deg)[0]%360
    print(i, e.label, e.event_class, round(az,1))