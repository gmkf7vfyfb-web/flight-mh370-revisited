
ej=json.load(open(f'{OD}/era5/era5_u10_v10_3h.series.json'))
for k,v in ej.items():
    print(k, (('list',len(v),json.dumps(v[:2])[:300]) if isinstance(v,list) else json.dumps(v)[:300]))
