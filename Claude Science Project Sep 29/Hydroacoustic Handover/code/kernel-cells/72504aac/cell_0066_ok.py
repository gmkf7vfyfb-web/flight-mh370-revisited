
def hpd_at(M,lat,lon):
    i=np.argmin(np.abs(yc_m-lat)); j=np.argmin(np.abs(xc_m-lon)); v=M[i,j]; return M[M>=v].sum()/M.sum()
for nm,M in [('core sm',CS),('D sm',DS_),('core raw',core),('D raw',dri)]:
    print(nm, {k:round(hpd_at(M,LOCI[k]['lat'],LOCI[k]['lon']),3) for k in LOCI})
