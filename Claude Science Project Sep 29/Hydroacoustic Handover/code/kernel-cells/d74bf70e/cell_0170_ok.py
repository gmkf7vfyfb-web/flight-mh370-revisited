def clusters(idx):
    if len(idx)==0: return []
    out=[]; s=idx[0]; p=idx[0]
    for v in idx[1:]:
        if v>p+1: out.append((s,p)); s=v
        p=v
    out.append((s,p)); return out
for name,(y0,y1) in {"DGN":(9,134),"DGS":(149,274),"CL":(289,414)}.items():
    rows=np.where((im[y0-8:y1+8, 25:49]<140).sum(1)>0)[0]+y0-8
    cl=clusters(rows); print(name, [(a,b,(a+b)/2) for a,b in cl])
cols=np.where((im[418:432, 40:351]<140).sum(0)>0)[0]+40
print("xlabels", [(a,b,(a+b)/2) for a,b in clusters(cols)])