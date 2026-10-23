print({(c['key'][:2],c['variant']):c['n_compatible_rows'] for c in CH2 if c['variant'] in ('T1.0','C1.0')})
print([f"{rg}:{g1(q1m,HK[0],rg,'share'):.5f}" for rg in ['H50','H100','H200','H400','X50','X100','X400']])
# Haixun cell inside 99% HPD?
hi=int((W.HX[0]-W.LOC['lat0'])/0.05); hj=int((W.HX[1]-W.LOC['lon0'])/0.05)
for d in range(6):
    k=HK[d]; out=[]
    for vn in ('T1.0','C1.0'):
        H,_=getmap('main',k,vn); l=hpd_levels(H); v=H[hi-1:hi+2,hj-1:hj+2].max(); out.append((vn, 'in50' if v>=l[0] else 'in90' if v>=l[1] else 'in99' if v>=l[2] else 'outside99'))
    print(d,out)
print(M.t_imp_min.max(), M.aloft_after_fo_min.max())