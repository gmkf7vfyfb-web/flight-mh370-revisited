
for shp,name in [((8,421,481,50,4),'t,lat,lon,z,v'),((8,421,481,4,50),'t,lat,lon,v,z'),((421,481,8,50,4),'lat,lon,t,z,v'),((8,50,421,481,4),'t,z,lat,lon,v')]:
    Q=np.memmap(P.filename,dtype='<f4',mode='r',shape=shp)
    if name=='t,lat,lon,z,v': x=Q[1,i,j]          # (z,v)
    elif name=='t,lat,lon,v,z': x=Q[1,i,j].T
    elif name=='lat,lon,t,z,v': x=Q[i,j,1]
    else: x=Q[1,:,i,j,:]
    print(name, np.round(x[[0,10,20,30,40,45,49]],3).tolist())
