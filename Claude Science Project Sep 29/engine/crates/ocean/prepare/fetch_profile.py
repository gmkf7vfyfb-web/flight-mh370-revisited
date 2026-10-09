"""Fetch the GLORYS12V1 full-depth daily fields (uo, vo, thetao, so) and the static model bathymetry
(deptho, deptho_lev, mask) for `GridProfile`, settling's GLORYS12 ProfileSource.

Default window: settling's seabed window, 80-112 E, 45-18 S; daily means 7-14 March 2014 (labels at
00:00; each is the mean of that day, placed at label + 12 h by the converter, as for the surface
series). Credentials: COPERNICUS (user:password). Writes to <out>/ and appends sha256 to
<out>/fetch-log.jsonl.

python fetch_profile.py <out_dir> [start end]
"""
import hashlib, json, os, sys, datetime
import copernicusmarine as cm

out = sys.argv[1]
start, end = (sys.argv[2], sys.argv[3]) if len(sys.argv) > 3 else ("2014-03-07T00:00:00", "2014-03-14T00:00:00")
os.makedirs(out, exist_ok=True)
user, pw = os.environ["COPERNICUS"].strip().split(":", 1)
BOX = dict(minimum_longitude=80, maximum_longitude=112, minimum_latitude=-45, maximum_latitude=-18,
           minimum_depth=0.49, maximum_depth=5728.0)


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
    rec = dict(file=name, bytes=os.path.getsize(path), sha256=sha256(path), request=req,
               box=BOX, fetched_utc=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    with open(os.path.join(out, "fetch-log.jsonl"), "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps({k: rec[k] for k in ("file", "bytes", "sha256")}))


get("glorys12v1_static_bathy.nc", dataset_id="cmems_mod_glo_phy_my_0.083deg_static", dataset_part="bathy",
    variables=["deptho", "deptho_lev", "mask"])
get(f"glorys12v1_uo_vo_thetao_so_{start[:10].replace('-', '')}-{end[:10].replace('-', '')}.nc",
    dataset_id="cmems_mod_glo_phy_my_0.083deg_P1D-m", variables=["uo", "vo", "thetao", "so"],
    start_datetime=start, end_datetime=end, service="arco-geo-series")
