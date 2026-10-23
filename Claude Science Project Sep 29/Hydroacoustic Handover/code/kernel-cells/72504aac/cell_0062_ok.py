
import importlib.util, sys
spec=importlib.util.spec_from_file_location('vc','repo/Claude Science Project Sep 29/results/composer-views-run-j/views_common.py'); vc=importlib.util.module_from_spec(spec); spec.loader.exec_module(vc)
print(vc.NY,vc.NX, vc.ROW_EDGES[:3], vc.ROW_EDGES[-2:])
MP=np.load(X+'/composer/run-j-views-v3.2/maps-v3.npz')
core=MP['D0|core'].reshape(vc.NY,vc.NX); dri=MP['D0|D'].reshape(vc.NY,vc.NX)
print(core.sum(), dri.sum(), core.min())
yc_m=0.5*(vc.ROW_EDGES[:-1]+vc.ROW_EDGES[1:])[:vc.NY]; xc_m=vc.LON0+(np.arange(vc.NX)+0.5)*vc.STEP
for nm,M in [('core',core),('D',dri)]:
    print(nm, 'north of 35S', M[yc_m>-35].sum()/M.sum(), 'north of 33S', M[yc_m>-33].sum()/M.sum())
print(os.path.exists(X+'/hydroacoustics/graphics-2026-10-22/ranked/ranked_pairs.csv'), os.listdir(X+'/hydroacoustics/graphics-2026-10-22') if os.path.exists(X+'/hydroacoustics/graphics-2026-10-22') else None)
