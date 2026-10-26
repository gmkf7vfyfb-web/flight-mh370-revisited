"""Download (EarthScope FDSN dataselect, anonymous) and process IMS triplet-days; keep only derived products.
Usage: python run_days.py <jobs.csv: station,day[,t0,t1 (HH:MM:SS) for a block]> <out_dir> <n_download_threads> <n_process_threads>
Raw miniSEED is deleted after each station-day is processed (derived products only are kept)."""
import sys, os, time, json, threading, queue, traceback
import numpy as np, pandas as pd, requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ims_proc as P, m1b_bank as MB
from obspy import read_inventory, read

URL = "https://service.earthscope.org/fdsnws/dataselect/1/query"
jobs = pd.read_csv(sys.argv[1]); OUT = Path(sys.argv[2]); ND, NP = int(sys.argv[3]), int(sys.argv[4])
RAW = OUT / "raw"; DAYS = OUT / "days"; RAW.mkdir(parents=True, exist_ok=True); DAYS.mkdir(parents=True, exist_ok=True)
LOG = open(OUT / "run_log.jsonl", "a"); LK = threading.Lock()
def log(**k):
    with LK:
        LOG.write(json.dumps(k) + "\n"); LOG.flush()
inv = read_inventory(str(Path(__file__).resolve().parent.parent / "meta" / "IM_hydro_response.xml"))
T = np.load(Path(__file__).resolve().parent.parent / "meta" / "templates_raw.npz")
bank, _ = MB.bank_env(T, MB.IMOS_BANK_RANGES, 100)

def fetch(el, day, s0="00:00:00", s1=None):
    fp = RAW / f"{el}_{day}.mseed"
    if fp.exists():
        try:
            st = read(str(fp)); log(ev="reuse", el=el, day=day); return fp
        except Exception:
            fp.unlink()
    t0 = f"{day}T{s0}"; t1 = (pd.Timestamp(day) + pd.Timedelta(days=1)).strftime("%Y-%m-%dT00:00:00") if s1 is None else f"{day}T{s1}"
    for att in range(5):
        t = time.time()
        try:
            with requests.get(URL, params=dict(net="IM", sta=el, cha="EDH", starttime=t0, endtime=t1, nodata=404), stream=True, timeout=(30, 300)) as r:
                if r.status_code == 404:
                    log(ev="nodata", el=el, day=day); return None
                r.raise_for_status()
                with open(fp, "wb") as f:
                    for ch in r.iter_content(1 << 20):
                        f.write(ch)
            st = read(str(fp))           # integrity check
            n = sum(tr.stats.npts for tr in st)
            log(ev="got", el=el, day=day, mb=os.path.getsize(fp) / 1e6, s=round(time.time() - t, 1), hours=round(n / 250 / 3600, 3), att=att)
            return fp
        except Exception as ex:
            log(ev="fetch_err", el=el, day=day, att=att, err=str(ex)[:200]); time.sleep(10 * (att + 1))
    return None

dq = ThreadPoolExecutor(ND)
pq = ThreadPoolExecutor(NP)
def process(st, day, futs):
    try:
        files = {el: f.result() for el, f in futs.items()}
        files = {el: fp for el, fp in files.items() if fp is not None}
        if not files:
            log(ev="day_empty", st=st, day=day); return
        t = time.time()
        res, noise, W = P.process_day(st, day, files, inv, bank)
        stem = DAYS / f"{st}_{day}"
        arr = {}
        for el, (P1, TO, SPL, ok) in noise.items():
            arr[f"{el}_psd1"] = P1.astype(np.float32); arr[f"{el}_to"] = TO; arr[f"{el}_spl540"] = SPL; arr[f"{el}_ok"] = ok
        np.savez_compressed(str(stem) + "_noise.npz", **arr)
        if W is not None:
            W.to_pickle(str(stem) + "_windows.pkl.gz")
        json.dump(res, open(str(stem) + "_info.json", "w"))
        log(ev="processed", st=st, day=day, s=round(time.time() - t, 1), info=res["info"])
        for el in futs:
            fp = RAW / f"{el}_{day}.mseed"
            if fp.exists(): fp.unlink()
    except Exception as ex:
        log(ev="proc_err", st=st, day=day, err=traceback.format_exc()[-800:])

pf = []
BLOCK = ("t0" in jobs.columns)
for r in jobs.itertuples():
    if (DAYS / f"{r.station}_{r.day}_info.json").exists():
        continue
    if BLOCK:
        futs = {f"{r.station}{i}": dq.submit(fetch, f"{r.station}{i}", r.day, r.t0, r.t1) for i in (1, 2, 3)}
    else:
        futs = {f"{r.station}{i}": dq.submit(fetch, f"{r.station}{i}", r.day) for i in (1, 2, 3)}
    pf.append(pq.submit(process, r.station, r.day, futs))
    # throttle: do not queue more raw than ~ 3 x process threads station-days ahead
    while sum(not f.done() for f in pf) > 3 * NP + ND // 3:
        time.sleep(5)
for f in pf: f.result()
log(ev="all_done")
print("done")
