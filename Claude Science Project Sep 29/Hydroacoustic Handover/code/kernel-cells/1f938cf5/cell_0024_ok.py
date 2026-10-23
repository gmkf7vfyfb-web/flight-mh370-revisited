
PJ=f'{OD}/glorys12/profile/grid_75-115E_45-10S/glorys12v1_uo_vo_thetao_so_75-115E_45-10S_20140307-20140314.profile.json'
pj=json.load(open(PJ))
for k,v in pj.items():
    if isinstance(v,list): print(k,'list',len(v),v[:3],v[-2:] if len(v)>3 else '')
    else: print(k, json.dumps(v)[:300])
