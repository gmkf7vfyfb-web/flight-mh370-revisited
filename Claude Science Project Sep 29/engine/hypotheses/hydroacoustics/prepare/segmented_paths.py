"""RETIRED 2026-10-09: superseded by the shared export fix (ocean_paths load window from the geodesic, merge
61b50a5). Re-export of all 44 paths with the fixed binary reproduces this script's rejoined output exactly
(same sample count, 0.0 m depth difference everywhere; data/ocean_paths/export_fix_check.json). Kept for
provenance of the stage B inputs, which it produced.

Consumer-side workaround for the shared ocean transport's path export (engine/crates/ocean
examples/ocean_paths.rs), which loads bathymetry only in a window of +/-1 deg around the two ENDPOINTS'
latitude/longitude range. A geodesic that bows outside that box (e.g. impact -> Portland reaches ~43 S while
both ends are near 38.5 S) silently loses its samples there (2,500-3,700 km gaps found 9 Oct 2026). Reported
to ocean transport; this script does not modify their crate.
Each requested path is split into consecutive WGS84 geodesic segments of SEG_M (a multiple of
profile_every_m, so sound-speed nodes stay on one grid), exported with the unchanged example binary, and
joined: bathymetry s_m offset by the segment start, the duplicate first sample of each later segment dropped;
sound-speed nodes renumbered globally, the duplicate node 0 of each later segment dropped. The joined
<name>_meta.json records the segmentation. Every output is checked for gaps > 1 km.
Usage: python segmented_paths.py <request.json> <example_binary> <work_dir> <out_dir> [name ...]"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Geod

SEG_M = 400_000.0
G = Geod(ellps="WGS84")


def main(req_path, binary, work, out, names):
    req = json.loads(Path(req_path).read_text())
    work, out = Path(work), Path(out)
    work.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    paths = [p for p in req["paths"] if not names or p["name"] in names]
    segs, plan = [], {}
    for p in paths:
        az, _, L = G.inv(p["a"][0], p["a"][1], p["b"][0], p["b"][1])
        assert SEG_M % p["profile_every_m"] == 0
        n = int(np.ceil(L / SEG_M))
        pts = [p["a"]] + [list(G.fwd(p["a"][0], p["a"][1], az, k * SEG_M)[:2]) for k in range(1, n)] + [p["b"]]
        plan[p["name"]] = dict(n=n, L=L)
        for k in range(n):
            segs.append(dict(p, name=f"{p['name']}__{k:03d}", a=pts[k], b=pts[k + 1]))
    sreq = work / "segments_request.json"
    sreq.write_text(json.dumps(dict(bathymetry=req["bathymetry"], soundspeed_dir=req["soundspeed_dir"], paths=segs)))
    subprocess.run([binary, str(sreq), str(work / "seg")], check=True, capture_output=True)
    for p in paths:
        nm, n = p["name"], plan[p["name"]]["n"]
        bs, ss, per = [], [], int(SEG_M / p["profile_every_m"])
        for k in range(n):
            b = pd.read_csv(work / "seg" / f"{nm}__{k:03d}_bathymetry.csv").copy()
            s = pd.read_csv(work / "seg" / f"{nm}__{k:03d}_soundspeed.csv").copy()
            if k < n - 1:                       # float length can add a node past SEG_M; keep 0..per only
                s = s[s.node <= per].copy()
                b = b[b.s_m <= SEG_M + 1.0].copy()
            b["s_m"] = b["s_m"] + k * SEG_M
            s["s_m"] = s["s_m"] + k * SEG_M
            s["node"] = s["node"] + k * per
            bs.append(b); ss.append(s)
        b = pd.concat(bs, ignore_index=True).sort_values("s_m", kind="stable")
        b = b[~b.s_m.round(0).duplicated(keep="first")].reset_index(drop=True)
        s = pd.concat(ss, ignore_index=True).sort_values(["node", "depth_m"], kind="stable")
        s = s[~s.duplicated(["node", "depth_m"], keep="first")].reset_index(drop=True)
        assert not s.duplicated(["node", "depth_m"]).any(), nm
        assert np.all(np.diff(b.s_m.values) > 0), nm
        g = np.diff(b.s_m.values)
        assert g.max() <= 1000.0 and abs(b.s_m.max() - plan[nm]["L"]) < 1000.0, (nm, g.max(), b.s_m.max(), plan[nm]["L"])
        b.to_csv(out / f"{nm}_bathymetry.csv", index=False)
        s.to_csv(out / f"{nm}_soundspeed.csv", index=False)
        m0 = json.loads((work / "seg" / f"{nm}__000_meta.json").read_text())
        m0.update(name=nm, a=p["a"], b=p["b"], geodesic_length_m=plan[nm]["L"], segmented=dict(n=n, seg_m=SEG_M, reason="endpoint-window bathymetry gaps in ocean_paths.rs"))
        (out / f"{nm}_meta.json").write_text(json.dumps(m0, indent=1))
        print(nm, n, "segments", round(plan[nm]["L"] / 1e3, 1), "km; max gap", round(g.max(), 1), "m")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5:])
