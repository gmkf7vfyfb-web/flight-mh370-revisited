import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from shapely.geometry import box
win=box(99.0,-27.5,103.5,-24.0)
fig,ax=plt.subplots(figsize=(8,7))
def drawgeom(g,**kw):
    gs=getattr(g,'geoms',[g])
    for q in gs:
        if q.geom_type=='Polygon':
            x,y=q.exterior.xy; ax.fill(x,y,**kw)
            for h in q.interiors: x,y=h.xy; ax.fill(x,y,color='white')
        elif hasattr(q,'geoms'): drawgeom(q,**kw)
for k,c in [('bathy150','#cfe'),('bs30','#9cf')]:
    g=make_valid(shape(G[k]['features'][0]['geometry'])).intersection(win)
    drawgeom(g,color=c,alpha=0.7)
oi_t=[f for f in G['caption']['features'] if f['properties']['id']=='OI2018'][0]
g=shape(oi_t['geometry']); 
gb=g.boundary if g.geom_type!='LineString' else g
for q in getattr(gb,'geoms',[gb]): x,y=q.xy; ax.plot(x,y,'r-',lw=1)
ax.plot(101.369,-25.732,'k*',ms=12); ax.plot(101.461,-25.975,'ko')
ax.set_xlim(99,103.5); ax.set_ylim(-27.5,-24); ax.set_aspect(1/np.cos(np.radians(25.7)))
fig.savefig('explore_local.png',dpi=90)
print(oi_t['geometry']['type'])