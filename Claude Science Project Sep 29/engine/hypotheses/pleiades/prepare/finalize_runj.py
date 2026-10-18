"""Finish the Pléiades run J exchange directory after score_runj.py (and score_runj_joined.py): surfaces copy, reader.py,
SHA256SUMS (each column file re-hashed and compared with the hash taken at write time), build-stats.json, a READY per complete
stratum, then README.md and the top-level READY last.

    python finalize_runj.py WORKDIR EXCHANGE_OUT README_TEXT_FILE
"""
import json
import shutil
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE))
import score_runj as SR  # noqa: E402
import build_columns as BC  # noqa: E402

EXPECT = {("prod", "run-j-waypoints"): 24, ("prod", "run-j-free"): 18, ("prod", "run-j-descent-climb"): 16,
          ("prod", "run-j-repro-radar"): 16, ("both", "run-j-waypoints"): 8}


def main(work, exch, readme):
    work, exch = Path(work), Path(exch)
    (exch / "surfaces").mkdir(parents=True, exist_ok=True)
    for f in sorted(SR.SURF.iterdir()):
        if f.suffix in (".f32", ".toml") and "gcdc" not in f.name:
            shutil.copy2(f, exch / "surfaces" / f.name)
    (exch / "reader.py").write_text(BC.READER)
    sums, stats, bad, per = [], [], [], {}
    for f in sorted(work.glob("*.npz")):
        if "partial" in f.name:
            continue
        z = np.load(f); r = json.loads(str(z["res"]))
        if f.name.startswith("joined_"):
            for stat, line in r.get("columns") or []:
                rel = line.split("  ", 1)[1]; p = exch / "joined-v2" / rel
                h = BC.sha(p); ok = h == line.split("  ", 1)[0] and len(np.load(p, mmap_mode="r")) == stat["rows"]
                (sums if ok else bad).append(f"{h}  joined-v2/{rel}"); stats.append(dict(stat, set="joined-v2"))
                per.setdefault(("joined", stat["stratum"]), []).append(ok)
            continue
        key = (r["set"], r["stratum"])
        if r["sha256"] is None:
            stats.append(dict(r["columns_stat"], set=r["set"])); per.setdefault(key, []).append(False); continue
        rel = r["sha256"].split("  ", 1)[1]; pre = "" if r["set"] == "prod" else "both-burst/"
        p = exch / pre / rel
        h = BC.sha(p); ok = h == r["sha256"].split("  ", 1)[0] and len(np.load(p, mmap_mode="r")) == r["rows"]
        (sums if ok else bad).append(f"{h}  {pre}{rel}")
        stats.append(dict(r["columns_stat"], set=r["set"])); per.setdefault(key, []).append(ok)
    sums += [f"{BC.sha(p)}  surfaces/{p.name}" for p in sorted((exch / "surfaces").iterdir())]
    sums.append(f"{BC.sha(exch / 'reader.py')}  reader.py")
    (exch / "SHA256SUMS").write_text("\n".join(sorted(sums, key=lambda l: l.split("  ", 1)[1])) + "\n")
    bs = dict(per_seed=stats, surfaces=str(SR.SURF), grid=dict(lon0=78.025, lat0=-44.975, nlon=740, nlat=800, step=0.05),
              stratum_codes={**BC.FAMILY_CODE, **BC.JOINED_CODE}, hash_mismatch=bad,
              max_not_computed_prior_weight_share=max((s.get("not_computed_prior_weight_share", 0.0) for s in stats), default=None))
    (exch / "build-stats.json").write_text(json.dumps(bs, indent=1))
    ready = {}
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    for key, oks in per.items():
        want = EXPECT.get(key)
        d = (exch / key[1]) if key[0] == "prod" else (exch / "both-burst" / key[1]) if key[0] == "both" else (exch / "joined-v2" / key[1])
        full = all(oks) and (want is None or len(oks) == want)
        ready[f"{key[0]}/{key[1]}"] = dict(seeds=len(oks), with_columns=sum(oks), complete=full)
        if full and d.exists():
            (d / "READY").write_text(f"{now} {len(oks)} seeds\n")
    shutil.copy2(readme, exch / "README.md")
    if not bad:
        (exch / "READY").write_text(f"{now}\n" + json.dumps(ready) + "\n")
    print(json.dumps(ready, indent=1), "hash mismatches:", len(bad))
    return ready, bad


if __name__ == "__main__":
    main(*sys.argv[1:4])
