
raw = np.fromfile("/Users/pete/Downloads/mh370-ocean-data/woa23/soundspeed/woa23_95A4_m03_c_mean.f32", dtype="<f4")
print(raw.size, nz*wj["nlat"]*wj["nlon"])
import itertools
for shp in [(nz,90,140),(90,140,nz),(140,90,nz),(90,nz,140)]:
    A = raw.reshape(shp)
    # pick index for lat -36.6 -> i=23, lon 102.23 -> j=62 ; depth axis should be smooth
    idx = {"z":slice(None)}
    if shp==(nz,90,140): prof=A[:,i,j]
    elif shp==(90,140,nz): prof=A[i,j,:]
    elif shp==(140,90,nz): prof=A[j,i,:]
    else: prof=A[i,:,j]
    print(shp, np.round(prof[[0,10,20,36,46,66,80,100]],1))
