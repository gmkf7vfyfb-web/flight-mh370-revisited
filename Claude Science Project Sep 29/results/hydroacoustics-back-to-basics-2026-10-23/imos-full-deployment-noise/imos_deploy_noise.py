#!/usr/bin/env python3
"""IMOS/Curtin CMST full-deployment noise statistics, stream-processed (download -> process -> delete raw).

Loggers: PAPCA/3376 (Perth Canyon), PAPOR/3274 (Portland), PAKIM/3250 (Scott Reef); the deployments that
cover 8 March 2014. Source: https://imos-data.s3-ap-southeast-2.amazonaws.com/IMOS/ANMN/Acoustic/<site>/<logger>/
<yyyymmdd>/raw/*.DAT and <site>/<logger>/extras/calibration_raw/<cal>.DAT (public, no login).

CALIBRATION is the module's chain (Hydroacoustic Handover/code/module/prepare/imos_noise.py; read_volts,
decimate, welch, band_mean, gain_db copied verbatim because that module imports pyproj/composer code at import
time): volts = counts*5/65536 mean removed; decimate 6000 -> 500 Hz (resample_poly 1/12); Welch 4 s Hann 50 %;
system gain G(f) = PSD(cal file) + 90 dB (white noise at -90 dB re 1 V^2/Hz input); dB re 1 uPa^2/Hz =
10log10(V^2/Hz) - G(f) - S_h, with S_h the metadata sensitivity read as dB re 1 V/uPa (disclosed units
deviation of the module). The 2-1000 Hz chain uses the same rule at 6 kHz (gain from a 1 s Hann Welch of the
cal file at 6 kHz, 1 Hz bins).

PER RECORD (rows parquet): times (footer First Data incl. n/65536 s; clock error e(t) linear between the
metadata clock sets; corrected UTC = logger - e, convention A), quality fields, Welch band levels (mean PSD
in band, dB re 1 uPa^2/Hz) for 2-5 ... 160-240 and 5-40 Hz, 5-40 Hz band SPL (dB re 1 uPa = mean PSD x 35 Hz),
base-10 third-octave SPLs 5-40 Hz (mean PSD x exact bandwidth), 1 s band-level percentiles 5/50/95 and excess
kurtosis of 1 s band energy (module definition), excess kurtosis of the 5-40 Hz band-passed waveform.
PER DAY (npz): psd = 10log10 of the 1 s Hann periodogram mean (Welch, 1 Hz bins) and percentiles
1,5,10,25,50,75,90,95,99 over 1 s segments, 2-1000 Hz, float16 dB; hist = per-bin counts of 1 s levels,
0.5 dB bins 20-180 dB, uint16; lev1s = 1 s band levels (module chain) float16; cube = 2-125 Hz spectrogram,
1 Hz x 0.5 s (1 s Hann, 50 % overlap, on the 500 Hz series), calibrated dB re 1 uPa^2/Hz, float16.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sys
import time
import traceback
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, ThreadPoolExecutor, wait
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import signal, stats

BUCKET = "https://imos-data.s3-ap-southeast-2.amazonaws.com"
ROOT = "IMOS/ANMN/Acoustic"
FS = 6000
FS_D = 500                      # decimated rate, Hz (module)
Q = 12                          # 6000 / 500 (module)
NPER = 4 * FS_D                 # 4 s Welch segments (module)
BANDS = [(2, 5), (5, 10), (10, 20), (20, 40), (40, 80), (80, 160), (160, 240), (5, 40)]
TOB_N = list(range(7, 17))      # base-10 third octaves, fc = 10^(n/10): 5.01 ... 39.8 Hz
TOB = [(10 ** (n / 10), 10 ** (n / 10 - 0.05), 10 ** (n / 10 + 0.05)) for n in TOB_N]
PCTS = [1, 5, 10, 25, 50, 75, 90, 95, 99]
F6_LO, F6_HI = 2, 1000          # 1 Hz bins kept, inclusive
H_LO, H_STEP, H_N = 20.0, 0.5, 320
CUBE_LO, CUBE_HI = 2, 125

# ---------------------------------------------------------------- module chain (verbatim from imos_noise.py)

def read_volts_bytes(raw):
    pos = 0
    for _ in range(5):
        pos = raw.index(b"\n", pos) + 1
    tail = raw[-1000:]
    footer_bytes = 1000 - tail.index(b"Record")
    end = len(raw) - footer_bytes - 2
    n = (end - pos) // 2
    c = np.frombuffer(raw, dtype=">u2", count=n, offset=pos)
    x = c.astype(np.float64) * (5.0 / 65536)
    return x - x.mean(), c


def decimate(x):
    return signal.resample_poly(x, 1, Q)


def welch(xd):
    return signal.welch(xd, fs=FS_D, window="hann", nperseg=NPER, noverlap=NPER // 2, detrend="constant")


def band_mean(f, p, lo, hi):
    m = (f >= lo) & (f < hi)
    return p[..., m].mean(axis=-1)


def gain_db_bytes(raw):
    f, p = welch(decimate(read_volts_bytes(raw)[0]))
    return f, 10 * np.log10(p) + 90.0


def gain6_db_bytes(raw):
    x = read_volts_bytes(raw)[0]
    f, p = signal.welch(x, fs=FS, window="hann", nperseg=FS, noverlap=FS // 2, detrend="constant")
    return f, 10 * np.log10(p) + 90.0

# ---------------------------------------------------------------- helpers

def parse_hdr(raw):
    pos, hdr = 0, []
    for _ in range(5):
        e = raw.index(b"\n", pos)
        hdr.append(raw[pos:e].decode("latin1").rstrip())
        pos = e + 1
    tail = raw[-1000:].decode("latin1")
    tail = tail[tail.index("Record"):]
    m = re.search(r"First Data-(\d{4}/\d\d/\d\d \d\d:\d\d:\d\d) - (\d+)", tail)
    fin = re.search(r"Finalised -(\d{4}/\d\d/\d\d \d\d:\d\d:\d\d) - (\d+)", tail)
    val = re.search(r"Data Validity - ([^\n]*)", tail)
    fs = int(re.search(r"Sample Rate (\d+)", hdr[2]).group(1))
    first = dt.datetime.strptime(m.group(1), "%Y/%m/%d %H:%M:%S").replace(tzinfo=dt.timezone.utc).timestamp() \
        + int(m.group(2)) / 65536.0
    finalised = (dt.datetime.strptime(fin.group(1), "%Y/%m/%d %H:%M:%S").replace(tzinfo=dt.timezone.utc).timestamp()
                 + int(fin.group(2)) / 65536.0) if fin else np.nan
    return dict(hdr0=hdr[0], schedule=hdr[1], fs=fs, filter0=hdr[3], filter1=hdr[4], first_data_unix=first,
                finalised_unix=finalised, validity=val.group(1).strip() if val else "")


def ts(s):
    return dt.datetime.strptime(s, "%d-%b-%Y %H:%M:%S").replace(tzinfo=dt.timezone.utc).timestamp()


def clock_err(L, t_unix):
    (t1, e1), (t2, e2) = (ts(L["clock1"][0]), L["clock1"][1]), (ts(L["clock2"][0]), L["clock2"][1])
    return e1 + (e2 - e1) * (t_unix - t1) / (t2 - t1)

# ---------------------------------------------------------------- worker

_G = {}


def init_worker(cfg, caldir):
    for lg, L in cfg.items():
        raw = (Path(caldir) / L["cal_file"]).read_bytes()
        fg, G = gain_db_bytes(raw)
        f6, G6 = gain6_db_bytes(raw)
        _G[lg] = dict(fg=fg, G=G, f6=f6, G6=G6, L=L)


def process_record(path, lg, key, size_s3):
    g = _G[lg]
    L = g["L"]
    raw = Path(path).read_bytes()
    row = dict(logger=lg, key=key, file=os.path.basename(key), size_bytes=len(raw), size_s3=size_s3,
               sha256=hashlib.sha256(raw).hexdigest())
    try:
        h = parse_hdr(raw)
        row.update(h)
        x, cnt = read_volts_bytes(raw)
        n = len(x)
        row.update(n_samples=n, dur_s=n / h["fs"], n_clip=int(np.count_nonzero((cnt == 0) | (cnt == 65535))),
                   mean_counts=float(cnt.mean()), rms_counts=float(cnt.std()))
        row["hex_unix"] = int(os.path.basename(key).split(".")[0], 16)
        e = clock_err(L, h["first_data_unix"])
        row["clock_err_s"] = e
        row["start_utc_unix"] = h["first_data_unix"] - e            # convention A: true = logger - e
        if h["fs"] != FS:
            raise ValueError(f"fs {h['fs']}")
        sens = L["sens_db"]
        # --- module chain: decimated Welch band levels
        xd = decimate(x)
        f, p = welch(xd)
        pu = p / 10 ** ((np.interp(f, g["fg"], g["G"]) + sens) / 10)
        for lo, hi in BANDS:
            row[f"L_{lo}_{hi}"] = float(10 * np.log10(band_mean(f, pu, lo, hi)))
        row["SPL_5_40"] = float(10 * np.log10(band_mean(f, pu, 5, 40) * 35.0))
        for fc, lo, hi in TOB:
            row[f"TOL_{fc:.1f}"] = float(10 * np.log10(band_mean(f, pu, lo, hi) * (hi - lo)))
        # --- module chain: 1 s Hann periodograms on decimated series
        nseg = len(xd) // FS_D
        seg = xd[: nseg * FS_D].reshape(nseg, FS_D)
        f1, p1 = signal.periodogram(seg, fs=FS_D, window="hann", detrend="constant", axis=-1)
        p1u = p1 / (10 ** ((np.interp(f1, g["fg"], g["G"]) + sens) / 10))
        lev1 = np.empty((len(BANDS), nseg), np.float32)
        for i, (lo, hi) in enumerate(BANDS):
            eb = band_mean(f1, p1u, lo, hi)
            db = 10 * np.log10(eb)
            lev1[i] = db
            row[f"p5_1s_{lo}_{hi}"], row[f"p50_1s_{lo}_{hi}"], row[f"p95_1s_{lo}_{hi}"] = \
                [float(v) for v in np.percentile(db, [5, 50, 95])]
            row[f"kurt_1s_{lo}_{hi}"] = float(stats.kurtosis(eb))
        sos = signal.butter(4, [5, 40], btype="bandpass", fs=FS_D, output="sos")
        row["kurt_wave_5_40"] = float(stats.kurtosis(signal.sosfiltfilt(sos, xd)))
        # --- 6 kHz chain: 1 s periodograms, 1 Hz bins, 2-1000 Hz
        ns6 = n // FS
        s6 = x[: ns6 * FS].reshape(ns6, FS)
        f6, q6 = signal.periodogram(s6, fs=FS, window="hann", detrend="constant", axis=-1)
        sl = slice(F6_LO, F6_HI + 1)
        q6u = q6[:, sl] / 10 ** ((g["G6"][sl] + sens) / 10)
        db6 = 10 * np.log10(q6u)
        psd = np.empty((1 + len(PCTS), q6u.shape[1]), np.float32)
        psd[0] = 10 * np.log10(q6u.mean(axis=0))
        psd[1:] = np.percentile(db6, PCTS, axis=0)
        idx = np.clip(np.floor((db6 - H_LO) / H_STEP), 0, H_N - 1).astype(np.int64)
        flat = idx + H_N * np.arange(q6u.shape[1])[None, :]
        hist = np.bincount(flat.ravel(), minlength=H_N * q6u.shape[1]).reshape(q6u.shape[1], H_N).astype(np.uint16)
        row["n_1s"] = int(nseg)
        # --- cube: 2-125 Hz, 1 Hz x 0.5 s
        fc_, tc_, S = signal.spectrogram(xd, fs=FS_D, window="hann", nperseg=FS_D, noverlap=FS_D // 2,
                                         detrend="constant", scaling="density", mode="psd")
        cm = (fc_ >= CUBE_LO) & (fc_ <= CUBE_HI)
        Su = S[cm, :] / 10 ** ((np.interp(fc_[cm], g["fg"], g["G"]) + sens) / 10)[:, None]
        cube = (10 * np.log10(Su)).T.astype(np.float16)                 # (frames, 124)
        row["error"] = ""
        return row, psd.astype(np.float16), hist, lev1.astype(np.float16), cube, tc_.astype(np.float32)
    except Exception as ex:  # noqa: BLE001
        row["error"] = f"{type(ex).__name__}: {ex}"
        return row, None, None, None, None, None

# ---------------------------------------------------------------- S3

NS = {"s": "http://s3.amazonaws.com/doc/2006-03-01/"}


def s3_list(prefix, delim="/"):
    out_p, out_k, tok = [], [], None
    while True:
        q = f"list-type=2&prefix={prefix}&delimiter={delim}"
        if tok:
            q += "&continuation-token=" + urllib.parse.quote(tok)
        for a in range(6):
            try:
                with urllib.request.urlopen(f"{BUCKET}/?{q}", timeout=120) as r:
                    root = ET.fromstring(r.read())
                break
            except Exception:  # noqa: BLE001
                time.sleep(5 * (a + 1))
        else:
            raise RuntimeError("list failed " + prefix)
        out_p += [e.find("s:Prefix", NS).text for e in root.findall("s:CommonPrefixes", NS)]
        out_k += [(e.find("s:Key", NS).text, int(e.find("s:Size", NS).text)) for e in root.findall("s:Contents", NS)]
        t = root.find("s:NextContinuationToken", NS)
        if t is None:
            return out_p, out_k
        tok = t.text


def fetch(key, size, dest):
    for a in range(8):
        try:
            tmp = dest + ".part"
            with urllib.request.urlopen(f"{BUCKET}/{key}", timeout=180) as r, open(tmp, "wb") as fo:
                shutil.copyfileobj(r, fo, 1 << 20)
            if os.path.getsize(tmp) != size:
                raise IOError("size mismatch")
            os.replace(tmp, dest)
            return dest
        except Exception:  # noqa: BLE001
            time.sleep(3 * (a + 1))
    raise RuntimeError("download failed " + key)

# ---------------------------------------------------------------- driver


def free_gb(p):
    s = os.statvfs(p)
    return s.f_bavail * s.f_frsize / 1e9


def task_order(days_by_lg, first_month="201403", centre="20140308"):
    c = dt.date(int(centre[:4]), int(centre[4:6]), int(centre[6:]))
    items = []
    for lg, days in days_by_lg.items():
        for d in days:
            dd = dt.date(int(d[:4]), int(d[4:6]), int(d[6:]))
            items.append((0 if d.startswith(first_month) else 1, abs((dd - c).days), lg, d))
    return [(lg, d) for *_, lg, d in sorted(items)]


def finalize(out, cube_dir, lg, day, recs):
    recs.sort(key=lambda r: r[0]["file"])
    rows = [r[0] for r in recs]
    ok = [r for r in recs if r[1] is not None]
    od = Path(out) / lg
    for sub in ("rows", "psd", "hist", "lev1s", "done"):
        (od / sub).mkdir(parents=True, exist_ok=True)
    (Path(cube_dir) / lg).mkdir(parents=True, exist_ok=True)
    if rows:
        pd.DataFrame(rows).to_parquet(od / "rows" / f"{day}.parquet", index=False)
    files = np.array([r[0]["file"] for r in ok])
    t0 = np.array([r[0]["start_utc_unix"] for r in ok])
    if ok:
        np.savez(od / "psd" / f"{day}.npz", files=files, start_utc_unix=t0,
                 f_hz=np.arange(F6_LO, F6_HI + 1), stats=np.array(["mean"] + [f"p{p}" for p in PCTS]),
                 psd_db=np.stack([r[1] for r in ok]))
        np.savez(od / "hist" / f"{day}.npz", f_hz=np.arange(F6_LO, F6_HI + 1),
                 edges_db=H_LO + H_STEP * np.arange(H_N + 1),
                 counts=np.sum([r[2].astype(np.uint32) for r in ok], axis=0).astype(np.uint16))
        nl = max(r[3].shape[1] for r in ok)
        lv = np.full((len(ok), len(BANDS), nl), np.nan, np.float16)
        for i, r in enumerate(ok):
            lv[i, :, : r[3].shape[1]] = r[3]
        np.savez(od / "lev1s" / f"{day}.npz", files=files, start_utc_unix=t0,
                 bands=np.array([f"{a}-{b}" for a, b in BANDS]), lev_db=lv)
        nf = max(r[4].shape[0] for r in ok)
        cb = np.full((len(ok), nf, ok[0][4].shape[1]), np.nan, np.float16)
        for i, r in enumerate(ok):
            cb[i, : r[4].shape[0]] = r[4]
        tc = max((r[5] for r in ok), key=len)
        np.savez(Path(cube_dir) / lg / f"{day}.npz", files=files, start_utc_unix=t0,
                 f_hz=np.arange(CUBE_LO, CUBE_HI + 1), t_offset_s=tc, psd_db=cb)
    (od / "done" / day).write_text(json.dumps(dict(n=len(rows), ok=len(ok), t=time.time())))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cfg", required=True)
    ap.add_argument("--work", default=os.path.expanduser("~/imos-noise"))
    ap.add_argument("--days", default="")           # comma list yyyymmdd to restrict
    ap.add_argument("--loggers", default="3376,3274,3250")
    ap.add_argument("--nproc", type=int, default=32)
    ap.add_argument("--ndl", type=int, default=96)
    ap.add_argument("--maxdays", type=int, default=4)
    ap.add_argument("--min_free_gb", type=float, default=6.0)
    a = ap.parse_args()
    cfg = json.loads(Path(a.cfg).read_text())
    cfg = {k: v for k, v in cfg.items() if k in a.loggers.split(",")}
    W = Path(a.work)
    out, cube_dir, rawroot, caldir = W / "out", W / "cube", W / "raw", W / "cal"
    for d in (out, cube_dir, rawroot, caldir):
        d.mkdir(parents=True, exist_ok=True)
    log = open(W / "driver.log", "a", buffering=1)

    def P(*s):
        print(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), *s, file=log)

    for lg, L in cfg.items():
        cp = caldir / L["cal_file"]
        if not cp.exists():
            ks = s3_list(f"{ROOT}/{L['cal_key']}", delim="")[1]
            fetch(ks[0][0], ks[0][1], str(cp))
    days_by_lg = {}
    for lg, L in cfg.items():
        pre = s3_list(f"{ROOT}/{L['site']}/{lg}/")[0]
        days = [p.rstrip("/").split("/")[-1] for p in pre]
        days = [d for d in days if re.fullmatch(r"\d{8}", d)]
        if a.days:
            days = [d for d in days if d in a.days.split(",")]
        done = {p.name for p in (out / lg / "done").glob("*")} if (out / lg / "done").exists() else set()
        days_by_lg[lg] = [d for d in days if d not in done]
        P("logger", lg, "days todo", len(days_by_lg[lg]), "done", len(done))
    tasks = task_order(days_by_lg)
    P("tasks", len(tasks))
    dl = ThreadPoolExecutor(a.ndl)
    pp = ProcessPoolExecutor(a.nproc, initializer=init_worker, initargs=(cfg, str(caldir)))
    fut = {}
    state = {}
    ti = 0
    t_start = time.time()
    nrec = 0
    while ti < len(tasks) or state:
        while ti < len(tasks) and len(state) < a.maxdays:
            if free_gb(W) < a.min_free_gb:
                P("LOW DISK", round(free_gb(W), 1), "GB; waiting")
                break
            lg, day = tasks[ti]
            ti += 1
            L = cfg[lg]
            keys = [(k, s) for k, s in s3_list(f"{ROOT}/{L['site']}/{lg}/{day}/raw/", delim="")[1] if k.endswith(".DAT")]
            rd = rawroot / lg / day
            rd.mkdir(parents=True, exist_ok=True)
            sid = (lg, day)
            if not keys:
                finalize(out, cube_dir, lg, day, [])
                P("EMPTY", lg, day)
                continue
            state[sid] = dict(n=len(keys), recs=[], t=time.time())
            for k, s in keys:
                fut[dl.submit(fetch, k, s, str(rd / os.path.basename(k)))] = ("dl", sid, k, s)
        if not fut:
            time.sleep(60)
            continue
        done, _ = wait(list(fut), timeout=120, return_when=FIRST_COMPLETED)
        for f in done:
            kind, sid, k, s = fut.pop(f)
            st = state[sid]
            if kind == "dl":
                try:
                    pth = f.result()
                    fut[pp.submit(process_record, pth, sid[0], k, s)] = ("pr", sid, k, s)
                    continue
                except Exception as ex:  # noqa: BLE001
                    st["recs"].append((dict(logger=sid[0], key=k, file=os.path.basename(k), size_s3=s,
                                            error=f"download: {ex}"), None, None, None, None, None))
            else:
                try:
                    res = f.result()
                except Exception as ex:  # noqa: BLE001
                    res = (dict(logger=sid[0], key=k, file=os.path.basename(k), size_s3=s,
                                error=f"process: {ex}"), None, None, None, None, None)
                st["recs"].append(res)
                try:
                    os.remove(rawroot / sid[0] / sid[1] / os.path.basename(k))
                except FileNotFoundError:
                    pass
            if len(st["recs"]) == st["n"]:
                finalize(out, cube_dir, sid[0], sid[1], st["recs"])
                shutil.rmtree(rawroot / sid[0] / sid[1], ignore_errors=True)
                nrec += st["n"]
                nerr = sum(1 for r in st["recs"] if r[0].get("error"))
                P("DONE", sid[0], sid[1], "n", st["n"], "err", nerr, "s", round(time.time() - st["t"]),
                  "total_rec", nrec, "rate_rec_per_min", round(nrec / (time.time() - t_start) * 60, 1),
                  "free_gb", round(free_gb(W), 1))
                del state[sid]
    P("ALL DONE")


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        raise
