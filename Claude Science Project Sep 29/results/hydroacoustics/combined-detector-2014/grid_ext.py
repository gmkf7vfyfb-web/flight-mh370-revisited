import sys, os, sqlite3, numpy as np, pandas as pd
sys.path.insert(0, os.getcwd())
from pyproj import Geod
from multiprocessing import Pool
import paths_lib as PL
GEOD=Geod(ellps='WGS84'); NM=1.852
DB='/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63/b3b0fe8f-b907-4214-9c02-18f9a4bf778c/v321ea0f6_hydro_data.sqlite'
con=sqlite3.connect(f'file:{DB}?mode=ro',uri=True)
site=pd.read_sql('select site_id, lat, lon from site',con).set_index('site_id')
rdep=pd.read_sql('select site_id, avg(receiver_depth_m) d from arc_path group by 1',con).set_index('site_id').d
ST=['H01W','H08S','IMOS3315','IMOS3376','IMOS3250','IMOS3274','IMOS3275']
arc=pd.read_csv('arcs-sea-level.csv').dropna(subset=['lon_arc7']); arc_lon=lambda la: float(np.interp(la,arc.lat,arc.lon_arc7))
sub=(0.570,64.252)
grid=[]
for la in np.arange(-20.0,-41.01,-1.0):
    lo=arc_lon(la); az_t,_,_=GEOD.inv(arc_lon(la-0.1),la-0.1,arc_lon(la+0.1),la+0.1)
    cand=[(az_t+90)%360,(az_t-90)%360]; az_c,_,_=GEOD.inv(lo,la,sub[1],sub[0])
    az_nw=min(cand,key=lambda a: abs(((a-az_c+180)%360)-180))
    for off in np.arange(-150,151,25):
        if off==0: glon,glat=lo,la
        else:
            a=az_nw if off>0 else (az_nw+180)%360; glon,glat,_=GEOD.fwd(lo,la,a,abs(off)*NM*1000)
        grid.append(dict(arc_lat=la,offset_nm=int(off),lat=glat,lon=glon))
grid=pd.DataFrame(grid); grid['point_id']=[f'{-r.arc_lat:.0f}S_{r.offset_nm:+d}NM' for r in grid.itertuples()]
def one(a):
    st,i=a; g=grid.iloc[i]; s=site.loc[st]
    q=PL.screen(g.lat,g.lon,s.lat,s.lon,float(rdep[st]))
    return dict(station=st,point_id=g.point_id,arc_lat=g.arc_lat,offset_nm=g.offset_nm,lat=g.lat,lon=g.lon,
                dist_km=q['dist_km'],path_class=q['cls'],baz_at_station_deg=q['baz_rcv_deg'])
if __name__=='__main__':
    with Pool(8) as p: R=p.map(one,[(st,i) for st in ST for i in range(len(grid))])
    G=pd.DataFrame(R); G.to_csv('grid_ext_paths.csv',index=False)
    print(G.groupby('station').path_class.value_counts().unstack().fillna(0))
    # check against the existing +-50 NM table
    old=pd.read_csv('arrival_windows_grid.csv')[['station','point_id','dist_km','path_class']]
    m=G.merge(old,on=['station','point_id'],suffixes=('','_old'))
    print('matched',len(m),'class agree',(m.path_class==m.path_class_old).mean().round(4),'max dist diff km',(m.dist_km-m.dist_km_old).abs().max().round(3))
