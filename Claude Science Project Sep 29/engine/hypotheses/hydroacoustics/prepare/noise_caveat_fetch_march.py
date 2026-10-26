#!/usr/bin/env python3
"""noise_caveat_fetch_march.py - fetch raw IMS H01W and H08S records for 8 March 2015-2019 in the clock windows of the
Kadri 2024 Fig. 9 panels (H01W 00:27-00:57 UTC, H08S 01:00-01:20 UTC), with StationXML responses. Open EarthScope FDSN
web services, no credentials. Used only to measure shape ratios (PP/RMS) for fix C1 (26 Oct 2026); no level from these
records enters the database as an 8 March 2014 value. Records are not committed (size); this script fetches them again.

Usage: python noise_caveat_fetch_march.py --out <dir>
"""
import argparse, hashlib, time, urllib.request
from pathlib import Path

DS = "https://service.earthscope.org/fdsnws/dataselect/1/query"
STN = "https://service.earthscope.org/fdsnws/station/1/query"
WIN = {"H01W": ("00:27:00", "00:57:00"), "H08S": ("01:00:00", "01:20:00")}
YEARS = [2015, 2016, 2017, 2018, 2019]


def get(url, path):
    for k in range(3):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                code, b = r.status, r.read()
            break
        except urllib.error.HTTPError as e:
            code, b = e.code, b""
            break
        except Exception:
            time.sleep(5); code, b = None, b""
    if code == 200 and b:
        Path(path).write_bytes(b)
    return code, len(b)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    log = ["station\tyear\tkind\turl\thttp\tbytes\tsha256"]
    for st, (t0, t1) in WIN.items():
        for y in YEARS:
            s, e = f"{y}-03-08T{t0}", f"{y}-03-08T{t1}"
            for kind, url, fn in [("mseed", f"{DS}?net=IM&sta={st}1,{st}2,{st}3&cha=EDH&starttime={s}&endtime={e}", out / f"{st}_{y}0308.mseed"),
                                  ("stationxml", f"{STN}?net=IM&sta={st}1,{st}2,{st}3&cha=EDH&starttime={s}&endtime={e}&level=response", out / f"{st}_{y}0308.xml")]:
                code, n = get(url, fn)
                h = hashlib.sha256(fn.read_bytes()).hexdigest() if (code == 200 and n) else ""
                log.append(f"{st}\t{y}\t{kind}\t{url}\t{code}\t{n}\t{h}")
                print(st, y, kind, code, n)
    (out / "fetch_log.tsv").write_text("\n".join(log) + "\n")


if __name__ == "__main__":
    main()
