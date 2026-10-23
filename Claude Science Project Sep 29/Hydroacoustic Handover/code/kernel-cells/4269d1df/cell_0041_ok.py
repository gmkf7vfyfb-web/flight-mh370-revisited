rel=json.load(open('L_releases.json'))
pts=[(r['point'],r['lat'],r['lon']) for r in rel if r['branch']=='T']
rng=np.random.default_rng(7)
def sband(m,lat):
    if m=='mean': return None
    return nsb[m][str(int(np.floor(lat)))]
def lnL_noise(lat,lon,m,opt,nrep=4000):
    nid,W=corners(lat,lon); nid=nid[0]; W=W[0]
    if m=='mean':
        a=[];
        for mm in ('glorys12','globcurrent'):
            Ln=node_L(mm,'h50',opt)[nid]; s=np.array([sband(mm,alat_n[k]) for k in nid])
            pert=Ln*np.exp(rng.normal(-s**2/2,s,(nrep,4))); a.append((pert*W).sum(1))
        v=0.5*(a[0]+a[1])
    else:
        Ln=node_L(m,'h50',opt)[nid]; s=np.array([sband(m,alat_n[k]) for k in nid])
        v=((Ln*np.exp(rng.normal(-s**2/2,s,(nrep,4))))*W).sum(1)
    lv=np.log(v)+LREF; return float(np.std(lv))
OPT={'none':'none','B':'B','C':'C','populated':'populated-only (reconstructed)'}
rows=[]
for name,la,lo in pts:
    for m in ('glorys12','globcurrent','mean'):
        for ok_,o in OPT.items():
            l=float(lnL_at(la,lo,m,opt=o)[0]); sd=lnL_noise(la,lo,m,o)
            for D in [f'D{d}' for d in range(6)]:
                ref=aus['cells'][D][f'{o}|{m}']['dlnZ_drift']
                refsd=an['cells'][D][f'{m}_h50']['transport_noise']['dlnZ_drift'][0]
                rows.append(dict(point=name,lat=la,lon=lo,model=m,option=ok_,D=D,lnL_point=l,sd_point=sd,lnZ_runJ=ref,sd_ref=refsd,LLR=l-ref,sd_LLR=float(np.hypot(sd,refsd))))
ex=pd.DataFrame(rows)
print(ex[(ex.D=='D0')&(ex.model=='mean')][['point','option','lnL_point','lnZ_runJ','LLR','sd_LLR']].round(2).to_string())
