"""Fetch the production surface forcing for drift's domain and period (ocean transport, item 2 of 9 Oct).

Box 15-120 E, 50-0 S; period 2014-03-07 to 2017-01-31. One product per invocation:

    python fetch_forcing.py glorys12|waverys|era5|bran2016

Writes to /Users/pete/Downloads/mh370-ocean-data/<product>/ and appends one JSON line per file
(name, bytes, sha256, retrieval time, request) to fetch-log.jsonl there. Checks the 100 GiB free-disk
floor before every file. Credentials: COPERNICUS (user:password) in the environment variable
COPERNICUS for the Copernicus Marine products; ERA5 (public ARCO-ERA5 bucket) and BRAN2016 (NCI
THREDDS) are anonymous.
"""
import concurrent.futures as cf
import datetime as dt
import hashlib
import json
import os
import shutil
import sys

import numpy as np
import requests

ROOT = "/Users/pete/Downloads/mh370-ocean-data"
FLOOR_GIB = 100.0
BOX = dict(minimum_longitude=15, maximum_longitude=120, minimum_latitude=-50, maximum_latitude=0)
START, END = dt.datetime(2014, 3, 7), dt.datetime(2017, 1, 31)
UTC = dt.timezone.utc


def floor_ok():
    free = shutil.disk_usage(ROOT).free / 2**30
    if free < FLOOR_GIB + 5:
        sys.exit(f"free disk {free:.1f} GiB is within 5 GiB of the {FLOOR_GIB} GiB floor; stopping")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def record(product, path, request):
    entry = dict(file=os.path.basename(path), bytes=os.path.getsize(path), sha256=sha256(path),
                 retrieved_utc=dt.datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), request=request)
    with open(os.path.join(ROOT, product, "fetch-log.jsonl"), "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(json.dumps({k: entry[k] for k in ("file", "bytes")}), flush=True)


def year_windows(start, end):
    y = start.year
    while y <= end.year:
        a = max(start, dt.datetime(y, 1, 1))
        b = min(end, dt.datetime(y, 12, 31, 23, 59, 59))
        yield a, b
        y += 1


def copernicus(product, dataset, variables, start, service, extra):
    import copernicusmarine as cm
    user, pw = os.environ["COPERNICUS"].strip().split(":", 1)
    out = os.path.join(ROOT, product)
    for a, b in year_windows(start, END):
        name = f"{product}_{'_'.join(variables)}_15-120E_50-0S_{a:%Y%m%d}-{b:%Y%m%d}.nc"
        if os.path.exists(os.path.join(out, name)):
            continue
        floor_ok()
        req = dict(dataset_id=dataset, variables=variables, **BOX, **extra,
                   start_datetime=a.isoformat(), end_datetime=b.isoformat(), service=service)
        cm.subset(**req, username=user, password=pw, output_directory=out, output_filename=name,
                  disable_progress_bar=True)
        record(product, os.path.join(out, name), req)


ERA5 = "https://gcp-public-data-arco-era5.storage.googleapis.com/ar/full_37-1h-0p25deg-chunk-1.zarr-v3"


def era5():
    """3-hourly instantaneous u10/v10 cut from ARCO-ERA5's hourly global chunks, written directly
    as GridField float32 ([time][lat ascending][lon][east, north]) plus manifest, one file per year."""
    import numcodecs
    out = os.path.join(ROOT, "era5")
    meta = requests.get(ERA5 + "/.zmetadata", timeout=120).json()["metadata"]
    blosc = numcodecs.get_codec(meta["10m_u_component_of_wind/.zarray"]["compressor"])

    def chunk(name, key):
        r = requests.get(f"{ERA5}/{name}/{key}", timeout=300)
        r.raise_for_status()
        return np.frombuffer(blosc.decode(r.content), dtype="<f4")

    lat = np.frombuffer(numcodecs.get_codec(meta["latitude/.zarray"]["compressor"]).decode(
        requests.get(ERA5 + "/latitude/0", timeout=120).content), dtype="<f4") if meta["latitude/.zarray"]["compressor"] else None
    lon = np.arange(1440) * 0.25
    if lat is None:
        lat = np.frombuffer(requests.get(ERA5 + "/latitude/0", timeout=120).content, dtype="<f4")
    rows = np.where((lat >= -50) & (lat <= 0))[0]
    cols = np.where((lon >= 15) & (lon <= 120))[0]
    lat_sel, lon_sel = lat[rows][::-1].astype(float), lon[cols].astype(float)
    epoch = dt.datetime(1900, 1, 1)
    for a, b in year_windows(START, END + dt.timedelta(hours=21)):
        name = f"era5_u10_v10_3h_15-120E_50-0S_{a:%Y%m%d}-{b:%Y%m%d}"
        if os.path.exists(os.path.join(out, name + ".json")):
            continue
        floor_ok()
        hours = list(range(int((a - epoch).total_seconds() // 3600), int((b - epoch).total_seconds() // 3600) + 1, 3))
        hours = [h for h in hours if h % 3 == 0]

        def one(h):
            u = chunk("10m_u_component_of_wind", f"{h}.0.0").reshape(721, 1440)[np.ix_(rows, cols)][::-1]
            v = chunk("10m_v_component_of_wind", f"{h}.0.0").reshape(721, 1440)[np.ix_(rows, cols)][::-1]
            return np.stack([u, v], axis=-1)

        with cf.ThreadPoolExecutor(8) as ex:
            data = np.stack(list(ex.map(one, hours))).astype("<f4")
        data.tofile(os.path.join(out, name + ".f32"))
        times = [(epoch + dt.timedelta(hours=h)).replace(tzinfo=UTC).timestamp() for h in hours]
        manifest = dict(product="era5-wind10", component="Wind10m",
                        description=f"ERA5 u10/v10 3-hourly instantaneous from ARCO-ERA5 ({ERA5}), {a:%Y-%m-%d} to {b:%Y-%m-%d}",
                        lon=lon_sel.tolist(), lat=lat_sel.tolist(), time_unix_s=times, data_file=name + ".f32",
                        time_placement="instantaneous; values at their own times",
                        layout="[time][lat][lon][east, north] little-endian float32")
        json.dump(manifest, open(os.path.join(out, name + ".json"), "w"))
        record("era5", os.path.join(out, name + ".f32"), dict(source=ERA5, hours_since_1900=[hours[0], hours[-1]], step_h=3))
        record("era5", os.path.join(out, name + ".json"), dict(manifest_for=name + ".f32"))


NCSS = "https://thredds.nci.org.au/thredds/ncss/grid/gb6/BRAN/BRAN_2016/OFAM"


def bran2016():
    """Top-level (2.5 m) u and v, monthly files, through the NCI NetCDF Subset Service. BRAN2016 ends in August 2016."""
    out = os.path.join(ROOT, "bran2016")
    y, m = 2014, 3
    while (y, m) <= (2016, 8):
        for var in ("u", "v"):
            name = f"bran2016_ocean_{var}_2p5m_15-120E_50-0S_{y}_{m:02d}_daily.nc"
            path = os.path.join(out, name)
            if not os.path.exists(path):
                floor_ok()
                url = (f"{NCSS}/ocean_{var}_{y}_{m:02d}.nc?var={var}&north=0&south=-50&west=15&east=120"
                       f"&vertCoord=2.5&temporal=all&accept=netcdf4")
                for attempt in range(5):
                    try:
                        with requests.get(url, stream=True, timeout=600) as r:
                            r.raise_for_status()
                            with open(path + ".part", "wb") as f:
                                for b in r.iter_content(1 << 22):
                                    f.write(b)
                        break
                    except (requests.exceptions.ChunkedEncodingError, requests.exceptions.ConnectionError) as e:
                        print(json.dumps(dict(retry=name, attempt=attempt + 1, error=str(e)[:120])), flush=True)
                else:
                    sys.exit(f"{name}: failed after 5 attempts")
                os.replace(path + ".part", path)
                record("bran2016", path, dict(url=url))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


if __name__ == "__main__":
    which = sys.argv[1]
    os.makedirs(os.path.join(ROOT, which), exist_ok=True)
    if which == "glorys12":
        copernicus("glorys12", "cmems_mod_glo_phy_my_0.083deg_P1D-m", ["uo", "vo"], dt.datetime(2014, 5, 1),
                   "arco-geo-series", dict(minimum_depth=0.49, maximum_depth=0.5))
    elif which == "waverys":
        copernicus("waverys", "cmems_mod_glo_wav_my_0.2deg_PT3H-i", ["VSDX", "VSDY"], START, "arco-time-series", {})
    elif which == "era5":
        era5()
    elif which == "bran2016":
        bran2016()
    else:
        sys.exit(f"unknown product {which}")
