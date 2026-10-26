#!/usr/bin/env python3
"""Phase 2 (26 Oct 2026): compare the hydroacoustics entries of the merged registry with the hydro module registry.

For each entry: the multiset of (bytes, SHA-256) in the project manifest against the hydro manifest (built at the commit named
in modules/hydroacoustics/entries.yaml). The two builds hash in different ways (project: SHA256SUMS values for the exchange
folder, SHA256SUMS or a hash < 1 GB for data homes, git blobs for the module branch; hydro: a hash of every file), so a
difference shows either a stale SHA256SUMS entry, a file >= 1 GB that the project build does not hash, or a different file list.
Also checks every tracked file under results/hydroacoustics*, coordination/*hydro*, threads/*hydro* is in a manifest.
Writes modules/hydroacoustics/merge_check.json. No file is changed.
"""
import collections, gzip, json, subprocess
from pathlib import Path
import yaml

HERE = Path(__file__).resolve().parent
WN = "Claude Science Project Sep 29"


def rows(blob):
    return [l.split("\t") for l in blob.splitlines()[1:]]


def main():
    R = json.load(open(HERE / "REGISTRY.json"))
    meta = yaml.safe_load(open(HERE / "modules/hydroacoustics/entries.yaml"))
    c = meta["hydro_registry_commit"]
    top = HERE.parent.parent
    hreg = WN + "/engine/hypotheses/hydroacoustics/registry"
    H = {e["id"]: e for e in json.loads(subprocess.run(["git", "show", f"{c}:{hreg}/REGISTRY.json"], cwd=top, capture_output=True).stdout)["entries"]}
    out = collections.Counter(); diffs = []; sums_stale = []
    for e in R["entries"]:
        if e["module"] != "hydroacoustics":
            continue
        h = H[e["module_registry_id"]]
        if not e.get("manifest") or not h.get("manifest"):
            out["no manifest in one or both"] += 1
            if bool(e.get("manifest")) != bool(h.get("manifest")):
                diffs.append({"id": e["id"], "project_manifest": bool(e.get("manifest")), "hydro_manifest": bool(h.get("manifest"))})
            continue
        pm = rows(gzip.open(HERE / e["manifest"], "rt").read())
        hm = rows(gzip.decompress(subprocess.run(["git", "show", f"{c}:{hreg}/{h['manifest']}"], cwd=top, capture_output=True).stdout).decode())
        P = collections.Counter((int(x[1]), x[2]) for x in pm); Q = collections.Counter((int(x[1]), x[2]) for x in hm)
        if P == Q:
            out["same files, bytes and SHA-256"] += 1; continue
        out["differ"] += 1
        hb = {x[2]: x[0] for x in hm}
        d = {"id": e["id"], "project_files": len(pm), "hydro_files": len(hm),
             "only_in_project": len(list((P - Q).elements())), "only_in_hydro": len(list((Q - P).elements())),
             "project_not_hashed": [x[0] for x in pm if not x[2]]}
        hrel = {x[0]: x for x in hm}
        for x in pm:
            if not e.get("exchange_prefix"):
                continue   # SHA256SUMS values are used only for exchange entries
            k = x[0][len(e["exchange_prefix"]) + 1:]
            y = hrel.get(k)
            if y and y[2] and x[2] and y[2] != x[2] and len(x) > 3 and x[3].startswith("SHA256SUMS"):
                sums_stale.append({"file": x[0], "sha256_in_SHA256SUMS": x[2], "sha256_of_file": y[2], "sums_file": x[3].split(":", 1)[1]})
        diffs.append(d)
    tracked = [p for p in subprocess.run(["git", "ls-files", "-z"], cwd=top, capture_output=True, text=True).stdout.split("\0") if p]
    cov = set(json.load(open(HERE / "coverage_files.json"))["not_covered"])
    hyd = [p for p in tracked if p.startswith((WN + "/results/hydroacoustics", WN + "/coordination/HYDRO", WN + "/coordination/hydro", WN + "/threads/master-prompts/hydro", WN + "/threads/work-orders/hydro"))]
    res = {"hydro_registry_commit": c, "entries": sum(out.values()), "counts": dict(out), "differences": diffs,
           "sha256sums_entries_that_differ_from_the_file": sums_stale,
           "hydro_tracked_files": len(hyd), "hydro_tracked_files_not_in_a_manifest": sorted(p for p in hyd if p in cov)}
    json.dump(res, open(HERE / "modules/hydroacoustics/merge_check.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "differences"}, indent=1))
    for d in diffs:
        print(d)


if __name__ == "__main__":
    main()
