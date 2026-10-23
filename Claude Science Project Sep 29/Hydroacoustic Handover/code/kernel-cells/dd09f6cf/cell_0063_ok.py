from PIL import Image
im=np.array(Image.open('dl/gebco_tid_corridor.png').convert('RGBA'))
blk=(im[...,3]>128)&(im[...,:3].sum(-1)<200)
ny,nx=blk.shape
lons=90+(np.arange(nx)+0.5)*13/nx; lats=-24-(np.arange(ny)+0.5)*13/ny
LO,LA=np.meshgrid(lons,lats)
from shapely import contains_xy
inB=contains_xy(bth,LO,LA); inOI=contains_xy(poly_oi,LO,LA)
p2=make_valid(shape([f for f in G['caption']['features'] if f['properties']['id']=='ATSB'][0]['geometry']))
inP2=contains_xy(p2,LO,LA)
sel=inOI&~inB&~inP2
print('OI-only pixels',sel.sum(),'black frac %.3f'%blk[sel].mean())
print('Phase1 bathy pixels black frac %.3f'%blk[inB].mean())
for la0,la1 in [(-30,-28),(-28,-26.5),(-26.5,-24.7),(-33,-30)]:
    m=sel&(LA>=la0)&(LA<la1); print(la0,la1,'OI-only px',m.sum(),'black %.3f'%(blk[m].mean() if m.sum() else np.nan))