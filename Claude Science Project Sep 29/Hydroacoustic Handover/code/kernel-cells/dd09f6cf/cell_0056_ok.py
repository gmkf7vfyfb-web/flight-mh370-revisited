from shapely.geometry import box as sbox
nb=bs.intersection(sbox(99,-27.6,103,-24.5)); nbt=bth.intersection(sbox(99,-27.6,103,-24.5))
print(nb.geom_type, len(getattr(nb,'geoms',[nb])), [round(x,3) for x in nb.bounds])
# width of the strip perpendicular to arc: sample at latitudes
for latq in (-27.0,-26.5,-26.0,-25.5,-25.0):
    hl=LineString([(99,latq),(103,latq)]).intersection(nb)
    segs=[(round(g.bounds[0],3),round(g.bounds[2],3)) for g in getattr(hl,'geoms',[hl]) if not g.is_empty]
    hb=LineString([(99,latq),(103,latq)]).intersection(nbt)
    segb=[(round(g.bounds[0],3),round(g.bounds[2],3)) for g in getattr(hb,'geoms',[hb]) if not g.is_empty]
    print(latq,'bs30',segs,'| bathy',segb)
# top vertices of bs30 north strip
coords=[]
for g in getattr(nb,'geoms',[nb]): coords+=list(g.exterior.coords)
coords=np.array(coords); top=coords[np.argsort(coords[:,1])[-3:]]; print('bs30 top vertices',top.round(4))
oc=np.array(sum([list(g.exterior.coords) for g in poly_oi.geoms],[])); print('OI tracing top', oc[np.argsort(oc[:,1])[-3:]].round(4))