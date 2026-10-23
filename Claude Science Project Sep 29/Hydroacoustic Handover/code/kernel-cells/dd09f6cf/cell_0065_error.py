PODK=['csiro','field','item']; ALS=['0.012','0.005','0.025']
Lgrid={}
for a in ALS:
    for pk in PODK:
        g_=np.full(GNY*GNX+1,np.nan)
        for part in ('sparse','dense'):
            zz=np.load(f'ocean/drift_{part}_{a}.npz'); g_[zz['cells']]=zz[f'L|{pk}']
        Lgrid[(a,pk)]=g_
# MC SE (dense cells)
zz=np.load('ocean/drift_dense_0.012.npz'); print('median per-cell SE csiro dense %.3f'%np.median(zz['Lsd|csiro']))
def E(hist,Lg):
    ok=np.isfinite(Lg)&(hist>0); return float((hist[ok]*Lg[ok]).sum()/hist[ok].sum()), float(hist[~np.isfinite(Lg)&(hist>0)].sum())
surf={}
for d in DK:
    for a in ALS:
        for pk in PODK:
            Lg=Lgrid[(a,pk)]
            Eall,miss=E(H[(d,'all')],Lg)
            row={'all':Eall,'miss_all':miss}
            for mk in MASKS:
                Em,_=E(H[(d,mk)],Lg); m=res[d][mk]['mass']; row[mk]=Em; row[mk+'_comp']=(Eall-m*Em)/(1-m)
            for ak in AK:
                row[ak],_=E(H[(d,ak)],Lg)
            surf[(d,a,pk)]=row
for d in DK:
    r=surf[(d,'0.012','csiro')]
    print(d,'all %.3f strip %.3f comp %.3f X50 %.3f X200 %.3f H50 %.3f | Tcore %.3f Twide %.3f Ccore %.3f Cwide %.3f'%(r['all'],r['strip'],r['strip_comp'],r['X50'],r['X200'],r['H50'],r['Tcore'],r['Twide'],r['Ccore'],r['Cwide']))
# latitude profile near the arc: cells within +-1 deg lon of arc? use D0 hist weighted per lat band
lat_cells=GLAT0+(np.arange(GNY*GNX)//GNX+0.5)*GST
h0=H[('D0','all')][:-1]; Lg=Lgrid[('0.012','csiro')][:-1]
for b0 in range(-42,-14,2):
    m=(lat_cells>=b0)&(lat_cells<b0+2)&(h0>0)&np.isfinite(Lg)
    if m.any(): print(b0, 'core-weighted L_surf %.3f  (mass %.4f)'%((h0[m]*Lg[m]).sum()/h0[m].sum(), h0[m].sum()))