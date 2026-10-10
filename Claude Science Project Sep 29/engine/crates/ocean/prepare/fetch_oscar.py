"""Fetch OSCAR v2.0 Final daily surface currents (ESR / NASA PO.DAAC, doi:10.5067/OSCAR-25F20,
collection C2098858642-POCLOUD) for 7 March 2014 - 31 January 2017. Each global daily file is verified
against PO.DAAC's published md5, hashed (sha256), cut to the transport domain 15-120 E, 50-0 S and
appended to yearly f32 parts in the crate's GridField layout ([time][lat][lon][east, north], NaN at
land); then the global file is removed from the scratch directory. The time is placed at the file's
day at 12:00 UTC: the handbook gives the file time as centred on the day, and the label is kept.

OSCAR is a COMPARISON product (Pete, 9 Oct 2026): it is held to compare with prior work and is never a
value of the ocean-model alternative.

Credential NASA_EARTHDATA: either "user:password" (Earthdata Login redirect) or a bearer token.

python fetch_oscar.py <scratch_dir> <out_dir> [start end] [prior_md5.json]
"""
import datetime as dt, hashlib, json, os, sys, time
from urllib.parse import urlparse
import numpy as np, requests, h5py

scratch, out = sys.argv[1], sys.argv[2]
start = dt.date.fromisoformat(sys.argv[3]) if len(sys.argv) > 4 else dt.date(2014, 3, 7)
end = dt.date.fromisoformat(sys.argv[4]) if len(sys.argv) > 4 else dt.date(2017, 1, 31)
prior = json.load(open(sys.argv[5])) if len(sys.argv) > 5 else {}
os.makedirs(scratch, exist_ok=True); os.makedirs(out, exist_ok=True)
URL = "https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-protected/OSCAR_L4_OC_FINAL_V2.0/oscar_currents_final_{d}.nc"
MD5 = "https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-public/OSCAR_L4_OC_FINAL_V2.0/oscar_currents_final_{d}.nc.md5"
LON, LAT = (15.0, 120.0), (-50.0, 0.0)


class Session(requests.Session):
    AUTH = "urs.earthdata.nasa.gov"

    def rebuild_auth(self, prepared, response):
        h = prepared.headers
        if "Authorization" in h:
            a, b = urlparse(response.request.url).hostname, urlparse(prepared.url).hostname
            if a != b and self.AUTH not in (a, b):
                del h["Authorization"]


cred = os.environ["NASA_EARTHDATA"].strip()
s = Session()
if ":" in cred:
    s.auth = tuple(cred.split(":", 1))
else:
    s.headers["Authorization"] = f"Bearer {cred}"


def digest(path, algo):
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 24), b""):
            h.update(c)
    return h.hexdigest()


