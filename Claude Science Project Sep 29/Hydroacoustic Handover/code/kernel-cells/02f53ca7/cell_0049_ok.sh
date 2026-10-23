AT=$PWD/tools; cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1
python - <<EOF
import sys; sys.path.insert(0,'.'); import numpy as np, pandas as pd, air9_tl_validation as A, kraken_tl as K
W='/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tlrecal/'
for name,bb,ss in [('a7p50','bathy_air7off+50_H01W.csv','ssp_air7_H01W.csv'),('a7p0','bathy_air7off+0_H01W.csv','ssp_air7_H01W.csv'),('a9','bathy_air9_H01W.csv','ssp_air9_H01W.csv')]:
    b=pd.read_csv(W+'sections/builder/'+bb); s=pd.read_csv(W+'sections/builder/'+ss); rprof,prof=A.build_profiles(b,s); L=rprof[-1]
    rr=np.append(np.arange(25,L,25),L)
    r,tl,nm,_=K.tl_path(W+'scratch_prof',name,31.5,prof,rprof,rr,[10.0],[1055.0],A.BOTTOMS['hard'],'$AT',fg=A.FG)
    cyl=10*np.log10(rr*1000)
    ex=tl[0]-cyl
    D=np.array([p[0] for p in prof])
    print(name,'L',int(L),'TL end',round(tl[0][-1],1),'modes',min(nm),max(nm))
    print('  range:excess over 10log r ', [(int(x),round(float(e),1)) for x,e in zip(rr[::8],ex[::8])])
    # where the excess jumps
    j=np.diff(ex); big=np.nonzero(np.abs(j)>3)[0]; print('  jumps >3 dB at', [(int(rr[i]),round(float(j[i]),1), int(D[np.argmin(np.abs(rprof-rr[i]))])) for i in big])
EOF