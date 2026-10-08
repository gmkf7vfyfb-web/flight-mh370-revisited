"""Fetch the GDP 6-hourly interpolated drifter subset used by the Davey ch. 11 reproduction.

Source: NOAA AOML Global Drifter Program, "Global Drifter Program - 6 Hour Interpolated QC
Drifter Data", ERDDAP tabledap dataset ``drifter_6hour_qc`` at
https://erddap.aoml.noaa.gov/gdp/erddap/tabledap/drifter_6hour_qc  (dataset DOI
10.25921/7ntx-z961, as stated in the dataset's own NC_GLOBAL ``doi`` attribute).

Subset (one netCDF-3 file per calendar year, 1979-2025):
  variables  ID, time, latitude, longitude, sst, drogue_lost_date
  latitude   -60 .. 10
  lon360     20 .. 140   (Indian Ocean, Reunion at 55.5E to beyond Australia's west coast)
  time       [YYYY-01-01, YYYY+1-01-01)

All rows are fetched, drogued and undrogued; the drogue split is done locally with
``time > drogue_lost_date`` (see load_gdp.py), because ERDDAP constraints cannot compare two
variables. sst is fetched for the deferred biofouling channel (A2); it is not used here.

Guards (binding overnight rules): total bytes <= 1 GiB, and free space on /Users/pete must stay
>= 25 GiB (the script stops at 26 GiB to keep a margin). A JSON manifest with URL, bytes and
sha256 of every file is written beside the data.

Usage: python fetch_gdp.py [OUTDIR]
"""
import hashlib
import json
import os
import shutil
import sys
import time
import urllib.parse
import urllib.request

BASE = "https://erddap.aoml.noaa.gov/gdp/erddap/tabledap/drifter_6hour_qc"
COLS = "ID,time,latitude,longitude,sst,drogue_lost_date"
LAT = (-60, 10)
LON360 = (20, 140)
YEARS = range(1979, 2026)
CAP_BYTES = 1 << 30
MIN_FREE = 26 * (1 << 30)


def query(t0, t1):
    cons = [f"latitude>={LAT[0]}", f"latitude<={LAT[1]}", f"lon360>={LON360[0]}",
            f"lon360<={LON360[1]}", f"time>={t0}", f"time<{t1}"]
    return COLS + "&" + "&".join(urllib.parse.quote(c, safe="=") for c in cons)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    man_path = os.path.join(outdir, "manifest.json")
    man = json.load(open(man_path)) if os.path.exists(man_path) else {"files": {}}
    man.update(dataset="drifter_6hour_qc", base=BASE, doi="10.25921/7ntx-z961",
               columns=COLS, lat=LAT, lon360=LON360)
    total = sum(v["bytes"] for v in man["files"].values())
    for y in YEARS:
        name = f"gdp6h_io_{y}.nc"
        if name in man["files"]:
            continue
        free = shutil.disk_usage("/Users/pete").free
        if free < MIN_FREE:
            sys.exit(f"STOP: free space {free/2**30:.1f} GiB below guard")
        if total > CAP_BYTES:
            sys.exit(f"STOP: cap reached {total} bytes")
        url = f"{BASE}.nc?{query(f'{y}-01-01', f'{y + 1}-01-01')}"
        path = os.path.join(outdir, name)
        for attempt in range(3):
            try:
                t = time.time()
                with urllib.request.urlopen(url, timeout=1200) as r, open(path + ".part", "wb") as f:
                    shutil.copyfileobj(r, f, 1 << 20)
                os.replace(path + ".part", path)
                break
            except urllib.error.HTTPError as e:
                body = e.read()[:300]
                if e.code == 404 and b"no matching results" in body.lower():
                    path = None
                    break
                print(y, "HTTP", e.code, body, flush=True)
                time.sleep(20)
            except Exception as e:  # network hiccup: retry
                print(y, "ERR", e, flush=True)
                time.sleep(20)
        else:
            sys.exit(f"STOP: {y} failed three times")
        if path is None:
            man["files"][name] = {"url": url, "bytes": 0, "sha256": None, "note": "no rows"}
        else:
            n = os.path.getsize(path)
            total += n
            man["files"][name] = {"url": url, "bytes": n, "sha256": sha256(path),
                                  "retrieved_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                  "seconds": round(time.time() - t, 1)}
        print(y, man["files"][name]["bytes"], f"total={total}", flush=True)
        json.dump(man, open(man_path, "w"), indent=1)
    man["total_bytes"] = total
    json.dump(man, open(man_path, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/Users/pete/Downloads/mh370-ocean-data/gdp")