log = open(os.path.join(out, "fetch-log.jsonl"), "a")
parts, cur = {}, None
grid = None
d = start
while d <= end:
    tag = d.strftime("%Y%m%d")
    path = os.path.join(scratch, f"oscar_currents_final_{tag}.nc")
    for attempt in range(4):
        try:
            r = s.get(URL.format(d=tag), timeout=300, stream=True)
            r.raise_for_status()
            with open(path, "wb") as f:
                for c in r.iter_content(1 << 22):
                    f.write(c)
            md5_pub = s.get(MD5.format(d=tag), timeout=60).text.split()[0]
            md5 = digest(path, "md5")
            if md5 != md5_pub:
                raise RuntimeError(f"md5 mismatch {md5} vs published {md5_pub}")
            break
        except Exception as e:
            if attempt == 3:
                raise
            time.sleep(10 * (attempt + 1))
    sha = digest(path, "sha256")
    with h5py.File(path, "r") as f:
        lon, lat = f["lon"][:].astype(float), f["lat"][:].astype(float)
        lon = np.where(lon > 180, lon - 360, lon)
        i = np.where((lon >= LON[0]) & (lon <= LON[1]))[0]
        j = np.where((lat >= LAT[0]) & (lat <= LAT[1]))[0]
        def get(name):
            v = f[name]
            a = v[0].astype(np.float64)                    # (lon, lat) per the handbook layout check below
            dims = [x.decode() if isinstance(x, bytes) else x for x in [dd.label for dd in v.dims]]
            fill = v.attrs.get("_FillValue")
            if fill is not None:
                a[a == fill[0]] = np.nan
            a = a * float(v.attrs.get("scale_factor", 1.0)) + float(v.attrs.get("add_offset", 0.0))
            return a, v.dims
        u, _ = get("u"); v, _ = get("v")
        shape = f["u"].shape
        # Layout: the handbook gives (time, longitude, latitude); verify from the shape.
        assert shape[1] == len(lon) and shape[2] == len(lat), shape
        u, v = u[np.ix_(i, j)].T, v[np.ix_(i, j)].T   # -> (lat, lon)
        tv = f["time"]
        units = tv.attrs["units"].decode() if isinstance(tv.attrs["units"], bytes) else tv.attrs["units"]
        label = float(tv[0])
    if grid is None:
        grid = dict(lon=[round(x, 6) for x in lon[i].tolist()], lat=[round(x, 6) for x in lat[j].tolist()], time_units=units)
    year = d.year
    if year not in parts:
        parts[year] = dict(times=[], labels=[], file=open(os.path.join(out, f"oscar_v2_final_uv_{year}.f32"), "wb"))
    unit, _, epoch = units.partition(" since ")
    ymd = [int(x) for x in epoch.strip().split()[0].split("T")[0].split("-")]
    e = dt.datetime(*ymd, tzinfo=dt.timezone.utc).timestamp()
    sec = {"days": 86400.0, "hours": 3600.0, "seconds": 1.0}[unit.strip()]
    lab = e + label * sec
    # The file's time is "centered on the day" (handbook); place every value at 12:00 UTC of its day,
    # whatever the label's hour, and keep the label for the record.
    centre = np.floor(lab / 86400.0) * 86400.0 + 43200.0
    assert dt.datetime.fromtimestamp(centre, dt.timezone.utc).date() == d, (lab, d)
    parts[year]["labels"].append(lab); parts[year]["times"].append(centre)
    np.stack([u, v], axis=-1).astype("<f4").tofile(parts[year]["file"])
    rec = dict(file=os.path.basename(path), bytes=os.path.getsize(path), md5=md5, md5_published=md5_pub, sha256=sha,
               md5_matches_prior_work=(prior.get(d.isoformat()) == md5) if prior.get(d.isoformat()) else None,
               time_label_utc=dt.datetime.fromtimestamp(lab, dt.timezone.utc).isoformat(),
               fetched_utc=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    log.write(json.dumps(rec) + "\n"); log.flush()
    os.remove(path)
    if d.day == 1 or d == start:
        print(json.dumps(dict(day=tag, sha256=sha[:12], label=rec["time_label_utc"], prior_md5=rec["md5_matches_prior_work"])), flush=True)
    d += dt.timedelta(days=1)
names = []
for year, p in sorted(parts.items()):
    p["file"].close()
    stem = f"oscar_v2_final_uv_{year}"
    json.dump(dict(product="oscar-v2-final", component="Current",
                   description=f"OSCAR v2.0 Final total current u/v (upper ~30 m), {year}, cut to 15-120E 50-0S; COMPARISON product",
                   lon=grid["lon"], lat=grid["lat"], time_unix_s=p["times"], time_placement="12:00 UTC of the averaged day (the file time is centred on the day)",
                   time_labels_unix_s=p["labels"], data_file=stem + ".f32",
                   layout="[time][lat][lon][east, north] little-endian float32, NaN = land"), open(os.path.join(out, stem + ".json"), "w"))
    names.append(stem + ".json")
json.dump(dict(parts=names), open(os.path.join(out, "oscar_v2_final_uv.series.json"), "w"))
print(json.dumps(dict(parts=names, days=(end - start).days + 1)))
