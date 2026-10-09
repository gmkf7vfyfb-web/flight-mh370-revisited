"""Fetch Copernicus-GlobCurrent (MULTIOBS_GLO_PHY_MYNRT_015_003, multi-year, v202411) total surface
current at 0 m over the transport domain 15-120 E, 50-0 S: hourly instantaneous for the Pleiades /
COSMO window (7-31 March 2014) and daily means with their uncertainties for the drift period
(7 March 2014 - 31 January 2017). Total = altimetric geostrophic + empirical Ekman (ERA5 wind stress)
+ barotropic tide (QUID CMEMS-MOB-QUID-015-003). Credentials: COPERNICUS (user:password).

python fetch_globcurrent.py <out_dir>
"""
import hashlib, json, os, sys, datetime
import copernicusmarine as cm

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
user, pw = os.environ["COPERNICUS"].strip().split(":", 1)
BOX = dict(minimum_longitude=15, maximum_longitude=120, minimum_latitude=-50, maximum_latitude=0, minimum_depth=0, maximum_depth=0)


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 24), b""):
            h.update(c)
    return h.hexdigest()


def get(name, **req):
    path = os.path.join(out, name)
    cm.subset(**req, **BOX, username=user, password=pw, output_directory=out, output_filename=name,
              overwrite=True, disable_progress_bar=True)
    rec = dict(file=name, bytes=os.path.getsize(path), sha256=sha256(path), request=req, box=BOX,
               fetched_utc=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    with open(os.path.join(out, "fetch-log.jsonl"), "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps({k: rec[k] for k in ("file", "bytes", "sha256")}), flush=True)


get("globcurrent_my_pt1h_uo_vo_0m_20140307-20140331.nc", dataset_id="cmems_obs-mob_glo_phy-cur_my_0.25deg_PT1H-i",
    dataset_version="202411", variables=["uo", "vo"], start_datetime="2014-03-07T00:00:00", end_datetime="2014-03-31T23:00:00")
get("globcurrent_my_p1d_uo_vo_err_0m_20140307-20170131.nc", dataset_id="cmems_obs-mob_glo_phy-cur_my_0.25deg_P1D-m",
    dataset_version="202411", variables=["uo", "vo", "err_uo", "err_vo"], start_datetime="2014-03-07T00:00:00", end_datetime="2017-01-31T00:00:00")
