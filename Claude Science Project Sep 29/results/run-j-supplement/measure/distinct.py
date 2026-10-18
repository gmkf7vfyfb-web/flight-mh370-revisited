import numpy as np, sys, pathlib
for sd in sys.argv[1:]:
    S=np.load(pathlib.Path(sd)/'handoff-m0011-supplement/handoff.npy'); P=np.load(pathlib.Path(sd)/'handoff-m0011/handoff.npy')
    out=[]
    for H in (S,P):
        _,sid=np.unique(H[:,[1,2,3,8]],axis=0,return_inverse=True); sid=sid.ravel(); lat=H[:,1]; w=H[:,0]*np.exp(H[:,13])
        row=[]
        for lo,hi in ((-34.5,-29.5),(-29.5,-25.5),(-25.5,-21)):
            b=(lat>lo)&(lat<=hi); ws=np.bincount(sid[b],w[b]); ws=ws[ws>0]
            row.append(f"{b.sum():6d}/{len(ws):6d}/{(ws.sum()**2/(ws**2).sum()) if len(ws) else 0:6.0f}")
        out.append(" ".join(row))
    print(pathlib.Path(sd).name, "| supp rows/distinct/ESS:", out[0], "| normal:", out[1])
