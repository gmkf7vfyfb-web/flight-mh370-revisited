"""Download raw IMS H11 hydrophone records (net IM, channel EDH, 250 Hz) for the F-35A event day, 9 April 2019,
from EarthScope FDSN dataselect (anonymous), plus the StationXML response. Event window 10:30-11:40 UTC;
background windows of 30 min the same day. Writes t1/data/*.mseed and a fetch log."""
import requests, json, time, pathlib, sys
OUT = pathlib.Path(__file__).resolve().parents[1] / "data"; OUT.mkdir(exist_ok=True)
DS = "https://service.earthscope.org/fdsnws/dataselect/1/query"
STN = "https://service.earthscope.org/fdsnws/station/1/query"
ELS = ["H11N1", "H11N2", "H11N3", "H11S1", "H11S2", "H11S3"]
WIN = {"event": ("2019-04-09T10:30:00", "2019-04-09T11:40:00")}
for h in ("01", "04", "07", "14", "17", "20", "23"):
    WIN[f"bg{h}"] = (f"2019-04-09T{h}:00:00", f"2019-04-09T{h}:30:00")
log = []
r = requests.get(STN, params=dict(net="IM", sta=",".join(ELS), cha="EDH", level="response", format="xml",
                                  starttime="2019-04-09T00:00:00", endtime="2019-04-10T00:00:00"), timeout=120)
(OUT / "H11_resp_2019-04-09.xml").write_bytes(r.content); log.append(dict(what="stationxml", http=r.status_code, bytes=len(r.content)))
for w, (t0, t1) in WIN.items():
    for el in ELS:
        f = OUT / f"{el}_{w}.mseed"
        if f.exists() and f.stat().st_size > 1000:
            continue
        a = time.time()
        r = requests.get(DS, params=dict(net="IM", sta=el, loc="*", cha="EDH", starttime=t0, endtime=t1, format="miniseed", nodata=404), timeout=600)
        if r.status_code == 200:
            f.write_bytes(r.content)
        log.append(dict(what=f"{el}_{w}", start=t0, end=t1, http=r.status_code, bytes=len(r.content), s=round(time.time() - a, 1)))
        print(log[-1], flush=True)
json.dump(log, open(OUT / "fetch_log.json", "w"), indent=1)
