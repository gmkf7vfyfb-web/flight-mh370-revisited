
src_lines=open('/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63/9edc3c46-2821-4762-835a-0214ee65b30a/v7cc6bf71_kadri_geom.py').read().split('\n')
KG={}; exec('\n'.join(src_lines[:25]),KG)
arcs={}
for lab,tg in [('c',18400),('p',18463),('m',18337)]:
    pts_=[KG['cross'](tg,0.0,'m0019a',az) for az in np.arange(303.5,309.01,0.25)]
    arcs[lab]=np.array([[p[1],p[2]] for p in pts_])
print(arcs['c'][[0,-1]], 'BTO at HX', KG['bto'](HX[0],HX[1],0.0))
# depth grid for regional map (GEBCO+AusSeabed) at ~1 km
glat_m=np.arange(-27.6,-23.4,0.01); glon_m=np.arange(98.8,103.2,0.01)
LA,LO=np.meshgrid(glat_m,glon_m,indexing='ij'); DEP,AUSM,TIDM=sm.seabed(LA,LO,with_src=True)
# zoom grid around HX at 150 m
zla=np.arange(HX[0]-0.12,HX[0]+0.12,0.0014); zlo=np.arange(HX[1]-0.13,HX[1]+0.13,0.0015)
ZLA,ZLO=np.meshgrid(zla,zlo,indexing='ij'); ZD,ZA,_=sm.seabed(ZLA,ZLO,with_src=True)
print(DEP.shape, np.nanmin(DEP),np.nanmax(DEP), AUSM.mean(), ZA.mean())
