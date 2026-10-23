
from pyproj import Geod
G = Geod(ellps="WGS84")
print(RC.C_SOFAR, getattr(RC,"C_SOFAR_SD",None), RS.T0 if hasattr(RS,"T0") else None)
T0 = 1394236800.0
tp = json.load(open(os.path.join(MOD,"results-data/tl_grid_run_j/table_points.json")))
pts = sorted([(v["lat"], v["lon"]) for v in tp.values() if v["offset_nm"] == 0])
arc_la = np.array([p[0] for p in pts]); arc_lo = np.array([p[1] for p in pts])
print(len(pts), arc_la.min(), arc_la.max())
RX = W.receivers()   # 14 receivers
print(RX)
def dist_km(lat, lon, rx):
    lat=np.atleast_1d(np.asarray(lat,float)); lon=np.atleast_1d(np.asarray(lon,float))
    rl, ro = RX[rx]
    _,_,d = G.inv(lon, lat, np.full_like(lon, ro), np.full_like(lat, rl)); return d/1000.
# IMOS record UTC spans (convention A, as imos_search)
rec = pd.read_csv(os.path.join(MOD,"data/imos/recordings.csv"), dtype={"logger":str})
meta = P.parse_meta()
import imos_search as IS
t_s=[];t_e=[]
for _, r in rec.iterrows():
    f = RS.IMOS_ROOT / r.file
    fs, first, n, _ = P.header(f)
    ts = first.timestamp() + IS.subsec(f) - P.clock_err(meta[r.logger], first)
    t_s.append(ts); t_e.append(ts + n/fs)
rec["t_start"]=t_s; rec["t_end"]=t_e
def hms(t):
    s = t - T0; sign = "-" if s<0 else ""; s=abs(s)
    return f"{sign}{int(s//3600):02d}:{int(s%3600//60):02d}:{s%60:04.1f}"
print(rec.groupby("logger").apply(lambda g: (len(g), hms(g.t_start.min()), hms(g.t_end.max()))).to_dict())
