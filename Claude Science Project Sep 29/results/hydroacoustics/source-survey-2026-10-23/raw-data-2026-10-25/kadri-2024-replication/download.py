"""Download IM EDH waveforms, impact-2 h to impact+4 h, all three elements of each triad, in 1-h chunks.
EarthScope FDSN dataselect, anonymous. 4 threads max (shared machine). Output kadri/data/<case>_<triad>.mseed + log."""
import sys, os, io, time
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
import requests
from obspy import read, Stream, UTCDateTime
sys.path.insert(0, os.path.dirname(__file__))
from cases import CASES
URL = "https://service.earthscope.org/fdsnws/dataselect/1/query"
OUT = os.path.join(os.path.dirname(__file__), "..", "data")

def get(net, sta, t0, t1):
    p = dict(net=net, sta=sta, loc="*", cha="EDH", start=t0.strftime("%Y-%m-%dT%H:%M:%S"), end=t1.strftime("%Y-%m-%dT%H:%M:%S"))
    for k in range(3):
        try:
            r = requests.get(URL, params=p, timeout=300)
            if r.status_code == 200:
                return r.status_code, r.content
            if r.status_code == 204:
                return 204, b""
        except Exception as e:
            err = str(e)
        time.sleep(5)
    return -1, b""

jobs = []
for k, c in CASES.items():
    t = c["off_t"]
    for tri in c["own_stations"]:
        for el in "123":
            for h in range(-2, 4):
                jobs.append((k, tri, tri + el, t + timedelta(hours=h), t + timedelta(hours=h + 1)))

def run(j):
    k, tri, sta, a, b = j
    code, data = get("IM", sta, a, b)
    return j, code, data

res = {}
log = open(os.path.join(OUT, "download_log.csv"), "w"); log.write("case,triad,station,start,end,http,bytes\n")
with ThreadPoolExecutor(max_workers=4) as ex:
    for j, code, data in ex.map(run, jobs):
        k, tri, sta, a, b = j
        log.write(f"{k},{tri},{sta},{a:%Y-%m-%dT%H:%M:%S},{b:%Y-%m-%dT%H:%M:%S},{code},{len(data)}\n"); log.flush()
        if data:
            res.setdefault((k, tri), Stream())
            res[(k, tri)] += read(io.BytesIO(data))
for (k, tri), st in res.items():
    st.merge(method=-1)  # merge only overlapping/contiguous segments; keep gaps as separate traces
    st.sort()
    st.write(os.path.join(OUT, f"{k}_{tri}.mseed"), format="MSEED")
    gaps = st.get_gaps()
    print(k, tri, len(st), "traces;", [(tr.id, str(tr.stats.starttime)[:19], str(tr.stats.endtime)[:19]) for tr in st][:9], "gaps:", [(g[1], str(g[4])[:19], round(g[6], 1)) for g in gaps][:6])
log.close()
