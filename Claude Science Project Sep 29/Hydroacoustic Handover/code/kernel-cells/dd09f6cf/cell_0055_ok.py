GNY,GNX=152,136
HK=['all','strip']+[f'X{r}' for r in (50,100,200,400)]+[f'H{r}' for r in (50,100,200,400)]+AK
H={}
for d in DK:
    for hk in HK:
        extra = hk if hk in AK else None
        L=seedlist(d,extra); cm=max(c for *_,c in L)
        h=sum(np.exp(c-cm)*Z[s][i][f'{d}|hist|{hk}'] for s,i,c in L)
        H[(d,hk)]=h/ h.sum() if h.sum()>0 else h
print('outside grid share D0', H[('D0','all')][-1])
need=np.zeros(GNY*GNX,bool)
for d in DK:
    for hk in HK:
        need |= H[(d,hk)][:-1]>1e-7
cells_all=np.flatnonzero(need)
print(len(cells_all), 'mass covered D0 all: %.6f'%H[('D0','all')][:-1][need].sum())
# dense cells: within strip/X400 or acoustic-weighted
dense=np.zeros(GNY*GNX,bool)
for d in DK:
    for hk in ['strip','X400','H400']+AK: dense |= H[(d,hk)][:-1]>0
dense&=need
print('dense',dense.sum())
np.save('ocean/cells_sparse.npy',np.flatnonzero(need&~dense)); np.save('ocean/cells_dense.npy',np.flatnonzero(dense))