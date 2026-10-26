#!/usr/bin/env python3
"""Phase 2 (26 Oct 2026): bring the hydroacoustics module registry into the project registry as module "hydroacoustics".

Input: the hydro registry at one commit of branch hypothesis/hydroacoustics (entries.yaml, entries-phase2.yaml, REGISTRY.json,
manifests, memory-notes/index.json), read with `git show <commit>:<path>` so that the result ties to that commit.
Output (generated; do not edit by hand):
  modules/hydroacoustics/entries.yaml     entries in the project schema, ids hydro.<hydro id>
  modules/hydroacoustics/constants.json   the hydro constants (values, status, source quote) as in the hydro registry
  modules/hydroacoustics/platform_artifacts.tsv  latest artifact versions of the three hydro threads of 23-25 Oct and the
                                          registered file with the same SHA-256 ("no copy" if none)
  registry_spec.json                      module "hydroacoustics" and the hydro defects (ids hydro.Dnn) are added
Roots: WORK -> WORK; EX:x -> EX:hydroacoustics/x; EOF:x -> EX:end-of-flight/x (not hashed; owned by end of flight);
INPUTS:x -> DL:mh370-inputs/hydroacoustics/x; OCEAN:x -> DL:mh370-ocean-data/x; MOD:x -> GIT:hypothesis/hydroacoustics@<commit>:<path>.
Status: the hydro registry gives it (rank module_registry, evidence = the status line of the entry in entries.yaml at <commit>);
for phase-2 entries the rank and evidence of entries-phase2.yaml are kept.
Usage: python3 import_hydro_registry.py --hydro-commit <sha> [--artifacts <thread_artifacts.json>] [--repo <repo top>]
"""
import argparse, collections, gzip, io, json, os, re, subprocess
from pathlib import Path
import yaml

HERE = Path(__file__).resolve().parent
WN = "Claude Science Project Sep 29"
HMOD = WN + "/engine/hypotheses/hydroacoustics"
HREG = HMOD + "/registry"
BR = "hypothesis/hydroacoustics"
THREADS = {"c764a583-f184-4087-b4ce-19c3b8a19483": "c764a583 (Aircraft Impact Acoustic Source Survey)",
           "c0b15646-883a-4dcf-811b-7a832a957069": "c0b15646 (Hydroacoustic Site Noise Characterization Review)",
           "9e0bf4fe-ff5d-4fc3-baee-4872ad64dc96": "9e0bf4fe (Hydroacoustic Data Inventory Review)"}


