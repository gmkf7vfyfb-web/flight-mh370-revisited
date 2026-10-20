"""Fetch the static ocean inputs (ocean transport, item 3 of 9 Oct): GEBCO_2026 elevation and Type
Identifier grids (global, BODC via CEDA) and World Ocean Atlas 2023 1-degree temperature and salinity
(monthly 01-12 for the upper 1,500 m, seasonal 13-16 to the bottom; t_an/s_an with t_sd/s_sd) for the
decades 1995-2004 (95A4), 2005-2014 (A5B4) and 2015-2022 (B5C2), and the all-decade average (decav,
1955-2022) whose objectively analysed standard deviations supply the spread.

    python fetch_static.py gebco|woa23

Files go to /Users/pete/Downloads/mh370-ocean-data/<product>/, one JSON line per file in
fetch-log.jsonl (name, bytes, sha256, retrieval time, URL). Streams to a .part file and renames, so an
interrupted file is never mistaken for a complete one. Checks the 100 GiB floor before every file.
"""
import datetime as dt
import json
import os
import sys

import requests
from fetch_forcing import ROOT, floor_ok, record

GEBCO = [
    "https://dap.ceda.ac.uk/bodc/gebco/global/gebco_2026/ice_surface_elevation/netcdf/GEBCO_2026.nc",
    "https://dap.ceda.ac.uk/bodc/gebco/global/gebco_2026/type_identifier_grid/netcdf/gebco_2026_tid.nc",
]
WOA = "https://www.ncei.noaa.gov/thredds-ocean/fileServer/woa23/DATA/{var}/netcdf/{dec}/1.00/woa23_{dec}_{v}{tt:02d}_01.nc"


def get(product, url):
    out = os.path.join(ROOT, product)
    path = os.path.join(out, url.rsplit("/", 1)[-1])
    if os.path.exists(path):
        return
    floor_ok()
    with requests.get(url, stream=True, timeout=1800) as r:
        r.raise_for_status()
        with open(path + ".part", "wb") as f:
            for b in r.iter_content(1 << 22):
                f.write(b)
    os.replace(path + ".part", path)
    record(product, path, dict(url=url))


if __name__ == "__main__":
    which = sys.argv[1]
    os.makedirs(os.path.join(ROOT, which), exist_ok=True)
    if which == "gebco":
        for u in GEBCO:
            get("gebco", u)
    elif which == "woa23":
        for dec in ("95A4", "A5B4", "B5C2", "decav"):
            for var, v in (("temperature", "t"), ("salinity", "s")):
                for tt in range(1, 17):
                    get("woa23", WOA.format(var=var, dec=dec, v=v, tt=tt))
    else:
        sys.exit(f"unknown product {which}")
