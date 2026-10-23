
m=json.load(open(paths.OCEAN/"woa23/soundspeed/woa23_95A4_m10.json"))
raw=np.fromfile(paths.OCEAN/"woa23/soundspeed"/m['c_mean_file'],dtype='<f4')
nz=len(m['depth_m']); lat,lon=-27.5612,98.8821
i=int(round(lat-m['lat0'])); j=int(round(lon-m['lon0']))
for shp,idx in [((m['nlat'],m['nlon'],nz),lambda a:a[i,j,:5]),((nz,m['nlat'],m['nlon']),lambda a:a[:5,i,j]),((m['nlon'],m['nlat'],nz),lambda a:a[j,i,:5])]:
    print(shp, idx(raw.reshape(shp)))
print(m['lon0'],m['lat0'])
