"""Download raw IMS H11N1-3 / H11S1-3 EDH (250 Hz) from EarthScope FDSN dataselect (anonymous) for the Transair 810
event day (2021-07-02 10:00-14:00 UTC) and background days (2021-06-25..07-01 and 07-03..07-09, 11:30-13:30 UTC).
One MiniSEED file per (day, element). 4 threads. Logs HTTP outcome per request to data/download_log.csv."""
import sys, time, csv
from concurrent.futures import ThreadPoolExecutor
from obspy import UTCDateTime
from obspy.clients.fdsn import Client
from obspy.clients.fdsn.header import FDSNNoDataException
EL = ["H11N1", "H11N2", "H11N3", "H11S1", "H11S2", "H11S3"]
jobs = [("2021-07-02", "10:00:00", "14:00:00")]
for d in [f"2021-06-{x:02d}" for x in range(25, 31)] + ["2021-07-01"] + [f"2021-07-{x:02d}" for x in range(3, 10)]:
    jobs.append((d, "11:30:00", "13:30:00"))
def one(a):
    (d, t0, t1), el = a
    fn = f"data/raw/{d}_{el}.mseed"
    for k in range(3):
        try:
            st = Client(base_url="https://service.earthscope.org", timeout=300).get_waveforms("IM", el, "*", "EDH", UTCDateTime(f"{d}T{t0}"), UTCDateTime(f"{d}T{t1}"))
            st.write(fn, format="MSEED")
            return (d, el, "ok", len(st), sum(tr.stats.npts for tr in st), str(st[0].stats.starttime), str(st[-1].stats.endtime))
        except FDSNNoDataException:
            return (d, el, "nodata", 0, 0, "", "")
        except Exception as e:
            err = repr(e)[:120]; time.sleep(5)
    return (d, el, "error " + err, 0, 0, "", "")
todo = [(j, el) for j in jobs for el in EL]
with ThreadPoolExecutor(4) as ex:
    res = list(ex.map(one, todo))
with open("data/download_log.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["day", "element", "status", "n_traces", "npts", "start", "end"]); w.writerows(res)
print(sum(r[2] == "ok" for r in res), "of", len(res), "ok")
