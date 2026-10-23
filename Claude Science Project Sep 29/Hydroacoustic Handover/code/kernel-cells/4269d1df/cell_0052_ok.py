dtG=np.dtype([('rel','u1'),('env','u1'),('cls','u1'),('fate','u1'),('pos','<f4',(4,2))])
SG={m:np.fromfile(f'hpc/0d37c2df-178b-41c2-ae15-2bb5437a8d9b/snapG-{m}.bin',dtype=dtG) for m in ('globcurrent','glorys12')}
lons=np.array(meta['grid_lons']); lats=np.array(meta['grid_lats']); ngrid=len(lons)*len(lats)
per=1200
for m,a in SG.items():
    assert len(a)==ngrid*per
    gidx=np.arange(len(a))//per   # releases in order within chunks, chunks concatenated in order
    olat=lats[gidx//len(lons)]; olon=lons[gidx%len(lons)]
    for k,tn in ((2,'5 Apr 00Z'),(3,'5 Apr 12Z')):
        lo,la=a['pos'][:,k,0],a['pos'][:,k,1]
        d=hav(HX[0],HX[1],la,lo); inring=(d>=70)&(d<110)
        cnt=np.bincount(gidx[inring],minlength=ngrid)
        print(m,tn,'n in ring',inring.sum(),'origin lon range',olon[inring].min() if inring.any() else None, olon[inring].max() if inring.any() else None,
              'lat',olat[inring].min() if inring.any() else None, olat[inring].max() if inring.any() else None,
              'share from east edge col (>=106)', float((olon[inring]>=106).mean()) if inring.any() else None)
