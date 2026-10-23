
glon=np.array(pj['lon']); glat=np.array(pj['lat']); gz=np.array(pj['depth_m']); gt=np.array(pj['time_unix_s'])
P=np.memmap(f'{OD}/glorys12/profile/grid_75-115E_45-10S/{pj["data_file"]}',dtype='<f4',mode='r',shape=(8,4,50,421,481))
DO=np.memmap(f'{OD}/glorys12/profile/grid_75-115E_45-10S/{pj["deptho_file"]}',dtype='<f4',mode='r',shape=(421,481))
i=np.argmin(abs(glat-HX[0])); j=np.argmin(abs(glon-HX[1]))
print(glat[i],glon[j],'deptho',DO[i,j])
for v in range(4): print(pj['variables'][v], np.round(P[1,v,[0,10,20,30,40,45,49],i,j],3))
