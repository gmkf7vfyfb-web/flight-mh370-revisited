#!/usr/bin/env python3
"""Record the head commit, tree and size of each module branch (GitHub REST API; no merge, no blob download). 25 Oct 2026.
Usage: GITHUB_TOKEN=... python3 record_branches.py --work-head <sha> > data_homes/branches.json"""
import argparse, json, os, sys, urllib.request
R = "https://api.github.com/repos/gmkf7vfyfb-web/flight-mh370-revisited"
BR = ["core-request21", "core-tau-h", "core/composer", "core/composer-pass0", "core/composer-pass1", "core/composer-pass1-runc",
      "core/composer-views-run-j", "core/composer-views-run-j-oi", "core/ocean-transport", "hypothesis/debris-drift", "hypothesis/end-of-flight",
      "hypothesis/pleiades", "hypothesis/seabed-search", "hypothesis/settling", "architecture/module-briefs-oct06", "sept-29-chatgpt-advances", "main"]
def get(u):
    q = urllib.request.Request(u, headers={"Authorization": "Bearer " + os.environ["GITHUB_TOKEN"], "Accept": "application/vnd.github+json"})
    return json.load(urllib.request.urlopen(q, timeout=120))
ap = argparse.ArgumentParser(); ap.add_argument("--work-head", required=True); a = ap.parse_args()
out = {}
for b in BR:
    c = get(f"{R}/commits/{b}"); t = get(f"{R}/git/trees/{c['commit']['tree']['sha']}?recursive=1")
    bl = [x for x in t["tree"] if x["type"] == "blob"]; cmp_ = get(f"{R}/compare/{c['sha']}...{a.work_head}")
    out[b] = {"sha": c["sha"], "date": c["commit"]["committer"]["date"], "subject": c["commit"]["message"].splitlines()[0][:200],
              "tree_sha": c["commit"]["tree"]["sha"], "n_files": len(bl), "bytes": sum(x["size"] for x in bl), "truncated": t.get("truncated"),
              "vs_work": {"work_head": a.work_head, "status": cmp_.get("status"), "branch_commits_not_in_work": cmp_.get("behind_by"),
                          "work_commits_not_in_branch": cmp_.get("ahead_by")}}
json.dump(out, sys.stdout, indent=1)
