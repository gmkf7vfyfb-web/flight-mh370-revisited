
import sys, json, importlib, os
AUD="audit/repo/Claude Science Project Sep 29/results/hydroacoustics-audit/"
sys.path.insert(0,AUD+"scripts"); import paths; importlib.reload(paths)
W="/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/d74bf70e-a424-46a9-8149-902d027e782a/"
req=json.load(open(W+"hydro/ocean_paths/request.json"))
pa={p['name']:p for p in req['paths']}
print([k for k in pa if 'air' in k or 'f35' in k])
p9=pa['air9-H01W']; print(p9)
os.makedirs('audit/work',exist_ok=True)
L,sh=paths.build('air9_H01W',(p9['a'][1],p9['a'][0]),(p9['b'][1],p9['b'][0]),'95A4',10,'audit/work/air9')
print(L,sh)
mb=pd.read_csv(W+"hydro/ocean_paths/out/air9-H01W_bathymetry.csv"); ms=pd.read_csv(W+"hydro/ocean_paths/out/air9-H01W_soundspeed.csv")
ab=pd.read_csv('audit/work/air9/bathy_air9_H01W.csv'); as_=pd.read_csv('audit/work/air9/ssp_air9_H01W.csv')
print(mb.columns.tolist()); print(ms.columns.tolist())
dm=np.interp(ab.range_km, mb.s_m/1000, mb.depth_m); print('depth diff median/p95',np.median(np.abs(-ab.elevation_m-dm)),np.percentile(np.abs(-ab.elevation_m-dm),95), 'L module',mb.s_m.iloc[-1]/1000)
n0=ms[ms.node==0]; a0=as_[as_.node==0]; print(np.c_[n0.depth_m.values[:5],n0.c_mean_m_s.values[:5],a0.c_m_s.values[:5]])
