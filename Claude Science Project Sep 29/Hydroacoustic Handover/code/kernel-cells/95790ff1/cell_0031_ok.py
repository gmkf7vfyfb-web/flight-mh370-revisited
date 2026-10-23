def panel(y0,y1): return f[y0+2:y1-1,53:338]
for name,(y0,y1) in zip(["DGN","DGS","CL"],[(9,134),(149,274),(289,414)]):
    p=panel(y0,y1); h=np.bincount(p.ravel()//20,minlength=13); print(name,h)