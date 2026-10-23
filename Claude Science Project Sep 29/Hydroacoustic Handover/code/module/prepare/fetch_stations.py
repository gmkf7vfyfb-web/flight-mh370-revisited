"""Rebuild data/stations.csv from one documented source: FDSN station metadata for network IM.

The archived configs disagreed with each other on station coordinates (brief section 11), so the
module takes every IMS hydrophone position from a single source, the FDSN station web service run
by EarthScope (formerly the IRIS DMC), at the epoch valid on 2014-03-08. Hydrophone depth is the
negative of the FDSN Elevation field. Triad centroids used by lib.rs are the plain mean of the three
elements, which is exact to well under a metre at a few-kilometre triad aperture.

Run: python prepare/fetch_stations.py   (writes data/stations.csv and prints the centroids)
"""

import csv
import datetime
import io
import pathlib
import urllib.request

URL = ("https://service.earthscope.org/fdsnws/station/1/query"
       "?net=IM&sta=H*&level=channel&format=text")
EPOCH = "2014-03-08T00:00:00"
TRIADS = ("H01W", "H08N", "H08S", "H11N", "H11S")
OUT = pathlib.Path(__file__).resolve().parents[1] / "data" / "stations.csv"


def main():
    text = urllib.request.urlopen(URL, timeout=120).read().decode()
    rows = list(csv.reader(io.StringIO(text), delimiter="|"))
    head = [h.strip().lstrip("#").strip() for h in rows[0]]
    keep = []
    for r in rows[1:]:
        d = dict(zip(head, r))
        sta, start, end = d["Station"], d["StartTime"], d["EndTime"]
        if d["Channel"] != "EDH" or sta[:4] not in TRIADS:
            continue
        if not (start <= EPOCH and (end == "" or end > EPOCH)):
            continue
        keep.append([sta, sta[:4], float(d["Latitude"]), float(d["Longitude"]),
                     -float(d["Elevation"]), float(d["SampleRate"]), start,
                     d["SensorDescription"].strip()])
    with OUT.open("w") as f:
        f.write("# IMS hydroacoustic triad elements valid on 2014-03-08, network IM.\n")
        f.write("# Source: FDSN station web service, EarthScope (formerly IRIS DMC), channel EDH,\n")
        f.write(f"#   {URL}\n")
        f.write(f"#   retrieved {datetime.date.today().isoformat()} by prepare/fetch_stations.py. "
                "hydrophone_depth_m = -Elevation (metres below sea level).\n")
        f.write("# H08 epochs in this source begin 2002-01-17: 2001 positions (Blackman air9) must "
                "come from UCRL-TR-207323 itself.\n")
        w = csv.writer(f)
        w.writerow(["element", "triad", "latitude_deg", "longitude_deg", "hydrophone_depth_m",
                    "sample_rate_hz", "epoch_start", "sensor"])
        for k in keep:
            w.writerow([k[0], k[1], f"{k[2]:.6f}", f"{k[3]:.6f}", f"{k[4]:.6f}", f"{k[5]:.6f}",
                        k[6], k[7]])
    for t in TRIADS:
        el = [k for k in keep if k[1] == t]
        lat = sum(k[2] for k in el) / len(el)
        lon = sum(k[3] for k in el) / len(el)
        print(f"{t}: n={len(el)} centroid {lat:.6f} {lon:.6f}")


if __name__ == "__main__":
    main()
