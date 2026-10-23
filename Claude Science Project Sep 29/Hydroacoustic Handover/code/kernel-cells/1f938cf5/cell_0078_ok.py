
def parse_dods_ascii(fn,shape):
    txt=open(fn).read(); body=txt.split('---------------------------------------------')[1]
    lines=body.strip().split('\n')[1:]
    arr=np.full(shape,np.nan,np.float32)
    for ln in lines:
        if not ln.startswith('['): break
        idx,vals=ln.split(',',1) if False else (ln[:ln.index(']',ln.rindex('['))+1], ln[ln.index(']',ln.rindex('['))+2:])
        ii=[int(x) for x in idx.strip('[]').split('][')]
        v=np.array([float(x) for x in vals.split(',')]); arr[tuple(ii)]=v
    return arr
shp=(2,40,39,33)
HY={v:parse_dods_ascii(f'hycom/{v}.small.ascii',shp) for v in ['water_u','water_v','water_temp','salinity']}
for v in HY:
    a=HY[v]; a[a==-30000]=np.nan; HY[v]=a*0.001 + (20.0 if v in ('water_temp','salinity') else 0.0)
print({v:(np.nanmin(a),np.nanmax(a)) for v,a in HY.items()})
