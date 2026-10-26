"""Map open IMS hydrophone availability at EarthScope FDSN dataselect (net IM, cha EDH) by short probes.
The FDSN availability service (fdsnws/availability, irisws/availability) returned 404 'retired' on 24 Oct 2026,
so each element-day is probed with two 30 s requests (00:30:00 and 12:00:00 UTC). HTTP 200 with bytes = data."""
import csv, datetime as dt, time, requests, sys
from concurrent.futures import ThreadPoolExecutor
URL = "https://service.earthscope.org/fdsnws/dataselect/1/query"
EL = [f"{s}{i}" for s in ("H01W", "H08S", "H08N") for i in (1, 2, 3)]
days = []
for y in range(2015, 2020):
    d = dt.date(y, 2, 1)
    while d <= dt.date(y, 4, 30):
        days.append(d); d += dt.timedelta(days=1)
for y in list(range(2010, 2015)) + list(range(2020, 2026)):
    days += [dt.date(y, 3, 1), dt.date(y, 3, 8), dt.date(y, 3, 15)]
jobs = [(e, d, hh) for e in EL for d in days for hh in ("00:30:00", "12:00:00")]
S = requests.Session()
def probe(j):
    e, d, hh = j
    t0 = f"{d.isoformat()}T{hh}"; t1 = (dt.datetime.fromisoformat(t0) + dt.timedelta(seconds=30)).isoformat()
    for attempt in range(4):
        try:
            r = S.get(URL, params=dict(net="IM", sta=e, cha="EDH", starttime=t0, endtime=t1, nodata=404), timeout=60)
            return (e, d.isoformat(), hh, r.status_code, len(r.content))
        except Exception as ex:
            time.sleep(2 + 3 * attempt)
    return (e, d.isoformat(), hh, -1, 0)
with ThreadPoolExecutor(6) as ex:
    res = list(ex.map(probe, jobs))
with open(sys.argv[1], "w", newline="") as f:
    w = csv.writer(f); w.writerow(["element", "date", "probe_utc", "http", "bytes"]); w.writerows(res)
print(len(res), sum(r[3] == 200 for r in res), sum(r[3] == -1 for r in res))
