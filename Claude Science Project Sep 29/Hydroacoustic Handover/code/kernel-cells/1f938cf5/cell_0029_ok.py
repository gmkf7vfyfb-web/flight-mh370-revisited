
e1=json.load(open(f'{OD}/era5/{ej["parts"][0]}'))
for k,v in e1.items():
    print(k, (('list',len(v),json.dumps(v[:3])[:200], v[-1] if v and not isinstance(v[-1],(dict,list)) else '') if isinstance(v,list) else json.dumps(v)[:300]))
print(os.listdir(f'{OD}/era5')[:20])
