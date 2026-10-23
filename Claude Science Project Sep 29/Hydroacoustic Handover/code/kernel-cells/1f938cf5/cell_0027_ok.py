
Q=np.memmap(P.filename,dtype='<f4',mode='r',shape=(8,421,481,4,50))
for la_ in (-12,-20,-26,-35,-43):
    ii=np.argmin(abs(glat-la_)); print(la_, 'SST',Q[1,ii,j,2,0], 'SSS',Q[1,ii,j,3,0], 'deptho',DO[ii,j], 'nlev valid',np.isfinite(Q[1,ii,j,0]).sum(), 'deepest valid z',gz[np.isfinite(Q[1,ii,j,0])].max() if np.isfinite(Q[1,ii,j,0]).any() else None)