def git(top, *a, binary=False):
    env = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null"}
    r = subprocess.run(["git", *a], cwd=top, capture_output=True, env=env)
    if r.returncode:
        raise RuntimeError(r.stderr.decode()[:300])
    return r.stdout if binary else r.stdout.decode()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--hydro-commit", required=True); ap.add_argument("--artifacts"); ap.add_argument("--repo")
    a = ap.parse_args()
    top = Path(a.repo or git(HERE, "rev-parse", "--show-toplevel").strip()).resolve()
    c = git(top, "rev-parse", a.hydro_commit + "^{commit}").strip()
    show = lambda p: git(top, "show", f"{c}:{p}")
    ent_txt = show(HREG + "/entries.yaml")
    spec_h = yaml.safe_load(ent_txt)
    ph2 = yaml.safe_load(show(HREG + "/entries-phase2.yaml"))
    reg = json.loads(show(HREG + "/REGISTRY.json"))
    mi = json.loads(show(HREG + "/memory-notes/index.json"))
    built = {e["id"]: e for e in reg["entries"]}
    src = {e["id"]: e for e in spec_h["entries"] + ph2["entries"]}
    lines = ent_txt.splitlines()
    gitref = lambda p: f"GIT:{BR}@{c}:{p}"

    def status_line(i):
        ln = next(k for k, l in enumerate(lines, 1) if l.strip() == f"- id: {i}")
        sl = next(k for k in range(ln, ln + 12) if lines[k - 1].strip().startswith("status:"))
        return sl, lines[sl - 1].strip()

    def conv_src(s):
        root, _, rel = s.partition(":")
        if root == "MOD":
            return gitref(HMOD + "/" + rel)
        if root == "EX":
            return "EX:hydroacoustics/" + rel
        if root == "EOF":
            return "EX:end-of-flight/" + rel
        return s

    out = []
    for e in spec_h["entries"] + ph2["entries"]:
        b = built[e["id"]]
        root, _, rel = e["path"].partition(":")
        r = {"id": "hydro." + e["id"], "module_registry_id": e["id"], "kind": e["kind"], "module": "hydroacoustics", "note": b.get("note") or "",
             "assignment_basis": "hydro module registry (phase 2)", "defects": ["hydro." + d for d in e.get("defects", [])],
             "superseded_by": ("hydro." + e["superseded_by"]) if e.get("superseded_by") else None, "inputs": [],
             "producing_thread": e.get("producing_thread"), "verified_this_run": bool(e.get("verified_this_run")), "status": e["status"],
             "module_registry_manifest_sha256": b.get("manifest_sha256")}
        if root == "WORK":
            r["path"] = f"WORK:{rel}"
            if e.get("file_list"):
                r["file_list"] = [f"{rel.rstrip('/')}/{f}" for f in e["file_list"]]
        elif root == "EX":
            r["path"] = "EX:hydroacoustics/" + rel if rel else "EX:hydroacoustics"
            if rel and e.get("hash", True) is not False:
                r["exchange_prefix"] = "hydroacoustics/" + rel.rstrip("/")
                r["exchange_top_files_only"] = False
                if e.get("file_list"):
                    r["exchange_file_list"] = e["file_list"]
            else:
                r["hash"] = False; r["hash_note"] = e.get("hash_note", "not hashed")
        elif root == "EOF":
            r["path"] = "EX:end-of-flight/" + rel; r["hash"] = False
            r["hash_note"] = e.get("hash_note", "owned by end of flight; not hashed here")
        elif root in ("INPUTS", "OCEAN"):
            r["path"] = ("DL:mh370-inputs/hydroacoustics/" if root == "INPUTS" else "DL:mh370-ocean-data/") + rel
            r["hash"] = "stat+lt1g"
            r["hash_note"] = "SHA-256 from SHA256SUMS files where present, else computed for files < 1 GB; files >= 1 GB with no SHA256SUMS entry are listed, not hashed"
        elif root == "MOD":
            r["path"] = f"GIT:{BR}@{c}"
            r["git_path"] = HMOD + "/" + rel
            r["hash"] = "git"
            r["hash_note"] = "files of the module branch at the commit; SHA-256 of each blob"
        elif root == "XDRIVE":
            r["path"] = e["path"]; r["hash"] = False; r["hash_note"] = e.get("hash_note", "external drive not mounted in this session")
        else:
            raise ValueError(f"{e['id']}: unknown root {root}")
        if e.get("status_evidence"):
            r["status_rank"] = e.get("status_rank", "readme")
            r["status_evidence"] = [{**x, "source": conv_src(x["source"])} for x in e["status_evidence"]]
        elif e["status"] != "UNCHECKED":
            sl, q = status_line(e["id"])
            r["status_rank"] = "module_registry"
            r["status_evidence"] = [{"rank": "module_registry", "source": gitref(HREG + "/entries.yaml") + f":{sl}", "quote": q,
                                     "basis": "status set in the hydro registry of the 23 Oct 2026 hydro clean-up run (Pete approved the run) and later sessions; "
                                              "the hydro registry quotes the defining lines and lists the defects"}]
        else:
            r["status_rank"] = "none"; r["status_evidence"] = []
        for k in ("status_note", "companion_of", "handoff_manifest"):
            if e.get(k):
                r[k] = ("hydro." + e[k]) if k == "companion_of" else e[k]
        d = b.get("definition") or {}
        if d.get("file"):
            r["definition"] = {"file": conv_src(d["file"]), "lines": d["lines"], "quote": (d.get("quote") or "")[:400]}
        mids = mi["links"].get(e["id"])
        if mids:
            r["memory_notes"] = {"n_rows": len(mids), "mem_ids": mids, "where": gitref(HREG + "/memory-notes/"),
                                 "nature": "records of what memory said; not verified facts"}
        out.append(r)
    # ---------- platform artifacts of the three threads ----------
    shamap = collections.defaultdict(list)
    for e in reg["entries"]:
        if e.get("manifest"):
            body = gzip.decompress(git(top, "show", f"{c}:{HREG}/{e['manifest']}", binary=True)).decode()
            for l in body.splitlines()[1:]:
                p = l.split("\t")
                if len(p) >= 3 and p[2]:
                    shamap[p[2]].append(("hydro." + e["id"], p[0]))
    hh = HERE / "modules/project/manifests/project.archive.hydroacoustic-handover.tsv.gz"
    if hh.exists():   # the Hydroacoustic Handover archive is a project entry (registered in phase 1)
        for l in gzip.open(hh, "rt").read().splitlines()[1:]:
            p = l.split("\t")
            if len(p) >= 3 and p[2]:
                shamap[p[2]].append(("project.archive.hydroacoustic-handover", p[0]))
    pa_rows, per = [], collections.defaultdict(list)
    if a.artifacts:
        for x in sorted(json.load(open(a.artifacts)), key=lambda x: (x["root_frame_id"], x["filename"])):
            if x["version_id"] != x["latest_version_id"]:
                continue
            hits = shamap.get(x["checksum"], [])
            pa_rows.append([THREADS[x["root_frame_id"]][:8], x["artifact_id"], x["version_id"], x["filename"], str(x["size_bytes"]), x["checksum"],
                            ";".join(f"{i}:{p}" for i, p in hits[:3]) or "no copy"])
            for i, p in hits[:1]:
                per[i].append(x["version_id"])
        with open(HERE / "modules/hydroacoustics/platform_artifacts.tsv", "w") as fh:
            fh.write("thread\tartifact_id\tversion_id\tfilename\tbytes\tsha256\tregistered_copy (entry:relpath)\n")
            for row in pa_rows:
                fh.write("\t".join(row) + "\n")
        for r in out:
            if per.get(r["id"]):
                r["platform_artifacts"] = {"n": len(per[r["id"]]), "where": "registry/modules/hydroacoustics/platform_artifacts.tsv",
                                           "note": "latest artifact versions of the 23-25 Oct hydro threads with the same SHA-256 as a file of this entry"}
    d = HERE / "modules" / "hydroacoustics"; d.mkdir(parents=True, exist_ok=True)
    yaml.safe_dump({"registry_version": f"hydroacoustics registry v1 phase 2 (2026-10-26), from {BR}@{c[:12]}", "module": "hydroacoustics",
                    "generated_by": "registry/import_hydro_registry.py (do not edit by hand; change the hydro registry and run again)",
                    "hydro_registry_commit": c, "entries": sorted(out, key=lambda x: x["id"])}, open(d / "entries.yaml", "w"), sort_keys=False, allow_unicode=True, width=160)
    json.dump({"from": f"{BR}@{c}:{HREG}/REGISTRY.json", "constant_status_values": reg["constant_status_values"], "constants": reg["constants"]},
              open(d / "constants.json", "w"), indent=1, ensure_ascii=False)
    spec = json.load(open(HERE / "registry_spec.json"))
    if "hydroacoustics" not in spec["modules"]:
        spec["modules"].append("hydroacoustics")
    spec["defects"] = [x for x in spec["defects"] if not x["id"].startswith("hydro.")]
    for x in reg["defects"]:
        ev = x.get("evidence") or [{}]
        f0 = ev[0]
        spec["defects"].append({"id": "hydro." + x["id"], "statement": f"{x.get('title', '')}. {x.get('what', '')}".strip(),
                                "evidence": {"file": conv_src(f0["file"]) if f0.get("file") else None, "line": (f0.get("lines") or [None])[0]},
                                "module_registry": gitref(HREG + "/REGISTRY.json")})
    spec["external_registries"] = [{"module": "hydroacoustics", "where": f"branch {BR}: {HREG}/REGISTRY.json",
                                    "note": f"Merged here as module hydroacoustics (phase 2, 26 Oct 2026) from commit {c}. The hydro registry stays the module's own record; its loader registry.py reads it."}]
    json.dump(spec, open(HERE / "registry_spec.json", "w"), indent=1, ensure_ascii=False)
    print(json.dumps({"hydro_commit": c, "entries": len(out), "status": collections.Counter(x["status"] for x in out),
                      "defects": len(reg["defects"]), "constants": len(reg["constants"]), "platform_artifacts_latest": len(pa_rows),
                      "with_copy": sum(1 for x in pa_rows if x[-1] != "no copy")}, indent=1, default=str))


if __name__ == "__main__":
    main()
