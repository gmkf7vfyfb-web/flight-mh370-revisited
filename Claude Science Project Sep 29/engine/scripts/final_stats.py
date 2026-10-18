"""Weighted summary of one seed's final.npy (standard library only, for deskstar): ln-weight-free quantities used by the
run-J supplement re-allocation check. Columns: filter::FINAL_COLUMNS (weight 0, latitude 1, longitude 2, stratum 12).
    python3 final_stats.py <seed dir> [out.json]   (default <seed dir>/final-stats.json)"""
import sys, os, json, struct, ast
from array import array
d = sys.argv[1]; p = os.path.join(d, "final.npy")
with open(p, "rb") as f:
    assert f.read(6) == b"\x93NUMPY"; major = f.read(2)[0]
    n = struct.unpack("<H" if major == 1 else "<I", f.read(2 if major == 1 else 4))[0]
    hdr = ast.literal_eval(f.read(n).decode("latin1")); assert hdr["descr"] == "<f4" and not hdr["fortran_order"]
    a = array("f"); a.frombytes(f.read())
rows, cols = hdr["shape"]; w = a[0::cols]; lat = a[1::cols]; lon = a[2::cols]; st = a[12::cols]
W = sum(w); out = {"rows": rows, "weight_sum": W}
out["mean_lat"] = sum(x * y for x, y in zip(w, lat)) / W; out["mean_lon"] = sum(x * y for x, y in zip(w, lon)) / W
out["north_of_33S"] = sum(x for x, y in zip(w, lat) if y > -33.0) / W; out["north_of_30S"] = sum(x for x, y in zip(w, lat) if y > -30.0) / W
out["shoulder_34p5_36p5"] = sum(x for x, y in zip(w, lat) if -36.5 <= y <= -34.5) / W
order = sorted(range(rows), key=lambda i: lat[i]); c = 0.0; q = {}
for i in order:
    c += w[i] / W
    for k in (0.025, 0.5, 0.975):
        if k not in q and c >= k: q[k] = lat[i]
out["lat_q025"], out["lat_median"], out["lat_q975"] = q[0.025], q[0.5], q[0.975]
out["stratum_mass"] = [sum(x for x, s in zip(w, st) if int(s) == m) / W for m in range(5)]
json.dump(out, open(sys.argv[2] if len(sys.argv) > 2 else os.path.join(d, "final-stats.json"), "w"), indent=1); print(json.dumps(out))
