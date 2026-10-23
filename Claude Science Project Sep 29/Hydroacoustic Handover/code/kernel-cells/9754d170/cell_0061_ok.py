
importlib.reload(paths)
L,sh=paths.build('air9_H01W',(p9['a'][1],p9['a'][0]),(p9['b'][1],p9['b'][0]),'95A4',10,'audit/work/air9')
as_=pd.read_csv('audit/work/air9/ssp_air9_H01W.csv')
mm=ms.merge(as_,left_on=['node','depth_m'],right_on=['node','depth_m'])
print('c diff median/p95 (valid)',np.nanmedian(np.abs(mm.c_mean_m_s-mm.c_m_s)),np.nanpercentile(np.abs(mm.c_mean_m_s-mm.c_m_s),95))
sys.path.insert(0,HB+"prepare")
import kraken_tl as K, air9_tl_validation as A
import time
bathy=pd.read_csv('audit/work/air9/bathy_air9_H01W.csv'); ssp=as_
rprof,profiles=A.build_profiles(bathy,ssp)
t0=time.time()
out=[]
for fc in [10.0,31.5]:
    r,tl,nm,dt=K.tl_path('audit/work/air9/k','f%g'%fc,fc,profiles,rprof,np.array([rprof[-1]]),[10.0],[1055.0],A.BOTTOMS['hard'],W+"at",fg=A.FG)
    out.append((fc,float(tl[0,-1]),nm[0]))
print(out, time.time()-t0)
print(mod[(mod.station=='H01W')&(mod.bottom=='hard')&(mod.src_depth_m==10)&(mod.fc_hz.isin([10,31.5]))][['fc_hz','tl_db']])
