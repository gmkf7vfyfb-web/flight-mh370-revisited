print(f[140:300,44:60].min(axis=1)[:5])
for y0,y1 in [(9,134),(149,274),(289,414)]:
    seg=f[y0:y1+1,40:60]
    t=[y0+i for i in range(seg.shape[0]) if (seg[i]<140).sum()>=3]
    print(t)
seg=f[405:425,51:340]; print([51+j for j in range(seg.shape[1]) if (seg[:,j]<140).sum()>=4])