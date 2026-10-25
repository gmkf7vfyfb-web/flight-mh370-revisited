"""Download raw IMS H10 hydrophone records (net IM, cha EDH, 250 Hz) from EarthScope FDSN dataselect, anonymous.
Windows: event origin + predicted travel time - 20 min ... + 25 min (FSST) or fixed windows (San Juan). Also StationXML response."""
import io, json, sys, time
import requests
from obspy import read, UTCDateTime as U, read_inventory
DS="https://service.earthscope.org/fdsnws/dataselect/1/query"; ST="https://service.earthscope.org/fdsnws/station/1/query"
EV={ # name: (origin_utc, window_start, window_end)  windows chosen to include >=10 min pre-arrival background
 "sj_event":   ("2017-11-15T13:51:05","2017-11-15T14:35:00","2017-11-15T15:30:00"),
 "sj_charge":  ("2017-12-01T20:04:30","2017-12-01T20:50:00","2017-12-01T21:45:00"),
 "fsst16_1":("2016-06-10T17:10:48.64",None,None),"fsst16_2":("2016-06-23T17:20:29.45",None,None),"fsst16_3":("2016-07-16T20:00:10.22",None,None),
 "fsst16_4":("2016-09-04T18:29:29.80",None,None),"fsst16_5":("2016-09-21T16:30:52.90",None,None),
 "fsst21_1":("2021-06-18T19:48:39.595",None,None),"fsst21_2":("2021-07-16T17:48:33.533",None,None),"fsst21_3":("2021-08-08T19:55:18.252",None,None)}
STAS=["H10N1","H10N2","H10N3","H10S1","H10S2","H10S3"]
log=[]
for name,(o,a,b) in EV.items():
    o=U(o)
    if a is None: a=o+62*60; b=o+115*60   # ~8,150 km at 1.48 km/s = 91.8 min
    else: a,b=U(a),U(b)
    for s in STAS:
        p=dict(net="IM",sta=s,loc="*",cha="EDH",starttime=a.isoformat(),endtime=b.isoformat())
        for k in range(3):
            try:
                r=requests.get(DS,params=p,timeout=300); break
            except Exception as e: err=str(e); time.sleep(5); r=None
        n=len(r.content) if r is not None else 0
        log.append(dict(event=name,station=s,start=str(a),end=str(b),http=r.status_code if r is not None else None,bytes=n))
        if r is not None and r.status_code==200:
            open(f"raw/{name}_{s}.mseed","wb").write(r.content)
        print(name,s,log[-1]["http"],n,flush=True)
    # response
    r=requests.get(ST,params=dict(net="IM",sta="H10*",cha="EDH",level="response",starttime=a.isoformat(),endtime=b.isoformat()),timeout=300)
    open(f"raw/{name}_resp.xml","wb").write(r.content); print(name,"resp",r.status_code,len(r.content))
json.dump(log,open("raw/download_log.json","w"),indent=1)
