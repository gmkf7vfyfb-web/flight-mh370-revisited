"""Merge the wave-3 DB rows from three tracks into one import set with unique ids.

Each track numbered its new rows from CV26 / OB07, so the ids collide. This script
gives every row a unique id that follows the base package (CV01-CV25, OB01-OB06),
keeps the track's own id in column `track_local_id`, and remaps id references in
db_impact_case_AC05_update.csv. Values are not changed.
Order: propagation check (keeps CV26-CV31, OB07-OB63), then Transair 810, then F-35A raw ridge.
"""
import re, sys
from pathlib import Path
import pandas as pd

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
pkg = Path(sys.argv[2]) if len(sys.argv) > 2 else None
out = root / "db-rows-merged"

cv_src = [("propagation-level-check", "propagation-level-check/db_coupling_value_new_rows.csv"),
          ("transair-810", "transair-810/db_coupling_value_new_rows.csv"),
          ("f35a-raw-ridge", "f35a-raw-ridge/f35a-raw-coupling-rows.csv")]
ob_src = [("propagation-level-check", "propagation-level-check/db_received_observation.csv"),
          ("f35a-raw-ridge", "f35a-raw-ridge/f35a-raw-received-observation-rows.csv"),
          ("transair-810", "transair-810/db_received_observation_new_rows.csv")]

def merge(src, idcol, prefix, start, width, skip_ids=()):
    rows, maps, n = [], {}, start
    for track, rel in src:
        d = pd.read_csv(root / rel)
        d = d[~d[idcol].isin(skip_ids)].copy()      # base rows repeated by a track
        m = {}
        for old in d[idcol]:
            m[old] = f"{prefix}{n:0{width}d}"; n += 1
        d.insert(1, "track_local_id", d[idcol]); d.insert(2, "track", track)
        d[idcol] = d[idcol].map(m)
        maps[track] = m; rows.append(d)
    return pd.concat(rows, ignore_index=True), maps

base_ob = [f"OB{i:02d}" for i in range(1, 7)]
cv, cvmap = merge(cv_src, "value_id", "CV", 26, 2)
ob, obmap = merge(ob_src, "obs_id", "OB", 7, 2, skip_ids=base_ob)
cv.to_csv(out / "db_coupling_value_wave3.csv", index=False)
ob.to_csv(out / "db_received_observation_wave3.csv", index=False)

ac = (root / "transair-810/db_impact_case_AC05_update.csv").read_text()
ac = re.sub(r"\bCV\d+\b", lambda x: cvmap["transair-810"].get(x.group(0), x.group(0)), ac)
(out / "db_impact_case_AC05_update.csv").write_text(ac)

idmap = pd.DataFrame([(t, "value_id", a, b) for t, m in cvmap.items() for a, b in m.items()] +
                     [(t, "obs_id", a, b) for t, m in obmap.items() for a, b in m.items()],
                     columns=["track", "column", "track_local_id", "merged_id"])
idmap.to_csv(out / "id-map.csv", index=False)
print(len(cv), "coupling rows", cv.value_id.iloc[0], "-", cv.value_id.iloc[-1])
print(len(ob), "observation rows", ob.obs_id.iloc[0], "-", ob.obs_id.iloc[-1])
assert cv.value_id.is_unique and ob.obs_id.is_unique
